from flask import Blueprint, request, jsonify, session, g
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity
)
from models.models import (
    db, User, SIMCard, Wallet, UserAuthLog,
    Transaction, UserRole,
    UserAccessControl, RealTimeLog, OTPCode,
    WebAuthnCredential, PasswordHistory,TenantUser
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


# Create Blueprint
iam_api_bp = Blueprint('iam_api', __name__, url_prefix='/api/v1/auth')

# FIDO2 Server for WebAuthn
rp = PublicKeyCredentialRpEntity(id="localhost.localdomain", name="ZTN Local")
server = Fido2Server(rp)


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

   # 🔥 Find existing core user by mobile number
    sim_card = SIMCard.query.filter_by(mobile_number=data['mobile_number'], status="active").first()
    if not sim_card:
        return jsonify({"error": "Mobile number not recognized or not active"}), 404

    user = User.query.get(sim_card.user_id)
    if not user:
        return jsonify({"error": "SIM card not linked to any user"}), 404

    # 🔥 Check if user already registered under this tenant
    existing_tenant_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        user_id=user.id
    ).first()

    if existing_tenant_user:
        return jsonify({"error": "User with this mobile number already registered under this tenant"}), 400

    # 🔥 Ensure company email not already used under tenant
    existing_email_user = TenantUser.query.filter_by(
        tenant_id=g.tenant.id,
        company_email=data['email']
    ).first()

    if existing_email_user:
        return jsonify({"error": "User with this email already registered under this tenant"}), 400

    # 🔥 Create new tenant user
    tenant_user = TenantUser(
        tenant_id=g.tenant.id,
        user_id=user.id,
        company_email=data['email'],
        password_hash=generate_password_hash(data['password'])  # use werkzeug.security
    )

    db.session.add(tenant_user)

    # 🔥 Assign "user" role automatically if you want (optional)

    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=g.tenant.id,
        action=f"🆕 IAMaaS User Registered via API (Mobile {data['mobile_number']})",
        ip_address=request.remote_addr,
        device_info="IAMaaS API",
        location=data.get('location', 'Unknown'),
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": "User registered successfully.",
        "mobile_number": data['mobile_number'],
        "tenant_email": data['email']
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
    device_info = "IAMaaS API Access"  # 🛡️ For APIs
    location = get_ip_location(ip_address)

    user = None

    # 📍 First try to find the SIM
    sim_card = SIMCard.query.filter_by(mobile_number=login_input, status='active').first()
    if sim_card and sim_card.user:
        user = sim_card.user

    # 📍 If not, try email matching
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

    # 📍 Now check if user is registered under this tenant
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

    # 🔥 Check lock
    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"Account locked. Try again after {user.locked_until}"}), 429

    # 🔥 Password check (we validate against TenantUser password, not base User anymore)
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

    # 🔥 Successful login
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
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "access_token": access_token,
        "require_totp": bool(user.otp_secret),
        "require_totp_setup": user.otp_secret is None,
        "require_totp_reset": user.otp_secret and user.otp_email_label != user.email
    }), 200

