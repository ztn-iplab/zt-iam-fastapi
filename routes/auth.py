from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models.models import User, Wallet, db, UserRole, UserAccessControl
 
auth_bp = Blueprint('auth', __name__)

# Render registration form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

# Render login form
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

# ----------------------------
# USER REGISTRATION (Self-Service)
# ----------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """Registers a new user and assigns a default role ('user')."""
    data = request.form if request.form else request.get_json()

    # Validate required fields
    if not data.get('mobile_number') or not data.get('first_name') or not data.get('password') or not data.get('email'):
        return jsonify({"error": "Mobile number, email, first name, and password are required"}), 400

    # Check if user already exists (by mobile number OR email) and is active
    existing_user = User.query.filter(
        ((User.mobile_number == data['mobile_number']) | (User.email == data['email'])) & (User.is_active == True)
    ).first()

    if existing_user:
        return jsonify({"error": "User with this mobile number or email already exists"}), 400

    # Create new user
    new_user = User(
        mobile_number=data['mobile_number'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data.get('last_name'),
        country=data.get('country'),
        identity_verified=data.get('identity_verified', False),
        is_active=True
    )
    new_user.password = data['password']  # Using the model's password setter

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"User creation failed: {e}"}), 500

    # Assign the default "user" role
    user_role = UserRole.query.filter_by(role_name="user").first()
    if user_role:
        new_access = UserAccessControl(user_id=new_user.id, role_id=user_role.id)
        db.session.add(new_access)

    # Automatically create a wallet with 0.0 RWF balance
    new_wallet = Wallet(user_id=new_user.id, balance=0.0, currency="RWF")
    db.session.add(new_wallet)
    db.session.commit()

    # For HTML form submissions, redirect to the login form
    if request.form:
        return redirect(url_for('auth.login_form', registered='1'))
    else:
        return jsonify({
            "message": "User registered successfully, assigned role: 'user', and wallet created.",
            "id": new_user.id,
            "mobile_number": new_user.mobile_number,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "country": new_user.country,
            "identity_verified": new_user.identity_verified,
            "role": "user",
            "wallet": {
                "balance": 0.0,
                "currency": "RWF"
            }
        }), 201




# Login Route (handles both form and JSON)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.form if request.form else request.get_json()
    mobile_number = data.get('mobile_number')
    password = data.get('password')

    # Find the user by mobile number, ensuring the account is active
    user = User.query.filter_by(mobile_number=mobile_number, is_active=True).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate JWT token for the user with identity as a string
    access_token = create_access_token(identity=str(user.id))

    # For HTML submissions, you might want to redirect to the dashboard or set a session.
    # For now, we return JSON with the token.
    return jsonify({
        "access_token": access_token,
        "user_id": user.id
    })
