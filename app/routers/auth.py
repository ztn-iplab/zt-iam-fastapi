from datetime import datetime, timedelta, timezone
from typing import Optional

import os
import pyotp
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from app.db import get_db
from app.jwt import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_access_cookie,
    set_refresh_cookie,
    unset_auth_cookies,
)
from app.models import (
    Device,
    DeviceKey,
    LoginChallenge,
    OTPCode,
    RecoveryCode,
    PasswordHistory,
    PendingTOTP,
    RealTimeLog,
    SIMCard,
    User,
    UserAccessControl,
    UserAuthLog,
    UserRole,
    Wallet,
    WebAuthnCredential,
)
from app.security import get_jwt_identity, get_request_fingerprint, verify_session_fingerprint
from utils.email_alerts import (
    send_admin_alert,
    send_password_reset_email,
    send_totp_reset_email,
    send_user_alert,
    send_webauthn_reset_email,
)
from utils.feedback import store_feedback
from utils.location import get_ip_location
from utils.logging_helpers import log_auth_event, log_realtime_event
from utils.security import generate_token, hash_token, is_strong_password
from utils.totp import verify_totp_code
from app.zt_authenticator import (
    build_device_proof_message,
    build_enrollment_payload,
    decode_enroll_token,
    generate_enrollment_qr,
    generate_nonce,
    generate_recovery_codes,
    hash_otp,
    hash_recovery_code,
    issue_enroll_token,
    issue_enrollment_code,
    resolve_api_base_url,
    resolve_enrollment_code,
    resolve_rp_id,
    verify_p256_signature,
)
from utils.user_trust_engine import evaluate_trust, evaluate_trust_details

router = APIRouter(prefix="/api/auth", tags=["Auth"])
templates = Jinja2Templates(directory="templates")


class LoginPayload(dict):
    pass


class RegisterPayload(dict):
    pass


def _webauthn_allowed(request: Request) -> bool:
    if os.getenv("ZT_DISABLE_WEBAUTHN", "").lower() in {"1", "true", "yes"}:
        return False
    return request.url.scheme == "https"


def _replace_recovery_codes(db: Session, user_id: int, tenant_id: int, count: int | None = None) -> list[str]:
    if count is None:
        count = int(os.getenv("ZT_RECOVERY_CODE_COUNT", "8"))
    count = max(1, count)
    codes = generate_recovery_codes(count)
    (
        db.query(RecoveryCode)
        .filter(
            RecoveryCode.user_id == user_id,
            RecoveryCode.tenant_id == tenant_id,
            RecoveryCode.used_at.is_(None),
        )
        .delete(synchronize_session=False)
    )
    for code in codes:
        db.add(
            RecoveryCode(
                user_id=user_id,
                tenant_id=tenant_id,
                code_hash=hash_recovery_code(code),
            )
        )
    return codes


def _consume_recovery_code(db: Session, user_id: int, tenant_id: int, code: str) -> bool:
    code_hash = hash_recovery_code(code)
    entry = (
        db.query(RecoveryCode)
        .filter(
            RecoveryCode.user_id == user_id,
            RecoveryCode.tenant_id == tenant_id,
            RecoveryCode.code_hash == code_hash,
            RecoveryCode.used_at.is_(None),
        )
        .first()
    )
    if not entry:
        return False
    entry.used_at = datetime.utcnow()
    return True


@router.get("/register_form", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login_form", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/verify-totp", response_class=HTMLResponse)
def verify_totp_form(request: Request):
    return templates.TemplateResponse("verify_totp.html", {"request": request})


@router.get(
    "/enroll-biometric",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_session_fingerprint)],
)
def enroll_biometric_page(request: Request):
    return templates.TemplateResponse("enroll_biometric.html", {"request": request})


@router.get(
    "/verify-biometric",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_session_fingerprint)],
)
def verify_biometric_page(request: Request):
    return templates.TemplateResponse("verify_biometric.html", {"request": request})


@router.get("/request-totp-reset", response_class=HTMLResponse)
def request_totp_reset_form(request: Request):
    return templates.TemplateResponse("request_totp_reset.html", {"request": request})


@router.get("/out-request-webauthn-reset", response_class=HTMLResponse)
def out_request_webauthn_reset_page(request: Request):
    return templates.TemplateResponse("request_webauthn_reset.html", {"request": request})


@router.get("/verify-webauthn-reset/{token}", response_class=HTMLResponse)
def verify_webauthn_reset_page(token: str, request: Request):
    return templates.TemplateResponse("verify_webauthn_reset.html", {"request": request, "token": token})


