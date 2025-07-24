from flask import Blueprint, request, jsonify, session, g
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity
)
from models.models import (
    db, User, SIMCard, Wallet, UserAuthLog,
    Transaction, UserRole,
    UserAccessControl, RealTimeLog, OTPCode,TenantTrustPolicyFile,
    WebAuthnCredential, PasswordHistory,TenantPasswordHistory,Tenant, TenantUser,PendingTOTP
)
from werkzeug.security import check_password_hash, generate_password_hash
from utils.security import (
    is_strong_password, verify_totp,
    generate_token, hash_token
)
from utils.location import get_ip_location
from utils.email_alerts import send_password_reset_email
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from fido2.server import Fido2Server
from fido2.utils import websafe_encode
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    AuthenticatorData,
    AuthenticatorAssertionResponse
)
import json
from utils.api_key import require_api_key
from utils.totp import verify_totp_code
from fido2 import cbor
from fido2.utils import websafe_decode, websafe_encode
from utils.user_trust_engine import evaluate_trust
from utils.iam_tenant_email import send_tenant_password_reset_email, send_tenant_totp_reset_email, send_tenant_webauthn_reset_email

# Create Blueprint
iam_api_bp = Blueprint('iam_api', __name__, url_prefix='/api/v1/auth')

# FIDO2 Server for WebAuthn
rp = PublicKeyCredentialRpEntity(id="localhost.localdomain", name="ZTN Local")
server = Fido2Server(rp)

def jsonify_webauthn(data):
    """
    Recursively convert bytes in publicKeyCredentialCreationOptions to base64url-encoded strings.
    This is needed because WebAuthn spec uses ArrayBuffers which must be encoded for JSON.
    """
    import base64

    def convert(value):
        if isinstance(value, bytes):
            return base64.urlsafe_b64encode(value).rstrip(b'=').decode('utf-8')
        elif isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert(v) for v in value]
        else:
            return value

    return convert(data)

@iam_api_bp.route('/register', methods=['POST'])
@require_api_key
def register_user():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400

    required_fields = ['mobile_number', 'first_name', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field.replace('_', ' ').capitalize()} is required"}), 400

    if not is_strong_password(data['password']):
        return jsonify({
            "error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
        }), 400

    sim_card = SIMCard.query.filter_by(mobile_number=data['mobile_number'], status="active").first()
    if not sim_card:
        return jsonify({"error": "Mobile number not recognized or not active"}), 404

    user = User.query.get(sim_card.user_id)
    if not user:
        return jsonify({"error": "SIM card not linked to any user"}), 404

    existing_tenant_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        user_id=user.id
    ).first()

    if existing_tenant_user:
        return jsonify({"error": "User with this mobile number already registered under this tenant"}), 400

    existing_email_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        company_email=data['email']
    ).first()

    if existing_email_user:
        return jsonify({"error": "User with this email already registered under this tenant"}), 400

    #  Create TenantUser entry
    tenant_user = TenantUser(
        tenant_id=g.tenant.id,
        user_id=user.id,
        company_email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(tenant_user)

    #  NEW: Assign specified role or fallback to "user"
    role_name = data.get("role", "user").lower()

    role = UserRole.query.filter_by(role_name=role_name, tenant_id=g.tenant.id).first()
    if not role:
        return jsonify({"error": f"Role '{role_name}' not found for this tenant"}), 400

    # Create UserAccessControl entry
    access_control = UserAccessControl(
        user_id=user.id,
        role_id=role.id,
        access_level=data.get("access_level", "read")  # Optional: default to 'read'
    )
    db.session.add(access_control)

    #  Log registration event
    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action=f"🆕 IAMaaS User Registered via API (Mobile {data['mobile_number']}, Role: {role_name})",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location=data.get('location', 'Unknown'),
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": f"User registered successfully with role '{role_name}'.",
        "mobile_number": data['mobile_number'],
        "tenant_email": data['email'],
        "role": role_name
    }), 201


# Tenant Login
@iam_api_bp.route('/login', methods=['POST'])
@require_api_key
def login_user():
    def count_recent_failures(user_id, method="password", window_minutes=5):
        threshold = datetime.utcnow() - timedelta(minutes=window_minutes)
        return UserAuthLog.query.filter_by(
            user_id=user_id,
            auth_method=method,
            auth_status="failed"
        ).filter(UserAuthLog.auth_timestamp >= threshold).count()

    data = request.get_json()
    if not data or 'identifier' not in data or 'password' not in data:
        return jsonify({"error": "Mobile number/email and password required"}), 400

    login_input = data.get('identifier')
    password = data.get('password')

    ip_address = request.remote_addr
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    user = None

    # Lookup by SIM
    sim_card = SIMCard.query.filter_by(mobile_number=login_input, status='active').first()
    if sim_card and sim_card.user:
        user = sim_card.user

    # Lookup by email
    if not user:
        user = User.query.filter_by(email=login_input).first()

    if not user:
        db.session.add(RealTimeLog(
            user_id=None,
            tenant_id=g.tenant.id,
            action=f"❌ Failed login: Unknown identifier {login_input}",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({"error": "User not found"}), 404

    # Check tenant mapping
    tenant_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        user_id=user.id
    ).first()

    if not tenant_user:
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action=f"❌ Failed login: User not under tenant",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({"error": "User not found under this tenant"}), 404

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"Account locked. Try again after {user.locked_until}"}), 429

    # Check password
    if not check_password_hash(tenant_user.password_hash, password):
        failed_count = count_recent_failures(user.id) + 1

        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="password",
            auth_status="failed",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            failed_attempts=failed_count,
            tenant_id=g.tenant.id
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action=f"❌ Failed login: Invalid password ({failed_count})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=(failed_count >= 3)
        ))

        if failed_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=g.tenant.id,
                action="🚨 Account temporarily locked after multiple failed attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))

        db.session.commit()
        return jsonify({"error": "Invalid credentials"}), 401

    # Successful login - now calculate trust score
    # context = {
    #     "ip_address": ip_address,
    #     "device_info": device_info
    # }
    context = {
        "ip_address": "198.51.100.90",  # Simulated new IP
        "device_info": "MyCustomTestDevice/1.01"  # Simulated new device
    }


    trust_score = evaluate_trust(user, context, tenant=g.tenant)
    risk_level = (
        "high" if trust_score >= 0.7 else
        "medium" if trust_score >= 0.4 else
        "low"
    )

    access_token = create_access_token(identity=str(user.id))

    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="password",
        auth_status="success",
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        failed_attempts=0,
        tenant_id=g.tenant.id
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="✅ Successful login",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=(risk_level == "high")
    ))

    db.session.commit()

    # Resolve tenant-specific role
    user_access = UserAccessControl.query.join(UserRole).filter(
        UserAccessControl.user_id == user.id,
        UserRole.tenant_id == g.tenant.id
    ).first()

    role = user_access.role.role_name if user_access else "user"

    preferred_mfa = (tenant_user.preferred_mfa or "both").lower()

    # Enforce global MFA policy if enabled
    if g.tenant.enforce_strict_mfa:
        preferred_mfa = "both"

    # Determine MFA requirements based on trust score and preference
    require_totp = False
    require_webauthn = False
    skip_all_mfa = False

    if trust_score >= 0.95:
        skip_all_mfa = True

    if not skip_all_mfa:
        if preferred_mfa == "totp":
            require_totp = bool(tenant_user.otp_secret)
        elif preferred_mfa == "webauthn":
            require_webauthn = True
        elif preferred_mfa == "both":
            require_totp = bool(tenant_user.otp_secret)
            require_webauthn = True
    print(f"🔐 MFA Settings for user {user.id}: {preferred_mfa}")
    print(f"➡️ TOTP: {require_totp}, WebAuthn: {require_webauthn}, Skip All: {skip_all_mfa}")

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "access_token": access_token,
        "role": role,
        "trust_score": trust_score,
        "risk_level": risk_level,
        "require_totp": require_totp,
        "require_totp_setup": tenant_user.otp_secret is None,
        "require_totp_reset": tenant_user.otp_secret and tenant_user.otp_email_label != tenant_user.company_email,
        "require_webauthn": require_webauthn,
        "skip_all_mfa": skip_all_mfa
    }), 200

