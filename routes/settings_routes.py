from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User
import json

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/user/settings', methods=['POST'])
@jwt_required()
def update_settings():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Update fields as needed (example: country)
    country = data.get('country')
    if country:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        user.country = country
        db.session.commit()
        return jsonify({"message": "Settings updated successfully"}), 200
    return jsonify({"error": "No valid fields provided"}), 400

@settings_bp.route('/user/change_password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Validate passwords (you can add more complex validations here)
    if not current_password or not new_password:
        return jsonify({"error": "Both current and new passwords are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if current password is correct (assuming you have user.check_password method)
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Update the password (user.password setter hashes the password)
    user.password = new_password
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200
