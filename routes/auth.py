from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response, session, current_app, flash
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,  # use this with refresh=True for refresh endpoints
    get_jwt_identity,
    unset_jwt_cookies,
    verify_jwt_in_request,
)
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRequestOptions

from utils.security import (
    generate_token,
    hash_token,
    verify_token,
    verify_totp,
    verify_secondary_method
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from models.models import User, Wallet, db, UserRole, UserAccessControl,SIMCard, OTPCode, RealTimeLog, UserAuthLog, PasswordHistory, WebAuthnCredential, PendingSIMSwap
from utils.logging_helpers import log_realtime_event, log_auth_event
from utils.otp import generate_otp_code  # Import your OTP logic
from utils.totp import verify_totp_code
from utils.location import get_ip_location
from utils.security import generate_challenge, is_strong_password
from base64 import urlsafe_b64decode, urlsafe_b64encode
import pyotp
import qrcode
import io
import os
import json
import base64
import hashlib
from flask import current_app
from utils.auth_decorators import require_full_mfa
from flask_mail import Message
from extensions import mail
from utils.email_alerts import send_admin_alert, send_user_alert, send_password_reset_email ,send_totp_reset_email, send_webauthn_reset_email
import pyotp
from utils.security import get_request_fingerprint
from utils.logger import app_logger
import secrets

auth_bp = Blueprint('auth', __name__)

#Register form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

#Login
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

from utils.logging_helpers import log_realtime_event, log_auth_event

@auth_bp.route('/login', methods=['POST'])
def login_route():
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
    device_info = request.user_agent.string
    location = get_ip_location(ip_address)

    user = User.query.filter_by(email=login_input).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=login_input, status='active').first()
        if sim:
            user = sim.user

    if not user:
        app_logger.warning(f"[USER-ENUM] login_input={login_input} ip={ip_address}")

        # 🛡️ Use helper here for unknown user
        log_realtime_event(
            user=None,
            action=f"❌ Failed login: Unknown identifier {login_input}",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True,
            # tenant_id=1
        )
        db.session.commit()
        return jsonify({"error": "User not found or SIM inactive"}), 404

    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"Account locked. Try again after {user.locked_until}"}), 429

    recent_fails = count_recent_failures(user.id)

    if not user.check_password(password):
        failed_count = recent_fails + 1
        app_logger.warning(f"[LOGIN-FAILED] user_id={user.id} failed_attempts={failed_count} ip={ip_address}")
        app_logger.warning("[LOGIN-FAILED] user_id=123 ip=192.168.2.100")

        log_auth_event(
            user=user,
            method="password",
            status="failed",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            failed_attempts=failed_count
        )

        log_realtime_event(
            user=user,
            action=f"❌ Failed login: Invalid password ({failed_count})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=(failed_count >= 3)
        )

        if failed_count >= 5:
            app_logger.warning(f"[ACCOUNT-LOCKED] user_id={user.id} ip={ip_address}")
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)

            log_realtime_event(
                user=user,
                action="🚨 Account temporarily locked due to failed login attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True
            )

            # ✅ Email alerts
            if user.email:
                send_user_alert(
                    user=user,
                    event_type="login_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info
                )

            send_admin_alert(
                user=user,
                event_type="login_lockout",
                ip_address=ip_address,
                location=location,
                device_info=device_info
            )

        db.session.commit()
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Success
    fp = get_request_fingerprint()
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"fp": fp}
    )
    # ✅ Success
    app_logger.info(f"[LOGIN] user_id={user.id} ip={ip_address}")

    response = jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "require_totp": bool(user.otp_secret),
        "require_totp_setup": user.otp_secret is None,
        "require_totp_reset": user.otp_secret and user.otp_email_label != user.email    
    })

    log_auth_event(
        user=user,
        method="password",
        status="success",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        failed_attempts=0
    )

    log_realtime_event(
        user=user,
        action="✅ Successful login",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False
    )

    db.session.commit()
    set_access_cookies(response, access_token)
    return response, 200