@iam_api_bp.route('/forgot-password', methods=['POST'])
@require_api_key
def forgot_password():
    data = request.get_json()
    identifier = data.get("identifier")
    redirect_url = data.get("redirect_url")

    if not identifier:
        return jsonify({"error": "Identifier (mobile number or email) is required."}), 400
    if not redirect_url:
        return jsonify({"error": "Missing redirect URL for client-side reset."}), 400

    tenant_user = TenantUser.query.filter_by(company_email=identifier, tenant_id=g.tenant.id).first()
    
    if tenant_user:
        user = tenant_user.user
    else:
        # fallback to SIM-based lookup
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        if sim and sim.user:
            tenant_user = TenantUser.query.filter_by(user_id=sim.user.id, tenant_id=g.tenant.id).first()
            user = tenant_user.user if tenant_user else None
        else:
            user = None

    if not user:
        db.session.add(RealTimeLog(
            user_id=None,
            tenant_id=g.tenant.id,
            action=f"❌ Failed password reset request: Unknown identifier {identifier}",
            ip_address=request.remote_addr,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.remote_addr),
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({"error": "User not found under this tenant"}), 404

    # 🔥 Generate secure reset token
    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)

    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="📧 Password reset requested",
        ip_address=request.remote_addr,
        device_info="IAMaaS API Access",
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))
    db.session.commit()

    # Construct tenant-scoped reset link
    reset_link = f"{redirect_url}?token={token}"

    send_tenant_password_reset_email(
        user=user,
        raw_token=token,
        tenant_name=g.tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link
    )

    return jsonify({"message": "Please check your email for a password reset link."}), 200


# Tenant reset password
@iam_api_bp.route('/reset-password', methods=['POST'])
@require_api_key
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not token or not new_password or not confirm_password:
        return jsonify({"error": "Token, new password, and confirmation are required."}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 400

    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized reset attempt."}), 403

    ip = request.remote_addr
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip)

    # Trust score enforcement
    if user.trust_score < 0.4:
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action="🚫 Password reset denied due to low trust score",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({
            "error": "This reset request was blocked due to suspicious activity."
        }), 403

    # Strength check
    if not is_strong_password(new_password):
        return jsonify({
            "error": (
                "Password must be at least 8 characters long and include an uppercase letter, "
                "lowercase letter, number, and special character."
            )
        }), 400

    # Session MFA logic
    if session.get("reset_token_checked") != token:
        session["reset_webauthn_verified"] = False
        session["reset_totp_verified"] = False
        session["reset_token_checked"] = token

    has_webauthn = WebAuthnCredential.query.filter_by(user_id=user.id).count() > 0
    has_totp = tenant_user.otp_secret is not None

    if has_webauthn and not session.get("reset_webauthn_verified"):
        return jsonify({
            "require_webauthn": True,
            "message": "WebAuthn verification required before resetting your password."
        }), 202

    if has_totp and not has_webauthn and not session.get("reset_totp_verified"):
        return jsonify({
            "require_totp": True,
            "message": "TOTP verification required before resetting your password."
        }), 202

    if not has_webauthn and not has_totp:
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action="❌ Password reset blocked — no MFA configured",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({
            "error": (
                "You need to have at least one multi-factor method (TOTP or WebAuthn) "
                "set up to reset your password."
            )
        }), 403

    # Reuse check — current password
    if check_password_hash(tenant_user.password_hash, new_password):
        return jsonify({"error": "New password must be different from the current password."}), 400

    # Reuse check — history
    old_passwords = TenantPasswordHistory.query.filter_by(tenant_user_id=tenant_user.id).all()
    for record in old_passwords:
        if check_password_hash(record.password_hash, new_password):
            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=g.tenant.id,
                action="❌ Attempted to reuse an old password during reset",
                ip_address=ip,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))
            db.session.commit()
            return jsonify({"error": "You have already used this password. Please choose a new one."}), 400

    # Hash and update password
    new_hash = generate_password_hash(new_password)
    tenant_user.password_hash = new_hash
    db.session.add(TenantPasswordHistory(
        tenant_user_id=tenant_user.id,
        password_hash=new_hash
    ))

    # Keep last 5 passwords
    history = TenantPasswordHistory.query.filter_by(tenant_user_id=tenant_user.id).order_by(
        TenantPasswordHistory.created_at.desc()).all()
    if len(history) > 5:
        for old in history[5:]:
            db.session.delete(old)

    #Clear reset token
    user.reset_token = None
    user.reset_token_expiry = None

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="✅ Password reset after MFA and checks",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False
    ))

    session.clear()

    db.session.commit()

    return jsonify({
        "message": "Your password has been successfully reset. You may now log in with your new credentials."
    }), 200


# Enroll the tenant's user TOTP
@iam_api_bp.route('/enroll-totp', methods=['GET'])
@jwt_required(locations=["headers"])
@require_api_key
def enroll_totp():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    tenant_user = TenantUser.query.filter_by(
        user_id=user_id,
        tenant_id=tenant_id
    ).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    if tenant_user.otp_secret:
        return jsonify({
            "message": "TOTP already configured.",
            "reset_required": False
        }), 200

    secret = pyotp.random_base32()
    email = tenant_user.company_email
    expires = datetime.utcnow() + timedelta(minutes=10)

    # Delete previous pending if exists
    PendingTOTP.query.filter_by(user_id=user_id, tenant_id=tenant_id).delete()

    pending = PendingTOTP(
        user_id=user_id,
        tenant_id=tenant_id,
        secret=secret,
        email=email,
        expires_at=expires
    )
    db.session.add(pending)
    db.session.commit()

    uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=f"{g.tenant.name} (IAMaaS)")
    qr = qrcode.make(uri)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()

    return jsonify({
        "qr_code": f"data:image/png;base64,{img_base64}",
        "manual_key": secret,
        "reset_required": True
    }), 200
    # Already configured and company email matches
    return jsonify({
        "message": "TOTP already configured.",
        "reset_required": False
    }), 200


