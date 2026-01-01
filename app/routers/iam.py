from datetime import datetime, timedelta
import base64
import json
import os
import re

import pyotp
from fido2 import cbor
from fido2.cose import CoseKey
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import Aaguid, AttestedCredentialData, PublicKeyCredentialRpEntity

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.api_key import require_api_key
from app.db import get_db
from app.jwt import (
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
    RecoveryCode,
    RealTimeLog,
    SIMCard,
    Tenant,
    TenantUser,
    TenantPasswordHistory,
    PendingTOTP,
    TenantTrustPolicyFile,
    User,
    UserAccessControl,
    UserAuthLog,
    UserRole,
    WebAuthnCredential,
)
from app.security import get_jwt_identity, get_request_fingerprint
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
from utils.location import get_ip_location
from utils.email_alerts import send_admin_alert, send_user_alert
from utils.iam_tenant_email import (
    send_tenant_password_reset_email,
    send_tenant_totp_reset_email,
    send_tenant_webauthn_reset_email,
)
from utils.security import generate_token, hash_token, is_strong_password
from utils.feedback import store_feedback
from utils.totp import verify_totp_code
from utils.user_trust_engine import evaluate_trust
from utils.policy_validator import validate_trust_policy

router = APIRouter(prefix="/api/v1/auth", tags=["IAM"])

rp = PublicKeyCredentialRpEntity(id="localhost.localdomain.com", name="ZTN Local")
webauthn_server = Fido2Server(rp)


def _webauthn_allowed(request: Request) -> bool:
    if os.getenv("ZT_DISABLE_WEBAUTHN", "").lower() in {"1", "true", "yes"}:
        return False
    return request.url.scheme == "https"


def _tenant_rp_id(request: Request, tenant: Tenant) -> str:
    header_rp = (request.headers.get("X-RP-ID") or request.headers.get("X-RP-Id") or "").strip()
    if header_rp:
        return header_rp
    base_name = (tenant.name or f"tenant-{tenant.id}").strip().lower()
    slug = re.sub(r"[^a-z0-9.-]+", "-", base_name).strip("-")
    if not slug:
        slug = f"tenant-{tenant.id}"
    suffix = os.getenv("ZT_TENANT_RP_SUFFIX", ".zt-iam").strip()
    if suffix and not suffix.startswith("."):
        suffix = f".{suffix}"
    return f"{slug}{suffix}"


def jsonify_webauthn(data):
    def convert(value):
        if isinstance(value, bytes):
            return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return convert(data)


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


@router.post("/register")
def register_user(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    required_fields = ["mobile_number", "first_name", "password", "email"]
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

    sim_card = (
        db.query(SIMCard)
        .filter_by(mobile_number=payload["mobile_number"], status="active")
        .first()
    )
    if not sim_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobile number not recognized or not active",
        )

    user = db.query(User).get(sim_card.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SIM card not linked to any user",
        )

    existing_tenant_user = (
        db.query(TenantUser)
        .filter_by(tenant_id=tenant.id, user_id=user.id)
        .first()
    )
    if existing_tenant_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already registered under this tenant",
        )

    existing_email_user = (
        db.query(TenantUser)
        .filter_by(tenant_id=tenant.id, company_email=payload["email"])
        .first()
    )
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already registered under this tenant",
        )

    tenant_user = TenantUser(
        tenant_id=tenant.id,
        user_id=user.id,
        company_email=payload["email"],
        password_hash=generate_password_hash(payload["password"]),
    )
    db.add(tenant_user)

    role_name = payload.get("role", "user").lower()
    role = db.query(UserRole).filter_by(role_name=role_name, tenant_id=tenant.id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_name}' not found for this tenant",
        )

    db.add(
        UserAccessControl(
            user_id=user.id,
            role_id=role.id,
            access_level=payload.get("access_level", "read"),
            tenant_id=tenant.id,
        )
    )

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action=f"IAM user registered via API (Mobile {payload['mobile_number']}, Role: {role_name})",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API",
            location=payload.get("location", "Unknown"),
            risk_alert=False,
        )
    )
    db.commit()

    return {
        "message": f"User registered successfully with role '{role_name}'.",
        "mobile_number": payload["mobile_number"],
        "tenant_email": payload["email"],
        "role": role_name,
    }