# ✅ Registering new user accounts
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # 🔹 Ensure request is parsed as JSON
        data = request.get_json(force=True)  
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

    # ✅ Validate required fields
    required_fields = ['iccid', 'first_name', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field.replace('_', ' ').capitalize()} is required"}), 400
    
    # ✅ Enforce strong password
    if not is_strong_password(data['password']):
        return jsonify({
            "error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
        }), 400

    # 🔹 Fetch the SIM card by ICCID
    sim_card = SIMCard.query.filter_by(iccid=data['iccid']).first()
    if not sim_card:
        return jsonify({"error": "Invalid ICCID. Please register a SIM first."}), 404

    # ✅ If SIM is found but unregistered, activate it
    if sim_card.status == "unregistered":
        sim_card.status = "active"
        db.session.commit()

    # 🔹 Check if a user is already linked to this SIM card or email exists
    existing_user = User.query.filter(
        (User.email == data['email']) | (User.id == sim_card.user_id)
    ).first()

    if existing_user:
        return jsonify({"error": "User with this email or SIM card already exists"}), 400

    # 🔹 Create a new user
    new_user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data.get('last_name'),
        country=data.get('country'),
        identity_verified=False,
        is_active=True,
        tenant_id=1
    )

    # ✅ Use the setter to ensure hashing works correctly
    new_user.password = data['password']

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"User creation failed: {e}"}), 500

    # 🔹 Assign the SIM card to the user
    sim_card.user_id = new_user.id
    db.session.add(sim_card)

    # 🔹 Assign Default "User" Role
    user_role = UserRole.query.filter_by(role_name="user").first()
    if not user_role:
        return jsonify({"error": "Default user role not found"}), 500

    new_access = UserAccessControl(user_id=new_user.id, role_id=user_role.id)
    db.session.add(new_access)

    # 🔹 Create Wallet for the User
    new_wallet = Wallet(user_id=new_user.id, balance=0.0, currency="RWF")
    db.session.add(new_wallet)

    # 🔹 Log registration event
    rt_log = RealTimeLog(
        user_id=new_user.id,
        action=f"🆕 New user registered using ICCID {data['iccid']} (SIM created by: {sim_card.registered_by})",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=data.get("location", "Unknown"),
        risk_alert=False,
        tenant_id=1  # 🛡️ Added
    )
    db.session.add(rt_log)

    db.session.commit()

    # 🔹 Generate JWT token for the newly registered user
    access_token = create_access_token(identity=new_user.id)

    # 🔹 Construct Response with Success Message & User Data
    response_data = {
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
        "wallet": {
            "balance": new_wallet.balance,
            "currency": "RWF"
        }
    }

    # 🔹 Set the JWT token in a secure, HttpOnly cookie
    response = make_response(response_data)
    response.set_cookie('auth_token', access_token, httponly=True, secure=True, samesite='Strict')

    return response, 201


# ✅ Getting the OTP
@auth_bp.route('/verify-totp', methods=['GET'])
def verify_totp_page():
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
        print("✅ Accessed /verify-totp page")
        print("🎯 Extracted user_id from JWT:", user_id)
    except Exception as e:
        print("❌ Token error on /verify-totp page:", e)
        return redirect(url_for('auth.login_form'))

    return render_template('verify_totp.html')