# Confirm the totp registration
@iam_api_bp.route('/setup-totp/confirm', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def confirm_totp_setup():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    pending = PendingTOTP.query.filter_by(user_id=user_id, tenant_id=tenant_id).first()
    if not pending or pending.expires_at < datetime.utcnow():
        return jsonify({"error": "No valid pending TOTP enrollment."}), 400

    tenant_user = TenantUser.query.filter_by(user_id=user_id, tenant_id=tenant_id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    tenant_user.otp_secret = pending.secret
    tenant_user.otp_email_label = pending.email
    db.session.delete(pending)
    db.session.commit()

    return jsonify({"message": "✅ TOTP enrollment confirmed."}), 200



# verify the tenants users totp
@iam_api_bp.route('/verify-totp-login', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def verify_totp_login():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    # Find the TenantUser association
    tenant_user = TenantUser.query.filter_by(
        user_id=user_id,
        tenant_id=tenant_id
    ).first()

    if not tenant_user or not tenant_user.otp_secret:
        return jsonify({"error": "Invalid user or TOTP not configured."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json()
    totp_code = data.get('totp')

    if not totp_code:
        return jsonify({"error": "TOTP code is required."}), 400

    ip_address = request.remote_addr
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    # Lockout check
    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"TOTP locked. Try again after {user.locked_until}."}), 429

    # Count recent OTP failures (last 5 minutes)
    threshold_time = datetime.utcnow() - timedelta(minutes=5)
    recent_otp_fails = UserAuthLog.query.filter_by(
        user_id=user.id,
        auth_method="totp",
        auth_status="failed"
    ).filter(UserAuthLog.auth_timestamp >= threshold_time).count()

    if not verify_totp_code(tenant_user.otp_secret, totp_code, valid_window=1):
        fail_count = recent_otp_fails + 1

        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="totp",
            auth_status="failed",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            failed_attempts=fail_count,
            tenant_id=tenant_id
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action=f"❌ Failed TOTP login ({fail_count} failures)",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))

        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=tenant_id,
                action="🚨 TOTP temporarily locked after multiple failed attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))

        db.session.commit()
        return jsonify({"error": "Invalid or expired TOTP code."}), 401

    # Successful TOTP verification
    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="totp",
        auth_status="success",
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        failed_attempts=0,
        tenant_id=tenant_id
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=tenant_id,
        action="✅ TOTP verified successfully",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False
    ))

    db.session.commit()

    # Check WebAuthn fallback status
    has_webauthn_credentials = WebAuthnCredential.query.filter_by(
        user_id=user.id,
        tenant_id=tenant_id
    ).first() is not None

    require_webauthn = tenant_user.preferred_mfa in ["both", "webauthn"]

    return jsonify({
        "message": "TOTP verified successfully.",
        "require_webauthn": require_webauthn,  
        "has_webauthn_credentials": has_webauthn_credentials,
        "user_id": user.id
    }), 200


# Tenant user totp reset from the Outside:
@iam_api_bp.route('/request-totp-reset', methods=['POST'])
@require_api_key
def request_totp_reset():
    data = request.get_json()
    identifier = data.get("identifier")
    redirect_url = data.get("redirect_url")

    if not identifier:
        return jsonify({"error": "Identifier (mobile number or email) is required."}), 400
    if not redirect_url:
        return jsonify({"error": "Missing redirect URL for client-side reset."}), 400

    # Resolve user from identifier
    user = User.query.filter_by(email=identifier).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        user = sim.user if sim else None

    if not user:
        return jsonify({"error": "No matching account found."}), 404

    # Tenant-aware match
    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
    if not tenant_user:
        return jsonify({"error": "User not registered under this tenant."}), 404

    # Generate secure reset token
    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    # Log request
    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="📨 TOTP reset link requested",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True
    ))

    db.session.commit()

    # Construct tenant-scoped reset link
    reset_link = f"{redirect_url}?token={token}"
    # Send tenant-customized email
    send_tenant_totp_reset_email(
        user=user,
        raw_token=token,
        tenant_name=g.tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link
    )

    return jsonify({"message": "TOTP reset link has been sent to your email."}), 200


@iam_api_bp.route('/verify-totp-reset', methods=['POST'])
@require_api_key
def verify_totp_reset_post():
    data = request.get_json()
    token = data.get("token")
    password = data.get("password")

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
    if not tenant_user:
        return jsonify({"error": "User not registered under this tenant."}), 403
    
    tenant_id = g.tenant.id
    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized reset attempt."}), 403

    #  Check tenant-specific password
    if not check_password_hash(tenant_user.password_hash, password):
        return jsonify({"error": "Invalid password."}), 403
    
    # # Check password
    # if not user.check_password(password):
    #     return jsonify({"error": "Incorrect password"}), 401

    ip = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip)

    # Trust score enforcement
    if user.trust_score < 0.5:
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action="⚠️ TOTP reset denied due to low trust score",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))

        send_admin_alert(
            user=user,
            event_type="Blocked TOTP Reset (Low Trust Score)",
            ip_address=ip,
            device_info=device_info,
            location=location
        )

        db.session.commit()
        return jsonify({
            "error": (
                "For your protection, this TOTP reset request has been blocked "
                "due to unusual activity or untrusted device. An administrator "
                "has been notified for further review."
            )
        }), 403

    # Optional WebAuthn enforcement
    has_webauthn = WebAuthnCredential.query.filter_by(user_id=user.id).count() > 0
    if has_webauthn and not session.get("reset_webauthn_verified"):
        return jsonify({
            "require_webauthn": True,
            "message": "WebAuthn verification required before TOTP reset."
        }), 202

    # Passed → reset tenant-scoped TOTP
    tenant_user.otp_secret = None
    tenant_user.otp_email_label = None
    user.reset_token = None
    user.reset_token_expiry = None

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="✅ TOTP reset after identity + trust check",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False
    ))

    session.pop("reset_webauthn_verified", None)

    db.session.commit()
    return jsonify({"message": "TOTP has been reset. You’ll be prompted to set it up on next login."}), 200



# Tenant user totp reset from the settings:
@iam_api_bp.route('/request-reset-totp', methods=['POST'])
@jwt_required()
@require_api_key
def request_reset_totp():
    user = TenantUser.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Make sure that user belongs to the tenant calling the API
    if user.tenant_id != g.tenant.id:
        return jsonify({"error": "Unauthorized access to user."}), 403

    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password is required."}), 400

    if not user.check_password(password):
        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="totp",
            auth_status="failed_reset",
            ip_address=request.remote_addr,
            location=get_ip_location(request.remote_addr),
            device_info="IAMaaS API Access",
            failed_attempts=1,
            tenant_id=g.tenant.id
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
            action="❌ Failed TOTP reset attempt: Incorrect password",
            ip_address=request.remote_addr,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.remote_addr),
            risk_alert=True
        ))

        db.session.commit()
        return jsonify({"error": "Incorrect password."}), 401

    # Clear TOTP info safely
    TenantUser.otp_secret = None
    TenantUser.otp_email_label = None

    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="totp",
        auth_status="reset",
        ip_address=request.remote_addr,
        location=get_ip_location(request.remote_addr),
        device_info="IAMaaS API Access",
        failed_attempts=0,
        tenant_id=g.tenant.id
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="🔁 TOTP reset successfully by user",
        ip_address=request.remote_addr,
        device_info="IAMaaS API Access",
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": "TOTP reset successfully. You’ll be asked to enroll TOTP again on next login."
    }), 200