@router.post("/login")
def login_route(payload: dict, request: Request, db: Session = Depends(get_db)):
    def count_recent_failures(user_id, method="password", window_minutes=5):
        threshold = datetime.utcnow() - timedelta(minutes=window_minutes)
        return (
            db.query(UserAuthLog)
            .filter_by(user_id=user_id, auth_method=method, auth_status="failed")
            .filter(UserAuthLog.auth_timestamp >= threshold)
            .count()
        )

    if "identifier" not in payload or "password" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number/email and password required",
        )

    login_input = payload.get("identifier")
    password = payload.get("password")

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    user = db.query(User).filter_by(email=login_input).first()
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=login_input, status="active").first()
        if sim:
            user = sim.user

    if not user:
        log_realtime_event(
            db,
            user=None,
            action=f"Failed login: Unknown identifier {login_input}",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or SIM inactive",
        )

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again after {user.locked_until}",
        )

    recent_fails = count_recent_failures(user.id)

    if not user.check_password(password):
        failed_count = recent_fails + 1

        log_auth_event(
            db,
            user=user,
            method="password",
            status="failed",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            failed_attempts=failed_count,
        )

        log_realtime_event(
            db,
            user=user,
            action=f"Failed login: Invalid password ({failed_count})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=(failed_count >= 3),
        )

        if failed_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            log_realtime_event(
                db,
                user=user,
                action="Account temporarily locked due to failed login attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
            if user.email:
                send_user_alert(
                    user=user,
                    event_type="login_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info,
                )
            send_admin_alert(
                user=user,
                event_type="login_lockout",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
            )

        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    fp = get_request_fingerprint(request)
    access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})

    rp_id = resolve_rp_id(request, "zt-iam")
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == user.tenant_id,
            DeviceKey.rp_id == rp_id,
        )
        .order_by(DeviceKey.created_at.desc())
        .first()
    )
    device_enrolled = device_key is not None
    context = {
        "ip_address": ip_address,
        "device_info": device_info,
        "location": location,
        "device_enrolled": device_enrolled,
    }
    risk_details = evaluate_trust_details(user, context)
    risk_score = risk_details["score"]
    risk_level = risk_details["level"]

    preferred_mfa = (user.preferred_mfa or "both").lower()
    require_totp = False
    require_webauthn = False
    skip_all_mfa = preferred_mfa == "none"

    if not skip_all_mfa:
        if preferred_mfa == "totp":
            require_totp = True
        elif preferred_mfa == "webauthn":
            require_webauthn = True
        elif preferred_mfa == "both":
            require_totp = True
            require_webauthn = True
        if require_webauthn and not _webauthn_allowed(request):
            require_webauthn = False
            if not require_totp:
                require_totp = True

    if risk_score >= 0.7:
        require_totp = True
        if _webauthn_allowed(request) and has_webauthn_credentials:
            require_webauthn = True

    if require_totp:
        if not device_enrolled:
            device_key = (
                db.query(DeviceKey)
                .join(Device, Device.id == DeviceKey.device_id)
                .filter(
                    Device.user_id == user.id,
                    Device.tenant_id == user.tenant_id,
                    DeviceKey.rp_id == rp_id,
                )
                .order_by(DeviceKey.created_at.desc())
                .first()
            )
            device_enrolled = device_key is not None
        if not device_enrolled:
            risk_score = min(risk_score + 0.15, 1.0)
            risk_level = "critical" if risk_score >= 0.8 else risk_level

    require_totp_setup = False
    require_totp_reset = False
    if require_totp:
        require_totp_setup = user.otp_secret is None
        require_totp_reset = bool(
            (user.otp_secret and user.otp_email_label != user.email)
            or (user.otp_secret and not device_enrolled)
        )

    log_auth_event(
        db,
        user=user,
        method="password",
        status="success",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        failed_attempts=0,
    )
    log_realtime_event(
        db,
        user=user,
        action="Successful login",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=(risk_level in {"high", "critical"}),
    )
    user.trust_score = risk_score
    db.commit()

    has_webauthn_credentials = bool(user.webauthn_credentials)

    response = JSONResponse(
        {
            "message": "Login successful",
            "user_id": user.id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "require_totp": require_totp,
            "require_totp_setup": require_totp_setup,
            "require_totp_reset": require_totp_reset,
            "require_webauthn": require_webauthn,
            "skip_all_mfa": skip_all_mfa,
            "has_webauthn_credentials": has_webauthn_credentials,
            "risk_factors": risk_details.get("factors", []),
        }
    )
    set_access_cookie(response, access_token)
    refresh_token = create_refresh_token(identity=str(user.id))
    set_refresh_cookie(response, refresh_token)
    return response