# ✅ Set up Token_OTP
@auth_bp.route('/setup-totp', methods=['GET'])
def setup_totp():
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
        print("✅ API: JWT verified for setup-totp:", user_id)
    except Exception as e:
        print("❌ API: JWT error in /setup-totp:", e)
        print("Cookies seen:", dict(request.cookies))
        return jsonify({"error": "Invalid or missing token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    reset_required = (
        user.otp_secret is None or
        (user.otp_secret and user.otp_email_label != user.email)
    )

    if reset_required:
        # 🔥 Generate new secret and store it temporarily in session
        secret = pyotp.random_base32()
        session['pending_totp_secret'] = secret
        session['pending_totp_email'] = user.email

        totp_uri = pyotp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="ZTN_MoMo_SIM"
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

    # 🔥 Already configured and no email mismatch
    return jsonify({
        "message": "TOTP already configured."
    }), 200

# confirm the totp registration
@auth_bp.route('/setup-totp/confirm', methods=['POST'])
def confirm_totp_setup():
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
    except Exception as e:
        return jsonify({"error": "Invalid or missing token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    secret = session.get('pending_totp_secret')
    email = session.get('pending_totp_email')

    if not secret or not email:
        return jsonify({"error": "No pending TOTP enrollment"}), 400

    # 🔥 Confirm: Save secret to user only after clicking "Continue"
    user.otp_secret = secret
    user.otp_email_label = email
    db.session.commit()

    # 🔥 Clean up session
    session.pop('pending_totp_secret', None)
    session.pop('pending_totp_email', None)

    return jsonify({"message": "✅ TOTP enrollment confirmed."}), 200


# ✅ Verifying the TOTP
@auth_bp.route('/verify-totp-login', methods=['POST'])
def verify_totp_login():   
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
    except NoAuthorizationError:
        return jsonify({"error": "Invalid or missing token"}), 401

    data = request.get_json()
    totp_code = data.get('totp')
    if not totp_code:
        return jsonify({"error": "TOTP code is required"}), 400

    user = User.query.get(user_id)
    if not user or not user.otp_secret:
        return jsonify({"error": "Invalid user or TOTP not configured"}), 403

    ip_address = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip_address)

    # Lockout check
    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"TOTP locked. Try again after {user.locked_until}"}), 429

    # Count recent failures
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
            tenant_id=1 # 🔥 tenant_id added
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
            action=f"❌ Failed TOTP verification ({fail_count})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True,
            tenant_id=1  # 🔥 tenant_id added
        ))

        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)

            db.session.add(RealTimeLog(
                user_id=user.id,
                action="🚨 TOTP temporarily locked after multiple failed attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1 # 🔥 tenant_id added
            ))

            # 🚨 Email alerts to admin and user
            if user.email:
                send_user_alert(
                    user=user,
                    event_type="totp_lockout",
                    ip_address=ip_address,
                    location=location,
                    device_info=device_info
                )

            send_admin_alert(
                user=user,
                event_type="totp_lockout",
                ip_address=ip_address,
                location=location,
                device_info=device_info
            )

        db.session.commit()
        return jsonify({"error": "Invalid or expired TOTP code"}), 401

    # ✅ Successful TOTP verification
    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="totp",
        auth_status="success",
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        failed_attempts=0,
        tenant_id=1 # 🔥 tenant_id added
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ TOTP verified successfully",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False,
        tenant_id=1# 🔥 tenant_id added
    ))

    db.session.commit()

    access = UserAccessControl.query.filter_by(user_id=user.id).first()
    role = db.session.get(UserRole, access.role_id).role_name.lower() if access else "user"

    urls = {
        "admin": url_for("admin.admin_dashboard", _external=True),
        "agent": url_for("agent.agent_dashboard", _external=True),
        "user": url_for("user.user_dashboard", _external=True)
    }

    session["mfa_totp_verified"] = True

    return jsonify({
        "message": "TOTP verified successfully",
        "require_webauthn": True,
        "has_webauthn_credentials": bool(user.webauthn_credentials),
        "user_id": user.id,
        "dashboard_url": urls.get(role, url_for("user.user_dashboard", _external=True))
    }), 200

# Whoami 
@auth_bp.route('/whoami', methods=['GET'])
@jwt_required()
def whoami():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    role = UserRole.query.get(user_access.role_id).role_name if user_access else "unknown"

    return jsonify({
        "role": role.lower()  # e.g., "admin", "agent", "user"
    })

# Verfy your TOTP for transactions
@auth_bp.route('/verify-totp', methods=['POST'])
@jwt_required()
def verify_transaction_totp():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    if not data.get("code"):
        return jsonify({"error": "TOTP code is required"}), 400

    if verify_totp_code(user.otp_secret, data['code']):
        return jsonify({"message": "✅ TOTP is valid"}), 200
    else:
        return jsonify({"error": "Invalid TOTP"}), 401

# Verifying the totp with a fallback sent access token
# =====================================================
@auth_bp.route('/verify-fallback_totp', methods=['POST'])
def verify_fallback_totp():
    data = request.get_json()
    token = data.get("token")
    code = data.get("code")

    if not token or not code:
        return jsonify({"error": "Reset token and TOTP code are required"}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

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

# Refres the access token
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    resp = jsonify({"access_token": new_access_token})
    set_access_cookies(resp, new_access_token)
    return resp, 200

#Logout
@auth_bp.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('auth.login_form')))
    unset_jwt_cookies(resp)
    return resp

# Debugging cookies
@auth_bp.route('/debug-cookie')
def debug_cookie():
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
        return f"✅ JWT verified! User ID: {user_id}"
    except Exception as e:
        print("❌ JWT Debug error:", e)
        return "❌ Invalid token", 401


@auth_bp.route("/enroll-biometric", methods=["GET"])
@jwt_required()
def enroll_biometric_page():
    return render_template("enroll_biometric.html")

