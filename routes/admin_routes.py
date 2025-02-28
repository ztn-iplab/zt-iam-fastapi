from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models.models import db, User, UserAccessControl, UserRole, Wallet, Transaction, UserAuthLog, SIMRegistration, RealTimeLog

admin_bp = Blueprint("admin", __name__)

# List all users
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_all_users():
    """Only admins can view all users"""
    try:
        users = User.query.all()
        users_list = []
        for u in users:
            users_list.append({
                "id": u.id,
                "name": f"{u.first_name} {u.last_name or ''}".strip(),
                "mobile_number": u.mobile_number,
                "email": u.email,
                "role": UserRole.query.get(u.user_access_control.role_id).role_name if u.user_access_control else None
            })
        return jsonify(users_list), 200
    except Exception as e:
        # Log the error (if you have logging set up)
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500


# Assign role to user
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


# Suspend the user
@admin_bp.route("/admin/suspend_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def suspend_user(user_id):
    """Suspend a user by setting is_active=False and marking for deletion."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Mark user as inactive and set deletion_requested to True
    user.is_active = False
    user.deletion_requested = True
    db.session.commit()

    return jsonify({"message": "User has been suspended and marked for deletion."}), 200



    
# verify or restore the user account
@admin_bp.route("/admin/verify_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def verify_user(user_id):
    """Verify a user by reactivating their account and canceling the deletion request."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Restore user account
    user.is_active = True
    user.deletion_requested = False
    db.session.commit()

    return jsonify({"message": "User account has been activated and verified."}), 200


# Permanent deletion of the user
@admin_bp.route("/admin/delete_user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_user(user_id):
    """Permanently delete a user and all associated records after a deletion request."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.deletion_requested:
        return jsonify({"error": "User has not requested account deletion."}), 400

    # Delete related records first to maintain database integrity
    Wallet.query.filter_by(user_id=user_id).delete()
    Transaction.query.filter_by(user_id=user_id).delete()
    UserAuthLog.query.filter_by(user_id=user_id).delete()
    SIMRegistration.query.filter_by(user_id=user_id).delete()
    UserAccessControl.query.filter_by(user_id=user_id).delete()
    RealTimeLog.query.filter_by(user_id=user_id).delete()

    # Finally, delete the user
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User and all related data have been permanently deleted."}), 200



    
# Updading the user
@admin_bp.route("/admin/edit_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def edit_user(user_id):
    """Allow an admin to edit user details."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    
    # Update only fields that were provided
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "email" in data:
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({"error": "Email already in use"}), 400
        user.email = data["email"]
    if "mobile_number" in data:
        existing_mobile = User.query.filter_by(mobile_number=data["mobile_number"]).first()
        if existing_mobile and existing_mobile.id != user_id:
            return jsonify({"error": "Mobile number already in use"}), 400
        user.mobile_number = data["mobile_number"]

    db.session.commit()
    return jsonify({"message": "User updated successfully!"}), 200