@iam_api_bp.route('/verify-fallback-totp', methods=['POST'])
@require_api_key
def verify_fallback_totp():
    data = request.get_json()
    token = data.get("token")
    code = data.get("code")

    if not token or not code:
        return jsonify({"error": "Reset token and TOTP code are required"}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
    if not tenant_user or not tenant_user.otp_secret:
        return jsonify({"error": "No TOTP method set up"}), 400

    if verify_totp_code(tenant_user.otp_secret, code):
        session["reset_totp_verified"] = True
        session["reset_token_checked"] = token

        return jsonify({
            "message": "✅ TOTP code verified successfully. You can now reset your password."
        }), 200
    else:
        return jsonify({"error": "Invalid TOTP code"}), 401


# Enroll the tenants user webauthn
@iam_api_bp.route('/webauthn/register-begin', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def begin_webauthn_registration():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    # Load user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Ensure tenant match
    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    # Exclude tenant-specific credentials
    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(',') if c.transports else [],
            "type": "public-key"
        }
        for c in user.webauthn_credentials if c.tenant_id == tenant_id
    ]

    try:
        # Begin WebAuthn registration
        registration_data, state = server.register_begin(
            {
                "id": str(user.id).encode(),
                "name": tenant_user.company_email,
                "displayName": f"{user.first_name} {user.last_name or ''}".strip()
            },
            credentials
        )

        # JSONify registration options
        public_key = jsonify_webauthn(registration_data["publicKey"])

        # Return both publicKey and state in response
        return jsonify({
            "public_key": public_key,
            "state": state  # 🔥 Send state to client
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server failed to prepare WebAuthn registration."}), 500




# Completing the tenants user webauthn registration
@iam_api_bp.route('/webauthn/register-complete', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def complete_webauthn_registration():
    try:
        user_id = get_jwt_identity()
        tenant_id = g.tenant.id

        # Load user + tenant context
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
        if not tenant_user:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()

        if not data or "state" not in data:
            return jsonify({"error": "Missing WebAuthn registration state."}), 400

        if data["id"] != data["rawId"]:
            return jsonify({"error": "Credential ID mismatch."}), 400

        # Wrap response data
        response = {
            "id": data["id"],
            "rawId": data["rawId"],
            "type": data["type"],
            "response": {
                "attestationObject": data["response"]["attestationObject"],
                "clientDataJSON": data["response"]["clientDataJSON"]
            }
        }

        # Finalize registration with the passed state
        auth_data = server.register_complete(data["state"], response)
        cred_data = auth_data.credential_data
        public_key_bytes = cbor.encode(cred_data.public_key)

        # Save the credential
        credential = WebAuthnCredential(
            user_id=user.id,
            tenant_id=tenant_id,
            credential_id=cred_data.credential_id,
            public_key=public_key_bytes,
            sign_count=0,
            transports=",".join(data.get("transports", []))
        )
        db.session.add(credential)

        # Audit log
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action="✅ WebAuthn credential registered",
            ip_address=request.remote_addr,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.remote_addr),
            risk_alert=False
        ))

        db.session.commit()

        return jsonify({
            "message": "✅ WebAuthn registered successfully. Proceed to verification.",
            "redirect": "/auth/verify-webauthn"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Registration failed: {str(e)}"
        }), 500


# Tenat User Assertion begin
@iam_api_bp.route('/webauthn/assertion-begin', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def begin_webauthn_assertion():
    try:
        user_id = get_jwt_identity()
        tenant_id = g.tenant.id

        # Fetch user and confirm tenant membership
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        tenant_user = TenantUser.query.filter_by(
            user_id=user.id,
            tenant_id=tenant_id
        ).first()
        if not tenant_user:
            return jsonify({"error": "Unauthorized"}), 403

        # Only get WebAuthn credentials tied to this tenant
        tenant_credentials = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            tenant_id=tenant_id
        ).all()

        if not tenant_credentials:
            return jsonify({"error": "No registered WebAuthn credentials found."}), 404

        credentials = [
            {
                "id": cred.credential_id,
                "type": "public-key",
                "transports": cred.transports.split(',') if cred.transports else []
            }
            for cred in tenant_credentials
        ]

        # Generate challenge
        assertion_data, state = server.authenticate_begin(credentials)

        session["webauthn_assertion_state"] = state
        session["assertion_user_id"] = user.id
        session["assertion_tenant_id"] = tenant_id
        session["mfa_webauthn_verified"] = False

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
                    "transports": [t.value for t in c.transports] if c.transports else []
                } for c in (public_key.allow_credentials or [])
            ]
        }

        return jsonify({
            "public_key": response_payload,
            "state": state,
            "user_id": user.id
        }), 200



    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Assertion begin failed: {str(e)}"}), 500