@auth_bp.route("/verify-biometric")
@jwt_required()
def verify_biometric_page():
    return render_template("verify_biometric.html")


@auth_bp.route("/log-webauthn-failure", methods=["POST"])
@jwt_required(optional=True)
def log_webauthn_client_failure():
    from flask_jwt_extended import get_jwt_identity

    data = request.get_json()
    error = data.get("error", "Unknown client error")
    ip = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip)

    user_id = get_jwt_identity() or session.get("assertion_user_id")

    db.session.add(RealTimeLog(
        user_id=user_id,
        action=f"⚠️ Client-side WebAuthn failure: {error}",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False,
        tenant_id=1# 🛡️ Added
    ))
    db.session.commit()

    return jsonify({"status": "logged"}), 200


# -----------------
# FallBacks control
# -----------------

# Forgot Password
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    identifier = data.get("identifier")

    if not identifier:
        return jsonify({"error": "Identifier (mobile or email) required"}), 400

    user = User.query.filter_by(email=identifier).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        user = sim.user if sim else None

    if not user:
        return jsonify({"error": "User not found"}), 404

    token = generate_token()  # ✅ Use its hash + expiration in DB
    expiry = datetime.utcnow() + timedelta(minutes=15)

    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    ip_address = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip_address)

    send_password_reset_email(user, token)

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="📧 Password reset requested",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False,
        tenant_id=1  # 🛡️ Added
    ))
    db.session.commit()
    return jsonify({"message": "Please check your email for a password reset link"}), 200

@auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_form():
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET'])
def reset_password_form():
    token = request.args.get("token")
    if not token:
        return redirect(url_for('auth.forgot_password_form'))  
    return render_template("reset_password.html", token=token)

# Reset Password
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not token or not new_password or not confirm_password:
        return jsonify({"error": "Token, new password, and confirmation are required"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token"}), 400

    ip = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip)

    # 🚫 Low trust score check
    if user.trust_score < 0.4:
        db.session.add(RealTimeLog(
            user_id=user.id,
            action="🚫 Password reset denied due to low trust score",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        send_admin_alert(
            user=user,
            event_type="Blocked Password Reset (Low Trust Score)",
            ip_address=ip,
            device_info=device_info,
            location=location
        )
        db.session.commit()
        return jsonify({
            "error": (
                "This reset request was blocked due to suspicious activity. "
                "An administrator has been notified for review."
            )
        }), 403

    # 🧠 Reuse check
    previous_passwords = PasswordHistory.query.filter_by(user_id=user.id).all()
    for record in previous_passwords:
        if check_password_hash(record.password_hash, new_password):
            db.session.add(RealTimeLog(
                user_id=user.id,
                action="❌ Attempted to reuse an old password during reset",
                ip_address=ip,
                device_info=device_info,
                location=location,
                risk_alert=True,
                tenant_id=1
            ))
            db.session.commit()
            return jsonify({"error": "You’ve already used this password. Please choose a new one."}), 400

    # 🔐 Strength check
    if not is_strong_password(new_password):
        return jsonify({
            "error": (
                "Password must be at least 8 characters long and include an uppercase letter, "
                "lowercase letter, number, and special character."
            )
        }), 400

    # 🔐 MFA Checks
    has_webauthn = WebAuthnCredential.query.filter_by(user_id=user.id).count() > 0
    has_totp = user.otp_secret is not None

    if session.get("reset_token_checked") != token:
        session["reset_webauthn_verified"] = False
        session["reset_totp_verified"] = False
        session["reset_token_checked"] = token

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
            action="❌ Password reset blocked — no MFA configured",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True,
            tenant_id=1 # 🛡️ Added
        ))
        send_admin_alert(
            user=user,
            event_type="Blocked Password Reset (No MFA)",
            ip_address=ip,
            device_info=device_info,
            location=location
        )
        db.session.commit()
        return jsonify({
            "error": (
                "You need to have at least one multi-factor method (TOTP or WebAuthn) "
                "set up to reset your password."
            )
        }), 403

    # ✅ Update password and history
    user.password = new_password
    db.session.add(PasswordHistory(user_id=user.id, password_hash=user.password_hash))

    # Keep only last 5
    history_records = PasswordHistory.query.filter_by(user_id=user.id).order_by(
        PasswordHistory.created_at.desc()).all()
    if len(history_records) > 5:
        for old in history_records[5:]:
            db.session.delete(old)

    user.reset_token = None
    user.reset_token_expiry = None

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ Password reset after MFA and checks",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False,
        tenant_id=1 # 🛡️ Added
    ))

    session.pop("reset_webauthn_verified", None)
    session.pop("reset_totp_verified", None)
    session.pop("reset_token_checked", None)

    db.session.commit()
    return jsonify({
        "message": "Your password has been successfully reset. You may now log in with your new credentials."
    }), 200



