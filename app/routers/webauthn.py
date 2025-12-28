import base64
import io
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fido2 import cbor
from fido2.cose import CoseKey
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import Aaguid, AttestedCredentialData, PublicKeyCredentialRpEntity
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PendingSIMSwap, RealTimeLog, User, UserAccessControl, UserAuthLog, UserRole, WebAuthnCredential
from app.security import get_jwt_identity, verify_session_fingerprint
from utils.email_alerts import send_admin_alert, send_user_alert
from utils.location import get_ip_location
from utils.security import hash_token

router = APIRouter(tags=["WebAuthn"])
templates = Jinja2Templates(directory="templates")

rp = PublicKeyCredentialRpEntity(id="localhost.localdomain.com", name="ZTN Local")
webauthn_server = Fido2Server(rp)


def jsonify_webauthn(data):
    def convert(value):
        if isinstance(value, bytes):
            return websafe_encode(value).decode()
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items() if k != "_field_keys"}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return convert(data)


@router.post("/webauthn/register-begin", dependencies=[Depends(verify_session_fingerprint)])
def begin_registration(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(",") if c.transports else [],
            "type": "public-key",
        }
        for c in user.webauthn_credentials
    ]

    registration_data, state = webauthn_server.register_begin(
        {
            "id": str(user.id).encode(),
            "name": user.email,
            "displayName": f"{user.first_name} {user.last_name or ''}".strip(),
        },
        credentials,
    )

    request.session["webauthn_register_state"] = state
    public_key = jsonify_webauthn(registration_data["publicKey"])
    return {"public_key": public_key}


@router.post("/webauthn/register-complete", dependencies=[Depends(verify_session_fingerprint)])
def complete_registration(payload: dict, request: Request, db: Session = Depends(get_db)):
    state = request.session.get("webauthn_register_state")
    if not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No registration in progress.")

    user = db.query(User).get(get_jwt_identity(request))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.get("id") != payload.get("rawId"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id does not match rawId")

    response = {
        "id": payload["id"],
        "rawId": payload["rawId"],
        "type": payload["type"],
        "response": {
            "attestationObject": payload["response"]["attestationObject"],
            "clientDataJSON": payload["response"]["clientDataJSON"],
        },
    }

    auth_data = webauthn_server.register_complete(state, response)
    cred_data = auth_data.credential_data
    public_key_bytes = cbor.encode(cred_data.public_key)

    credential = WebAuthnCredential(
        user_id=user.id,
        tenant_id=user.tenant_id or 1,
        credential_id=cred_data.credential_id,
        public_key=public_key_bytes,
        sign_count=0,
        transports=",".join(payload.get("transports", [])),
    )
    db.add(credential)
    request.session.pop("webauthn_register_state", None)
    request.session["pending_webauthn_verification"] = True
    request.session["webauthn_user_id"] = str(user.id)
    db.commit()

    return {"message": "WebAuthn credential registered.", "redirect": "/webauthn/assertion"}


@router.get("/webauthn/assertion", response_class=HTMLResponse)
def webauthn_assertion_page(request: Request):
    return templates.TemplateResponse("verify_biometric.html", {"request": request})


@router.post("/webauthn/assertion-begin", dependencies=[Depends(verify_session_fingerprint)])
def begin_assertion(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user or not user.webauthn_credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No registered WebAuthn credentials for this user"
        )

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(",") if c.transports else [],
            "type": "public-key",
        }
        for c in user.webauthn_credentials
    ]

    assertion_data, state = webauthn_server.authenticate_begin(credentials)
    request.session["webauthn_assertion_state"] = state
    request.session["assertion_user_id"] = user.id
    request.session["mfa_webauthn_verified"] = False

    options = assertion_data.public_key
    public_key_dict = {
        "challenge": websafe_encode(options.challenge),
        "rpId": options.rp_id,
        "allowCredentials": [
            {
                "type": c.type.value,
                "id": websafe_encode(c.id),
                "transports": [t.value for t in c.transports] if c.transports else [],
            }
            for c in options.allow_credentials or []
        ],
        "userVerification": options.user_verification,
        "timeout": options.timeout,
    }
    return {"public_key": public_key_dict}