@router.post("/register")
def register(payload: dict, request: Request, db: Session = Depends(get_db)):
    required_fields = ["iccid", "first_name", "password", "email"]
    for field in required_fields:
        if not payload.get(field):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field.replace('_', ' ').capitalize()} is required",
            )

    if not is_strong_password(payload["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long and include uppercase, "
                "lowercase, number, and special character."
            ),
        )

    sim_card = db.query(SIMCard).filter_by(iccid=payload["iccid"]).first()
    if not sim_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid ICCID. Please register a SIM first.",
        )

    if sim_card.status == "unregistered":
        sim_card.status = "active"
        db.commit()

    existing_user = (
        db.query(User)
        .filter((User.email == payload["email"]) | (User.id == sim_card.user_id))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or SIM card already exists",
        )

    new_user = User(
        email=payload["email"],
        first_name=payload["first_name"],
        last_name=payload.get("last_name"),
        country=payload.get("country"),
        identity_verified=False,
        is_active=True,
        tenant_id=1,
    )
    new_user.password = payload["password"]

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    sim_card.user_id = new_user.id
    db.add(sim_card)

    user_role = db.query(UserRole).filter_by(role_name="user").first()
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user role not found",
        )

    db.add(UserAccessControl(user_id=new_user.id, role_id=user_role.id, tenant_id=new_user.tenant_id))
    new_wallet = Wallet(user_id=new_user.id, balance=0.0, currency="RWF")
    db.add(new_wallet)
    db.add(PasswordHistory(user_id=new_user.id, password_hash=new_user.password_hash))

    db.add(
        RealTimeLog(
            user_id=new_user.id,
            action=f"New user registered using ICCID {payload['iccid']} (SIM created by: {sim_card.registered_by})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    fp = get_request_fingerprint(request)
    access_token = create_access_token(identity=str(new_user.id), additional_claims={"fp": fp})
    refresh_token = create_refresh_token(identity=str(new_user.id))
    response = JSONResponse(
        {
            "message": "User registered successfully, assigned role: 'user', and wallet created.",
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "country": new_user.country,
            "identity_verified": new_user.identity_verified,
            "mobile_number": sim_card.mobile_number,
            "iccid": sim_card.iccid,
            "role": "user",
            "wallet": {"balance": new_wallet.balance, "currency": "RWF"},
        },
        status_code=status.HTTP_201_CREATED,
    )
    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    return response


@router.get("/setup-totp")
def setup_totp(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    rp_id = resolve_rp_id(request, "zt-iam")
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == user.tenant_id,
            DeviceKey.rp_id == rp_id,
        )
        .order_by(DeviceKey.created_at.desc())
        .first()
    )
    device_enrolled = device_key is not None
    reset_required = (
        user.otp_secret is None
        or (user.otp_secret and user.otp_email_label != user.email)
        or not device_enrolled
    )
    if not reset_required:
        return {"message": "TOTP already configured."}

    secret = pyotp.random_base32()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.query(PendingTOTP).filter_by(user_id=user.id, tenant_id=user.tenant_id).delete()
    pending = PendingTOTP(
        user_id=user.id,
        tenant_id=user.tenant_id,
        secret=secret,
        email=user.email,
        expires_at=expires_at,
    )
    db.add(pending)
    db.commit()

    rp_id = resolve_rp_id(request, "zt-iam")
    enroll_token = issue_enroll_token(
        {
            "pending_id": pending.id,
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "rp_id": rp_id,
        }
    )
    api_base_url = resolve_api_base_url(request, "/api/auth")

    payload = build_enrollment_payload(
        email=user.email,
        rp_id=rp_id,
        rp_display_name="ZT-IAM",
        issuer="ZT-IAM",
        account_name=user.email,
        device_label="ZT-Authenticator Device",
        enroll_token=enroll_token,
        api_base_url=api_base_url,
    )

    api_base_url = resolve_api_base_url(request, "/api/auth")
    short_code = issue_enrollment_code(payload)
    manual_url = f"{api_base_url}/enroll-code/{short_code}"
    response = {
        "qr_code": generate_enrollment_qr(payload),
        "manual_key": manual_url,
        "reset_required": True,
    }
    if request.query_params.get("include_payload") == "1":
        response["payload"] = payload
    return response


@router.get("/enroll-code/{code}")
def resolve_enroll_code(code: str):
    payload = resolve_enrollment_code(code)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment code expired or invalid.")
    return payload


@router.post("/setup-totp/confirm")
def confirm_totp_setup(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    pending = (
        db.query(PendingTOTP)
        .filter_by(user_id=user.id, tenant_id=user.tenant_id)
        .first()
    )
    if pending and pending.expires_at >= datetime.utcnow():
        user.otp_secret = pending.secret
        user.otp_email_label = pending.email
        db.delete(pending)
    elif not user.otp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending TOTP enrollment")

    recovery_codes = _replace_recovery_codes(db, user.id, user.tenant_id)
    db.commit()

    message = "TOTP enrollment confirmed." if pending else "TOTP already configured."
    return {"message": message, "recovery_codes": recovery_codes}


@router.post("/verify-totp-login")
def verify_totp_login(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    totp_code = payload.get("totp")
    if not totp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP code is required")

    user = db.query(User).get(user_id)
    if not user or not user.otp_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or TOTP not configured")

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"TOTP locked. Try again after {user.locked_until}",
        )

    threshold_time = datetime.utcnow() - timedelta(minutes=5)
    recent_otp_fails = (
        db.query(UserAuthLog)
        .filter_by(user_id=user.id, auth_method="totp", auth_status="failed")
        .filter(UserAuthLog.auth_timestamp >= threshold_time)
        .count()
    )

    if not verify_totp_code(user.otp_secret, totp_code, valid_window=2):
        fail_count = recent_otp_fails + 1
        db.add(
            UserAuthLog(
                user_id=user.id,
                auth_method="totp",
                auth_status="failed",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
                failed_attempts=fail_count,
                tenant_id=1,
            )
        )
        db.add(
            RealTimeLog(
                user_id=user.id,
                action=f"Failed TOTP verification ({fail_count})",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1,
            )
        )
        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.add(
                RealTimeLog(
                    user_id=user.id,
                    action="TOTP temporarily locked after multiple failed attempts",
                    ip_address=ip_address,
                    device_info=device_info,
                    location=location,
                    risk_alert=True,
                    tenant_id=1,
                )
            )
            if user.email:
                send_user_alert(
                    user=user,
                    event_type="totp_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info,
                )
            send_admin_alert(
                user=user,
                event_type="totp_lockout",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
            )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired TOTP code")

    rp_id = resolve_rp_id(request, "zt-iam")
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == user.tenant_id,
            DeviceKey.rp_id == rp_id,
        )
        .order_by(DeviceKey.created_at.desc())
        .first()
    )
    if not device_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No ZT-Authenticator device enrolled for this account.",
        )

    challenge = LoginChallenge(
        user_id=user.id,
        tenant_id=user.tenant_id,
        device_id=device_key.device_id,
        rp_id=rp_id,
        nonce=generate_nonce(),
        otp_hash=hash_otp(totp_code),
        status="pending",
        expires_at=datetime.utcnow() + timedelta(minutes=2),
    )
    db.add(challenge)
    db.add(
        UserAuthLog(
            user_id=user.id,
            auth_method="totp_device",
            auth_status="pending",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            failed_attempts=0,
            tenant_id=user.tenant_id,
        )
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="TOTP verified; awaiting device approval",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=user.tenant_id,
        )
    )
    db.commit()
    request.session["pending_login_id"] = challenge.id
    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(access.role_id).role_name.lower() if access else "user"
    urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }

    preferred_mfa = (user.preferred_mfa or "both").lower()
    require_webauthn = preferred_mfa in ["webauthn", "both"] and _webauthn_allowed(request)
    has_webauthn_credentials = bool(user.webauthn_credentials)
    request.session["mfa_webauthn_required"] = require_webauthn
    request.session["mfa_webauthn_has_credentials"] = has_webauthn_credentials

    return {
        "message": "TOTP verified. Awaiting device approval.",
        "user_id": user.id,
        "require_device_approval": True,
        "login_id": challenge.id,
        "expires_in": 120,
        "require_webauthn": require_webauthn,
        "has_webauthn_credentials": has_webauthn_credentials,
        "dashboard_url": urls.get(role, "/user/dashboard"),
    }


