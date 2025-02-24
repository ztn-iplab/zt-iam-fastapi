from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from models.models import db, User, UserAccessControl, UserRole

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_all_users():
    """Only admins can view all users"""
    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "name": f"{u.first_name} {u.last_name or ''}",
            "mobile_number": u.mobile_number,
            "email": u.email,
            "role": u.user_access_control.role_id if u.user_access_control else None
        } 
        for u in users
    ]), 200



@admin_bp.route("/admin/assign_role", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def assign_role():
    """Admins assign roles to users"""
    data = request.get_json()
    user = User.query.get(data.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Validate the role name
    role = UserRole.query.filter_by(role_name=data.get("role_name")).first()
    if not role:
        return jsonify({"error": "Invalid role"}), 400

    # Assign or update user role
    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    if user_access:
        user_access.role_id = role.id  # Update existing role
    else:
        new_access = UserAccessControl(user_id=user.id, role_id=role.id)
        db.session.add(new_access)

    db.session.commit()
    return jsonify({"message": f"Role '{role.role_name}' assigned to user {user.mobile_number}"}), 200

@admin_bp.route("/admin/suspend_user/<int:user_id>", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def suspend_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User suspended successfully"}), 200

@admin_bp.route("/admin/verify_user/<int:user_id>", methods=["POST"])
@jwt_required()
@role_required(["admin", "agent"])
def verify_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.identity_verified = True
    db.session.commit()
    return jsonify({"message": "User verified successfully"}), 200