@iam_api_bp.route('/forgot-password', methods=['POST'])
@require_api_key
def forgot_password():
    data = request.get_json()
    identifier = data.get("identifier")

    if not identifier:
        return jsonify({"error": "Identifier (mobile number or email) is required."}), 400

    # 🔥 Lookup user inside the current tenant (by email or SIM)
    user = User.query.filter_by(email=identifier, tenant_id=g.tenant.id).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        if sim and sim.user and sim.user.tenant_id == g.tenant.id:
            user = sim.user

    if not user:
        # 🔥 Log failed reset attempt
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

    # 🔥 Log the password reset request
    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=user.tenant_id,
        action="📧 Password reset requested",
        ip_address=request.remote_addr,
        device_info="IAMaaS API Access",
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))
    db.session.commit()

    # 🔥 Send reset link via email
    send_password_reset_email(user, token)

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

    # 🔥 Find user by token
    user = User.query.filter_by(reset_token=hash_token(token)).first()

    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 400

    # 🛡️ Tenant security check
    if user.tenant_id != g.tenant.id:
        return jsonify({"error": "Unauthorized reset attempt."}), 403

    ip = request.remote_addr
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip)

    # 🔥 Trust Score Check
    if user.trust_score < 0.4:
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action="🚫 Password reset denied due to low trust score",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({
            "error": (
                "This reset request was blocked due to suspicious activity. "
                "An administrator has been notified."
            )
        }), 403

    # 🔥 Password strength check
    if not is_strong_password(new_password):
        return jsonify({
            "error": (
                "Password must be at least 8 characters long and include an uppercase letter, "
                "lowercase letter, number, and special character."
            )
        }), 400

    # 🔥 Password reuse check
    previous_passwords = PasswordHistory.query.filter_by(user_id=user.id).all()
    for record in previous_passwords:
        if check_password_hash(record.password_hash, new_password):
            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=user.tenant_id,
                action="❌ Attempted to reuse an old password during reset",
                ip_address=ip,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))
            db.session.commit()
            return jsonify({"error": "You have already used this password before. Please choose a new one."}), 400

    # 🔥 Update password
    user.password = new_password
    db.session.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    # 🔥 Keep last 5 password history
    history_records = PasswordHistory.query.filter_by(user_id=user.id).order_by(
        PasswordHistory.created_at.desc()).all()
    if len(history_records) > 5:
        for old_record in history_records[5:]:
            db.session.delete(old_record)

    # 🔥 Clear reset token
    user.reset_token = None
    user.reset_token_expiry = None

    # 🔥 Log success
    db.session.add(RealTimeLog(
        user_id=user.id,
        tenant_id=user.tenant_id,
        action="✅ Password reset successfully",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False
    ))

    db.session.commit()

    return jsonify({
        "message": "Your password has been successfully reset. You may now log in with your new credentials."
    }), 200

# Enroll the tenants user totp
@iam_api_bp.route('/enroll-totp', methods=['GET'])
@jwt_required(locations=["headers"])
@require_api_key
def enroll_totp():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    # 🔥 Find the TenantUser association first
    tenant_user = TenantUser.query.filter_by(
        user_id=user_id,
        tenant_id=tenant_id
    ).first()

    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # 🔥 Determine if TOTP setup or reset is needed
    reset_required = (
        user.otp_secret is None or
        (user.otp_secret and user.otp_email_label != tenant_user.company_email)
    )

    if reset_required:
        secret = pyotp.random_base32()

        # 🚨 DON'T commit yet! Save temporarily in session!
        session['pending_totp_secret'] = secret
        session['pending_totp_email'] = tenant_user.company_email

        # 🔥 Generate QR Code for the TOTP
        totp_uri = pyotp.TOTP(secret).provisioning_uri(
            name=tenant_user.company_email,
            issuer_name="ZTN_IAMaaS"
        )

        qr = qrcode.make(totp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()

        return jsonify({
            "qr_code": f"data:image/png;base64,{img_base64}",
            "manual_key": secret,
            "reset_required": True
        }), 200

    # 🔥 Already configured and company email matches
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
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    secret = session.get('pending_totp_secret')
    email = session.get('pending_totp_email')

    if not secret or not email:
        return jsonify({"error": "No pending TOTP enrollment"}), 400

    # 🔥 Confirm: Save secret to user only after clicking "Continue"
    user.otp_secret = secret
    user.otp_email_label = email
    db.session.commit()

    session.pop('pending_totp_secret', None)
    session.pop('pending_totp_email', None)

    return jsonify({"message": "✅ TOTP enrollment confirmed."}), 200



# verify the tenants users totp
@iam_api_bp.route('/verify-totp-login', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def verify_totp_login():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    # 🔥 Find the TenantUser association
    tenant_user = TenantUser.query.filter_by(
        user_id=user_id,
        tenant_id=tenant_id
    ).first()

    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user or not user.otp_secret:
        return jsonify({"error": "Invalid user or TOTP not configured."}), 403

    data = request.get_json()
    totp_code = data.get('totp')

    if not totp_code:
        return jsonify({"error": "TOTP code is required."}), 400

    ip_address = request.remote_addr
    device_info = "IAMaaS API Access"
    location = get_ip_location(ip_address)

    # 🔥 Lockout check
    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"TOTP locked. Try again after {user.locked_until}."}), 429

    # 🔥 Count recent OTP failures (last 5 minutes)
    threshold_time = datetime.utcnow() - timedelta(minutes=5)
    recent_otp_fails = UserAuthLog.query.filter_by(
        user_id=user.id,
        auth_method="totp",
        auth_status="failed"
    ).filter(UserAuthLog.auth_timestamp >= threshold_time).count()

    if not verify_totp_code(user.otp_secret, totp_code):
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

    # ✅ Successful TOTP verification
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

    # 🔥 Check WebAuthn status
    has_webauthn_credentials = bool(user.webauthn_credentials)

    return jsonify({
        "message": "TOTP verified successfully.",
        "require_webauthn": True,
        "has_webauthn_credentials": has_webauthn_credentials,
        "user_id": user.id
    }), 200


