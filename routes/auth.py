from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,  # use this with refresh=True for refresh endpoints
    get_jwt_identity,
    unset_jwt_cookies,
)
from werkzeug.security import check_password_hash
from models.models import User, Wallet, db, UserRole, UserAccessControl,SIMCard


auth_bp = Blueprint('auth', __name__)

#Register form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

#Login
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

#Login Endpoint
@auth_bp.route('/login', methods=['POST'])
def login_route():
    """Handles user login using mobile number and redirects to the correct dashboard"""

    data = request.get_json()
    if not data or 'mobile_number' not in data or 'password' not in data:
        return jsonify({"error": "Mobile number and password are required"}), 400

    mobile_number = data.get('mobile_number')
    password = data.get('password')

    # ✅ Find the SIM card by mobile number
    sim_card = SIMCard.query.filter_by(mobile_number=mobile_number, status="active").first()
    if not sim_card:
        return jsonify({"error": "Invalid mobile number or inactive SIM card"}), 401

    # ✅ Get the linked user from the SIM card
    user = sim_card.user
    if not user:
        return jsonify({"error": "User not found for this mobile number"}), 404

    # ✅ Validate password
    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Check User Role
    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    if not user_access:
        return jsonify({"error": "User has no assigned role"}), 403

    user_role = db.session.get(UserRole, user_access.role_id)
    if not user_role:
        return jsonify({"error": "User role not found"}), 403

    role_name = user_role.role_name

    access_token = create_access_token(identity=str(user.id))

    # ✅ Define dashboard URLs based on roles
    dashboard_urls = {
        "admin": url_for("admin.admin_dashboard", _external=True),
        "agent": url_for("agent.agent_dashboard", _external=True),
        "user": url_for("user.user_dashboard", _external=True)
    }

    dashboard_url = dashboard_urls.get(role_name, url_for("user.user_dashboard", _external=True))

    response = jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "mobile_number": sim_card.mobile_number,  # ✅ Mobile number included
        "iccid": sim_card.iccid,  # ✅ ICCID included for internal reference
        "role": role_name,
        "dashboard_url": dashboard_url
    })

    set_access_cookies(response, access_token)  # ✅ Store token securely in HTTP-Only Cookie

    return response, 200


# 📌 Register a New User (Using ICCID)
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # 🔹 Ensure request is parsed as JSON
        data = request.get_json(force=True)  
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400

    # ✅ Validate required fields
    if not data.get('iccid') or not data.get('first_name') or not data.get('password') or not data.get('email'):
        return jsonify({"error": "ICCID, email, first name, and password are required"}), 400

    # 🔹 Fetch the SIM card by ICCID
    sim_card = SIMCard.query.filter_by(iccid=data['iccid']).first()

    if not sim_card:
        return jsonify({"error": "Invalid ICCID. Please register a SIM first."}), 404

    # ✅ If SIM is found but unregistered, activate it
    if sim_card.status == "unregistered":
        sim_card.status = "active"
        db.session.commit()

    if not sim_card:
        return jsonify({"error": "Invalid ICCID. Please register a SIM first."}), 404

    # 🔹 Check if a user is already linked to this SIM card
    existing_user = User.query.filter((User.email == data['email']) | (User.id == sim_card.user_id)).first()
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
    if user_role:
        new_access = UserAccessControl(user_id=new_user.id, role_id=user_role.id)
        db.session.add(new_access)
    else:
        return jsonify({"error": "Default user role not found"}), 500

    # 🔹 Create Wallet for the User
    new_wallet = Wallet(user_id=new_user.id, balance=0.0, currency="RWF")
    db.session.add(new_wallet)
    db.session.commit()

    # 🔹 Return response
    return jsonify({
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
            "balance": 0.0,
            "currency": "RWF"
        }
    }), 201

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
