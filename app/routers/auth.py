import base64
import io
from datetime import datetime, timedelta

import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request, status
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
    OTPCode,
    PasswordHistory,
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
from utils.location import get_ip_location
from utils.logging_helpers import log_auth_event, log_realtime_event
from utils.security import generate_token, hash_token, is_strong_password
from utils.totp import verify_totp_code
from utils.user_trust_engine import evaluate_trust

router = APIRouter(prefix="/api/auth", tags=["Auth"])
templates = Jinja2Templates(directory="templates")


class LoginPayload(dict):
    pass


class RegisterPayload(dict):
    pass


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

    context = {"ip_address": ip_address, "device_info": device_info}
    trust_score = evaluate_trust(user, context)
    risk_level = "high" if trust_score >= 0.7 else "medium" if trust_score >= 0.4 else "low"

    preferred_mfa = (user.preferred_mfa or "both").lower()
    require_totp = False
    require_webauthn = False
    skip_all_mfa = False

    if trust_score >= 0.95:
        skip_all_mfa = True

    if not skip_all_mfa:
        if preferred_mfa == "totp":
            require_totp = bool(user.otp_secret)
        elif preferred_mfa == "webauthn":
            require_webauthn = True
        elif preferred_mfa == "both":
            require_totp = bool(user.otp_secret)
            require_webauthn = True

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
        risk_alert=(risk_level == "high"),
    )
    db.commit()

    response = JSONResponse(
        {
            "message": "Login successful",
            "user_id": user.id,
            "trust_score": trust_score,
            "risk_level": risk_level,
            "require_totp": require_totp,
            "require_totp_setup": user.otp_secret is None,
            "require_totp_reset": bool(user.otp_secret and user.otp_email_label != user.email),
            "require_webauthn": require_webauthn,
            "skip_all_mfa": skip_all_mfa,
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

    reset_required = user.otp_secret is None or (
        user.otp_secret and user.otp_email_label != user.email
    )
    if reset_required:
        secret = pyotp.random_base32()
        request.session["pending_totp_secret"] = secret
        request.session["pending_totp_email"] = user.email

        totp_uri = pyotp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name="ZTN_MoMo_SIM"
        )
        qr = qrcode.make(totp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()

        return {
            "qr_code": f"data:image/png;base64,{img_base64}",
            "manual_key": secret,
            "reset_required": True,
        }

    return {"message": "TOTP already configured."}


@router.post("/setup-totp/confirm")
def confirm_totp_setup(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    secret = request.session.get("pending_totp_secret")
    email = request.session.get("pending_totp_email")
    if not secret or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending TOTP enrollment")

    user.otp_secret = secret
    user.otp_email_label = email
    db.commit()

    request.session.pop("pending_totp_secret", None)
    request.session.pop("pending_totp_email", None)

    return {"message": "TOTP enrollment confirmed."}


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

    if not verify_totp_code(user.otp_secret, totp_code):
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

    db.add(
        UserAuthLog(
            user_id=user.id,
            auth_method="totp",
            auth_status="success",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            failed_attempts=0,
            tenant_id=1,
        )
    )
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="TOTP verification success",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    request.session["mfa_totp_verified"] = True
    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(access.role_id).role_name.lower() if access else "user"
    urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }

    preferred_mfa = (user.preferred_mfa or "both").lower()
    require_webauthn = preferred_mfa in ["webauthn", "both"]
    has_webauthn_credentials = bool(user.webauthn_credentials)

    return {
        "message": "TOTP verified",
        "user_id": user.id,
        "require_webauthn": require_webauthn,
        "has_webauthn_credentials": has_webauthn_credentials,
        "dashboard_url": urls.get(role, "/user/dashboard"),
    }


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
    if has_webauthn and not request.session.get("reset_webauthn_verified"):
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
    if not user:
        sim = db.query(SIMCard).filter_by(mobile_number=identifier, status="active").first()
        user = sim.user if sim else None

    if not user:
        return {"message": "Please check your email for a WebAuthn reset link"}

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

    if user.trust_score < 0.4:
        db.add(
            RealTimeLog(
                user_id=user.id,
                action="Password reset denied due to low trust score",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1,
            )
        )
        send_admin_alert(
            user=user,
            event_type="Blocked Password Reset (Low Trust Score)",
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

    if has_webauthn and not request.session.get("reset_webauthn_verified"):
        return JSONResponse(
            {
                "require_webauthn": True,
                "message": "WebAuthn verification required before resetting your password.",
            },
            status_code=status.HTTP_202_ACCEPTED,
        )

    if has_totp and not has_webauthn and not request.session.get("reset_totp_verified"):
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
