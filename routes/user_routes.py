from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User,UserAccessControl, UserRole, SIMCard
from utils.decorators import role_required, session_protected
from utils.decorators import require_totp_setup
from utils.auth_decorators import require_full_mfa


user_bp = Blueprint('user', __name__)

#User Dashboard
@user_bp.route("/user/dashboard")
@jwt_required()
@session_protected()
@require_totp_setup
@require_full_mfa
def user_dashboard():  # ✅ Function name must be "user_dashboard"
    """User dashboard view"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return render_template("user_dashboard.html", user=user)

#Create User
@user_bp.route('/users', methods=['POST'])
@jwt_required()

def create_user():
    # User creation logic
    data = request.get_json()
    if not data.get('mobile_number') or not data.get('first_name'):
        return jsonify({"error": "Mobile number and first name are required"}), 400
    new_user = User(
        mobile_number=data['mobile_number'],
        full_name=data['first_name'],
        country=data.get('country'),
        identity_verified=data.get('identity_verified', False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "id": new_user.id,
        "mobile_number": new_user.mobile_number,
        "first_name": new_user.first_name,
        "country": new_user.country,
        "identity_verified": new_user.identity_verified
    }), 201

# Get the current user details
@user_bp.route('/user', methods=['GET'])
@jwt_required()
@session_protected()
def get_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check the user's role
    role = "user"  # Default role
    if user.user_access_control:  
        user_role = UserRole.query.get(user.user_access_control.role_id)
        if user_role:
            role = user_role.role_name  # 'admin', 'agent', or 'user'

    user_data = {
        "id": user.id,
        "mobile_number": user.mobile_number,
        "first_name": user.first_name,
        "email": user.email,
        "country": user.country,
        "identity_verified": user.identity_verified,
        "trust_score": user.trust_score,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "role": role,
        "wallet": None if role == "admin" else {
            "balance": user.wallet.balance,
            "currency": user.wallet.currency,
            "last_transaction_at": user.wallet.last_transaction_at.isoformat() if user.wallet.last_transaction_at else None
        }
    }

    return jsonify(user_data), 200



# Update the current user details
@user_bp.route('/user', methods=['PUT'])
@jwt_required()
@session_protected()
def update_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'country' in data:
        user.country = data['country']
    if 'identity_verified' in data:
        user.identity_verified = data['identity_verified']
    # If updating the password, use the model's password setter
    if 'password' in data:
        user.password = data['password']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

# Delete the current user account
@user_bp.route('/user', methods=['DELETE'])
@jwt_required()
@session_protected()
def delete_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

# Profile route
@user_bp.route('/user/profile', methods=['GET'])
@jwt_required()
@session_protected()
def profile():
    current_user_id = get_jwt_identity()  # Extract user ID from JWT
    user = User.query.get(current_user_id)  # Fetch user from DB

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "mobile_number": user.mobile_number,
        "first_name": user.first_name,
        "country": user.country,
        "identity_verified": user.identity_verified
    }), 200

#Request Deletion
@user_bp.route('/user/request_deletion', methods=['POST'])
@jwt_required()
@session_protected()
def request_deletion():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Option 1: If you have a deletion_requested column in the User model:
    # user.deletion_requested = True
    # db.session.commit()

    # Option 2: Log the request or send an email to admin (for simulation, we'll return a success message)
    # For now, we simply return a message.
    return jsonify({"message": "Your account deletion request has been submitted. An administrator will review your request shortly."}), 200


    # ✅ API: Fetch Basic User Info by Mobile Number
@user_bp.route('/user-info/<string:mobile_number>', methods=['GET'])
@jwt_required()
@session_protected()
def get_user_info(mobile_number):
    sim = SIMCard.query.filter_by(mobile_number=mobile_number).first()
    
    if not sim or not sim.user:
        return jsonify({"error": "User not found for this mobile number."}), 404

    user = sim.user
    
    return jsonify({
        "id": user.id,
        "mobile_number": sim.mobile_number,
        "name": f"{user.first_name} {user.last_name}".strip() or "Unknown"
    }), 200

# set up the TOTP for transactions
@user_bp.route('/setup-totp')
@jwt_required()
@session_protected()
def show_totp_setup():
    return render_template('setup_totp.html')
