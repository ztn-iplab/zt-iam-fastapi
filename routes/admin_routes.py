from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models.models import (
    db,
    User, 
    UserAccessControl, 
    UserRole, 
    Wallet, 
    Transaction,
    UserAuthLog, 
    SIMCard, 
    RealTimeLog,
    Tenant,
    TenantUser,
    TenantPasswordHistory, 
    HeadquartersWallet)
import random
import json
import threading
from sqlalchemy import func, text
from datetime import datetime
from threading import Timer
from utils.auth_decorators import require_full_mfa
from datetime import datetime, timedelta
from utils.decorators import session_protected
from utils.email_alerts import send_tenant_api_key_email, send_rotated_api_key_email
from utils.location import get_ip_location
from werkzeug.security import check_password_hash, generate_password_hash

admin_bp = Blueprint("admin", __name__)

# FINALIZE FUNCTION 
def finalize_reversal(app, reversal_id, sender_wallet_id, amount):
    try:
        with app.app_context():

            reversal_tx = db.session.get(Transaction, reversal_id)
            sender_wallet = db.session.get(Wallet, sender_wallet_id)

            if not reversal_tx:
                print(f"❌ Reversal transaction {reversal_id} not found.")
                return

            if not sender_wallet:
                print(f"❌ Sender wallet {sender_wallet_id} not found.")
                return

            if reversal_tx.status != "pending":
                print(f"⚠️ Reversal TX {reversal_id} is already completed.")
                return

            sender_wallet.balance += amount
            reversal_tx.status = "completed"

            try:
                tx_meta = json.loads(reversal_tx.transaction_metadata)
                original_tx_id = tx_meta.get("reversal_of_transaction_id", "Unknown")
            except:
                original_tx_id = "Unknown"

            completion_log = RealTimeLog(
                user_id=reversal_tx.user_id,
                action=f"✅ Reversal completed: {amount} RWF refunded to sender for TX #{original_tx_id}",
                ip_address="System",
                device_info="Auto Processor",
                location="Headquarters",
                risk_alert=False,
                tenant_id=1
            )

            db.session.add(completion_log)
            db.session.commit()

            print(f"✅ TX #{reversal_id} refunded {amount} to sender.")

    except Exception as e:
        print(f"❌ finalize_reversal() crashed: {e}")

#Admin Dashboard
@admin_bp.route('/admin/dashboard')
@jwt_required()
@session_protected()
@role_required(['admin'])
@require_full_mfa
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


#  List all users (Admin Only)
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def get_all_users():
    """ZTN-IAM Admins view all users (Master Tenant only)"""
    try:
        users = User.query.all()
        users_list = []

        for u in users:
            # 📱 Fetch active SIM only
            primary_sim = SIMCard.query.filter_by(user_id=u.id, status="active").first()

            # 🔐 Enforce Master Tenant access (must match both tenant + role)
            access = (
                UserAccessControl.query
                .join(UserRole, UserAccessControl.role_id == UserRole.id)
                .filter(
                    UserAccessControl.user_id == u.id,
                    UserAccessControl.tenant_id == 1,         # 👈 Must be from Master Tenant
                    UserRole.tenant_id == 1                   # 👈 Role must also belong to Master Tenant
                )
                .first()
            )

            if not access or not access.role:
                continue  # Skip users who do not have a valid MasterTenant role

            role_name = access.role.role_name

            is_locked = u.locked_until is not None and u.locked_until > datetime.utcnow()

            users_list.append({
                "id": u.id,
                "name": f"{u.first_name} {u.last_name or ''}".strip(),
                "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",
                "email": u.email,
                "role": role_name,
                "is_locked": is_locked,
                "locked_until": u.locked_until.isoformat() if u.locked_until else None
            })

        return jsonify(users_list), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch users",
            "details": str(e)
        }), 500