@router.post("/webauthn/assertion-complete", dependencies=[Depends(verify_session_fingerprint)])
def complete_assertion(payload: dict, request: Request, db: Session = Depends(get_db)):
    state = request.session.get("webauthn_assertion_state")
    user_id = request.session.get("assertion_user_id")
    if not state or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No assertion in progress.")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    credential_id = websafe_decode(payload["credentialId"])
    credential = db.query(WebAuthnCredential).filter_by(user_id=user.id, credential_id=credential_id).first()

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Webauthn locked. Try again after {user.locked_until}",
        )

    if not credential:
        threshold_time = datetime.utcnow() - timedelta(minutes=5)
        fail_count = (
            db.query(UserAuthLog)
            .filter_by(user_id=user.id, auth_method="webauthn", auth_status="failed")
            .filter(UserAuthLog.auth_timestamp >= threshold_time)
            .count()
            + 1
        )
        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.add(
            UserAuthLog(
                user_id=user.id,
                auth_method="webauthn",
                auth_status="failed",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
                failed_attempts=fail_count,
                tenant_id=user.tenant_id or 1,
            )
        )
        db.add(
            RealTimeLog(
                user_id=user.id,
                action=f"Failed WebAuthn: Credential not found ({fail_count})",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=(fail_count >= 3),
                tenant_id=user.tenant_id or 1,
            )
        )
        if fail_count >= 5:
            if user.email:
                send_user_alert(
                    user=user,
                    event_type="webauthn_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info,
                )
            send_admin_alert(
                user=user,
                event_type="webauthn_lockout",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
            )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid WebAuthn credential.")

    assertion = {
        "id": payload["credentialId"],
        "rawId": payload["credentialId"],
        "type": "public-key",
        "response": {
            "authenticatorData": payload["authenticatorData"],
            "clientDataJSON": payload["clientDataJSON"],
            "signature": payload["signature"],
            "userHandle": payload.get("userHandle"),
        },
    }
    public_key_source = AttestedCredentialData.create(
        Aaguid.NONE,
        credential.credential_id,
        CoseKey.parse(cbor.decode(credential.public_key)),
    )
    webauthn_server.authenticate_complete(state, [public_key_source], assertion)

    credential.sign_count += 1
    db.commit()
    request.session["mfa_webauthn_verified"] = True
    request.session.pop("webauthn_assertion_state", None)
    request.session.pop("assertion_user_id", None)

    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(access.role_id).role_name.lower() if access else "user"
    urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }

    db.add(
        RealTimeLog(
            user_id=user.id,
            action="Logged in via WebAuthn",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=user.tenant_id or 1,
        )
    )
    db.add(
        UserAuthLog(
            user_id=user.id,
            auth_method="webauthn",
            auth_status="success",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            failed_attempts=0,
            tenant_id=user.tenant_id or 1,
        )
    )
    db.commit()

    return {
        "message": "Biometric/passkey login successful",
        "user_id": user.id,
        "dashboard_url": urls.get(role, "/user/dashboard"),
    }


@router.post("/webauthn/reset-assertion-begin")
def begin_reset_assertion(payload: dict, request: Request, db: Session = Depends(get_db)):
    token = payload.get("token")
    context = payload.get("context", "totp")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token")

    user = None
    if context == "sim_swap":
        token_hash = hash_token(token)
        pending = db.query(PendingSIMSwap).filter_by(token_hash=token_hash).first()
        if not pending or pending.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SIM swap token invalid or expired.")
        user = db.query(User).get(pending.user_id)
    else:
        user = db.query(User).filter_by(reset_token=hash_token(token)).first()
        if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reset token invalid or expired.")

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not user.webauthn_credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no registered WebAuthn credentials"
        )

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(",") if c.transports else [],
            "type": "public-key",
        }
        for c in user.webauthn_credentials
    ]
    assertion_data, state = webauthn_server.authenticate_begin(credentials)
    request.session["reset_webauthn_assertion_state"] = state
    request.session["reset_user_id"] = user.id
    request.session["reset_context"] = context
    return {"public_key": jsonify_webauthn(assertion_data["publicKey"])}


@router.post("/webauthn/reset-assertion-complete")
def complete_reset_assertion(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("reset_user_id")
    state = request.session.get("reset_webauthn_assertion_state")
    context = request.session.get("reset_context")
    if not state or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No reset verification in progress.")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    credential_id = websafe_decode(payload["credentialId"])
    credential = db.query(WebAuthnCredential).filter_by(user_id=user.id, credential_id=credential_id).first()
    if not credential:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential.")

    assertion = {
        "id": payload["credentialId"],
        "rawId": payload["credentialId"],
        "type": "public-key",
        "response": {
            "authenticatorData": payload["authenticatorData"],
            "clientDataJSON": payload["clientDataJSON"],
            "signature": payload["signature"],
            "userHandle": payload.get("userHandle"),
        },
    }
    public_key_source = AttestedCredentialData.create(
        Aaguid.NONE,
        credential.credential_id,
        CoseKey.parse(cbor.decode(credential.public_key)),
    )
    webauthn_server.authenticate_complete(state, [public_key_source], assertion)

    credential.sign_count += 1
    db.commit()

    request.session["reset_webauthn_verified"] = True
    request.session.pop("reset_webauthn_assertion_state", None)
    return {"message": "Verified via WebAuthn for reset", "context": context}
