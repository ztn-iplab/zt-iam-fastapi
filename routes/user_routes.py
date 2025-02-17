from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User

user_bp = Blueprint('user', __name__)
#Create User
@user_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    # User creation logic
    data = request.get_json()
    if not data.get('mobile_number') or not data.get('full_name'):
        return jsonify({"error": "Mobile number and full name are required"}), 400
    new_user = User(
        mobile_number=data['mobile_number'],
        full_name=data['full_name'],
        country=data.get('country'),
        identity_verified=data.get('identity_verified', False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "id": new_user.id,
        "mobile_number": new_user.mobile_number,
        "full_name": new_user.full_name,
        "country": new_user.country,
        "identity_verified": new_user.identity_verified
    }), 201

# Get the current user details
@user_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        "id": user.id,
        "mobile_number": user.mobile_number,
        "full_name": user.full_name,
        "country": user.country,
        "identity_verified": user.identity_verified,
        "trust_score": user.trust_score,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 200

# Update the current user details
@user_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'full_name' in data:
        user.full_name = data['full_name']
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
def delete_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

    # Profile route
@user_bp.route('user/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()  # Extract user ID from JWT
    user = User.query.get(current_user_id)  # Fetch user from DB

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "mobile_number": user.mobile_number,
        "full_name": user.full_name,
        "country": user.country,
        "identity_verified": user.identity_verified
    }), 200