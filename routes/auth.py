from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response, session, current_app
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,  # use this with refresh=True for refresh endpoints
    get_jwt_identity,
    unset_jwt_cookies,
    verify_jwt_in_request,
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from models.models import User, Wallet, db, UserRole, UserAccessControl,SIMCard, OTPCode, RealTimeLog, UserAuthLog
from utils.otp import generate_otp_code  # Import your OTP logic
from utils.totp import verify_totp_code
from utils.location import get_ip_location
import pyotp
import qrcode
import io
import base64
from flask import current_app
from utils.auth_decorators import require_full_mfa
from flask_mail import Message
from extensions import mail
from utils.email_alerts import send_admin_alert, send_user_alert



auth_bp = Blueprint('auth', __name__)

#Register form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

#Login
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

# def send_admin_alert(subject, body):
#     try:
#         msg = Message(
#             subject=subject,
#             recipients=[current_app.config["ADMIN_ALERT_EMAIL"]],
#             body=body
#         )
#         mail.send(msg)
#     except Exception as e:
#         print(f"❌ Failed to send alert email: {e}")

# def send_user_alert(user_email, subject, body):
#     if user_email:
#         msg = Message(subject=subject, recipients=[user_email], body=body)
#         mail.send(msg)

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
        db.session.add(RealTimeLog(
            user_id=None,
            action=f"❌ Failed login: Unknown identifier {login_input}",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))
        db.session.commit()
        return jsonify({"error": "User not found or SIM inactive"}), 404

    if user.locked_until and user.locked_until > datetime.utcnow():
        return jsonify({"error": f"Account locked. Try again after {user.locked_until}"}), 429

    recent_fails = count_recent_failures(user.id)

    if not user.check_password(password):
        failed_count = recent_fails + 1

        db.session.add(UserAuthLog(
            user_id=user.id,
            auth_method="password",
            auth_status="failed",
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            failed_attempts=failed_count
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
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
                action="🚨 Account temporarily locked due to failed login attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))

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
    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "require_totp": bool(user.otp_secret),
        "require_totp_setup": user.otp_secret is None,
        "require_totp_reset": user.otp_secret and user.otp_email_label != user.email    
    })

    db.session.add(UserAuthLog(
        user_id=user.id,
        auth_method="password",
        auth_status="success",
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        failed_attempts=0
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ Successful login",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False
    ))

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
        is_active=True
    )

    # ✅ Use the setter to ensure hashing works correctly
    new_user.password = data['password']  # This will hash the password automatically

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
    
    db.session.commit()  # ✅ Ensure all database changes are saved

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

    # ✅ Determine if setup or reset is needed
    reset_required = (
        user.otp_secret is None or
        (user.otp_secret and user.otp_email_label != user.email)
    )
    if reset_required:
        secret = pyotp.random_base32()
        user.otp_secret = secret
        user.otp_email_label = user.email  # ✅ Track email used
        db.session.commit()

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

    # ✅ Already configured and no email mismatch
    return jsonify({
        "message": "TOTP already configured."
    }), 200


# ✅ Verifying the TOTP
@auth_bp.route('/verify-totp-login', methods=['POST'])
def verify_totp_login():   
    try:
        verify_jwt_in_request(locations=["cookies"])
        user_id = get_jwt_identity()
    except NoAuthorizationError as e:
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
            failed_attempts=fail_count
        ))

        db.session.add(RealTimeLog(
            user_id=user.id,
            action=f"❌ Failed TOTP verification ({fail_count})",
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=True
        ))

        if fail_count >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)

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


            db.session.add(RealTimeLog(
                user_id=user.id,
                action="🚨 TOTP temporarily locked after multiple failed attempts",
                ip_address=ip_address,
                device_info=device_info,
                location=location,
                risk_alert=True
            ))

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
        failed_attempts=0
    ))

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="✅ TOTP verified successfully",
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=False
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

# Verfy your TOTP
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
        risk_alert=False
    ))
    db.session.commit()

    return jsonify({"status": "logged"}), 200