@router.post("/login")
def login_user(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
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
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    user = None
    sim_card = db.query(SIMCard).filter_by(mobile_number=login_input, status="active").first()
    if sim_card and sim_card.user:
        user = sim_card.user

    if not user:
        user = db.query(User).filter_by(email=login_input).first()

    if not user:
        db.add(
            RealTimeLog(
                user_id=None,
                tenant_id=tenant.id,
                action=f"Failed login: Unknown identifier {login_input}",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tenant_user = (
        db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=user.id).first()
    )
    if not tenant_user:
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action="Failed login: User not under tenant",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found under this tenant"
        )

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again after {user.locked_until}",
        )

    recent_fails = count_recent_failures(user.id)
    if not user.check_password(password):
        failed_count = recent_fails + 1
        db.add(
            UserAuthLog(
                user_id=user.id,
                auth_method="password",
                auth_status="failed",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
                failed_attempts=failed_count,
                tenant_id=tenant.id,
            )
        )
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action=f"Failed login: Invalid password ({failed_count})",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=(failed_count >= 3),
            )
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = (
        db.query(UserAccessControl)
        .join(UserRole, UserRole.id == UserAccessControl.role_id)
        .filter(
            UserAccessControl.user_id == user.id,
            UserAccessControl.tenant_id == tenant.id,
            UserRole.tenant_id == tenant.id,
        )
        .first()
    )
    role_name = access.role.role_name if access and access.role else "user"

    has_webauthn_credentials = (
        db.query(WebAuthnCredential)
        .filter_by(user_id=user.id, tenant_id=tenant.id)
        .first()
        is not None
    )
    preferred_mfa = (tenant_user.preferred_mfa or "both").lower()
    require_totp = False
    require_webauthn = False
    require_totp_setup = False
    skip_all_mfa = False

    if tenant.enforce_strict_mfa:
        if preferred_mfa == "webauthn" and has_webauthn_credentials and _webauthn_allowed(request):
            require_webauthn = True
        else:
            require_totp = True
    else:
        if preferred_mfa == "totp":
            require_totp = True
        elif preferred_mfa == "webauthn":
            require_webauthn = has_webauthn_credentials and _webauthn_allowed(request)
            if not require_webauthn:
                require_totp = True
        else:
            require_totp = True
            require_webauthn = has_webauthn_credentials and _webauthn_allowed(request)

    if require_totp and not tenant_user.otp_secret:
        require_totp_setup = True
        require_totp = False

    fp = get_request_fingerprint(request, tenant.id)
    access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})
    refresh_token = create_refresh_token(identity=str(user.id))
    response = {
        "message": "Login successful",
        "user_id": user.id,
        "access_token": access_token,
        "role": role_name,
        "trust_score": round(user.trust_score or 0.0, 2),
        "require_totp": require_totp,
        "require_webauthn": require_webauthn,
        "require_totp_setup": require_totp_setup,
        "skip_all_mfa": skip_all_mfa,
        "has_webauthn_credentials": has_webauthn_credentials,
    }
    response_obj = JSONResponse(response)
    set_access_cookie(response_obj, access_token)
    set_refresh_cookie(response_obj, refresh_token)
    return response_obj


@router.post("/forgot-password")
def forgot_password(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    identifier = payload.get("identifier")
    redirect_url = payload.get("redirect_url")
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier (mobile number or email) is required.",
        )
    if not redirect_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing redirect URL for client-side reset.",
        )

    tenant_user = db.query(TenantUser).filter_by(
        company_email=identifier, tenant_id=tenant.id
    ).first()

    if tenant_user:
        user = tenant_user.user
    else:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        tenant_user = (
            db.query(TenantUser).filter_by(user_id=sim.user.id, tenant_id=tenant.id).first()
            if sim and sim.user
            else None
        )
        user = tenant_user.user if tenant_user else None

    if not user:
        db.add(
            RealTimeLog(
                user_id=None,
                tenant_id=tenant.id,
                action=f"Failed password reset request: Unknown identifier {identifier}",
                ip_address=request.client.host if request.client else None,
                device_info="IAMaaS API Access",
                location=get_ip_location(request.client.host if request.client else ""),
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found under this tenant",
        )

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="Password reset requested",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=False,
        )
    )
    db.commit()

    reset_link = f"{redirect_url}?token={token}"
    send_tenant_password_reset_email(
        user=user,
        raw_token=token,
        tenant_name=tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link,
    )
    return {"message": "Please check your email for a password reset link."}


@router.post("/reset-password")
def reset_password(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    token = payload.get("token")
    new_password = payload.get("new_password")
    confirm_password = payload.get("confirm_password")
    if not token or not new_password or not confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token, new password, and confirmation are required.",
        )
    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token.")

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized reset attempt.")

    ip_address = request.client.host if request.client else None
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    if user.trust_score >= 0.6:
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action="Password reset denied due to elevated risk score",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This reset request was blocked due to suspicious activity.",
        )

    if not is_strong_password(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least 8 characters long and include an uppercase letter, "
                "lowercase letter, number, and special character."
            ),
        )

    if check_password_hash(tenant_user.password_hash, new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password.",
        )

    old_passwords = db.query(TenantPasswordHistory).filter_by(tenant_user_id=tenant_user.id).all()
    for record in old_passwords:
        if check_password_hash(record.password_hash, new_password):
            db.add(
                RealTimeLog(
                    user_id=user.id,
                    tenant_id=tenant.id,
                    action="Attempted to reuse an old password during reset",
                    ip_address=ip_address,
                    device_info=device_info,
                    location=location,
                    risk_alert=True,
                )
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used this password. Please choose a new one.",
            )

    new_hash = generate_password_hash(new_password)
    tenant_user.password_hash = new_hash
    db.add(TenantPasswordHistory(tenant_user_id=tenant_user.id, password_hash=new_hash))

    history = (
        db.query(TenantPasswordHistory)
        .filter_by(tenant_user_id=tenant_user.id)
        .order_by(TenantPasswordHistory.created_at.desc())
        .all()
    )
    if len(history) > 5:
        for old in history[5:]:
            db.delete(old)

    user.reset_token = None
    user.reset_token_expiry = None
    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="Password reset after MFA and checks",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
        )
    )
    request.session.clear()
    db.commit()
    return {"message": "Your password has been successfully reset. You may now log in with your new credentials."}