# Tenant User Webauthn Assertion complete
@iam_api_bp.route('/webauthn/assertion-complete', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def complete_webauthn_assertion():
    from fido2.utils import websafe_decode

    try:
        data = request.get_json()
        
        # Restore session manually (if using API call with JWT)
        if "webauthn_assertion_state" not in session or "assertion_user_id" not in session:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found."}), 404

            #  Restore manually
            session["assertion_user_id"] = user.id
            session["webauthn_assertion_state"] = data.get("state")
        
        # Now fetch the restored values
        state = session.get("webauthn_assertion_state")
        user_id = session.get("assertion_user_id")
        tenant_id = g.tenant.id

        if not state or not user_id:
            return jsonify({"error": "No assertion in progress."}), 400

        # Unpack and rebuild valid state
        state = {
            "challenge": state.get("challenge"),
            "user_verification": state.get("user_verification")
        }


        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
        if not tenant_user:
            return jsonify({"error": "Unauthorized."}), 403

        credential_id = websafe_decode(data["credentialId"])
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id,
            tenant_id=tenant_id
        ).first()

        ip_address = request.remote_addr
        location = get_ip_location(ip_address)
        device_info = "IAMaaS API Access"

        if user.locked_until and user.locked_until > datetime.utcnow():
            return jsonify({"error": f"WebAuthn locked. Try again after {user.locked_until}"}), 429

        if not credential:
            threshold_time = datetime.utcnow() - timedelta(minutes=5)
            fail_count = UserAuthLog.query.filter_by(
                user_id=user.id,
                auth_method="webauthn",
                auth_status="failed"
            ).filter(UserAuthLog.auth_timestamp >= threshold_time).count() + 1

            if fail_count >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)

            db.session.add(UserAuthLog(
                user_id=user.id,
                auth_method="webauthn",
                auth_status="failed",
                ip_address=ip_address,
                location=location,
                device_info=device_info,
                failed_attempts=fail_count,
                tenant_id=tenant_id
            ))

            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=tenant_id,
                action=f"❌ Failed WebAuthn: Credential not found ({fail_count})",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=(fail_count >= 3)
            ))

            if fail_count >= 5:
                if user.email:
                    send_user_alert(
                        user=user,
                        event_type="webauthn_lockout",
                        ip_address=ip_address,
                        location=location,
                        device_info=device_info
                    )
                send_admin_alert(
                    user=user,
                    event_type="webauthn_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info
                )

            db.session.commit()
            return jsonify({"error": "Invalid WebAuthn credential."}), 401

        # Ensure data is a proper dictionary
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid request payload. Expected a JSON object."}), 400

        required_keys = {"credentialId", "authenticatorData", "clientDataJSON", "signature"}
        missing_keys = required_keys - data.keys()
        if missing_keys:
            return jsonify({"error": f"Missing fields: {', '.join(missing_keys)}"}), 400

        

       # Build WebAuthn response object (as dict)
            assertion = {
                "id": data["credentialId"],
                "rawId": websafe_decode(data["credentialId"]),
                "type": "public-key",
                "response": {
                    "authenticatorData": websafe_decode(data["authenticatorData"]),
                    "clientDataJSON": websafe_decode(data["clientDataJSON"]),
                    "signature": websafe_decode(data["signature"]),
                    "userHandle": websafe_decode(data["userHandle"]) if data.get("userHandle") else None
                }
            }

            #  Credential from DB
            public_key_source = {
                "id": credential.credential_id,
                "public_key": credential.public_key,
                "sign_count": credential.sign_count,
                "transports": credential.transports.split(",") if credential.transports else [],
                "user_handle": None,
            }

            #  Final auth check (note: NO brackets on `assertion`)
            server.authenticate_complete(
                state,
                assertion,
                [public_key_source]
            )


        session["mfa_webauthn_verified"] = True
        session.pop("webauthn_assertion_state", None)
        session.pop("assertion_user_id", None)

        
        # Get tenant-specific role for the user
        tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()

        role = "user"  # default fallback
        if tenant_user:
            access = UserAccessControl.query.join(UserRole).filter(
                UserAccessControl.user_id == tenant_user.user_id,
                UserRole.id == UserAccessControl.role_id,
                UserRole.tenant_id == tenant_id
            ).first()

            if access and access.role:
                role = access.role.role_name.lower()

        print("🧪 Resolved tenant role:", role)

        # Dashboard resolution
        if tenant_id == 1:
            urls = {
                "admin": url_for("admin.admin_dashboard", _external=True),
                "agent": url_for("agent.agent_dashboard", _external=True),
                "user": url_for("user.user_dashboard", _external=True)
            }
            dashboard_url = urls.get(role, url_for("user.user_dashboard", _external=True))
        else:
            if "localhost" in request.host or "127.0.0.1" in request.host:
                dashboard_url = f"https://localhost.localdomain:5000/{role}/dashboard"
            else:
                dashboard_url = f"https://{g.tenant.name.lower()}.yourdomain.com/{role}/dashboard"


        transports = credential.transports.split(",") if credential.transports else []
        if "hybrid" in transports:
            method = "cross-device passkey"
        elif "usb" in transports:
            method = "USB security key"
        elif "internal" in transports:
            method = "platform authenticator (fingerprint)"
        else:
            method = "unknown method"

        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action=f"🔐 Logged in via WebAuthn ({method})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False
        ))

        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="webauthn",
            auth_status="success",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            failed_attempts=0,
            tenant_id=tenant_id
        ))

        db.session.commit()

        # Issue final access_token after WebAuthn is complete
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "message": "✅ Login successful",
            "user_id": user.id,
            "access_token": access_token,
            "dashboard_url": dashboard_url
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"❌ Assertion failed: {str(e)}"
        }), 500


# ///////////////////////////////////
# Tenant User Webauth FallBack Section 
# ////////////////////////////////////
@iam_api_bp.route('/webauthn/reset-assertion-begin', methods=['POST'])
@require_api_key
def begin_reset_webauthn_assertion():
    try:
        data = request.get_json()
        token = data.get("token")
        if not token:
            return jsonify({"error": "Missing token."}), 400

        user = User.query.filter_by(reset_token=hash_token(token)).first()

        # Enforce tenant isolation
        tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first() if user else None
        if not tenant_user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
            return jsonify({"error": "Reset token invalid or expired."}), 403

        if not user.webauthn_credentials:
            return jsonify({"error": "User has no registered WebAuthn credentials."}), 404

        credentials = [
            {
                "id": c.credential_id,
                "transports": c.transports.split(',') if c.transports else [],
                "type": "public-key"
            }
            for c in user.webauthn_credentials
        ]

        assertion_data, state = server.authenticate_begin(credentials)

        session["reset_webauthn_assertion_state"] = state
        session["reset_user_id"] = user.id
        session["reset_token_checked"] = token  
        session["reset_context"] = "iam_reset"

        return jsonify({
            "public_key": jsonify_webauthn(assertion_data["publicKey"])
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Reset WebAuthn begin failed: {str(e)}"}), 500


@iam_api_bp.route('/webauthn/reset-assertion-complete', methods=['POST'])
@require_api_key
def complete_reset_webauthn_assertion():
    try:
        user_id = session.get("reset_user_id")
        state = session.get("reset_webauthn_assertion_state")

        if not state or not user_id:
            return jsonify({"error": "No reset verification in progress."}), 400

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({"error": "Invalid payload format. Expected a JSON object."}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        #  Enforce tenant isolation
        tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
        if not tenant_user:
            return jsonify({"error": "Unauthorized: Wrong tenant."}), 403

        credential_id = websafe_decode(data["credentialId"])
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id
        ).first()

        if not credential:
            return jsonify({"error": "Invalid credential."}), 401

        
        #  Build WebAuthn response object (as dict)
            assertion = {
                "id": data["credentialId"],
                "rawId": websafe_decode(data["credentialId"]),
                "type": "public-key",
                "response": {
                    "authenticatorData": websafe_decode(data["authenticatorData"]),
                    "clientDataJSON": websafe_decode(data["clientDataJSON"]),
                    "signature": websafe_decode(data["signature"]),
                    "userHandle": websafe_decode(data["userHandle"]) if data.get("userHandle") else None
                }
            }


        #  Credential from DB
            public_key_source = {
                "id": credential.credential_id,
                "public_key": credential.public_key,
                "sign_count": credential.sign_count,
                "transports": credential.transports.split(",") if credential.transports else [],
                "user_handle": None,
            }


        #  Final auth check (note: NO brackets on `assertion`)
            server.authenticate_complete(
                state,
                assertion,
                [public_key_source]
            )


        credential.sign_count += 1
        db.session.commit()

        #  Set verification flag
        session["reset_webauthn_verified"] = True
        session.pop("reset_webauthn_assertion_state", None)
        

        return jsonify({
            "message": "✅ Verified via WebAuthn for reset",
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"❌ Reset WebAuthn failed: {str(e)}"}), 500


@iam_api_bp.route('/verify-totp-reset', methods=['POST'])
@require_api_key
def verify_totp_reset():
    data = request.get_json()
    token = data.get("token")
    code = data.get("code")

    if not token or not code:
        return jsonify({"error": "Reset token and TOTP code are required"}), 400

    tenant_user = TenantUser.query.join(User).filter(
        User.reset_token == hash_token(token),
        User.reset_token_expiry > datetime.utcnow(),
        TenantUser.tenant_id == g.tenant.id
    ).first()

    user = tenant_user.user if tenant_user else None

    if not user:
        return jsonify({"error": "Invalid or expired token or unauthorized tenant access."}), 403

    if not user.otp_secret:
        return jsonify({"error": "No TOTP method set up"}), 400

    if verify_totp_code(user.otp_secret, code):
        # Mark TOTP as verified in session for this token
        session["reset_totp_verified"] = True
        session["reset_token_checked"] = token

        return jsonify({
            "message": "✅ TOTP code verified successfully. You can now reset your password."
        }), 200
    else:
        return jsonify({"error": "Invalid TOTP code"}), 401



# Tenants Logout and discarding the access token
@iam_api_bp.route('/logout', methods=['POST'])
@jwt_required()
@require_api_key
def logout_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    # 🔥 Log logout action
    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="🚪 User logged out",
        ip_address=request.remote_addr,
        device_info="IAMaaS API Access",
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))

    db.session.commit()

    # Note: in real stateless JWT, logout = client discards token.
    # Optionally, you can also add token to a blacklist if you want extra security.

    return jsonify({
        "message": "Successfully logged out. Please discard your access token."
    }), 200