# Change password from the settings
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # ✅ Step 1: Verify current password
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect."}), 401
    # ✅ Step 2: Check password strength
    if not is_strong_password(new_password):
        return jsonify({"error": "Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character."}), 400

    # ✅ Step 3: Check if new password was previously used
    previous_passwords = PasswordHistory.query.filter_by(user_id=user.id).all()
    for record in previous_passwords:
        if check_password_hash(record.password_hash, new_password):
            db.session.add(RealTimeLog(
                user_id=user.id,
                action="❌ Attempted to reuse an old password",
                ip_address=request.remote_addr,
                device_info=request.user_agent.string,
                location=get_ip_location(request.remote_addr),
                risk_alert=True,
                tenant_id=1
            ))
            db.session.commit()
            return jsonify({"error": "You’ve already used this password. Please choose a new one."}), 400

    # ✅ Step 4: Update user password
    user.password = new_password  # triggers password hashing via @password.setter

    # ✅ Step 4: Save current password to password history
    db.session.add(PasswordHistory(
        user_id=user.id,
        password_hash=user.password_hash
    ))

    # ✅ Step 6: Keep only the last 5 password records
    history_records = PasswordHistory.query.filter_by(user_id=user.id).order_by(
        PasswordHistory.created_at.desc()).all()

    if len(history_records) > 5:
        for old_record in history_records[5:]:
            db.session.delete(old_record)

    # ✅ Step 7: Log the event
    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="password",
        auth_status="change",
        ip_address=request.remote_addr,
        location=get_ip_location(request.remote_addr),
        device_info=request.user_agent.string,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="🔐 Changed account password",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=False,
        tenant_id=1# 🛡️ Added
    ))

    db.session.commit()
    return jsonify({"message": "Password updated successfully."}), 200


# Reset TOTP from user settings
@auth_bp.route('/request-reset-totp', methods=['POST'])
@jwt_required()
def request_reset_totp():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    password = data.get('password')

    # ✅ Verify password before resetting TOTP
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password."}), 401

    # ✅ Clear TOTP info
    user.otp_secret = None
    user.otp_email_label = None

    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="totp",
        auth_status="reset",
        ip_address=request.remote_addr,
        location=get_ip_location(request.remote_addr),
        device_info=request.user_agent.string,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="🔁 TOTP reset requested by user",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True,
        tenant_id=1# 🛡️ Added
    ))

    db.session.commit()

    return jsonify({
        "message": "TOTP reset successfully. You’ll be asked to set it up again on next login.",
        "redirect": "/settings"  # or any page you want to take them back to
    }), 200


# Reset the totp from the outside when you have lost access to authenticator app
@auth_bp.route('/request-totp-reset', methods=['POST'])
def request_totp_reset():
    data = request.get_json()
    identifier = data.get("identifier")

    if not identifier:
        return jsonify({"error": "Identifier (email or mobile number) is required."}), 400

    user = User.query.filter_by(email=identifier).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        user = sim.user if sim else None

    if not user:
        return jsonify({"error": "No matching account found."}), 404

    # ✅ Generate secure token
    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="📨 TOTP reset link requested",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.commit()

    # ✅ Send email with the reset link
    send_totp_reset_email(user, token)

    return jsonify({"message": "TOTP reset link has been sent to your email."}), 200

# Get the totp_reset page
@auth_bp.route('/request-totp-reset', methods=['GET'])
def request_totp_reset_form():
    return render_template("request_totp_reset.html")