@router.get("/enroll-totp")
def enroll_totp(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    tenant_user = db.query(TenantUser).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    rp_id = _tenant_rp_id(request, tenant)
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user_id,
            Device.tenant_id == tenant.id,
            DeviceKey.rp_id == rp_id,
        )
        .order_by(DeviceKey.created_at.desc())
        .first()
    )
    device_enrolled = device_key is not None
    reset_required = (
        tenant_user.otp_secret is None
        or (tenant_user.otp_secret and tenant_user.otp_email_label != tenant_user.company_email)
        or not device_enrolled
    )
    if not reset_required:
        return {"message": "TOTP already configured.", "reset_required": False}

    secret = pyotp.random_base32()
    email = tenant_user.company_email
    expires = datetime.utcnow() + timedelta(minutes=10)
    db.query(PendingTOTP).filter_by(user_id=user_id, tenant_id=tenant.id).delete()
    pending = PendingTOTP(
        user_id=user_id,
        tenant_id=tenant.id,
        secret=secret,
        email=email,
        expires_at=expires,
    )
    db.add(pending)
    db.commit()

    enroll_token = issue_enroll_token(
        {
            "pending_id": pending.id,
            "user_id": user_id,
            "tenant_id": tenant.id,
            "email": email,
            "rp_id": rp_id,
        }
    )
    api_base_url = resolve_api_base_url(request, "/api/v1/auth", override_env="ZT_AUTH_IAM_API_BASE_URL")

    payload = build_enrollment_payload(
        email=email,
        rp_id=rp_id,
        rp_display_name=tenant.name or "ZT-IAM",
        issuer=tenant.name or "ZT-IAM",
        account_name=email,
        device_label="ZT-Authenticator Device",
        enroll_token=enroll_token,
        api_base_url=api_base_url,
    )

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
def confirm_totp_setup(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    tenant_user = db.query(TenantUser).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    pending = db.query(PendingTOTP).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if pending and pending.expires_at >= datetime.utcnow():
        tenant_user.otp_secret = pending.secret
        tenant_user.otp_email_label = pending.email
        db.delete(pending)
    elif not tenant_user.otp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid pending TOTP enrollment.")

    recovery_codes = _replace_recovery_codes(db, user_id, tenant.id)
    db.commit()
    message = "TOTP enrollment confirmed." if pending else "TOTP already configured."
    return {"message": message, "recovery_codes": recovery_codes}


@router.post("/verify-totp-login")
def verify_totp_login(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    tenant_user = db.query(TenantUser).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if not tenant_user or not tenant_user.otp_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user or TOTP not configured.")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    totp_code = payload.get("totp")
    if not totp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP code is required.")

    ip_address = request.client.host if request.client else None
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"TOTP locked. Try again after {user.locked_until}.",
        )

    threshold_time = datetime.utcnow() - timedelta(minutes=5)
    recent_otp_fails = (
        db.query(UserAuthLog)
        .filter_by(user_id=user.id, auth_method="totp", auth_status="failed")
        .filter(UserAuthLog.auth_timestamp >= threshold_time)
        .count()
    )

    if not verify_totp_code(tenant_user.otp_secret, totp_code, valid_window=1):
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
                tenant_id=tenant.id,
            )
        )
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action=f"Failed TOTP login ({fail_count} failures)",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
        )
        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.add(
                RealTimeLog(
                    user_id=user.id,
                    tenant_id=tenant.id,
                    action="TOTP temporarily locked after multiple failed attempts",
                    ip_address=ip_address,
                    device_info=device_info,
                    location=location,
                    risk_alert=True,
                )
            )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired TOTP code.")

    rp_id = _tenant_rp_id(request, tenant)
    device_key = (
        db.query(DeviceKey)
        .join(Device, Device.id == DeviceKey.device_id)
        .filter(
            Device.user_id == user.id,
            Device.tenant_id == tenant.id,
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
        tenant_id=tenant.id,
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
            tenant_id=tenant.id,
        )
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="TOTP verified; awaiting device approval",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
        )
    )
    db.commit()

    has_webauthn_credentials = (
        db.query(WebAuthnCredential)
        .filter_by(user_id=user.id, tenant_id=tenant.id)
        .first()
        is not None
    )
    require_webauthn = tenant_user.preferred_mfa in ["both", "webauthn"]
    return {
        "message": "TOTP verified. Awaiting device approval.",
        "require_device_approval": True,
        "login_id": challenge.id,
        "expires_in": 120,
        "require_webauthn": require_webauthn,
        "has_webauthn_credentials": has_webauthn_credentials,
        "user_id": user.id,
    }


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

    token_user_id = token_data.get("user_id")
    token_tenant_id = token_data.get("tenant_id")
    if str(pending.user_id) != str(token_user_id) or str(pending.tenant_id) != str(token_tenant_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment token mismatch")

    user = db.query(User).get(token_data.get("user_id"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tenant_user = (
        db.query(TenantUser)
        .filter_by(user_id=user.id, tenant_id=token_data.get("tenant_id"))
        .first()
    )
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    device = Device(
        user_id=user.id,
        tenant_id=tenant_user.tenant_id,
        device_label=payload.get("device_label") or "ZT-Authenticator Device",
        platform=payload.get("platform") or "unknown",
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    device_key = DeviceKey(
        device_id=device.id,
        tenant_id=tenant_user.tenant_id,
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
        .filter(Device.user_id == user.id, DeviceKey.rp_id == rp_id)
        .order_by(DeviceKey.created_at.desc())
        .first()
    )
    if not device_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device not enrolled")

    tenant_user = (
        db.query(TenantUser)
        .filter_by(user_id=user.id, tenant_id=device_key.tenant_id)
        .first()
    )
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    pending = (
        db.query(PendingTOTP)
        .filter_by(user_id=user.id, tenant_id=device_key.tenant_id)
        .first()
    )
    if not pending or pending.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending TOTP enrollment")

    tenant_user.otp_secret = pending.secret
    tenant_user.otp_email_label = pending.email
    db.delete(pending)
    recovery_codes = _replace_recovery_codes(db, user.id, device_key.tenant_id)
    db.commit()

    otpauth_uri = pyotp.TOTP(tenant_user.otp_secret).provisioning_uri(
        name=account_name,
        issuer_name=issuer,
    )
    return {"otpauth_uri": otpauth_uri, "recovery_codes": recovery_codes}


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

    expires_in = int((challenge.expires_at - datetime.utcnow()).total_seconds())
    return {
        "status": "pending",
        "login_id": str(challenge.id),
        "nonce": challenge.nonce,
        "rp_id": challenge.rp_id,
        "device_id": str(challenge.device_id),
        "expires_in": max(expires_in, 0),
    }


@router.post("/login/recover")
def login_recover(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    identifier = (payload.get("identifier") or payload.get("email") or "").strip()
    recovery_code = (payload.get("recovery_code") or "").strip()
    if not identifier or not recovery_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier and recovery_code are required",
        )

    user = None
    sim_card = (
        db.query(SIMCard)
        .filter_by(mobile_number=identifier, status="active")
        .first()
    )
    if sim_card and sim_card.user:
        user = sim_card.user

    if not user:
        user = db.query(User).filter_by(email=identifier).first()
    if not user:
        return {"status": "denied", "reason": "user_not_found"}

    tenant_user = (
        db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=user.id).first()
    )
    if not tenant_user:
        return {"status": "denied", "reason": "unauthorized"}

    if user.locked_until and user.locked_until > datetime.utcnow():
        return {"status": "denied", "reason": "locked"}

    if not _consume_recovery_code(db, user.id, tenant.id, recovery_code):
        return {"status": "denied", "reason": "invalid_recovery_code"}

    fp = get_request_fingerprint(request, tenant.id)
    access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})
    refresh_token = create_refresh_token(identity=str(user.id))

    db.commit()
    request.session["mfa_totp_verified"] = True
    request.session["mfa_webauthn_verified"] = True
    response = JSONResponse({"status": "ok", "reason": None})
    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    return response


@router.get("/login-status")
@router.get("/login/status")
def login_status(
    request: Request,
    login_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge or challenge.tenant_id != tenant.id:
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

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        return {"status": "denied", "reason": "unauthorized"}

    has_webauthn_credentials = (
        db.query(WebAuthnCredential)
        .filter_by(user_id=user.id, tenant_id=tenant.id)
        .first()
        is not None
    )
    require_webauthn = tenant_user.preferred_mfa in ["both", "webauthn"]
    return {
        "status": "ok",
        "require_webauthn": require_webauthn,
        "has_webauthn_credentials": has_webauthn_credentials,
        "user_id": user.id,
    }


@router.post("/login/deny")
def login_deny(
    payload: dict,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    login_id = payload.get("login_id")
    if not login_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login_id is required")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge or challenge.tenant_id != tenant.id:
        return {"status": "denied", "reason": "not_found"}

    if challenge.status == "pending":
        challenge.status = "denied"
        challenge.denied_reason = "cancelled"
        db.commit()

    return {"status": challenge.status, "reason": challenge.denied_reason}


@router.post("/feedback")
def submit_feedback(
    payload: dict,
    request: Request,
):
    store_feedback(
        payload,
        source="zt-authenticator-v1",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    return {"status": "ok"}


@router.post("/login/resend")
def login_resend(
    payload: dict,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    login_id = payload.get("login_id")
    if not login_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login_id is required")

    challenge = db.query(LoginChallenge).get(login_id)
    if not challenge or challenge.tenant_id != tenant.id:
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

    return {
        "status": "pending",
        "login_id": new_challenge.id,
        "expires_in": 120,
    }


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

    tenant_user = (
        db.query(TenantUser)
        .filter_by(user_id=challenge.user_id, tenant_id=challenge.tenant_id)
        .first()
    )
    if not tenant_user or not tenant_user.otp_secret:
        challenge.status = "denied"
        challenge.denied_reason = "totp_not_configured"
        db.commit()
        return {"status": "denied", "reason": "totp_not_configured"}

    if not verify_totp_code(tenant_user.otp_secret, otp, valid_window=1):
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
            user_id=tenant_user.user_id,
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
            user_id=tenant_user.user_id,
            tenant_id=challenge.tenant_id,
            action="ZT-Authenticator device approval success",
            ip_address=request.client.host if request.client else None,
            device_info="ZT-Authenticator device approval",
            location=get_ip_location(request.client.host) if request.client else None,
            risk_alert=False,
        )
    )
    db.commit()
    return {"status": "ok"}


@router.post("/request-totp-reset")
def request_totp_reset(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    identifier = payload.get("identifier")
    redirect_url = payload.get("redirect_url")
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier (mobile number or email) is required.",
        )
    if not redirect_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing redirect URL for client-side reset.",
        )

    user = db.query(User).filter_by(email=identifier).first()
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        user = sim.user if sim else None
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching account found.")

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered under this tenant.",
        )

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="TOTP reset link requested",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=True,
        )
    )
    db.commit()

    reset_link = f"{redirect_url}?token={token}"
    send_tenant_totp_reset_email(
        user=user,
        raw_token=token,
        tenant_name=tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link,
    )
    return {"message": "TOTP reset link has been sent to your email."}