@iam_api_bp.route("/health-check", methods=["GET"])
@require_api_key
def health_check():
    return jsonify({"message": "API key is valid and system is healthy."}), 200

@iam_api_bp.route('/trust-score', methods=['GET'])
@jwt_required()
@require_api_key
def get_trust_score():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    context = {
        "ip_address": request.remote_addr,
        "device_info": request.user_agent.string
    }

    tenant = g.tenant  # Injected from @require_api_key
    score = evaluate_trust(user, context, tenant=tenant)

    return jsonify({
        "user_id": user.id,
        "trust_score": score,
        "risk_level": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
    }), 200


# 1. Request to reset WebAuthn
@iam_api_bp.route('/out-request-webauthn-reset', methods=['POST'])
@require_api_key
def request_webauthn_reset():
    data = request.get_json()
    identifier = data.get("identifier")
    redirect_url = data.get("redirect_url")

    if not identifier:
        return jsonify({"error": "Identifier (email or mobile number) is required."}), 400

    user = User.query.filter_by(email=identifier).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        user = sim.user if sim else None

    if not user:
        return jsonify({"error": "No matching account found."}), 404

    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=g.tenant.id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized reset attempt for this tenant."}), 403

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)

    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry
    db.session.commit()

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action="📨 WebAuthn reset link requested",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True
    ))
    db.session.commit()

    #  Construct reset link
    reset_link = f"{redirect_url}?token={token}"
    # 📧 Send tenant-customized email

    send_tenant_webauthn_reset_email(
        user=user,
        raw_token=token,
        tenant_name=g.tenant.name,
        tenant_email=tenant_user.company_email,
        reset_link=reset_link
    )

    return jsonify({"message": "WebAuthn reset link has been sent to your email."}), 200

# Step 2: Verify Token and Reset WebAuthn (Password + TOTP Required)
@iam_api_bp.route('/out-verify-webauthn-reset/<token>', methods=['POST'])
@require_api_key
def verify_webauthn_reset(token):
    data = request.get_json()
    password = data.get("password")
    totp = data.get("totp")

    if not password or not totp:
        return jsonify({"error": "Password and TOTP code are required."}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 403

    #  Enforce tenant boundary
    tenant_id = g.tenant.id
    tenant_user = TenantUser.query.filter_by(user_id=user.id, tenant_id=tenant_id).first()
    if not tenant_user:
        return jsonify({"error": "Unauthorized reset attempt."}), 403

    #  Check tenant-specific password
    if not check_password_hash(tenant_user.password_hash, password):
        return jsonify({"error": "Invalid password."}), 403

    #  TOTP validation
    if not tenant_user.otp_secret:
        return jsonify({"error": "No TOTP configured for this account."}), 403

    totp_validator = pyotp.TOTP(tenant_user.otp_secret)
    if not totp_validator.verify(totp, valid_window=1):
        return jsonify({"error": "Invalid TOTP code."}), 403

    #  Tenant-scoped WebAuthn deletion
    WebAuthnCredential.query.filter_by(user_id=user.id, tenant_id=tenant_id).delete()
    db.session.flush()

    #  Clear reset token and flag for passkey re-registration
    user.reset_token = None
    user.reset_token_expiry = None
    user.passkey_required = True

    #  Audit Logs
    ip_address = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip_address)

    db.session.add_all([
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action="✅ WebAuthn reset verified",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ),
        RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action="🗑️ Deleted WebAuthn credentials",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=False
        )
    ])

    db.session.commit()

    return jsonify({
        "message": "✅ WebAuthn reset successful. Please log in and re-enroll your passkey."
    }), 200