#  Assign Role to User (Fixed for New Approach)
ZTN_MASTER_TENANT_ID = 1
@admin_bp.route("/admin/assign_role", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def assign_role():
    data = request.get_json()

    user = User.query.get(data.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404

    role = UserRole.query.get(data.get("role_id"))
    if not role:
        return jsonify({"error": "Invalid role ID"}), 400

    # Enforce that the role is from master tenant
    if role.tenant_id != ZTN_MASTER_TENANT_ID:
        return jsonify({"error": "Cross-tenant role assignment is not allowed"}), 400

    #  Assign or update access control for master tenant
    user_access = UserAccessControl.query.filter_by(
        user_id=user.id,
        tenant_id=ZTN_MASTER_TENANT_ID
    ).first()

    if user_access:
        user_access.role_id = role.id
        user_access.access_level = data.get("access_level", "read")
    else:
        new_access = UserAccessControl(
            user_id=user.id,
            role_id=role.id,
            tenant_id=ZTN_MASTER_TENANT_ID,
            access_level=data.get("access_level", "read")
        )
        db.session.add(new_access)

    # Logging
    user_sim = SIMCard.query.filter_by(user_id=user.id, status="active").first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    admin_id = int(get_jwt_identity())
    rt_log = RealTimeLog(
        user_id=admin_id,
        tenant_id=ZTN_MASTER_TENANT_ID,
        action=f"🛠️ Assigned role '{role.role_name}' to user {user.first_name} {user.last_name} ({mobile_number})",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin Panel"),
        location="Headquarters",
        risk_alert=False
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({
        "message": f"✅ Role '{role.role_name}' assigned to user with mobile {mobile_number}"
    }), 200


# Suspend the user
@admin_bp.route("/admin/suspend_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def suspend_user(user_id):
    """Suspend a user by setting is_active=False and marking for deletion."""

    current_user_id = get_jwt_identity()

    #  Prevent self-suspension
    if current_user_id == user_id:
        return jsonify({"error": "Admins are not allowed to suspend their own accounts."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    #  Suspend user and flag for deletion
    user.is_active = False
    user.deletion_requested = True

    #  Log suspension
    admin_user = User.query.get(current_user_id)
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    rt_log = RealTimeLog(
        user_id=admin_user.id,
        action=f"🚫 Suspended user {user.first_name} {user.last_name} ({mobile_number}) and marked for deletion.",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin Panel"),
        location="Headquarters",
        risk_alert=True, 
        tenant_id=1
    )
    db.session.add(rt_log)

    db.session.commit()

    return jsonify({"message": "User has been suspended and marked for deletion."}), 200

   
# verify or restore the user account
@admin_bp.route("/admin/verify_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def verify_user(user_id):
    """Verify a user by reactivating their account and canceling the deletion request."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    #  Restore user account
    user.is_active = True
    user.deletion_requested = False

    #  Admin details
    admin_id = int(get_jwt_identity())
    admin_user = User.query.get(admin_id)

    #  Get user's mobile number (if available)
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    # Log admin verification action
    rt_log = RealTimeLog(
        user_id=admin_user.id,
        action=f"✅ Verified and reactivated user {user.first_name} {user.last_name} ({mobile_number})",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin Panel"),
        location="Headquarters",
        risk_alert=False,
        tenant_id=1
    )
    db.session.add(rt_log)

    db.session.commit()

    return jsonify({"message": "User account has been activated and verified."}), 200


# Permanent deletion of the user
@admin_bp.route("/admin/delete_user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def delete_user(user_id):
    """Permanently delete a user and all associated records after a deletion request."""

    current_user_id = get_jwt_identity()

    # Prevent self-deletion
    if current_user_id == user_id:
        return jsonify({"error": "Admins are not allowed to delete their own accounts."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.deletion_requested:
        return jsonify({"error": "User has not requested account deletion."}), 400

    # Fetch user's SIM card before deleting
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    # Log the deletion BEFORE removing the user
    admin_user = User.query.get(current_user_id)
    rt_log = RealTimeLog(
        user_id=admin_user.id,
        action=f"🗑️ Deleted user {user.first_name} {user.last_name} ({mobile_number}) and all associated records",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin Panel"),
        location="Headquarters",
        risk_alert=True,
        tenant_id=1
    )
    db.session.add(rt_log)

    # Delete related records
    Wallet.query.filter_by(user_id=user_id).delete()
    Transaction.query.filter_by(user_id=user_id).delete()
    UserAuthLog.query.filter_by(user_id=user_id).delete()
    SIMCard.query.filter_by(user_id=user_id).delete()
    UserAccessControl.query.filter_by(user_id=user_id).delete()
    RealTimeLog.query.filter_by(user_id=user_id).delete()  # Clear user-specific logs

    #Finally, delete the user
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": f"User with mobile {mobile_number} and all related data have been permanently deleted."
    }), 200



   
# Admin Updates a User's Information
@admin_bp.route("/admin/edit_user/<int:user_id>", methods=["PUT"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def edit_user(user_id):
    """Allow an admin to edit user details, including email & SIM-linked mobile number."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    changes = []  # To track what was modified

    #  Update only the provided fields
    if "first_name" in data:
        user.first_name = data["first_name"]
        changes.append("first_name")

    if "last_name" in data:
        user.last_name = data["last_name"]
        changes.append("last_name")

    if "email" in data:
        existing_email = User.query.filter_by(email=data["email"]).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({"error": "Email already in use"}), 400
        user.email = data["email"]
        changes.append("email")

    #  Handle Mobile Number Update
    if "mobile_number" in data:
        existing_sim = SIMCard.query.filter_by(mobile_number=data["mobile_number"]).first()
        if existing_sim and existing_sim.user_id != user_id:
            return jsonify({"error": "Mobile number already in use"}), 400

        user_sim = SIMCard.query.filter_by(user_id=user.id).first()
        if user_sim:
            user_sim.mobile_number = data["mobile_number"]
            changes.append("mobile_number")
        else:
            return jsonify({"error": "No SIM card linked to this user"}), 400

    #  Log admin edit action
    if changes:
        admin_id = int(get_jwt_identity())
        admin_user = User.query.get(admin_id)

        user_sim = SIMCard.query.filter_by(user_id=user.id).first()
        mobile_number = user_sim.mobile_number if user_sim else "N/A"

        rt_log = RealTimeLog(
            user_id=admin_id,
            action=f"✏️ Edited user {user.first_name} {user.last_name} ({mobile_number}) — Fields updated: {', '.join(changes)}",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
            tenant_id=1
        )
        db.session.add(rt_log)

    db.session.commit()
    return jsonify({"message": "User updated successfully!"}), 200


# Generate Unique Mobile Number
def generate_unique_mobile_number():
    """Generate a mobile number that does not exist in the database."""
    while True:
        new_number = "0787" + str(random.randint(100000, 999999))  # Example format
        existing_number = SIMCard.query.filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number

#  Generate Unique ICCID
def generate_unique_iccid():
    """Generate a unique SIM Serial Number (ICCID)."""
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = SIMCard.query.filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid

# API: Generate New SIM for User Registration
@admin_bp.route("/admin/generate_sim", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def generate_sim():
    """Admin generates a new SIM card for a user."""
    try:
        new_iccid = generate_unique_iccid()
        new_mobile_number = generate_unique_mobile_number()

        new_sim = SIMCard(
            iccid=new_iccid,
            mobile_number=new_mobile_number,
            network_provider="MTN Rwanda",  # Example network
            status="unregistered",
            registered_by="Admin"
        )

        db.session.add(new_sim)

        #  Real-time log entry
        admin_id = int(get_jwt_identity())
        admin_user = User.query.get(admin_id)

        rt_log = RealTimeLog(
            user_id=admin_user.id,
            action=f"📱 Admin generated SIM: {new_iccid} with mobile {new_mobile_number}",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
            tenant_id=1
        )
        db.session.add(rt_log)

        db.session.commit()

        return jsonify({
            "iccid": new_sim.iccid,
            "mobile_number": new_sim.mobile_number
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to generate SIM: {str(e)}"}), 500


# View User Details
ZTN_MASTER_TENANT_ID = 1

@admin_bp.route("/admin/view_user/<int:user_id>", methods=["GET"])
@jwt_required()
@session_protected()
def view_user(user_id):
    """Admin views user details (ZTN-IAM context only)."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    #  Get active SIM
    primary_sim = SIMCard.query.filter_by(user_id=user.id, status="active").first()

    #  Get role scoped to master tenant
    access = UserAccessControl.query.filter_by(
        user_id=user.id,
        tenant_id=ZTN_MASTER_TENANT_ID
    ).first()

    user_role = UserRole.query.get(access.role_id) if access else None
    role_name = user_role.role_name if user_role else "N/A"

    #  Log view action
    admin_id = int(get_jwt_identity())
    admin_user = User.query.get(admin_id)

    rt_log = RealTimeLog(
        user_id=admin_id,
        action=f"👁️ Viewed profile of {user.first_name} {user.last_name or ''} ({primary_sim.mobile_number if primary_sim else 'N/A'})",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin Panel"),
        location="Headquarters",
        risk_alert=False,
        tenant_id=ZTN_MASTER_TENANT_ID
    )
    db.session.add(rt_log)
    db.session.commit()

    #  Prepare user details
    user_details = {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",
        "email": user.email,
        "role": role_name,
        "is_verified": user.identity_verified,
        "is_suspended": not user.is_active,
        "can_assign_role": True,
        "can_suspend": not user.is_active,
        "can_verify": not user.identity_verified,
        "can_delete": True,
        "can_edit": True,
    }

    return jsonify(user_details), 200

# Sending froats to agents
from decimal import Decimal, InvalidOperation
@admin_bp.route('/admin/fund-agent', methods=['POST'])
@jwt_required()
@session_protected()
@role_required(['admin'])
def fund_agent():
    data = request.get_json()
    admin_id = get_jwt_identity()

    agent_mobile = data.get('agent_mobile')
    raw_amount = data.get('amount')  # Still raw string/float from JSON
    device_info = data.get('device_info')
    location = data.get('location')

    if not agent_mobile or not raw_amount:
        return jsonify({"error": "Missing agent mobile or amount."}), 400

    try:
        amount = Decimal(str(raw_amount))  # Secure conversion
        if amount <= 0:
            return jsonify({"error": "Invalid amount. Must be positive."}), 400
    except (InvalidOperation, ValueError) as e:
        print(f"[ERROR] Amount parse error: {e}")
        return jsonify({"error": "Amount must be a valid number."}), 400

    #  Fetch HQ wallet
    hq_wallet = HeadquartersWallet.query.first()
    if not hq_wallet:
        print("[ERROR] HQ Wallet not found.")
        return jsonify({"error": "HQ Wallet not found"}), 404

    hq_balance = hq_wallet.balance


    if hq_balance < amount:
        print(f"[BLOCKED] HQ balance too low. Requested: {amount}, Available: {hq_balance}")
        return jsonify({
            "error": f"Insufficient HQ funds. Available: {hq_balance} RWF, Requested: {amount} RWF"
        }), 400

    # Find the agent
    agent_sim = SIMCard.query.filter_by(mobile_number=agent_mobile).first()
    if not agent_sim or not agent_sim.user_id:
        return jsonify({"error": "Agent SIM is not assigned to any user."}), 400

    agent = User.query.get(agent_sim.user_id)
    if not agent:
        return jsonify({"error": "Agent user not found."}), 404

    agent_wallet = Wallet.query.filter_by(user_id=agent.id).first()
    if not agent_wallet:
        return jsonify({"error": "Agent wallet not found"}), 404

    #Perform the float transfer
    hq_wallet.balance -= amount
    agent_wallet.balance += float(amount)
    # Record the transaction
    float_tx = Transaction(
        user_id=agent.id,
        amount=float(amount),  # If Transaction.amount is still Float
        transaction_type="float_received",
        status="completed",
        location=json.dumps(location),
        device_info=json.dumps(device_info),
        transaction_metadata=json.dumps({
            "from_admin": admin_id,
            "approved_by": "admin",
            "float_source": "HQ Wallet"
        }),
        fraud_flag=False,
        risk_score=0.0,
        tenant_id=1
    )
    db.session.add(float_tx)

    # Log to RealTimeLog
    rt_log = RealTimeLog(
        user_id=admin_id,
        action=f"💸 Funded agent {agent.first_name} ({agent_mobile}) with {amount} RWF from HQ Wallet",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent"),
        location=json.dumps(location),
        risk_alert=False,
        tenant_id=1
    )
    db.session.add(rt_log)

    db.session.commit()
    return jsonify({
        "message": f"✅ {amount} RWF successfully sent to {agent.first_name} ({agent_mobile})"
    }), 200

# HeadQuater's Balance
@admin_bp.route('/admin/hq-balance', methods=['GET'])
@jwt_required()
@session_protected()
@role_required(['admin'])
def get_hq_balance():
    hq_wallet = HeadquartersWallet.query.first()
    if not hq_wallet:
        return jsonify({"error": "HQ Wallet not found"}), 404

    return jsonify({"balance": round(hq_wallet.balance, 2)}), 200

@admin_bp.route('/admin/float-history', methods=['GET'])
@jwt_required()
@session_protected()
@role_required(['admin'])
def float_history():
    transactions = Transaction.query.filter_by(transaction_type='float_received').order_by(Transaction.timestamp.desc()).limit(20).all()
    result = []
    for tx in transactions:
        agent = User.query.get(tx.user_id)
        sim = SIMCard.query.filter_by(user_id=agent.id).first()
        result.append({
            "timestamp": tx.timestamp,
            "amount": tx.amount,
            "agent_name": f"{agent.first_name} {agent.last_name}",
            "agent_mobile": sim.mobile_number if sim else "N/A"
        })
    return jsonify({"transfers": result}), 200


# FLagged Transactions
@admin_bp.route('/admin/flagged-transactions', methods=['GET'])
@jwt_required()
@session_protected()
def get_flagged_transactions():
    flagged = Transaction.query.filter_by(fraud_flag=True).order_by(Transaction.timestamp.desc()).all()
    result = []
    for tx in flagged:
        user = User.query.get(tx.user_id)
        result.append({
            "id": tx.id,
            "user": f"{user.first_name} {user.last_name}",
            "amount": tx.amount,
            "type": tx.transaction_type,
            "risk_score": tx.risk_score,
            "status": tx.status,
            "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(result), 200


# Real time Logs
@admin_bp.route("/admin/real-time-logs", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def get_real_time_logs():
    logs = RealTimeLog.query.order_by(RealTimeLog.timestamp.desc()).limit(50).all()

    result = []
    for log in logs:
        result.append({
            "user": f"{log.user.first_name} {log.user.last_name}" if log.user else "Unknown",
            "action": log.action,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M"),
            "ip": log.ip_address,
            "location": log.location,
            "device": log.device_info,
            "risk_alert": log.risk_alert
        })

    return jsonify(result), 200


@admin_bp.route('/admin/user-auth-logs', methods=['GET'])
@jwt_required()
@session_protected()
def get_user_auth_logs():
    logs = UserAuthLog.query.order_by(UserAuthLog.auth_timestamp.desc()).limit(100).all()
    result = []
    for log in logs:
        user = User.query.get(log.user_id)
        result.append({
            "user": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "method": log.auth_method,
            "status": log.auth_status,
            "timestamp": log.auth_timestamp.strftime("%Y-%m-%d %H:%M"),
            "ip": log.ip_address,
            "device": log.device_info,
            "location": log.location,
            "fails": log.failed_attempts
        })
    return jsonify(result), 200

@admin_bp.route('/admin/unlock-user/<int:user_id>', methods=['PATCH'])
@jwt_required()
@session_protected()
@role_required(['admin'])
def unlock_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Unlock the user
    user.locked_until = None
    db.session.commit()

    # Log the action to RealTimeLog
    admin_id = get_jwt_identity()
    admin_user = User.query.get(admin_id)
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    rt_log = RealTimeLog(
        user_id=admin_id,
        action=f"🔓 Unlocked user account for {user.first_name} {user.last_name} ({mobile_number})",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location="Admin Panel",
        risk_alert=False,
        tenant_id=1
    )

    db.session.add(rt_log)
    db.session.commit()

    return jsonify({"message": "✅ User account unlocked"}), 200


# Admin View all transactions
@admin_bp.route("/admin/all-transactions", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def all_transactions():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    result = []

    for tx in transactions:
        user = db.session.get(User, tx.user_id)
        result.append({
            "id": tx.id,
            "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "transaction_type": tx.transaction_type,
            "amount": tx.amount,
            "status": tx.status,
            "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({"transactions": result}), 200




# ROUTE (cleaned + safe)
@admin_bp.route("/admin/reverse-transfer/<int:transaction_id>", methods=["POST"])
@jwt_required()
@session_protected()
@role_required(["admin"])
def reverse_transfer(transaction_id):
    transaction = Transaction.query.get(transaction_id)

    if not transaction or transaction.transaction_type != "transfer" or transaction.status != "completed":
        return jsonify({"error": "This transaction is not eligible for reversal."}), 400

    try:
        metadata = json.loads(transaction.transaction_metadata or "{}")
    except Exception as e:
        return jsonify({"error": "Invalid metadata", "details": str(e)}), 400

    existing_reversal = Transaction.query.filter(
        Transaction.transaction_type == "reversal",
        Transaction.transaction_metadata.contains(f'"reversal_of_transaction_id": {transaction.id}')
    ).first()

    if existing_reversal:
        return jsonify({"error": "This transaction has already been reversed."}), 400

    time_since_tx = datetime.utcnow() - transaction.timestamp
    if time_since_tx.total_seconds() > 86400:
        return jsonify({"error": "This transaction is too old to be reversed."}), 403

    sender_id = transaction.user_id
    recipient_id = metadata.get("recipient_id")
    if not recipient_id:
        return jsonify({"error": "Missing recipient info in metadata."}), 400

    sender_wallet = Wallet.query.filter_by(user_id=sender_id).first()
    recipient_wallet = Wallet.query.filter_by(user_id=recipient_id).first()

    if not sender_wallet or not recipient_wallet:
        return jsonify({"error": "One of the wallets is missing"}), 404

    if recipient_wallet.balance < transaction.amount:
        return jsonify({"error": "Recipient does not have sufficient balance for reversal"}), 400

    recipient_wallet.balance -= transaction.amount

    reversal_metadata = {
        "reversal_of_transaction_id": transaction.id,
        "original_sender": sender_id,
        "original_recipient": recipient_id,
        "reversed_by_admin": get_jwt_identity(),
        "delayed_refund": True
    }

    reversal = Transaction(
        user_id=sender_id,
        amount=transaction.amount,
        transaction_type="reversal",
        status="pending",
        transaction_metadata=json.dumps(reversal_metadata),
        timestamp=datetime.utcnow(),
        tenant_id=1
    )

    db.session.add(reversal)

    admin_user = db.session.get(User, get_jwt_identity())
    rt_log = RealTimeLog(
        user_id=admin_user.id,
        action=f"🔁 Reversal initiated: TX #{transaction.id} — {transaction.amount} RWF back to sender",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin HQ"),
        location="Headquarters",
        risk_alert=True,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    # 10-second test delay (increase in prod)
    app = current_app._get_current_object()
    print("Scheduling finalize_reversal in 10 seconds...")

    threading.Timer(10, finalize_reversal, args=(app, reversal.id, sender_wallet.id, transaction.amount)).start()

    return jsonify({
        "message": "✅ Reversal initiated. Refund will be processed shortly.",
        "reversed_transaction_id": reversal.id
    }), 200


# Admin Metrics
@admin_bp.route("/api/admin/metrics")
@jwt_required()
@session_protected()
def admin_dashboard_metrics():
    from flask import request
    from sqlalchemy import text
    from datetime import datetime, timedelta

    def daterange(start_date, end_date):
        for n in range((end_date - start_date).days + 1):
            yield start_date + timedelta(n)

    from_str = request.args.get("from")
    to_str = request.args.get("to")

    now = datetime.utcnow()
    default_from = (now - timedelta(days=7)).date()
    default_to = now.date()

    try:
        start_date = datetime.strptime(from_str, "%Y-%m-%d").date() if from_str else default_from
        end_date = datetime.strptime(to_str, "%Y-%m-%d").date() if to_str else default_to
    except Exception:
        return jsonify({"error": "Invalid date format"}), 400

    #Login method breakdown
    login_methods = {
        "password": UserAuthLog.query.filter_by(auth_method="password", auth_status="success").count(),
        "totp": UserAuthLog.query.filter_by(auth_method="totp", auth_status="success").count(),
        "webauthn": UserAuthLog.query.filter_by(auth_method="webauthn", auth_status="success").count()
    }

    # Authentication failures padded by day
    failures = (
        db.session.query(
            func.date(UserAuthLog.auth_timestamp).label('day'),
            func.count().label('count')
        )
        .filter(
            UserAuthLog.auth_status == 'failed',
            func.date(UserAuthLog.auth_timestamp) >= start_date,
            func.date(UserAuthLog.auth_timestamp) <= end_date
        )
        .group_by('day')
        .order_by('day')
        .all()
    )
    failure_dict = {r.day.strftime('%Y-%m-%d'): r.count for r in failures}
    padded_dates = [d.strftime('%Y-%m-%d') for d in daterange(start_date, end_date)]
    padded_counts = [failure_dict.get(d, 0) for d in padded_dates]
    auth_failures = {
        "dates": padded_dates,
        "counts": padded_counts
    }

    # Transaction source detection
    actor_query = text("""
        SELECT
            CASE
                WHEN transaction_metadata::json->>'initiated_by' = 'user' THEN 'user'
                WHEN transaction_metadata::json->>'transfer_by' = 'Agent' THEN 'agent'
                WHEN transaction_metadata::json->>'withdrawal_method' = 'Agent Processed' THEN 'agent'
                ELSE 'admin'
            END AS actor,
            COUNT(*) AS count
        FROM transactions
        GROUP BY actor
    """)
    actor_results = db.session.execute(actor_query)
    actor_counts = {row.actor: row.count for row in actor_results}
    transaction_sources = [
        actor_counts.get("user", 0),
        actor_counts.get("agent", 0),
        actor_counts.get("admin", 0)
    ]

    #  Flagged vs Clean transactions
    flagged = {
        "flagged": Transaction.query.filter(Transaction.risk_score >= 0.7).count(),
        "clean": Transaction.query.filter(Transaction.risk_score < 0.7).count()
    }

    # User states
    user_states = {
        "active": User.query.filter_by(is_active=True).count(),
        "inactive": User.query.filter_by(is_active=False).count(),
        "suspended": User.query.filter(User.locked_until != None).count(),
        "unverified": User.query.filter_by(identity_verified=False).count()
    }


    #  SIM stats (only if SIMCard model exists)
    sim_stats = {
        "new": SIMCard.query.filter(SIMCard.status == "active").count(),
        "swapped": SIMCard.query.filter(SIMCard.status == "swapped").count(),
        "suspended": SIMCard.query.filter(SIMCard.status == "suspended").count()
    }

    #  Anomaly detection
    multi_failures = (
        db.session.query(UserAuthLog.user_id, func.count().label("fail_count"))
        .filter(
            UserAuthLog.auth_status == "failed",
            UserAuthLog.auth_timestamp >= datetime.utcnow() - timedelta(days=1)
        )
        .group_by(UserAuthLog.user_id)
        .having(func.count() >= 3)
        .all()
    )
    flagged_users = (
        db.session.query(Transaction.user_id, func.count().label("flagged_count"))
        .filter(Transaction.risk_score >= 0.7)
        .group_by(Transaction.user_id)
        .having(func.count() >= 1)
        .all()
    )
    anomalies = {
        "multiple_failed_logins": [
            {"user_id": u.user_id, "count": u.fail_count} for u in multi_failures
        ],
        "frequent_flagged_users": [
            {"user_id": u.user_id, "count": u.flagged_count} for u in flagged_users
        ]
    }

    #  Heatmap logs (basic location-based grouping)
    logs = [
        {"location": log.location or "Unknown"}
        for log in RealTimeLog.query
        .filter(
            func.date(RealTimeLog.timestamp) >= start_date,
            func.date(RealTimeLog.timestamp) <= end_date
        )
        .limit(1000)
        .all()
    ]

    return jsonify({
        "login_methods": login_methods,
        "auth_failures": auth_failures,
        "transaction_sources": transaction_sources,
        "flagged": flagged,
        "user_states": user_states,
        "sim_stats": sim_stats,
        "anomalies": anomalies,
        "logs": logs
    })


# Tenants Registration
@admin_bp.route('/admin/register-tenant', methods=['POST'])
@jwt_required()
@session_protected()
def register_tenant():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    if not user_access:
        return jsonify({"error": "Unauthorized."}), 403

    user_role = UserRole.query.get(user_access.role_id)
    if not user_role or user_role.role_name.lower() != "admin":
        return jsonify({"error": "Only admins can register tenants."}), 403

    data = request.get_json()
    name = data.get('name')
    contact_email = data.get('contact_email')
    custom_api_key = data.get('api_key')
    admin_info = data.get("admin_user")

    if not name:
        return jsonify({"error": "Tenant name is required."}), 400
    if not contact_email:
        return jsonify({"error": "Contact email is required."}), 400
    if Tenant.query.filter_by(name=name).first():
        return jsonify({"error": "A tenant with this name already exists."}), 409

    from utils.security import generate_custom_api_key

    tenant_api_key = custom_api_key or generate_custom_api_key(name)

    # Step 1: Create the tenant
    new_tenant = Tenant(
        name=name,
        api_key=tenant_api_key,
        contact_email=contact_email
    )
    db.session.add(new_tenant)
    db.session.flush()  # So new_tenant.id is available

    # Step 2: Optionally create initial admin user
    if admin_info:
        required_fields = ['mobile_number', 'first_name', 'email', 'password']
        for field in required_fields:
            if not admin_info.get(field):
                return jsonify({"error": f"Admin user {field} is required."}), 400

        sim_card = SIMCard.query.filter_by(mobile_number=admin_info['mobile_number'], status="active").first()
        if not sim_card:
            return jsonify({"error": "Mobile number not valid or not active"}), 404

        linked_user = User.query.get(sim_card.user_id)
        if not linked_user:
            return jsonify({"error": "SIM not linked to any user"}), 404

        # Check if already exists under tenant
        if TenantUser.query.filter_by(tenant_id=new_tenant.id, user_id=linked_user.id).first():
            return jsonify({"error": "Admin user already exists under this tenant."}), 400
        from utils.security import is_strong_password
        # Validate password strength
        if not is_strong_password(admin_info['password']):
            return jsonify({"error": "Admin password does not meet security requirements."}), 400

        # Create TenantUser
        tenant_user = TenantUser(
            tenant_id=new_tenant.id,
            user_id=linked_user.id,
            company_email=admin_info['email'],
            password_hash=generate_password_hash(admin_info['password'])
        )
        db.session.add(tenant_user)

        # Ensure 'admin' role exists for this tenant
        admin_role = UserRole.query.filter_by(role_name='admin', tenant_id=new_tenant.id).first()
        if not admin_role:
            admin_role = UserRole(role_name='admin', tenant_id=new_tenant.id)
            db.session.add(admin_role)
            db.session.flush()

        # Assign access
        access = UserAccessControl(
            user_id=linked_user.id,
            role_id=admin_role.id,
            access_level="full",
            tenant_id=new_tenant.id
        )
        db.session.add(access)

        # Log this action
        db.session.add(RealTimeLog(
            user_id=linked_user.id,
            action=f"🆕 Initial Admin User Registered for Tenant: {name}",
            ip_address=request.remote_addr,
            device_info=request.user_agent.string,
            location=get_ip_location(request.remote_addr),
            tenant_id=new_tenant.id,
            risk_alert=False
        ))

    # Log tenant registration (initiator = platform admin)
    db.session.add(RealTimeLog(
        user_id=user.id,
        action=f"🏢 Registered new Tenant: {name}",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        tenant_id=new_tenant.id
    ))

    db.session.commit()

    # Email API key to tenant
    email_sent = False
    try:
        send_tenant_api_key_email(name, tenant_api_key, contact_email)
        email_sent = True
    except Exception as e:
        print(f"❌ Email delivery failed: {e}")

    return jsonify({
        "message": "Tenant and Admin registered successfully.",
        "tenant_id": new_tenant.id,
        "api_key": tenant_api_key,
        "email_sent": email_sent
    }), 201



#Rotate Tenant API Key
@admin_bp.route('/admin/rotate-api-key/<int:tenant_id>', methods=['POST'])
@jwt_required()
@session_protected()
def rotate_api_key(tenant_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user:
        return jsonify({"error": "Unauthorized"}), 403

    tenant = Tenant.query.get(tenant_id)
    if not tenant or tenant.name.lower() == "dummytenant":
        return jsonify({"error": "Cannot rotate key for this tenant."}), 403

    from utils.security import generate_custom_api_key
    old_key = tenant.api_key
    new_key = generate_custom_api_key(tenant.name)

    tenant.api_key = new_key
    tenant.api_key_rotated_at = datetime.utcnow()

    db.session.add(RealTimeLog(
        user_id=admin_user.id,
        action=f"🔁 Rotated API Key for Tenant: {tenant.name}",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        tenant_id=tenant.id
    ))

    db.session.commit()

    try:
        send_rotated_api_key_email(tenant.name, new_key, tenant.contact_email)
    except Exception as e:
        print(f"❌ Failed to send rotated API key to tenant contact: {e}")

    return jsonify({"message": "API key rotated successfully."}), 200


@admin_bp.route('/admin/tenants', methods=['GET'])
@jwt_required()
@session_protected()
def list_tenants():
    # Exclude the Master Tenant from the list
    tenants = Tenant.query.filter(Tenant.name != "Master Tenant").order_by(Tenant.created_at.desc()).all()
    
    return jsonify([
        {
            "id": t.id,
            "name": t.name,
            "contact_email": t.contact_email,
            "plan": t.plan,
            "is_active": t.is_active,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "last_api_access": t.last_api_access.strftime("%Y-%m-%d %H:%M:%S") if t.last_api_access else None,
            "api_score": float(t.api_score) if t.api_score is not None else 0.0,
        } for t in tenants
    ])

@admin_bp.route('/admin/toggle-tenant/<int:tenant_id>', methods=['POST'])
@jwt_required()
@session_protected()
def toggle_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    tenant.is_active = not tenant.is_active
    db.session.commit()
    return jsonify({"message": f"Tenant {'enabled' if tenant.is_active else 'suspended'}."})

from utils.admin_tools import delete_tenant_cascade
from utils.logger import app_logger

@admin_bp.route('/admin/delete-tenant/<int:tenant_id>', methods=['DELETE'])
@jwt_required()
@session_protected()
def delete_tenant(tenant_id):
    result, status = delete_tenant_cascade(tenant_id, logger=app_logger)
    return jsonify(result), status

@admin_bp.route('/admin/update-tenant/<int:tenant_id>', methods=['PUT'])
@jwt_required()
@session_protected()
def update_tenant(tenant_id):
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_access = UserAccessControl.query.filter_by(user_id=user.id).first()
    user_role = UserRole.query.get(user_access.role_id) if user_access else None
    if not user_role or user_role.role_name.lower() != "admin":
        return jsonify({"error": "Only admins can update tenants."}), 403

    tenant = Tenant.query.get(tenant_id)
    if not tenant or tenant.name.lower() == "mastertenant":
        return jsonify({"error": "Tenant not found or not editable."}), 404

    data = request.get_json()
    new_email = data.get("contact_email")
    new_plan = data.get("plan")

    plan_changed = False
    if new_email:
        tenant.contact_email = new_email.strip()
    if new_plan and new_plan.strip().lower() != tenant.plan.lower():
        tenant.plan = new_plan.strip().lower()
        plan_changed = True

    # Automatically upgrade settings if plan changed
    if plan_changed:
        if tenant.plan == "premium":
            tenant.api_key_expires_at = datetime.utcnow() + timedelta(days=90)
        elif tenant.plan == "enterprise":
            tenant.api_key_expires_at = datetime.utcnow() + timedelta(days=365)
        else:  # fallback for 'free' or unknown plans
            tenant.api_key_expires_at = None  # or set a shorter duration if you wish

        # Optional: Reset abuse tracking for fresh start on plan upgrade
        tenant.api_score = 0.0
        tenant.api_request_count = 0
        tenant.api_error_count = 0
        tenant.api_last_reset = datetime.utcnow()

    db.session.commit()

    return jsonify({"message": "Tenant updated successfully."}), 200


# Reset a tenant's API trust score and unsuspend
@admin_bp.route('/admin/reset-trust-score/<int:tenant_id>', methods=['POST'])
@jwt_required()
@session_protected()
@role_required(["admin"])
def reset_trust_score(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404

    tenant.api_score = 0.0
    tenant.api_error_count = 0
    tenant.api_request_count = 0
    tenant.api_last_reset = datetime.utcnow()
    tenant.is_active = True  # Optionally reactivate
    db.session.commit()

    # Log it
    db.session.add(RealTimeLog(
        user_id=get_jwt_identity(),
        tenant_id=tenant.id,
        action=f"🔁 Trust score reset for tenant: {tenant.name}",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr)
    ))
    db.session.commit()

    return jsonify({"message": f"Trust score reset for {tenant.name}."}), 200


@admin_bp.route("/admin/tenant-details/<int:tenant_id>")
@jwt_required()
@session_protected()
@role_required(["admin"])
def get_tenant_details(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    data = {
        "id": tenant.id,
        "name": tenant.name,
        "contact_email": tenant.contact_email,
        "plan": tenant.plan,
        "created_at": tenant.created_at.isoformat(),
        "last_api_access": tenant.last_api_access.isoformat() if tenant.last_api_access else "Never",
        "api_key_expires_at": tenant.api_key_expires_at.isoformat() if tenant.api_key_expires_at else "Never",
        "api_request_count": tenant.api_request_count,
        "api_error_count": tenant.api_error_count,
        "api_score": round(tenant.api_score or 0.0, 2),
        "is_active": tenant.is_active
    }
    return jsonify(data), 200
