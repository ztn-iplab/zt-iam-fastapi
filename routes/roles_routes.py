from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.models import db, User, UserRole, UserAccessControl
from utils.decorators import session_protected

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['GET'])
@jwt_required()
@session_protected()
def get_roles():
    roles = UserRole.query.all()
    roles_data = [{
        "id": role.id,
        "role_name": role.role_name,
        "permissions": role.permissions if hasattr(role, "permissions") else None
    } for role in roles]
    return jsonify(roles_data), 200

@roles_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@session_protected()
def get_user_role(user_id):
    user_access = UserAccessControl.query.filter_by(user_id=user_id).first()
    if not user_access:
        return jsonify({"error": "User has no assigned role"}), 404
    user_role = UserRole.query.get(user_access.role_id)
    if not user_role:
        return jsonify({"error": "User role not found"}), 404
    return jsonify({"user_id": user_id, "role": user_role.role_name}), 200

@roles_bp.route('/assign_role', methods=['POST'])
@jwt_required()
@session_protected()
def assign_role():
    data = request.get_json()
    user_id = data.get("user_id")
    role_id = data.get("role_id")
    access_level = data.get("access_level", "read")
    
    if not user_id or not role_id:
        return jsonify({"error": "User ID and Role ID are required"}), 400

    # Check if the user already has an assignment.
    user_access = UserAccessControl.query.filter_by(user_id=user_id).first()
    if user_access:
        user_access.role_id = role_id
        user_access.access_level = access_level
    else:
        user_access = UserAccessControl(user_id=user_id, role_id=role_id, access_level=access_level)
        db.session.add(user_access)
    
    db.session.commit()
    return jsonify({"message": "Role assigned successfully", "user_id": user_id, "role_id": role_id}), 200