# Verify totp rest request from user settings
@auth_bp.route('/verify-totp-reset', methods=['POST'])
def verify_totp_reset_post():
    data = request.get_json()
    token = data.get("token")
    password = data.get("password")

    user = User.query.filter_by(reset_token=hash_token(token)).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    if not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Token expired"}), 410

    # ✅ Check password
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401

    ip = request.remote_addr
    device_info = request.user_agent.string
    location = get_ip_location(ip)

    # ✅ Trust Score Check
    if user.trust_score < 0.5:
        db.session.add(RealTimeLog(
            user_id=user.id,
            action="⚠️ TOTP reset denied due to low trust score",
            ip_address=ip,
            device_info=device_info,
            location=location,
            risk_alert=True,
            tenant_id=1
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

    # ✅ WebAuthn Check: only proceed if verified
    has_webauthn = WebAuthnCredential.query.filter_by(user_id=user.id).count() > 0
    webauthn_verified = session.get("reset_webauthn_verified")

    if has_webauthn and not webauthn_verified:
        return jsonify({
            "require_webauthn": True,
            "message": "WebAuthn verification required before TOTP reset."
        }), 202

    # ✅ Passed → reset TOTP
    user.otp_secret = None
    user.otp_email_label = None
    user.reset_token = None
    user.reset_token_expiry = None

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ TOTP reset after identity + trust check",
        ip_address=ip,
        device_info=device_info,
        location=location,
        risk_alert=False,
        tenant_id=1 # 🛡️ Added
    ))

    # ✅ Clean up session
    session.pop("reset_webauthn_verified", None)

    db.session.commit()
    return jsonify({"message": "TOTP has been reset. You’ll be prompted to set it up on next login."}), 200




# 
@auth_bp.route('/verify-totp-reset', methods=['GET'])
def verify_totp_reset():
    token = request.args.get("token")
    if not token:
        return redirect(url_for('auth.request_totp_reset_form'))

    return render_template("totp_reset_verification.html", token=token)



# Reset WebAuthn Credential from the settings
@auth_bp.route('/request-reset-webauthn', methods=['POST'])
@jwt_required()
def request_reset_webauthn():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    password = data.get('password')

    # ✅ Check current password before reset
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password."}), 401

    # ✅ Remove all user's WebAuthn credentials
    WebAuthnCredential.query.filter_by(user_id=user.id).delete()

    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="webauthn",
        auth_status="reset",
        ip_address=request.remote_addr,
        location=get_ip_location(request.remote_addr),
        device_info=request.user_agent.string,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="🔁 WebAuthn reset requested by user",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.commit()

    return jsonify({
        "message": "WebAuthn reset successfully. You’ll be prompted to re-register on next login.",
        "redirect": "/settings"
    }), 200



# Route to handle WebAuthn reset from outside
# This is the route to show the WebAuthn reset request page
@auth_bp.route('/out-request-webauthn-reset', methods=['GET'])
def out_request_webauthn_reset_page():
    return render_template('request_webauthn_reset.html')

# Step 1: Request WebAuthn Reset (Identifier Only)
@auth_bp.route('/out-request-webauthn-reset', methods=['POST'])
def request_webauthn_reset():
    data = request.get_json()
    identifier = data.get("identifier")

    if not identifier:
        return jsonify({"error": "Identifier (email or mobile number) is required."}), 400

    user = User.query.filter_by(email=identifier).first()
    if not user:
        sim = SIMCard.query.filter_by(mobile_number=identifier, status='active').first()
        user = sim.user if sim else None

    if not user:
        return jsonify({"error": "No matching account found."}), 404

    token = generate_token()
    expiry = datetime.utcnow() + timedelta(minutes=15)

    user.reset_token = hash_token(token)
    user.reset_token_expiry = expiry
    db.session.commit()

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="📨 WebAuthn reset link requested",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True,
        tenant_id=1 # 🛡️ Added
    ))
    db.session.commit()

    send_webauthn_reset_email(user, token)
    return jsonify({"message": "WebAuthn reset link has been sent to your email."}), 200

# Getting the verifications page:
@auth_bp.route('/out-verify-webauthn-reset/<token>', methods=['GET'])
def out_verify_webauthn_reset_page(token):
    return render_template("verify_webauthn_reset.html", token=token)

