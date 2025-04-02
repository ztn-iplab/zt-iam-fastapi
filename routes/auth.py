from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,  # use this with refresh=True for refresh endpoints
    get_jwt_identity,
    unset_jwt_cookies,
)
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from models.models import User, Wallet, db, UserRole, UserAccessControl,SIMCard, OTPCode
from utils.otp import generate_otp_code  # Import your OTP logic
import pyotp
import qrcode
import io
import base64
from flask import current_app




auth_bp = Blueprint('auth', __name__)

#Register form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

#Login
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_route():
    """Handles user login using mobile number or email and triggers TOTP verification if configured"""

    data = request.get_json()
    if not data or 'identifier' not in data or 'password' not in data:
        return jsonify({"error": "Mobile number or email and password are required"}), 400

    login_input = data.get('identifier')
    password = data.get('password')

    user = None
    sim_card = None

    # Try as email
    user = User.query.filter_by(email=login_input).first()

    if user:
        sim_card = SIMCard.query.filter_by(user_id=user.id, status='active').first()
    else:
        # Try as mobile number
        sim_card = SIMCard.query.filter_by(mobile_number=login_input, status='active').first()
        if sim_card:
            user = sim_card.user

    if not user:
        return jsonify({"error": "User not found or SIM inactive"}), 404

    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.otp_secret:
        return jsonify({
            "message": "TOTP is not configured. Redirecting to setup.",
            "require_totp_setup": True,
            "user_id": user.id
        }), 200

    return jsonify({
        "message": "Password verified. Enter your TOTP code to complete login.",
        "require_totp": True,
        "user_id": user.id
    }), 200



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

# ✅ Setting the OTP
@auth_bp.route('/setup-totp')
def show_setup_totp():
    print("✅ Reached /setup-totp route")
    return render_template('setup_totp.html')

# ✅ Getting the OTP
@auth_bp.route('/verify-totp', methods=['GET'])
def verify_totp_page():
    return render_template('verify_totp.html')


# ✅ Verifying the OTP
@auth_bp.route('/verify-totp-login', methods=['POST'])
def verify_totp_login():
    data = request.get_json()
    user_id = data.get('user_id')
    totp_code = data.get('totp')

    if not user_id or not totp_code:
        return jsonify({"error": "User ID and TOTP code are required"}), 400

    user = User.query.get(user_id)
    if not user or not user.otp_secret:
        return jsonify({"error": "Invalid user or TOTP not configured"}), 403

    from utils.totp import verify_totp_code
    if not verify_totp_code(user.otp_secret, totp_code):
        return jsonify({"error": "Invalid or expired TOTP code"}), 401

    # Fetch role and wallet info
    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    user_role = db.session.get(UserRole, user_access.role_id)
    role_name = user_role.role_name.lower()

    sim_card = SIMCard.query.filter_by(user_id=user.id, status='active').first()
    dashboard_urls = {
        "admin": url_for("admin.admin_dashboard", _external=True),
        "agent": url_for("agent.agent_dashboard", _external=True),
        "user": url_for("user.user_dashboard", _external=True)
    }
    dashboard_url = dashboard_urls.get(role_name, url_for("user.user_dashboard", _external=True))

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user_id": user.id,
        "mobile_number": sim_card.mobile_number if sim_card else None,
        "iccid": sim_card.iccid if sim_card else None,
        "role": role_name,
        "dashboard_url": dashboard_url
    })
    set_access_cookies(response, access_token)
    return response, 200



 
# ✅ Set up Token_OTP
@auth_bp.route('/setup-totp', methods=['GET'])
@jwt_required()
def setup_transaction_totp():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.otp_secret:
        return jsonify({"message": "TOTP already configured."}), 200

    # Generate a new secret key for TOTP
    secret = pyotp.random_base32()
    user.otp_secret = secret
    db.session.commit()

    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="ZTN_MoMo_SIM"
    )

    # Generate QR code for TOTP
    qr = qrcode.make(totp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()

    return jsonify({
        "qr_code": f"data:image/png;base64,{img_base64}",
        "manual_key": secret
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