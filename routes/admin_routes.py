from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models.models import db, User, UserAccessControl, UserRole, Wallet, Transaction, UserAuthLog, SIMCard, RealTimeLog
import random
admin_bp = Blueprint("admin", __name__)

#Admin Dashboard
@admin_bp.route('/admin/dashboard')
@jwt_required()
@role_required(['admin'])
def admin_dashboard():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch the role properly from UserAccessControl or UserRole table
    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    role = db.session.get(UserRole, user_access.role_id).role_name if user_access else "Unknown"

    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    first_name = user.first_name  # extract the first name for the welcome message

    # Pass both first_name and full_name to the template
    admin_user = { 'first_name': first_name, 'full_name': full_name, 'role': role }
    
    return render_template('admin_dashboard.html', user=admin_user)


# ✅ List all users (Admin Only)
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_all_users():
    """Only admins can view all users"""
    try:
        users = User.query.all()  # Fetch all users
        users_list = []

        for u in users:
            # Fetch the SIM Card associated with the user
            primary_sim = SIMCard.query.filter_by(user_id=u.id, status="active").first()

            # Safely get the user's role (check if user_access_control exists)
            user_role = UserRole.query.get(u.user_access_control.role_id) if u.user_access_control else None
            role_name = user_role.role_name if user_role else "N/A"

            users_list.append({
                "id": u.id,
                "name": f"{u.first_name} {u.last_name or ''}".strip(),
                "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",  # Get the assigned number
                "email": u.email,
                "role": role_name  # Safely fetch the role name
            })

        return jsonify(users_list), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500

# ✅ Assign Role to User (Fixed for New Approach)
@admin_bp.route("/admin/assign_role", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def assign_role():
    """Admins assign roles to users"""
    data = request.get_json()

    user = User.query.get(data.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Get user's mobile number from SIMCard (since it's not in the User model anymore)
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    # ✅ Validate the role ID instead of role name
    role = UserRole.query.get(data.get("role_id"))
    if not role:
        return jsonify({"error": "Invalid role ID"}), 400

    # ✅ Assign or update user role
    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    if user_access:
        user_access.role_id = role.id  # ✅ Update existing role
    else:
        new_access = UserAccessControl(user_id=user.id, role_id=role.id)
        db.session.add(new_access)

    db.session.commit()
    return jsonify({"message": f"✅ Role '{role.role_name}' assigned to user with mobile {mobile_number}"}), 200


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

    # ✅ Fetch user's SIM card before deleting
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    # Delete related records first to maintain database integrity
    Wallet.query.filter_by(user_id=user_id).delete()
    Transaction.query.filter_by(user_id=user_id).delete()
    UserAuthLog.query.filter_by(user_id=user_id).delete()
    SIMCard.query.filter_by(user_id=user_id).delete()  # ✅ Changed from `SIMRegistration`
    UserAccessControl.query.filter_by(user_id=user_id).delete()
    RealTimeLog.query.filter_by(user_id=user_id).delete()

    # Finally, delete the user
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": f"User with mobile {mobile_number} and all related data have been permanently deleted."
    }), 200



   
# ✅ Admin Updates a User's Information
@admin_bp.route("/admin/edit_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def edit_user(user_id):
    """Allow an admin to edit user details, including email & SIM-linked mobile number."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    
    # ✅ Update only the provided fields
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "email" in data:
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({"error": "Email already in use"}), 400
        user.email = data["email"]

    # ✅ Handle Mobile Number Update (Check in SIMCard, not User)
    if "mobile_number" in data:
        existing_sim = SIMCard.query.filter_by(mobile_number=data["mobile_number"]).first()
        if existing_sim and existing_sim.user_id != user_id:
            return jsonify({"error": "Mobile number already in use"}), 400

        # ✅ Update the SIM Card's mobile number (if user has one)
        user_sim = SIMCard.query.filter_by(user_id=user.id).first()
        if user_sim:
            user_sim.mobile_number = data["mobile_number"]
        else:
            return jsonify({"error": "No SIM card linked to this user"}), 400

    db.session.commit()
    return jsonify({"message": "User updated successfully!"}), 200

# 📌 ✅ Generate Unique Mobile Number
def generate_unique_mobile_number():
    """Generate a mobile number that does not exist in the database."""
    while True:
        new_number = "0787" + str(random.randint(100000, 999999))  # Example format
        existing_number = SIMCard.query.filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number

# 📌 ✅ Generate Unique ICCID
def generate_unique_iccid():
    """Generate a unique SIM Serial Number (ICCID)."""
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = SIMCard.query.filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid

# 📌 ✅ API: Generate New SIM for User Registration
@admin_bp.route("/admin/generate_sim", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def generate_sim():
    """Admin generates a new SIM card for a user."""
    try:
        new_iccid = generate_unique_iccid()  # ✅ Generate ICCID
        new_mobile_number = generate_unique_mobile_number()  # ✅ Generate Mobile Number

        new_sim = SIMCard(
            iccid=new_iccid,
            mobile_number=new_mobile_number,
            network_provider="MTN Rwanda",  # Example network
            status="unregistered",
            registered_by="Admin"
        )

        db.session.add(new_sim)
        db.session.commit()

        return jsonify({
            "iccid": new_sim.iccid,
            "mobile_number": new_sim.mobile_number
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to generate SIM: {str(e)}"}), 500

# View User Details
@admin_bp.route("/admin/view_user/<int:user_id>", methods=["GET"])
@jwt_required()
def view_user(user_id):
    """Admin views user details and action buttons based on status."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch the active SIM card associated with the user
    primary_sim = SIMCard.query.filter_by(user_id=user.id, status="active").first()
    
    # Safely fetch the user's role
    user_role = UserRole.query.get(user.user_access_control.role_id) if user.user_access_control else None
    role_name = user_role.role_name if user_role else "N/A"
    
    # Prepare user details
    user_details = {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",  # Fetch mobile from SIMCard
        "email": user.email,
        "role": role_name,  # Fetch role name
        "is_verified": user.identity_verified,
        "is_suspended": user.is_active == False,
        "can_assign_role": True,  # Add this as true, so front end knows to display "Assign Role"
        "can_suspend": not user.is_active,  # Can suspend if user is active
        "can_verify": not user.identity_verified,  # Can verify if not verified
        "can_delete": True,  # Can always delete (after deletion request)
        "can_edit": True,  # Can always edit
    }

    return jsonify(user_details), 200