# Tenant user totp reset from the settings:
@iam_api_bp.route('/request-reset-totp', methods=['POST'])
@jwt_required()
@require_api_key
def request_reset_totp():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found."}), 404

    # 🔥 Make sure that user belongs to the tenant calling the API
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

    # 🔥 Clear TOTP info safely
    user.otp_secret = None
    user.otp_email_label = None

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


# Enroll the tenants user webauthn
@iam_api_bp.route('/webauthn/register-begin', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def begin_webauthn_registration():
    user_id = get_jwt_identity()
    tenant_id = g.tenant.id

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found."}), 404

    # 🛡️ Confirm that user belongs to this tenant
    tenant_user = TenantUser.query.filter_by(
        user_id=user.id,
        tenant_id=tenant_id
    ).first()

    if not tenant_user:
        return jsonify({"error": "Unauthorized"}), 403

    # 🔥 Fetch existing credentials to exclude duplicates
    credentials = [
        {
            "id": c.credential_id,
            "transports": c.transports.split(',') if c.transports else [],
            "type": "public-key"
        }
        for c in user.webauthn_credentials
    ]

    try:
        # 🔥 Start WebAuthn registration
        registration_data, state = server.register_begin(
            {
                "id": str(user.id).encode(),
                "name": tenant_user.company_email,  # 🛡️ Use company email as identity inside tenant
                "displayName": f"{user.first_name} {user.last_name or ''}".strip()
            },
            credentials
        )

        session['webauthn_register_state'] = state
        session['webauthn_register_user_id'] = user.id  # 🔥 Save user_id separately

        public_key = jsonify_webauthn(registration_data["publicKey"])

        return jsonify({
            "public_key": public_key
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

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found."}), 404

        # 🛡️ Ensure the user belongs to the tenant making the API call
        tenant_user = TenantUser.query.filter_by(
            user_id=user.id,
            tenant_id=tenant_id
        ).first()

        if not tenant_user:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        state = session.get('webauthn_register_state')

        if not state:
            return jsonify({"error": "No WebAuthn registration session found."}), 400

        if data["id"] != data["rawId"]:
            return jsonify({"error": "id does not match rawId"}), 400

        response = {
            "id": data["id"],
            "rawId": data["rawId"],
            "type": data["type"],
            "response": {
                "attestationObject": data["response"]["attestationObject"],
                "clientDataJSON": data["response"]["clientDataJSON"]
            }
        }

        # 🔥 Complete WebAuthn registration
        auth_data = server.register_complete(state, response)
        cred_data = auth_data.credential_data

        public_key_bytes = cbor.encode(cred_data.public_key)

        # 🔥 Save WebAuthn credential
        credential = WebAuthnCredential(
            user_id=user.id,
            credential_id=cred_data.credential_id,
            public_key=public_key_bytes,
            sign_count=0,
            transports=",".join(data.get("transports", []))
        )

        db.session.add(credential)
        session.pop('webauthn_register_state', None)

        # 🔥 Log success
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=tenant_id,
            action="✅ WebAuthn credential registered successfully",
            ip_address=request.remote_addr,
            device_info="IAMaaS API Access",
            location=get_ip_location(request.remote_addr),
            risk_alert=False
        ))

        db.session.commit()

        return jsonify({
            "message": "✅ WebAuthn credential registered successfully."
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


# Tenat User Assertion begin
@iam_api_bp.route('/webauthn/assertion-begin', methods=['POST'])
@jwt_required(locations=["headers"])
@require_api_key
def begin_webauthn_assertion():
    try:
        from fido2.webauthn import PublicKeyCredentialRequestOptions

        user_id = get_jwt_identity()
        tenant_id = g.tenant.id

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found."}), 404

        # 🛡️ Make sure user belongs to the tenant calling the API
        tenant_user = TenantUser.query.filter_by(
            user_id=user.id,
            tenant_id=tenant_id
        ).first()

        if not tenant_user:
            return jsonify({"error": "Unauthorized"}), 403

        if not user.webauthn_credentials:
            return jsonify({"error": "No registered WebAuthn credentials for this user."}), 404

        credentials = [
            {
                "id": c.credential_id,
                "transports": c.transports.split(',') if c.transports else [],
                "type": "public-key"
            }
            for c in user.webauthn_credentials
        ]

        # 🔥 Begin authentication challenge
        assertion_data, state = server.authenticate_begin(credentials)

        # 🔐 Save state for assertion complete
        session["webauthn_assertion_state"] = state
        session["assertion_user_id"] = user.id
        session["mfa_webauthn_verified"] = False

        # ✅ Prepare clean publicKey dict
        options: PublicKeyCredentialRequestOptions = assertion_data.public_key

        public_key_dict = {
            "challenge": websafe_encode(options.challenge),
            "rpId": options.rp_id,
            "allowCredentials": [
                {
                    "type": c.type.value,
                    "id": websafe_encode(c.id),
                    "transports": [t.value for t in c.transports] if c.transports else []
                }
                for c in options.allow_credentials or []
            ],
            "userVerification": options.user_verification,
            "timeout": options.timeout
        }

        return jsonify({"public_key": public_key_dict}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Assertion begin failed: {str(e)}"}), 500

# Tenant User Webauthn Assertion complete
@iam_api_bp.route('/webauthn/assertion-complete', methods=['POST'])
@jwt_required()
@require_api_key
def complete_webauthn_assertion():
    from fido2.utils import websafe_decode

    try:
        data = request.get_json()
        state = session.get("webauthn_assertion_state")
        user_id = session.get("assertion_user_id")

        if not state or not user_id:
            return jsonify({"error": "No assertion in progress."}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        # 🛡️ Make sure user belongs to the tenant
        tenant_user = TenantUser.query.filter_by(
            user_id=user.id,
            tenant_id=g.tenant.id
        ).first()

        if not tenant_user:
            return jsonify({"error": "Unauthorized."}), 403

        credential_id = websafe_decode(data["credentialId"])
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id
        ).first()

        ip_address = request.remote_addr
        device_info = "IAMaaS API Access"
        location = get_ip_location(ip_address)

        # 🔥 Lockout check
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
                tenant_id=user.tenant_id
            ))

            db.session.add(RealTimeLog(
                user_id=user.id,
                tenant_id=g.tenant.id,
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

        # ✅ Build final assertion data
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

        public_key_source = {
            "id": credential.credential_id,
            "public_key": credential.public_key,
            "sign_count": credential.sign_count,
            "transports": credential.transports.split(",") if credential.transports else [],
            "user_handle": None
        }

        # 🔥 Authenticate WebAuthn assertion
        server.authenticate_complete(state, assertion, [public_key_source])

        credential.sign_count += 1
        db.session.commit()

        session["mfa_webauthn_verified"] = True
        session.pop("webauthn_assertion_state", None)
        session.pop("assertion_user_id", None)

        access = UserAccessControl.query.filter_by(user_id=user.id).first()
        role = db.session.get(UserRole, access.role_id).role_name.lower() if access else "user"

        if user.tenant_id == 1:
            urls = {
                "admin": url_for("admin.admin_dashboard", _external=True),
                "agent": url_for("agent.agent_dashboard", _external=True),
                "user": url_for("user.user_dashboard", _external=True)
            }
            dashboard_url = urls.get(role, url_for("user.user_dashboard", _external=True))
        else:
            dashboard_url = f"https://{g.tenant.name.lower()}.yourdomain.com/dashboard"

        # 🧬 Determine transport method
        transports = credential.transports.split(",") if credential.transports else []
        if "hybrid" in transports:
            method = "cross-device passkey"
        elif "usb" in transports:
            method = "USB security key"
        elif "internal" in transports:
            method = "platform authenticator (fingerprint)"
        else:
            method = "unknown method"

        # 🔥 Log successful WebAuthn login
        db.session.add(RealTimeLog(
            user_id=user.id,
            tenant_id=g.tenant.id,
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
            tenant_id=user.tenant_id
        ))

        db.session.commit()

        return jsonify({
            "message": "✅ Biometric/passkey login successful",
            "user_id": user.id,
            "dashboard_url": urls.get(role, url_for("user.user_dashboard", _external=True))
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"❌ Assertion failed: {str(e)}"}), 500



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

        if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
            return jsonify({"error": "Reset token invalid or expired."}), 403

        # 🛡️ Ensure the user belongs to this tenant
        if user.tenant_id != g.tenant.id:
            return jsonify({"error": "Unauthorized: Wrong tenant."}), 403

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

        # 🔥 Begin WebAuthn assertion
        assertion_data, state = server.authenticate_begin(credentials)

        session["reset_webauthn_assertion_state"] = state
        session["reset_user_id"] = user.id
        session["reset_context"] = "iam_reset"

        return jsonify({
            "public_key": jsonify_webauthn(assertion_data["publicKey"])
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Reset WebAuthn begin failed: {str(e)}"}), 500

# Tenant User Webauth reset-assertion complete
@iam_api_bp.route('/webauthn/reset-assertion-complete', methods=['POST'])
@require_api_key
def complete_reset_webauthn_assertion():
    try:
        user_id = session.get("reset_user_id")
        state = session.get("reset_webauthn_assertion_state")

        if not state or not user_id:
            return jsonify({"error": "No reset verification in progress."}), 400

        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        # 🛡️ Ensure the user belongs to this tenant
        if user.tenant_id != g.tenant.id:
            return jsonify({"error": "Unauthorized: Wrong tenant."}), 403

        credential_id = websafe_decode(data["credentialId"])
        credential = WebAuthnCredential.query.filter_by(
            user_id=user.id,
            credential_id=credential_id
        ).first()

        if not credential:
            return jsonify({"error": "Invalid credential."}), 401

        # ✅ Build WebAuthn response object (as dict)
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

        # ✅ Credential from DB
        public_key_source = {
            "id": credential.credential_id,
            "public_key": credential.public_key,
            "sign_count": credential.sign_count,
            "transports": credential.transports.split(",") if credential.transports else [],
            "user_handle": None,
        }

        # ✅ Final auth check
        server.authenticate_complete(
            state,
            assertion,
            [public_key_source]
        )

        # ✅ Update credential sign count
        credential.sign_count += 1
        db.session.commit()

        # ✅ After success
        session.pop("reset_token", None)
        session.pop("reset_webauthn_assertion_state", None)
        session["reset_webauthn_verified"] = True

        return jsonify({"message": "✅ Verified via WebAuthn for reset"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"❌ Reset WebAuthn failed: {str(e)}"}), 500










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