@router.post("/out-request-webauthn-reset")
def out_request_webauthn_reset(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    identifier = (payload.get("identifier") or "").strip()
    redirect_url = payload.get("redirect_url")
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identifier (mobile or email) required")
    if not redirect_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing redirect URL for client-side reset.",
        )

    tenant_user = (
        db.query(TenantUser)
        .filter_by(company_email=identifier, tenant_id=tenant.id)
        .first()
    )
    if not tenant_user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        tenant_user = (
            db.query(TenantUser)
            .filter_by(user_id=sim.user.id, tenant_id=tenant.id)
            .first()
            if sim and sim.user
            else None
        )

    if not tenant_user:
        return {"message": "Please check your email for a WebAuthn reset link"}

    user = tenant_user.user
    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    reset_link = f"{redirect_url}?token={token}"
    send_tenant_webauthn_reset_email(
        user=user,
        raw_token=token,
        tenant_name=tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link,
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="WebAuthn reset requested",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "Please check your email for a WebAuthn reset link"}


@router.post("/out-verify-webauthn-reset/{token}")
def out_verify_webauthn_reset(
    token: str,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    password = payload.get("password")
    totp = payload.get("totp")
    if not password or not totp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password and TOTP code are required"
        )

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not registered under this tenant.")

    if not check_password_hash(tenant_user.password_hash, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not tenant_user.otp_secret or not verify_totp_code(tenant_user.otp_secret, totp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    creds = db.query(WebAuthnCredential).filter_by(user_id=user.id, tenant_id=tenant.id).all()
    if not creds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No WebAuthn credentials to reset")

    for cred in creds:
        db.delete(cred)

    user.reset_token = None
    user.reset_token_expiry = None

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="WebAuthn reset after verification",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "WebAuthn reset complete. Please enroll a new passkey."}


@router.post("/verify-totp-reset")
def verify_totp_reset_post(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    token = payload.get("token")
    password = payload.get("password")
    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not registered under this tenant.")

    if not check_password_hash(tenant_user.password_hash, password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password.")

    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")
    location = get_ip_location(ip_address)

    if user.trust_score >= 0.6:
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action="TOTP reset denied due to elevated risk score",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This TOTP reset request was blocked due to suspicious activity.",
        )

    has_webauthn = db.query(WebAuthnCredential).filter_by(user_id=user.id).count() > 0
    if has_webauthn and not request.session.get("reset_webauthn_verified"):
        return JSONResponse(
            {
                "require_webauthn": True,
                "message": "WebAuthn verification required before TOTP reset.",
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    tenant_user.otp_secret = None
    tenant_user.otp_email_label = None
    user.reset_token = None
    user.reset_token_expiry = None

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="TOTP reset after identity + trust check",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
        )
    )
    request.session.pop("reset_webauthn_verified", None)
    db.commit()
    return {"message": "TOTP has been reset. You will be prompted to set it up on next login."}


@router.post("/verify-fallback-totp")
def verify_fallback_totp(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
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

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user or not tenant_user.otp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No TOTP method set up")

    if verify_totp_code(tenant_user.otp_secret, code):
        request.session["reset_totp_verified"] = True
        request.session["reset_token_checked"] = token
        return {"message": "TOTP code verified successfully. You can now reset your password."}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")


@router.post("/logout")
def logout():
    response = JSONResponse({"message": "Logged out"})
    unset_auth_cookies(response)
    return response


@router.get("/health-check")
def health_check():
    return {"status": "ok"}


@router.get("/trust-score")
def trust_score(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    context = {
        "ip_address": request.client.host if request.client else None,
        "device_info": request.headers.get("User-Agent", ""),
    }
    score = evaluate_trust(user, context, tenant=tenant)
    return {"user_id": user.id, "trust_score": score}


@router.get("/tenant/roles")
def get_roles(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    roles = db.query(UserRole).filter(UserRole.tenant_id == tenant.id).all()
    return [{"id": role.id, "role_name": role.role_name} for role in roles]


@router.post("/tenant/roles")
def create_role(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    role_name = payload.get("role_name")
    if not role_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name is required")
    existing = db.query(UserRole).filter_by(role_name=role_name, tenant_id=tenant.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    role = UserRole(role_name=role_name, tenant_id=tenant.id)
    db.add(role)
    db.commit()
    return {"message": "Role created successfully", "role_id": role.id}


@router.put("/tenant/users/{user_id}")
def update_tenant_user(
    user_id: int,
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    tenant_user = db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=user_id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    email = payload.get("email")
    if email:
        tenant_user.company_email = email
    password = payload.get("password")
    if password:
        tenant_user.password_hash = generate_password_hash(password)
    new_mfa = payload.get("preferred_mfa")
    if new_mfa in ["totp", "webauthn", "both"]:
        tenant_user.preferred_mfa = new_mfa

    role_name = payload.get("role", "user").lower()
    role = db.query(UserRole).filter_by(role_name=role_name, tenant_id=tenant.id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role '{role_name}' not found")

    access_control = db.query(UserAccessControl).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if access_control:
        access_control.role_id = role.id
    else:
        db.add(UserAccessControl(user_id=user_id, role_id=role.id, tenant_id=tenant.id))

    db.commit()
    return {"message": "Tenant user updated successfully."}


@router.delete("/tenant/users/{user_id}")
def delete_tenant_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    tenant_user = db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=user_id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this tenant")

    access = db.query(UserAccessControl).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if access:
        db.delete(access)
    db.delete(tenant_user)
    db.commit()
    return {"message": "Tenant user deleted successfully"}


@router.get("/tenant/users")
def get_tenant_users(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    tenant_users = db.query(TenantUser).filter_by(tenant_id=tenant.id).all()
    users_data = []
    for t_user in tenant_users:
        user = t_user.user
        access = (
            db.query(UserAccessControl)
            .join(UserRole, UserRole.id == UserAccessControl.role_id)
            .filter(
                UserAccessControl.user_id == user.id,
                UserAccessControl.tenant_id == tenant.id,
                UserRole.tenant_id == tenant.id,
            )
            .first()
        )
        role_name = access.role.role_name if access and access.role else "N/A"
        sim = db.query(SIMCard).filter_by(user_id=user.id, status="active").first()
        mobile_number = sim.mobile_number if sim else "N/A"
        users_data.append(
            {
                "user_id": user.id,
                "mobile_number": mobile_number,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "email": t_user.company_email,
                "role": role_name,
            }
        )
    return {"users": users_data}


@router.get("/tenant/users/{user_id}")
def get_single_tenant_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    tenant_user = db.query(TenantUser).filter_by(tenant_id=tenant.id, user_id=user_id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in this tenant")

    access = (
        db.query(UserAccessControl)
        .join(UserRole, UserRole.id == UserAccessControl.role_id)
        .filter(
            UserAccessControl.user_id == user_id,
            UserRole.tenant_id == tenant.id,
        )
        .first()
    )
    role_name = access.role.role_name if access and access.role else "user"

    user = db.query(User).get(user_id)
    sim = db.query(SIMCard).filter_by(user_id=user.id, status="active").first()
    return {
        "user_id": user.id,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "email": tenant_user.company_email,
        "mobile_number": sim.mobile_number if sim else None,
        "role": role_name,
        "preferred_mfa": tenant_user.preferred_mfa,
    }


@router.post("/tenant/users")
def register_tenant_user(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    required_fields = ["mobile_number", "first_name", "password", "email"]
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

    sim_card = (
        db.query(SIMCard)
        .filter_by(mobile_number=payload["mobile_number"], status="active")
        .first()
    )
    if not sim_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobile number not recognized or not active",
        )

    user = db.query(User).get(sim_card.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SIM card not linked to any user",
        )

    if not user.first_name:
        user.first_name = payload.get("first_name", "").strip()
        user.last_name = ""
        db.add(user)

    existing_tenant_user = (
        db.query(TenantUser)
        .filter_by(tenant_id=tenant.id, user_id=user.id)
        .first()
    )
    if existing_tenant_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already registered under this tenant",
        )

    existing_email_user = (
        db.query(TenantUser)
        .filter_by(tenant_id=tenant.id, company_email=payload["email"])
        .first()
    )
    if existing_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already registered under this tenant",
        )

    tenant_user = TenantUser(
        tenant_id=tenant.id,
        user_id=user.id,
        company_email=payload["email"],
        password_hash=generate_password_hash(payload["password"]),
    )
    db.add(tenant_user)

    role_name = payload.get("role", "user").strip().lower()
    role = db.query(UserRole).filter_by(role_name=role_name, tenant_id=tenant.id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

    db.add(
        UserAccessControl(
            user_id=user.id,
            role_id=role.id,
            tenant_id=tenant.id,
            access_level=payload.get("access_level", "read"),
        )
    )

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action=f"IAM user registered via API (Mobile {payload['mobile_number']}, Role: {role_name})",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API",
            location=payload.get("location", "Unknown"),
            risk_alert=False,
        )
    )

    db.commit()
    return {
        "message": f"User registered successfully with role '{role_name}'.",
        "mobile_number": payload["mobile_number"],
        "tenant_email": payload["email"],
        "role": role_name,
    }


@router.post("/refresh")
def external_refresh(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        decoded = decode_token(refresh_token)
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token (no subject)")
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed to refresh.")

        fp = get_request_fingerprint(request, tenant.id)
        access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})
        resp = JSONResponse({"access_token": access_token})
        set_access_cookie(resp, access_token)

        db.add(
            RealTimeLog(
                user_id=user_id,
                tenant_id=tenant.id,
                action="token_refresh",
                ip_address=request.client.host if request.client else None,
                device_info=request.headers.get("User-Agent", "unknown"),
                location="external_client",
                risk_alert=False,
            )
        )
        db.commit()
        return resp
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token refresh failed: {exc}")


@router.get("/tenant-settings")
def get_tenant_settings(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    return {"api_key": tenant.api_key, "plan": tenant.plan or "Basic"}


@router.post("/change-plan")
def change_tenant_plan(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    new_plan = payload.get("plan", "").capitalize()
    allowed_plans = ["Basic", "Premium", "Enterprise"]
    if new_plan not in allowed_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: '{new_plan}'. Allowed plans: {', '.join(allowed_plans)}",
        )
    old_plan = tenant.plan or "Basic"
    tenant.plan = new_plan
    db.add(tenant)
    db.add(
        RealTimeLog(
            tenant_id=tenant.id,
            action=f"Plan changed from {old_plan} to {new_plan} via dashboard",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API",
            location="Tenant Self-Service",
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": f"Plan updated to '{new_plan}'", "plan": new_plan}


@router.get("/tenant/system-metrics")
def get_tenant_system_metrics(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    total_users = db.query(TenantUser).filter_by(tenant_id=tenant.id).count()
    today = datetime.utcnow().date()
    active_users_today = (
        db.query(UserAuthLog.user_id)
        .filter(
            UserAuthLog.tenant_id == tenant.id,
            UserAuthLog.auth_status == "success",
            UserAuthLog.auth_timestamp >= datetime.combine(today, datetime.min.time()),
        )
        .distinct()
        .count()
    )
    past_7_days = datetime.utcnow() - timedelta(days=7)
    logins_last_7_days = (
        db.query(UserAuthLog)
        .filter(
            UserAuthLog.tenant_id == tenant.id,
            UserAuthLog.auth_status == "success",
            UserAuthLog.auth_timestamp >= past_7_days,
        )
        .count()
    )
    totp_users = (
        db.query(TenantUser)
        .filter(TenantUser.tenant_id == tenant.id, TenantUser.otp_secret.isnot(None))
        .count()
    )
    webauthn_users = (
        db.query(WebAuthnCredential)
        .filter_by(tenant_id=tenant.id)
        .distinct(WebAuthnCredential.user_id)
        .count()
    )
    totp_percent = round((totp_users / total_users) * 100, 1) if total_users else 0
    webauthn_percent = round((webauthn_users / total_users) * 100, 1) if total_users else 0
    since_24h = datetime.utcnow() - timedelta(hours=24)
    api_calls_24h = (
        db.query(RealTimeLog)
        .filter(
            RealTimeLog.tenant_id == tenant.id,
            RealTimeLog.timestamp >= since_24h,
            RealTimeLog.action.ilike("%api%"),
        )
        .count()
    )
    return {
        "total_users": total_users,
        "active_users_today": active_users_today,
        "logins_last_7_days": logins_last_7_days,
        "totp_percent": totp_percent,
        "webauthn_percent": webauthn_percent,
        "api_calls_24h": api_calls_24h,
    }


@router.post("/tenant/trust-policy/upload")
def upload_trust_policy_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .json files are allowed")

    try:
        contents = file.file.read()
        parsed = json.loads(contents.decode("utf-8"))
        validate_trust_policy(parsed)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid policy file: {exc}")

    existing = db.query(TenantTrustPolicyFile).filter_by(tenant_id=tenant.id).first()
    if existing:
        existing.config_json = parsed
        existing.filename = file.filename
        existing.uploaded_at = datetime.utcnow()
    else:
        db.add(
            TenantTrustPolicyFile(
                tenant_id=tenant.id,
                filename=file.filename,
                config_json=parsed,
                uploaded_at=datetime.utcnow(),
            )
        )

    db.add(
        RealTimeLog(
            tenant_id=tenant.id,
            action=f"Trust Policy File Uploaded: {file.filename}",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API",
            location="Tenant Self-Service",
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "Trust policy uploaded successfully."}


@router.get("/tenant/trust-policy")
def get_uploaded_policy(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    policy = db.query(TenantTrustPolicyFile).filter_by(tenant_id=tenant.id).first()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No policy uploaded")
    return {
        "filename": policy.filename,
        "uploaded_at": policy.uploaded_at.isoformat() + "Z",
        "config": policy.config_json,
    }


@router.put("/tenant/trust-policy/edit")
def edit_trust_policy_json(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing JSON payload")
    try:
        validate_trust_policy(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid policy structure: {exc}"
        )

    policy = db.query(TenantTrustPolicyFile).filter_by(tenant_id=tenant.id).first()
    if policy:
        policy.config_json = payload
        policy.uploaded_at = datetime.utcnow()
    else:
        policy = TenantTrustPolicyFile(
            tenant_id=tenant.id,
            filename="inline_editor.json",
            config_json=payload,
            uploaded_at=datetime.utcnow(),
        )
        db.add(policy)

    db.add(
        RealTimeLog(
            tenant_id=tenant.id,
            action="Trust Policy Edited Inline (JSON)",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API",
            location="Tenant Dashboard",
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "Trust policy updated successfully."}


@router.delete("/tenant/trust-policy/clear")
def clear_trust_policy(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    existing = db.query(TenantTrustPolicyFile).filter_by(tenant_id=tenant.id).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No policy to clear")
    db.delete(existing)
    db.add(
        RealTimeLog(
            user_id=int(get_jwt_identity(request)),
            tenant_id=tenant.id,
            action="Trust policy cleared by tenant admin",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "Trust policy cleared successfully"}


@router.put("/tenant/user/preferred-mfa")
def update_user_mfa_preference(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = int(get_jwt_identity(request))
    preferred_mfa = payload.get("preferred_mfa")
    if preferred_mfa not in ["totp", "webauthn", "both"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA selection")

    tenant_user = db.query(TenantUser).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in this tenant")

    tenant_user.preferred_mfa = preferred_mfa
    db.commit()
    return {"message": "MFA preference updated"}


@router.get("/tenant/mfa-policy")
def get_mfa_policy(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    tenant_obj = db.query(Tenant).get(tenant.id)
    return {"enforce_strict_mfa": tenant_obj.enforce_strict_mfa}


@router.put("/tenant/mfa-policy")
def update_mfa_policy(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    value = payload.get("enforce_strict_mfa")
    if not isinstance(value, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid value")

    tenant_obj = db.query(Tenant).get(tenant.id)
    tenant_obj.enforce_strict_mfa = value
    db.commit()
    return {"message": "MFA policy updated", "enforce_strict_mfa": value}


@router.post("/webauthn/register-begin")
def begin_webauthn_registration(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(",") if c.transports else [],
            "type": "public-key",
        }
        for c in user.webauthn_credentials
        if c.tenant_id == tenant.id
    ]

    registration_data, state = webauthn_server.register_begin(
        {
            "id": str(user.id).encode(),
            "name": tenant_user.company_email,
            "displayName": f"{user.first_name} {user.last_name or ''}".strip(),
        },
        credentials,
    )
    public_key = jsonify_webauthn(registration_data["publicKey"])
    return {"public_key": public_key, "state": state}


@router.post("/webauthn/register-complete")
def complete_webauthn_registration(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    if not payload or "state" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing WebAuthn registration state.")
    if payload.get("id") != payload.get("rawId"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credential ID mismatch.")

    response = {
        "id": payload["id"],
        "rawId": payload["rawId"],
        "type": payload["type"],
        "response": {
            "attestationObject": payload["response"]["attestationObject"],
            "clientDataJSON": payload["response"]["clientDataJSON"],
        },
    }

    auth_data = webauthn_server.register_complete(payload["state"], response)
    cred_data = auth_data.credential_data
    public_key_bytes = cbor.encode(cred_data.public_key)

    credential = WebAuthnCredential(
        user_id=user.id,
        tenant_id=tenant.id,
        credential_id=cred_data.credential_id,
        public_key=public_key_bytes,
        sign_count=0,
        transports=",".join(payload.get("transports", [])),
    )
    db.add(credential)
    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="WebAuthn credential registered",
            ip_address=request.client.host if request.client else None,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": "WebAuthn registered successfully."}


@router.post("/webauthn/assertion-begin")
def begin_webauthn_assertion(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    tenant_credentials = db.query(WebAuthnCredential).filter_by(user_id=user.id, tenant_id=tenant.id).all()
    if not tenant_credentials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No registered WebAuthn credentials found.")

    credentials = [
        {
            "id": cred.credential_id,
            "type": "public-key",
            "transports": cred.transports.split(",") if cred.transports else [],
        }
        for cred in tenant_credentials
    ]

    assertion_data, state = webauthn_server.authenticate_begin(credentials)
    request.session["webauthn_assertion_state"] = state
    request.session["assertion_user_id"] = user.id
    request.session["assertion_tenant_id"] = tenant.id
    request.session["mfa_webauthn_verified"] = False

    public_key = assertion_data.public_key
    response_payload = {
        "challenge": websafe_encode(public_key.challenge),
        "rpId": public_key.rp_id,
        "userVerification": public_key.user_verification,
        "timeout": public_key.timeout,
        "allowCredentials": [
            {
                "type": c.type.value,
                "id": websafe_encode(c.id),
                "transports": [t.value for t in c.transports] if c.transports else [],
            }
            for c in (public_key.allow_credentials or [])
        ],
    }

    return {"public_key": response_payload, "state": state, "user_id": user.id}


@router.post("/webauthn/assertion-complete")
def complete_webauthn_assertion(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    state = request.session.get("webauthn_assertion_state") or payload.get("state")
    user_id = request.session.get("assertion_user_id") or get_jwt_identity(request)
    if not state or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No assertion in progress.")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

    credential_id = websafe_decode(payload["credentialId"])
    credential = (
        db.query(WebAuthnCredential)
        .filter_by(user_id=user.id, credential_id=credential_id, tenant_id=tenant.id)
        .first()
    )

    ip_address = request.client.host if request.client else None
    location = get_ip_location(ip_address)
    device_info = "IAMaaS API Access"

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"WebAuthn locked. Try again after {user.locked_until}",
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
                tenant_id=tenant.id,
            )
        )
        db.add(
            RealTimeLog(
                user_id=user.id,
                tenant_id=tenant.id,
                action=f"Failed WebAuthn: Credential not found ({fail_count})",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=(fail_count >= 3),
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

    request.session["mfa_webauthn_verified"] = True
    request.session.pop("webauthn_assertion_state", None)
    request.session.pop("assertion_user_id", None)

    db.add(
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant.id,
            action="Logged in via WebAuthn",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
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
            tenant_id=tenant.id,
        )
    )
    db.commit()

    fp = get_request_fingerprint(request, tenant.id)
    access_token = create_access_token(identity=str(user.id), additional_claims={"fp": fp})
    response = JSONResponse({"message": "Login successful", "user_id": user.id, "access_token": access_token})
    set_access_cookie(response, access_token)
    return response


@router.post("/webauthn/reset-assertion-begin")
def begin_reset_webauthn_assertion(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token.")

    user = db.query(User).filter_by(reset_token=hash_token(token)).first()
    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first() if user else None
    if not tenant_user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reset token invalid or expired.")
    if not user.webauthn_credentials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no registered WebAuthn credentials.")

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
    request.session["reset_token_checked"] = token
    request.session["reset_context"] = "iam_reset"

    return {"public_key": jsonify_webauthn(assertion_data["publicKey"])}


@router.post("/webauthn/reset-assertion-complete")
def complete_reset_webauthn_assertion(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    user_id = request.session.get("reset_user_id")
    state = request.session.get("reset_webauthn_assertion_state")
    if not state or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No reset verification in progress.")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    tenant_user = db.query(TenantUser).filter_by(user_id=user.id, tenant_id=tenant.id).first()
    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Wrong tenant.")

    credential_id = websafe_decode(payload["credentialId"])
    credential = (
        db.query(WebAuthnCredential)
        .filter_by(user_id=user.id, credential_id=credential_id, tenant_id=tenant.id)
        .first()
    )
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found.")

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

    request.session["reset_webauthn_verified"] = True
    request.session.pop("reset_webauthn_assertion_state", None)
    request.session.pop("reset_user_id", None)

    return {"message": "WebAuthn reset assertion verified."}