@router.get("/device-approval", response_class=HTMLResponse)
def device_approval_page(request: Request, login_id: Optional[int] = None):
    return templates.TemplateResponse(
        "device_approval.html",
        {"request": request, "login_id": login_id or ""},
    )


@router.post("/login/recover")
def login_recover(payload: dict, request: Request, db: Session = Depends(get_db)):
    email = (payload.get("email") or "").strip().lower()
    recovery_code = (payload.get("recovery_code") or "").strip()
    if not email or not recovery_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and recovery_code are required")

    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        return {"status": "denied", "reason": "user_not_found"}

    if user.locked_until and user.locked_until > datetime.utcnow():
        return {"status": "denied", "reason": "locked"}

    if not _consume_recovery_code(db, user.id, user.tenant_id, recovery_code):
        return {"status": "denied", "reason": "invalid_recovery_code"}

    fp = get_request_fingerprint(request)
    access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})
    refresh_token = create_refresh_token(identity=str(user.id))

    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(access.role_id).role_name.lower() if access else "user"
    urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)
    log_auth_event(
        db,
        user=user,
        method="recovery",
        status="success",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        failed_attempts=0,
    )
    log_realtime_event(
        db,
        user=user,
        action="Successful recovery code login",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False,
    )
    db.commit()
    request.session["mfa_totp_verified"] = True
    request.session["mfa_webauthn_verified"] = True
    request.session["mfa_webauthn_required"] = False
    request.session["mfa_webauthn_has_credentials"] = False

    response = JSONResponse(
        {
            "status": "ok",
            "reason": None,
            "dashboard_url": urls.get(role, "/user/dashboard"),
        }
    )
    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    return response


@router.get("/login-status")
def login_status(
    request: Request,
    login_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    pending_id = login_id or request.session.get("pending_login_id")
    if not pending_id:
        return {"status": "denied", "reason": "missing_login_id"}

    challenge = db.query(LoginChallenge).get(pending_id)
    if not challenge:
        return {"status": "denied", "reason": "not_found"}

    if challenge.expires_at < datetime.utcnow() and challenge.status == "pending":
        challenge.status = "denied"
        challenge.denied_reason = "expired"
        db.commit()
        return {"status": "denied", "reason": "expired"}

    if challenge.status == "pending":
        remaining = int((challenge.expires_at - datetime.utcnow()).total_seconds())
        return {"status": "pending", "expires_in": max(0, remaining)}
    if challenge.status != "ok":
        return {"status": challenge.status, "reason": challenge.denied_reason}

    user = db.query(User).get(challenge.user_id)
    if not user:
        return {"status": "denied", "reason": "user_not_found"}

    request.session["mfa_totp_verified"] = True
    request.session.pop("pending_login_id", None)

    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(access.role_id).role_name.lower() if access else "user"
    urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }

    preferred_mfa = (user.preferred_mfa or "both").lower()
    require_webauthn = preferred_mfa in ["webauthn", "both"] and _webauthn_allowed(request)
    has_webauthn_credentials = bool(user.webauthn_credentials)
    request.session["mfa_webauthn_required"] = require_webauthn
    request.session["mfa_webauthn_has_credentials"] = has_webauthn_credentials

    return {
        "status": "ok",
        "require_webauthn": require_webauthn,
        "has_webauthn_credentials": has_webauthn_credentials,
        "dashboard_url": urls.get(role, "/user/dashboard"),
    }


@router.post("/login/resend")
def login_resend(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
):
    login_id = payload.get("login_id") or request.session.get("pending_login_id")
    if not login_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login_id is required")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge:
        return {"status": "denied", "reason": "not_found"}

    if challenge.expires_at < datetime.utcnow():
        challenge.status = "denied"
        challenge.denied_reason = "expired"
        db.commit()
        return {"status": "denied", "reason": "expired"}

    if challenge.status != "pending":
        return {"status": challenge.status, "reason": challenge.denied_reason}

    new_challenge = LoginChallenge(
        user_id=challenge.user_id,
        tenant_id=challenge.tenant_id,
        device_id=challenge.device_id,
        rp_id=challenge.rp_id,
        nonce=generate_nonce(),
        otp_hash=None,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(minutes=2),
    )
    challenge.status = "denied"
    challenge.denied_reason = "resent"
    db.add(new_challenge)
    db.commit()

    request.session["pending_login_id"] = new_challenge.id
    return {"status": "pending", "login_id": new_challenge.id, "expires_in": 120}