# Tenants User Management
@iam_api_bp.route('/tenant/roles', methods=['GET'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_roles():
    roles = UserRole.query.filter(UserRole.tenant_id == g.tenant.id).all()

    return jsonify([
        {"id": r.id, "role_name": r.role_name}
        for r in roles
    ]), 200

@iam_api_bp.route('/tenant/roles', methods=['POST'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def create_role():
    data = request.get_json()
    role_name = data.get("role_name")

    if not role_name:
        return jsonify({"error": "Role name is required"}), 400

    existing = UserRole.query.filter_by(role_name=role_name, tenant_id=g.tenant.id).first()
    if existing:
        return jsonify({"error": "Role already exists"}), 400

    role = UserRole(role_name=role_name, tenant_id=g.tenant.id)
    db.session.add(role)
    db.session.commit()
    return jsonify({"message": "Role created successfully", "role_id": role.id}), 201


@iam_api_bp.route('/tenant/users/<int:user_id>', methods=['PUT'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def update_tenant_user(user_id):
    tenant_user = TenantUser.query.filter_by(tenant_id=g.tenant.id, user_id=user_id).first()
    if not tenant_user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    email = data.get("email")
    if email:
        tenant_user.company_email = email

    password = data.get("password")
    if password:
        tenant_user.password_hash = generate_password_hash(password)

    new_mfa = data.get("preferred_mfa")
    if new_mfa in ["totp", "webauthn", "both"]:
        tenant_user.preferred_mfa = new_mfa

    role_name = data.get("role", "user").lower()
    role = UserRole.query.filter_by(role_name=role_name, tenant_id=g.tenant.id).first()
    if not role:
        return jsonify({"error": f"Role '{role_name}' not found"}), 400

    access_control = UserAccessControl.query.filter_by(user_id=user_id).first()
    if access_control:
        access_control.role_id = role.id
    else:
        db.session.add(UserAccessControl(user_id=user_id, role_id=role.id))

    db.session.commit()

    return jsonify({"message": "Tenant user updated successfully."}), 200


@iam_api_bp.route('/tenant/users/<int:user_id>', methods=['DELETE'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def delete_tenant_user(user_id):
    tenant_user = TenantUser.query.filter_by(tenant_id=g.tenant.id, user_id=user_id).first()
    if not tenant_user:
        return jsonify({"error": "User not found for this tenant"}), 404

    access = UserAccessControl.query.filter_by(user_id=user_id).first()
    if access:
        db.session.delete(access)

    db.session.delete(tenant_user)
    db.session.commit()

    return jsonify({"message": "Tenant user deleted successfully"}), 200


@iam_api_bp.route('/tenant/users', methods=['GET'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_tenant_users():
    tenant_users = TenantUser.query.filter_by(tenant_id=g.tenant.id).all()
    users_data = []

    for t_user in tenant_users:
        user = t_user.user

        # 🧠 Get correct tenant-specific role
        access = UserAccessControl.query.join(UserRole).filter(
            UserAccessControl.user_id == user.id,
            UserAccessControl.tenant_id == g.tenant.id,
            UserAccessControl.role_id == UserRole.id,
            UserRole.tenant_id == g.tenant.id
        ).first()

        role_name = access.role.role_name if access and access.role else "N/A"

        #  Fetch active SIM only to avoid SWP_/OLD_ numbers
        sim = SIMCard.query.filter_by(user_id=user.id, status="active").first()
        mobile_number = sim.mobile_number if sim else "N/A"

        users_data.append({
            "user_id": user.id,
            "mobile_number": mobile_number,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "email": t_user.company_email,
            "role": role_name
        })

    return jsonify({"users": users_data}), 200


@iam_api_bp.route('/tenant/users/<int:user_id>', methods=['GET'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_single_tenant_user(user_id):
    tenant_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        user_id=user_id
    ).first()

    if not tenant_user:
        return jsonify({"error": "User not found in this tenant"}), 404

    #  Get the role assigned for this tenant
    access = UserAccessControl.query.join(UserRole).filter(
        UserAccessControl.user_id == user_id,
        UserRole.id == UserAccessControl.role_id,
        UserRole.tenant_id == g.tenant.id
    ).first()

    role_name = access.role.role_name if access and access.role else "user"

    # 🔍 Fetch user profile from core user table
    user = User.query.get(user_id)

    #  Only show the active SIM’s mobile number
    sim = SIMCard.query.filter_by(user_id=user.id, status="active").first()

    return jsonify({
        "user_id": user.id,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "email": tenant_user.company_email,
        "mobile_number": sim.mobile_number if sim else None,
        "role": role_name,
        "preferred_mfa": tenant_user.preferred_mfa
    }), 200


@iam_api_bp.route('/tenant/users', methods=['POST'])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def register_tenant_user():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400

    required_fields = ['mobile_number', 'first_name', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field.replace('_', ' ').capitalize()} is required"}), 400

    if not is_strong_password(data['password']):
        return jsonify({
            "error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
        }), 400

    sim_card = SIMCard.query.filter_by(mobile_number=data['mobile_number'], status="active").first()
    if not sim_card:
        return jsonify({"error": "Mobile number not recognized or not active"}), 404

    user = User.query.get(sim_card.user_id)
    if not user:
        return jsonify({"error": "SIM card not linked to any user"}), 404

    #  Only update first_name; treat it as full name
    if not user.first_name:
        user.first_name = data.get("first_name", "").strip()
        user.last_name = ""  # Or None — your choice
        db.session.add(user)

    existing_tenant_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        user_id=user.id
    ).first()

    if existing_tenant_user:
        return jsonify({"error": "User with this mobile number already registered under this tenant"}), 400

    existing_email_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        company_email=data['email']
    ).first()

    if existing_email_user:
        return jsonify({"error": "User with this email already registered under this tenant"}), 400

    tenant_user = TenantUser(
        tenant_id=g.tenant.id,
        user_id=user.id,
        company_email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(tenant_user)

    role_name = data.get("role", "user").strip().lower()
    role = UserRole.query.filter_by(role_name=role_name, tenant_id=g.tenant.id).first()

    access_control = UserAccessControl(
        user_id=user.id,
        role_id=role.id,
        tenant_id=g.tenant.id,
        access_level=data.get("access_level", "read")
    )
    db.session.add(access_control)

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action=f"🆕 IAMaaS User Registered via API (Mobile {data['mobile_number']}, Role: {role_name})",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location=data.get('location', 'Unknown'),
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": f"User registered successfully with role '{role_name}'.",
        "mobile_number": data['mobile_number'],
        "tenant_email": data['email'],
        "role": role_name
    }), 201



# Allowing external application to refresh access tokens
@iam_api_bp.route("/refresh", methods=["POST"])
@require_api_key
def external_refresh():
    """Allow external client apps to refresh access token via refresh token cookie."""
    refresh_token = request.cookies.get("refresh_token_cookie")

    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 401

    try:
        decoded = decode_token(refresh_token)
        user_id = decoded.get("sub")

        if not user_id:
            return jsonify({"error": "Invalid token (no subject)"}), 401

        #  Load user and tenant
        user = User.query.get(user_id)
        if not user or user.status == "suspended":
            return jsonify({"error": "User not allowed to refresh."}), 403

        tenant_id = user.tenant_id  # ⬅️ Assuming you have this field

        #  Generate fingerprint
        fingerprint = get_request_fingerprint(tenant_id)

        #  Issue new access token
        access_token = create_access_token(identity=str(user.id))
        resp = jsonify({"access_token": access_token})
        set_access_cookies(resp, access_token)

        #  Log refresh attempt
        log = RealTimeLog(
            actor="user",
            event="token_refresh",
            user_id=user_id,
            tenant_id=tenant_id,
            ip=request.headers.get("X-Real-IP") or request.remote_addr,
            fingerprint=fingerprint,
            metadata={
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "source": "external_client"
            }
        )
        db.session.add(log)
        db.session.commit()

        return resp, 200

    except Exception as e:
        return jsonify({"error": f"Token refresh failed: {str(e)}"}), 401


# Tenants Settings Self Management
@iam_api_bp.route("/tenant-settings", methods=["GET"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_tenant_settings():
    tenant = g.tenant
    return jsonify({
        "api_key": tenant.api_key,
        "plan": tenant.plan or "Basic"
    }), 200

@iam_api_bp.route("/change-plan", methods=["POST"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def change_tenant_plan():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400

    new_plan = data.get("plan", "").capitalize()
    allowed_plans = ["Basic", "Premium", "Enterprise"]

    if new_plan not in allowed_plans:
        return jsonify({"error": f"Invalid plan: '{new_plan}'. Allowed plans: {', '.join(allowed_plans)}"}), 400

    tenant = g.tenant
    old_plan = tenant.plan or "Basic"
    tenant.plan = new_plan
    db.session.add(tenant)

    db.session.add(RealTimeLog(
        tenant_id=tenant.id,
        action=f"📦 Plan changed from {old_plan} to {new_plan} via dashboard",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location="Tenant Self-Service",
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": f"Plan updated to '{new_plan}'",
        "plan": new_plan
    }), 200


# Tenants System Metrics
@iam_api_bp.route("/tenant/system-metrics", methods=["GET"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_tenant_system_metrics():
    tenant = g.tenant

    total_users = (
        db.session.query(TenantUser)
        .filter_by(tenant_id=tenant.id)
        .count()
    )

    today = datetime.utcnow().date()
    active_users_today = (
        db.session.query(UserAuthLog.user_id)
        .filter(
            UserAuthLog.tenant_id == tenant.id,
            db.func.date(UserAuthLog.auth_timestamp) == today,
            UserAuthLog.auth_status == "success"
        )
        .distinct()
        .count()
    )

    past_7_days = datetime.utcnow() - timedelta(days=7)
    logins_last_7_days = (
        db.session.query(UserAuthLog)
        .filter(
            UserAuthLog.tenant_id == tenant.id,
            UserAuthLog.auth_status == "success",
            UserAuthLog.auth_timestamp >= past_7_days
        )
        .count()
    )

    #  Count TOTP enrolled users (those with non-null otp_secret)
    totp_users = (
        db.session.query(TenantUser)
        .filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.otp_secret.isnot(None)
        )
        .count()
    )

    #  Count WebAuthn enrolled users
    webauthn_users = (
        db.session.query(WebAuthnCredential)
        .filter_by(tenant_id=tenant.id)
        .distinct(WebAuthnCredential.user_id)
        .count()
    )

    totp_percent = round((totp_users / total_users) * 100, 1) if total_users else 0
    webauthn_percent = round((webauthn_users / total_users) * 100, 1) if total_users else 0

    since_24h = datetime.utcnow() - timedelta(hours=24)
    api_calls_24h = (
        db.session.query(RealTimeLog)
        .filter(
            RealTimeLog.tenant_id == tenant.id,
            RealTimeLog.timestamp >= since_24h,
            RealTimeLog.action.ilike("%api%")
        )
        .count()
    )

    return jsonify({
        "total_users": total_users,
        "active_users_today": active_users_today,
        "logins_last_7_days": logins_last_7_days,
        "totp_percent": totp_percent,
        "webauthn_percent": webauthn_percent,
        "api_calls_24h": api_calls_24h
    }), 200


# Tenants Policy Management:
from utils.policy_validator import validate_trust_policy
@iam_api_bp.route("/tenant/trust-policy/upload", methods=["POST"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def upload_trust_policy_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    if not file.filename.endswith(".json"):
        return jsonify({"error": "Only .json files are allowed"}), 400

    try:
        parsed = json.load(file)
        validate_trust_policy(parsed)
    except Exception as e:
        return jsonify({"error": f"Invalid policy file: {str(e)}"}), 400

    tenant_id = g.tenant.id
    existing = TenantTrustPolicyFile.query.filter_by(tenant_id=tenant_id).first()

    if existing:
        existing.config_json = parsed
        existing.filename = file.filename
        existing.uploaded_at = datetime.utcnow()
    else:
        db.session.add(TenantTrustPolicyFile(
            tenant_id=tenant_id,
            filename=file.filename,
            config_json=parsed,
            uploaded_at=datetime.utcnow()
        ))


    db.session.add(RealTimeLog(
        tenant_id=tenant_id,
        action=f"📤 Trust Policy File Uploaded: {file.filename}",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location="Tenant Self-Service",
        risk_alert=False
    ))
    db.session.commit()

    return jsonify({"message": "Trust policy uploaded successfully."}), 200

@iam_api_bp.route("/tenant/trust-policy", methods=["GET"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def get_uploaded_policy():
    policy = TenantTrustPolicyFile.query.filter_by(tenant_id=g.tenant.id).first()
    if not policy:
        return jsonify({"error": "No policy uploaded"}), 404

    return jsonify({
    "filename": policy.filename,
    "uploaded_at": policy.uploaded_at.isoformat() + "Z",  
    "config": policy.config_json
}), 200


# Real time udpdate of the Tenant uploaded policy
@iam_api_bp.route("/tenant/trust-policy/edit", methods=["PUT"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def edit_trust_policy_json():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    try:
        validate_trust_policy(data)
    except Exception as e:
        return jsonify({"error": f"Invalid policy structure: {str(e)}"}), 400

    tenant_id = g.tenant.id
    policy = TenantTrustPolicyFile.query.filter_by(tenant_id=tenant_id).first()

    if policy:
        policy.config_json = data
        policy.uploaded_at = datetime.utcnow()
    else:
        policy = TenantTrustPolicyFile(
            tenant_id=tenant_id,
            filename="inline_editor.json",
            config_json=data,
            uploaded_at=datetime.utcnow()
        )
        db.session.add(policy)

    db.session.add(RealTimeLog(
        tenant_id=tenant_id,
        action="📝 Trust Policy Edited Inline (JSON)",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location="Tenant Dashboard",
        risk_alert=False
    ))

    db.session.commit()
    return jsonify({"message": "Trust policy updated successfully."}), 200


@iam_api_bp.route("/tenant/trust-policy/clear", methods=["DELETE"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def clear_trust_policy():
    if not g.tenant:
        return jsonify({"error": "No tenant context found"}), 400

    existing = TenantTrustPolicyFile.query.filter_by(tenant_id=g.tenant.id).first()
    if not existing:
        return jsonify({"error": "No policy to clear"}), 404

    db.session.delete(existing)
    db.session.add(RealTimeLog(
        user_id=get_jwt_identity(),
        tenant_id=g.tenant.id,
        action="🗑️ Trust policy cleared by tenant admin",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))
    db.session.commit()

    return jsonify({"message": "Trust policy cleared successfully"}), 200


# User profile management
@iam_api_bp.route("/tenant/user/preferred-mfa", methods=["PUT"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def update_user_mfa_preference():
    try:
        user_id = int(get_jwt_identity())
        tenant_id = g.tenant.id
        data = request.get_json()

        preferred_mfa = data.get("preferred_mfa")
        if preferred_mfa not in ["totp", "webauthn", "both"]:
            return jsonify({"error": "Invalid MFA selection"}), 400

        tenant_user = TenantUser.query.filter_by(user_id=user_id, tenant_id=tenant_id).first()
        if not tenant_user:
            return jsonify({"error": "User not found in this tenant"}), 404

        tenant_user.preferred_mfa = preferred_mfa
        db.session.commit()
        print("✅ New preferred_mfa:", tenant_user.preferred_mfa)
        return jsonify({"message": "MFA preference updated"}), 200

    except Exception as e:
        print("❌ MFA preference update error:", e)
        db.session.rollback()
        return jsonify({"error": "Failed to update MFA preference"}), 500

# Admin enforeces mfa policy for all the users
@iam_api_bp.route("/tenant/mfa-policy", methods=["GET", "PUT"])
@jwt_required(locations=['cookies', 'headers'])
@require_api_key
def manage_mfa_policy():
    tenant_id = g.tenant.id
    tenant = Tenant.query.get(tenant_id)

    if request.method == "GET":
        return jsonify({"enforce_strict_mfa": tenant.enforce_strict_mfa}), 200

    if request.method == "PUT":
        data = request.get_json()
        value = data.get("enforce_strict_mfa")
        if not isinstance(value, bool):
            return jsonify({"error": "Invalid value"}), 400

        tenant.enforce_strict_mfa = value
        db.session.commit()
        return jsonify({"message": "MFA policy updated", "enforce_strict_mfa": value}), 200