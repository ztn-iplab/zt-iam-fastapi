from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, UserRole, UserAccessControl

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = UserRole.query.all()
    roles_data = [{
        "id": role.id,
        "role_name": role.role_name,
        "permissions": role.permissions
    } for role in roles]
    return jsonify(roles_data), 200

@roles_bp.route('/assign_role', methods=['POST'])
@jwt_required()
def assign_role():
    data = request.get_json()
    user_id = data.get("user_id")
    role_id = data.get("role_id")
    access_level = data.get("access_level", "read")
    if not user_id or not role_id:
        return jsonify({"error": "User ID and Role ID are required"}), 400

    # Optional: You could add logic here to verify the current user is an admin.
    # For now, we simply create the assignment.
    new_assignment = UserAccessControl(user_id=user_id, role_id=role_id, access_level=access_level)
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({"message": "Role assigned successfully"}), 200