@router.api_route("/login/deny", methods=["GET", "POST"])
def login_deny(
    request: Request,
    db: Session = Depends(get_db),
    payload: dict = Body(default_factory=dict),
):
    login_id = payload.get("login_id") or request.query_params.get("login_id") or request.session.get("pending_login_id")
    reason = payload.get("reason", "cancelled")
    if not login_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login_id is required")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge:
        return {"status": "denied", "reason": "not_found"}

    if challenge.status == "pending":
        challenge.status = "denied"
        challenge.denied_reason = reason
        db.commit()

    request.session.pop("pending_login_id", None)
    return {"status": challenge.status, "reason": challenge.denied_reason}


@router.get("/login/pending")
def login_pending(user_id: int, request: Request, db: Session = Depends(get_db)):
    challenge = (
        db.query(LoginChallenge)
        .filter_by(user_id=user_id, status="pending")
        .order_by(LoginChallenge.created_at.desc())
        .first()
    )
    if not challenge:
        return {"status": "none"}

    if challenge.expires_at < datetime.utcnow():
        challenge.status = "denied"
        challenge.denied_reason = "expired"
        db.commit()
        return {"status": "none"}

    expires_in = int((challenge.expires_at - challenge.created_at).total_seconds())
    return {
        "status": "pending",
        "login_id": str(challenge.id),
        "nonce": challenge.nonce,
        "rp_id": challenge.rp_id,
        "device_id": str(challenge.device_id),
        "expires_in": expires_in,
    }


