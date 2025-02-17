from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models.models import User, Wallet, db
 
auth_bp = Blueprint('auth', __name__)

# Render registration form
@auth_bp.route('/register_form', methods=['GET'])
def register_form():
    return render_template('register.html')

# Render login form
@auth_bp.route('/login_form', methods=['GET'])
def login_form():
    return render_template('login.html')

# Registration Route (can accept form data as well as JSON)
@auth_bp.route('/register', methods=['POST'])
def register():
    # If the request is coming from an HTML form, data will be in request.form
    data = request.form if request.form else request.get_json()

    # Validate input
    if not data.get('mobile_number') or not data.get('full_name') or not data.get('password'):
        return jsonify({"error": "Mobile number, full name, and password are required"}), 400

    # Check if the user already exists
    if User.query.filter_by(mobile_number=data['mobile_number'], is_active=True).first():
        return jsonify({"error": "User already exists"}), 400

    # Create a new user using the provided data
    new_user = User(
        mobile_number=data['mobile_number'],
        full_name=data['full_name'],
        country=data.get('country'),
        identity_verified=data.get('identity_verified', False)
    )
    
    # Hash and store the password using the model's setter
    new_user.password = data['password']

    db.session.add(new_user)
    db.session.commit()

    # Auto-create a wallet for the new user
    new_wallet = Wallet(user_id=new_user.id, balance=0.0, currency="RWF")
    db.session.add(new_wallet)
    db.session.commit()

    # Check if the request is a form submission (HTML) or JSON request
    if request.form:
        # For HTML form submission, redirect to login page after registration
        return redirect(url_for('auth.login_form'))
    else:
        # For JSON API request, return the user data
        return jsonify({
            "id": new_user.id,
            "mobile_number": new_user.mobile_number,
            "full_name": new_user.full_name,
            "country": new_user.country,
            "identity_verified": new_user.identity_verified
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