# Step 2: Verify Token and Reset WebAuthn (Password + TOTP Required)
@auth_bp.route('/out-verify-webauthn-reset/<token>', methods=['POST'])
def verify_webauthn_reset(token):
    data = request.get_json()
    password = data.get("password")
    totp = data.get("totp")

    if not password or not totp:
        return jsonify({"error": "Password and TOTP code are required."}), 400

    user = User.query.filter_by(reset_token=hash_token(token)).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Invalid or expired token."}), 403

    if not user.check_password(password):
        return jsonify({"error": "Invalid password."}), 403

    if not user.otp_secret:
        return jsonify({"error": "No TOTP configured for this account."}), 403

    totp_validator = pyotp.TOTP(user.otp_secret)
    if not totp_validator.verify(totp, valid_window=1):
        return jsonify({"error": "Invalid TOTP code."}), 403

    # Delete the User webauthn credentials
    WebAuthnCredential.query.filter_by(user_id=user.id).delete()

    # Clear token and mark WebAuthn as reset
    user.reset_token = None
    user.reset_token_expiry = None
    user.passkey_required = True  # Flag to prompt re-enrollment next login

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ WebAuthn reset verified",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True,
        tenant_id=1 # 🛡️ Added
    ))

    db.session.commit()

    send_user_alert(
    user,
    "WebAuthn Reset Completed",
    request.remote_addr,
    get_ip_location(request.remote_addr),
    request.user_agent.string
    )


    return jsonify({
        "message": "✅ WebAuthn reset successful. Please log in and re-enroll your passkey."
    }), 200


@auth_bp.route("/verify-sim-swap", methods=["GET", "POST"])
def verify_sim_swap():
    token = request.args.get("token") if request.method == "GET" else request.json.get("token")
    if not token:
        return jsonify({"error": "Missing token."}), 400

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    pending = PendingSIMSwap.query.filter_by(token_hash=token_hash).first()

    if not pending or pending.expires_at < datetime.utcnow():
        return jsonify({"error": "This SIM swap link is invalid or has expired."}), 410

    user = User.query.get(pending.user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # GET: Render form
    if request.method == "GET":
        return render_template("verify_sim_swap.html", token=token, user=user)

    # POST: Step 1 - Validate password + TOTP
    password = request.json.get("password")
    totp_code = request.json.get("totp_code")
    webauthn_done = request.json.get("webauthn_done", False)

    if not user.check_password(password):
        db.session.add(RealTimeLog(
            user_id=user.id,
            action="❌ SIM swap verification failed (bad password)",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=get_ip_location(request.remote_addr),
            risk_alert=True,
            tenant_id=1
        ))
        db.session.commit()
        return jsonify({"error": "Incorrect password."}), 401

    if not verify_totp(user, totp_code):
        db.session.add(RealTimeLog(
            user_id=user.id,
            action="❌ SIM swap verification failed (bad TOTP)",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=get_ip_location(request.remote_addr),
            risk_alert=True,
            tenant_id=1
        ))
        db.session.commit()
        return jsonify({"error": "Invalid TOTP code."}), 401

    if not session.get("reset_webauthn_verified"):
        return jsonify({"require_webauthn": True}), 202

    # ✅ Finalize SIM swap
    old_sim = SIMCard.query.filter_by(iccid=pending.old_iccid).first()
    new_sim = SIMCard.query.filter_by(iccid=pending.new_iccid).first()

    if not old_sim or not new_sim:
        return jsonify({"error": "SIMs not found."}), 404

    # ✅ Preserve user's mobile number
    preserved_mobile_number = old_sim.mobile_number

    # ✅ Generate safe SWP suffix for old SIM
    while True:
        suffix = f"SWP_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(2)}"
        if len(suffix) > 20:
            suffix = suffix[:20]
        if not SIMCard.query.filter_by(mobile_number=suffix).first():
            break

    # ✅ Update old SIM
    old_sim.status = "swapped"
    old_sim.mobile_number = suffix

    # ✅ Assign new SIM with preserved number
    new_sim.status = "active"
    new_sim.user_id = user.id
    new_sim.mobile_number = preserved_mobile_number
    new_sim.registration_date = datetime.utcnow()
    new_sim.registered_by = f"user-{user.id}"

    # ✅ Log success
    db.session.add(RealTimeLog(
        user_id=user.id,
        action=f"✅ Verified SIM Swap {old_sim.iccid} ➡️ {new_sim.iccid}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=get_ip_location(request.remote_addr),
        risk_alert=False,
        tenant_id=1
    ))

    # ✅ Clean up session and pending
    db.session.delete(pending)
    session.pop("reset_webauthn_verified", None)
    session.pop("reset_user_id", None)
    session.pop("reset_webauthn_assertion_state", None)

    db.session.commit()

    return jsonify({"message": "✅ SIM swap completed successfully."}), 200