@router.post("/feedback")
def submit_feedback(
    payload: dict,
    request: Request,
):
    store_feedback(
        payload,
        source="zt-authenticator",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    return {"status": "ok"}


@router.post("/login/approve")
def login_approve(payload: dict, request: Request, db: Session = Depends(get_db)):
    login_id = payload.get("login_id")
    device_id = payload.get("device_id")
    rp_id = payload.get("rp_id")
    otp = payload.get("otp")
    nonce = payload.get("nonce")
    signature = payload.get("signature")

    if not all([login_id, device_id, rp_id, otp, nonce, signature]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge or challenge.status != "pending":
        return {"status": "denied", "reason": "not_pending"}

    if challenge.expires_at < datetime.utcnow():
        challenge.status = "denied"
        challenge.denied_reason = "expired"
        db.commit()
        return {"status": "denied", "reason": "expired"}

    if challenge.device_id != int(device_id) or challenge.rp_id != rp_id:
        challenge.status = "denied"
        challenge.denied_reason = "mismatch"
        db.commit()
        return {"status": "denied", "reason": "mismatch"}

    user = db.query(User).get(challenge.user_id)
    if not user or not user.otp_secret:
        challenge.status = "denied"
        challenge.denied_reason = "totp_not_configured"
        db.commit()
        return {"status": "denied", "reason": "totp_not_configured"}

    if not verify_totp_code(user.otp_secret, otp, valid_window=2):
        challenge.status = "denied"
        challenge.denied_reason = "invalid_otp"
        db.commit()
        return {"status": "denied", "reason": "invalid_otp"}

    if challenge.otp_hash:
        if challenge.otp_hash != hash_otp(otp):
            challenge.status = "denied"
            challenge.denied_reason = "otp_mismatch"
            db.commit()
            return {"status": "denied", "reason": "otp_mismatch"}

    device_key = (
        db.query(DeviceKey)
        .filter_by(device_id=challenge.device_id, rp_id=rp_id, tenant_id=challenge.tenant_id)
        .first()
    )
    if not device_key:
        challenge.status = "denied"
        challenge.denied_reason = "device_not_enrolled"
        db.commit()
        return {"status": "denied", "reason": "device_not_enrolled"}

    message = build_device_proof_message(nonce, str(device_id), rp_id, otp)
    if not verify_p256_signature(device_key.public_key, message, signature):
        challenge.status = "denied"
        challenge.denied_reason = "invalid_device_proof"
        db.commit()
        return {"status": "denied", "reason": "invalid_device_proof"}

    challenge.status = "ok"
    challenge.approved_at = datetime.utcnow()
    db.add(
        UserAuthLog(
            user_id=user.id,
            auth_method="totp_device",
            auth_status="success",
            ip_address=request.client.host if request.client else None,
            location=get_ip_location(request.client.host) if request.client else None,
            device_info="ZT-Authenticator device approval",
            failed_attempts=0,
            tenant_id=challenge.tenant_id,
        )
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="ZT-Authenticator device approval success",
            ip_address=request.client.host if request.client else None,
            device_info="ZT-Authenticator device approval",
            location=get_ip_location(request.client.host) if request.client else None,
            risk_alert=False,
            tenant_id=challenge.tenant_id,
        )
    )
    db.commit()
    return {"status": "ok"}


@router.post("/login/deny-legacy")
def login_deny_legacy(payload: dict, request: Request, db: Session = Depends(get_db)):
    login_id = payload.get("login_id")
    reason = payload.get("reason", "user_denied")
    if not login_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login_id is required")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge:
        return {"status": "denied", "reason": "not_found"}
    if challenge.status != "pending":
        return {"status": challenge.status, "reason": challenge.denied_reason}

    challenge.status = "denied"
    challenge.denied_reason = reason
    db.commit()
    return {"status": "denied", "reason": reason}


@router.post("/enroll")
def enroll_device(payload: dict, request: Request, db: Session = Depends(get_db)):
    enroll_token = (payload.get("enroll_token") or "").strip()
    if not enroll_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment token is required")

    try:
        token_data = decode_enroll_token(enroll_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid enrollment token")

    email = (payload.get("email") or "").strip().lower()
    rp_id = (payload.get("rp_id") or "").strip()
    if not email or not rp_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and rp_id are required")

    if token_data.get("email", "").lower() != email or token_data.get("rp_id") != rp_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment token mismatch")

    pending = db.query(PendingTOTP).get(token_data.get("pending_id"))
    if not pending or pending.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment token expired")

    user = db.query(User).get(token_data.get("user_id"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    device = Device(
        user_id=user.id,
        tenant_id=user.tenant_id,
        device_label=payload.get("device_label") or "ZT-Authenticator Device",
        platform=payload.get("platform") or "unknown",
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    device_key = DeviceKey(
        device_id=device.id,
        tenant_id=user.tenant_id,
        rp_id=rp_id,
        key_type=payload.get("key_type") or "p256",
        public_key=payload.get("public_key") or "",
    )
    if not device_key.public_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="public_key is required")
    db.add(device_key)
    db.commit()

    return {"user": {"id": str(user.id)}, "device": {"id": str(device.id)}}


@router.post("/totp/register")
def register_totp(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = payload.get("user_id")
    rp_id = (payload.get("rp_id") or "").strip()
    issuer = (payload.get("issuer") or "ZT-IAM").strip()
    account_name = (payload.get("account_name") or "").strip()
    if not user_id or not rp_id or not account_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == user.tenant_id,
            DeviceKey.rp_id == rp_id,
        )
        .first()
    )
    if not device_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device not enrolled")

    pending = (
        db.query(PendingTOTP)
        .filter_by(user_id=user.id, tenant_id=user.tenant_id)
        .first()
    )
    if not pending or pending.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending TOTP enrollment")

    user.otp_secret = pending.secret
    user.otp_email_label = pending.email
    db.delete(pending)
    recovery_codes = _replace_recovery_codes(db, user.id, user.tenant_id)
    db.commit()

    otpauth_uri = pyotp.TOTP(user.otp_secret).provisioning_uri(
        name=account_name,
        issuer_name=issuer,
    )
    return {"otpauth_uri": otpauth_uri, "recovery_codes": recovery_codes}


@router.get("/whoami")
def whoami(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = "unknown"
    if user_access:
        role_obj = db.query(UserRole).get(user_access.role_id)
        if role_obj:
            role = role_obj.role_name
    return {"role": role.lower()}


@router.get("/risk-score")
def risk_score(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)
    rp_id = resolve_rp_id(request, "zt-iam")
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == user.tenant_id,
            DeviceKey.rp_id == rp_id,
        )
        .first()
    )
    context = {
        "ip_address": ip_address,
        "device_info": device_info,
        "location": location,
        "device_enrolled": device_key is not None,
    }
    details = evaluate_trust_details(user, context)
    user.trust_score = details["score"]
    db.commit()
    return {
        "user_id": user.id,
        "risk_score": details["score"],
        "risk_level": details["level"],
        "factors": details["factors"],
    }


@router.post("/verify-totp")
def verify_transaction_totp(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not payload.get("code"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP code is required")
    if verify_totp_code(user.otp_secret, payload["code"]):
        return {"message": "TOTP is valid"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP")


@router.post("/verify-fallback_totp")
def verify_fallback_totp(payload: dict, request: Request, db: Session = Depends(get_db)):
    token = payload.get("token")
    code = payload.get("code")
    if not token or not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token and TOTP code are required",
        )

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    if not user.otp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No TOTP method set up")
    if verify_totp_code(user.otp_secret, code):
        request.session["reset_totp_verified"] = True
        request.session["reset_token_checked"] = token
        return {"message": "TOTP code verified successfully. You can now reset your password."}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")


@router.post("/zt/rotate-key")
def rotate_device_key(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    device_id = payload.get("device_id")
    rp_id = (payload.get("rp_id") or "").strip()
    public_key = payload.get("public_key") or ""
    key_type = payload.get("key_type") or "p256"

    if not device_id or not rp_id or not public_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")

    device = db.query(Device).filter_by(id=device_id, user_id=user_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    device_key = (
        db.query(DeviceKey)
        .filter_by(device_id=device.id, rp_id=rp_id, tenant_id=device.tenant_id)
        .first()
    )
    if not device_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device key not found")

    device_key.public_key = public_key
    device_key.key_type = key_type
    device_key.created_at = datetime.utcnow()
    db.commit()

    return {"status": "ok"}


@router.post("/log-webauthn-failure")
def log_webauthn_failure(payload: dict, request: Request, db: Session = Depends(get_db)):
    error = payload.get("error") if isinstance(payload, dict) else None
    user_id = None
    try:
        user_id = get_jwt_identity(request)
    except HTTPException:
        user_id = None

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    db.add(
        RealTimeLog(
            user_id=user_id,
            action=f"WebAuthn failure reported: {error or 'unknown error'}",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "logged"}


@router.get("/preferred-mfa", dependencies=[Depends(verify_session_fingerprint)])
def get_preferred_mfa(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"preferred_mfa": (user.preferred_mfa or "both").lower()}


@router.put("/preferred-mfa", dependencies=[Depends(verify_session_fingerprint)])
def update_preferred_mfa(payload: dict, request: Request, db: Session = Depends(get_db)):
    preferred_mfa = (payload.get("preferred_mfa") or "").lower().strip()
    if preferred_mfa not in {"totp", "webauthn", "both"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid preferred MFA value")

    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.preferred_mfa = preferred_mfa
    db.add(
        RealTimeLog(
            user_id=user.id,
            action=f"Updated preferred MFA to {preferred_mfa}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
            tenant_id=user.tenant_id or 1,
        )
    )
    db.commit()
    return {"message": "Preferred MFA updated", "preferred_mfa": preferred_mfa}


@router.post("/request-totp-reset")
def request_totp_reset(payload: dict, request: Request, db: Session = Depends(get_db)):
    identifier = (payload.get("identifier") or "").strip()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier (mobile or email) required",
        )

    user = db.query(User).filter(func.lower(User.email) == identifier.lower()).first()
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        user = sim.user if sim else None

    if not user:
        return {"message": "Please check your email for a password reset link"}

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    send_totp_reset_email(user, token)
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="TOTP reset requested",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "Please check your email for a TOTP reset link"}


@router.post("/request-reset-totp", dependencies=[Depends(verify_session_fingerprint)])
def request_reset_totp_authenticated(payload: dict, request: Request, db: Session = Depends(get_db)):
    password = payload.get("password")
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")

    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user or not user.check_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    send_totp_reset_email(user, token)
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="TOTP reset requested (authenticated)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
            tenant_id=user.tenant_id or 1,
        )
    )
    db.commit()
    return {
        "message": "Check your email to verify the TOTP reset.",
        "redirect": f"/api/auth/verify-totp-reset?token={token}",
    }


@router.get("/verify-totp-reset", response_class=HTMLResponse)
def verify_totp_reset_form(request: Request):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token")
    return templates.TemplateResponse("totp_reset_verification.html", {"request": request, "token": token})


@router.post("/verify-totp-reset")
def verify_totp_reset(payload: dict, request: Request, db: Session = Depends(get_db)):
    token = payload.get("token")
    password = payload.get("password")
    if not token or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token and password are required")

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    if not user.check_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    if request.session.get("reset_token_checked") != token:
        request.session["reset_webauthn_verified"] = False
        request.session["reset_token_checked"] = token

    has_webauthn = db.query(WebAuthnCredential).filter_by(user_id=user.id).count() > 0
    if has_webauthn and _webauthn_allowed(request) and not request.session.get("reset_webauthn_verified"):
        return JSONResponse(
            {
                "require_webauthn": True,
                "message": "WebAuthn verification required before resetting TOTP.",
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    user.otp_secret = None
    user.otp_email_label = None
    user.reset_token = None
    user.reset_token_expiry = None

    db.add(
        RealTimeLog(
            user_id=user.id,
            action="TOTP reset after verification",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    request.session.pop("reset_webauthn_verified", None)
    request.session.pop("reset_token_checked", None)
    return {"message": "TOTP has been reset. Please enroll again to continue."}


@router.post("/out-request-webauthn-reset")
def out_request_webauthn_reset(payload: dict, request: Request, db: Session = Depends(get_db)):
    identifier = (payload.get("identifier") or "").strip()
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifier (mobile or email) required")

    user = db.query(User).filter(func.lower(User.email) == identifier.lower()).first()
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        user = sim.user if sim else None

    if not user:
        return {"message": "Please check your email for a TOTP reset link"}

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    send_webauthn_reset_email(user, token)
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="WebAuthn reset requested",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "Please check your email for a WebAuthn reset link"}


@router.post("/request-reset-webauthn", dependencies=[Depends(verify_session_fingerprint)])
def request_reset_webauthn_authenticated(payload: dict, request: Request, db: Session = Depends(get_db)):
    password = payload.get("password")
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")

    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user or not user.check_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    send_webauthn_reset_email(user, token)
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="WebAuthn reset requested (authenticated)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
            tenant_id=user.tenant_id or 1,
        )
    )
    db.commit()
    return {
        "message": "Check your email to verify the WebAuthn reset.",
        "redirect": f"/api/auth/verify-webauthn-reset/{token}",
    }


@router.post("/out-verify-webauthn-reset/{token}")
def out_verify_webauthn_reset(token: str, payload: dict, request: Request, db: Session = Depends(get_db)):
    password = payload.get("password")
    totp = payload.get("totp")
    if not password or not totp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password and TOTP code are required"
        )

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    if not user.check_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not user.otp_secret or not verify_totp_code(user.otp_secret, totp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    creds = db.query(WebAuthnCredential).filter_by(user_id=user.id).all()
    if not creds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No WebAuthn credentials to reset")

    for cred in creds:
        db.delete(cred)

    user.reset_token = None
    user.reset_token_expiry = None

    db.add(
        RealTimeLog(
            user_id=user.id,
            action="WebAuthn reset after verification",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "WebAuthn reset complete. Please enroll a new passkey."}


@router.post("/refresh")
def refresh(request: Request):
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    payload = decode_token(refresh_token)
    user_id = payload.get("sub")
    fp = get_request_fingerprint(request)
    new_access_token = create_access_token(identity=str(user_id), additional_claims={"fp": fp})
    response = JSONResponse({"access_token": new_access_token})
    set_access_cookie(response, new_access_token)
    return response


@router.get("/logout")
def logout():
    response = JSONResponse({"message": "Logged out"})
    unset_auth_cookies(response)
    return response


@router.post("/logout")
def logout_post():
    response = JSONResponse({"message": "Logged out"})
    unset_auth_cookies(response)
    return response


@router.get("/debug-cookie")
def debug_cookie(request: Request):
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    payload = decode_token(token)
    return f"JWT verified! User ID: {payload.get('sub')}"


@router.post("/forgot-password")
def forgot_password(payload: dict, request: Request, db: Session = Depends(get_db)):
    identifier = (payload.get("identifier") or "").strip()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier (mobile or email) required",
        )

    user = db.query(User).filter(func.lower(User.email) == identifier.lower()).first()
    sim = None
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier).first()
        if sim and sim.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone number is inactive. Please contact support.",
            )
        user = sim.user if sim and sim.status == "active" else None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for that email or phone number.",
        )

    if not user.is_active or user.deletion_requested:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive. Please contact support.",
        )
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="This account is temporarily locked. Please try again later.",
        )

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    send_password_reset_email(user, token)

    db.add(
        RealTimeLog(
            user_id=user.id,
            action="Password reset requested",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "Please check your email for a password reset link"}


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_form(request: Request):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token")
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


@router.post("/reset-password")
def reset_password(payload: dict, request: Request, db: Session = Depends(get_db)):
    token = payload.get("token")
    new_password = payload.get("new_password")
    confirm_password = payload.get("confirm_password")
    if not token or not new_password or not confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token, new password, and confirmation are required",
        )
    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    if user.trust_score >= 0.6:
        db.add(
            RealTimeLog(
                user_id=user.id,
                action="Password reset denied due to elevated risk score",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1,
            )
        )
        send_admin_alert(
            user=user,
            event_type="Blocked Password Reset (High Risk Score)",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This reset request was blocked due to suspicious activity.",
        )

    if user.password_hash and check_password_hash(user.password_hash, new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already used this password. Please choose a new one.",
        )

    previous_passwords = db.query(PasswordHistory).filter_by(user_id=user.id).all()
    for record in previous_passwords:
        if record.password_hash and check_password_hash(record.password_hash, new_password):
            db.add(
                RealTimeLog(
                    user_id=user.id,
                    action="Attempted to reuse an old password during reset",
                    ip_address=ip_address,
                    device_info=device_info,
                    location=location,
                    risk_alert=True,
                    tenant_id=1,
                )
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used this password. Please choose a new one.",
            )

    if not is_strong_password(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long and include an uppercase letter, "
                "lowercase letter, number, and special character."
            ),
        )

    has_webauthn = db.query(WebAuthnCredential).filter_by(user_id=user.id).count() > 0
    has_totp = user.otp_secret is not None

    if request.session.get("reset_token_checked") != token:
        request.session["reset_webauthn_verified"] = False
        request.session["reset_totp_verified"] = False
        request.session["reset_token_checked"] = token

    if has_webauthn and _webauthn_allowed(request) and not request.session.get("reset_webauthn_verified"):
        return JSONResponse(
            {
                "require_webauthn": True,
                "message": "WebAuthn verification required before resetting your password.",
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    if has_totp and not request.session.get("reset_totp_verified"):
        return JSONResponse(
            {
                "require_totp": True,
                "message": "TOTP verification required before resetting your password.",
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    if not has_webauthn and not has_totp:
        db.add(
            RealTimeLog(
                user_id=user.id,
                action="Password reset blocked — no MFA configured",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1,
            )
        )
        send_admin_alert(
            user=user,
            event_type="Blocked Password Reset (No MFA)",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to have at least one MFA method set up to reset your password.",
        )

    if not previous_passwords and user.password_hash:
        db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    user.password = new_password
    db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    history_records = (
        db.query(PasswordHistory)
        .filter_by(user_id=user.id)
        .order_by(PasswordHistory.created_at.desc())
        .all()
    )
    if len(history_records) > 5:
        for old in history_records[5:]:
            db.delete(old)

    user.reset_token = None
    user.reset_token_expiry = None

    db.add(
        RealTimeLog(
            user_id=user.id,
            action="Password reset after MFA and checks",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=1,
        )
    )

    request.session.pop("reset_webauthn_verified", None)
    request.session.pop("reset_totp_verified", None)
    request.session.pop("reset_token_checked", None)

    db.commit()
    return {"message": "Your password has been successfully reset. You may now log in with your new credentials."}


@router.post("/change-password")
def change_password(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    if not user.check_password(current_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect.")
    if not is_strong_password(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character.",
        )

    if user.password_hash and check_password_hash(user.password_hash, new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already used this password. Please choose a new one.",
        )

    previous_passwords = db.query(PasswordHistory).filter_by(user_id=user.id).all()
    for record in previous_passwords:
        if record.password_hash and check_password_hash(record.password_hash, new_password):
            db.add(
                RealTimeLog(
                    user_id=user.id,
                    action="Attempted to reuse an old password",
                    ip_address=request.client.host if request.client else None,
                    device_info=request.headers.get("User-Agent", ""),
                    location=get_ip_location(request.client.host if request.client else ""),
                    risk_alert=True,
                    tenant_id=1,
                )
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used this password. Please choose a new one.",
            )

    if not previous_passwords and user.password_hash:
        db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    user.password = new_password
    db.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    history_records = (
        db.query(PasswordHistory)
        .filter_by(user_id=user.id)
        .order_by(PasswordHistory.created_at.desc())
        .all()
    )
    if len(history_records) > 5:
        for old_record in history_records[5:]:
            db.delete(old_record)

    db.add(
        UserAuthLog(
            user_id=user.id,
            auth_method="password",
            auth_status="change",
            ip_address=request.client.host if request.client else None,
            location=get_ip_location(request.client.host if request.client else ""),
            device_info=request.headers.get("User-Agent", ""),
            tenant_id=1,
        )
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="Changed account password",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=False,
            tenant_id=1,
        )
    )

    db.commit()
    return {"message": "Password updated successfully."}
