from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models.models import db, User, UserAccessControl, UserRole, Wallet, Transaction, UserAuthLog, SIMCard, RealTimeLog, HeadquartersWallet
import random
import json
import threading
from datetime import datetime
from threading import Timer
from utils.auth_decorators import require_full_mfa


admin_bp = Blueprint("admin", __name__)

# ✅ FINALIZE FUNCTION (move this OUTSIDE any route)
def finalize_reversal(app, reversal_id, sender_wallet_id, amount):
    try:
        with app.app_context():
            print("🧠 finalize_reversal() running...")

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
                risk_alert=False
            )

            db.session.add(completion_log)
            db.session.commit()

            print(f"✅ TX #{reversal_id} refunded {amount} to sender.")

    except Exception as e:
        print(f"❌ finalize_reversal() crashed: {e}")

#Admin Dashboard
@admin_bp.route('/admin/dashboard')
@jwt_required()
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


# ✅ List all users (Admin Only)
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_all_users():
    """Only admins can view all users"""
    try:
        users = User.query.all()
        users_list = []

        for u in users:
            primary_sim = SIMCard.query.filter_by(user_id=u.id, status="active").first()

            user_role = UserRole.query.get(u.user_access_control.role_id) if u.user_access_control else None
            role_name = user_role.role_name if user_role else "N/A"

            # ✅ Check if user is locked
            is_locked = u.locked_until is not None and u.locked_until > datetime.utcnow()

            users_list.append({
                "id": u.id,
                "name": f"{u.first_name} {u.last_name or ''}".strip(),
                "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",
                "email": u.email,
                "role": role_name,
                "is_locked": u.locked_until is not None and u.locked_until > datetime.utcnow(),
                "locked_until": u.locked_until.isoformat() if u.locked_until else None  # ✅ NEW
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

    current_user_id = get_jwt_identity()

    # 🚫 Prevent self-suspension
    if current_user_id == user_id:
        return jsonify({"error": "Admins are not allowed to suspend their own accounts."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 🔒 Suspend user and flag for deletion
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

    current_user_id = get_jwt_identity()

    # 🚫 Prevent self-deletion
    if current_user_id == user_id:
        return jsonify({"error": "Admins are not allowed to delete their own accounts."}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.deletion_requested:
        return jsonify({"error": "User has not requested account deletion."}), 400

    # ✅ Fetch user's SIM card before deleting
    user_sim = SIMCard.query.filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    # Delete related records to maintain database integrity
    Wallet.query.filter_by(user_id=user_id).delete()
    Transaction.query.filter_by(user_id=user_id).delete()
    UserAuthLog.query.filter_by(user_id=user_id).delete()
    SIMCard.query.filter_by(user_id=user_id).delete()
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

# Sending froats to agents
@admin_bp.route('/admin/fund-agent', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def fund_agent():
    data = request.get_json()
    admin_id = get_jwt_identity()

    agent_mobile = data.get('agent_mobile')
    amount = data.get('amount')
    device_info = data.get('device_info')
    location = data.get('location')

    if not agent_mobile or not amount:
        return jsonify({"error": "Missing agent mobile or amount."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Invalid amount."}), 400
    except:
        return jsonify({"error": "Amount must be a number."}), 400

    # ✅ Use HeadquartersWallet instead of admin's personal wallet
    hq_wallet = HeadquartersWallet.query.first()
    if not hq_wallet or hq_wallet.balance < amount:
        return jsonify({"error": "Insufficient HQ funds"}), 400

    # ✅ Find the agent and their wallet
    agent_sim = SIMCard.query.filter_by(mobile_number=agent_mobile).first()
    if not agent_sim or not agent_sim.user_id:
        return jsonify({"error": "Agent SIM is not assigned to any user."}), 400

    agent = User.query.get(agent_sim.user_id)
    if not agent:
        return jsonify({"error": "Agent user not found."}), 404


    agent = User.query.get(agent_sim.user_id)
    agent_wallet = Wallet.query.filter_by(user_id=agent.id).first()
    if not agent_wallet:
        return jsonify({"error": "Agent wallet not found"}), 404

    # 💸 Perform the transfer
    hq_wallet.balance -= amount
    agent_wallet.balance += amount

    # 🧾 Record the transaction
    float_tx = Transaction(
    user_id=agent.id,
    amount=amount,
    transaction_type="float_received",
    status="completed",
    location=json.dumps(location),         # ✅ serialized
    device_info=json.dumps(device_info),   # ✅ serialized
    transaction_metadata=json.dumps({
        "from_admin": admin_id,
        "approved_by": "admin",
        "float_source": "HQ Wallet"
    }),
    fraud_flag=False,
    risk_score=0.0
)
    db.session.add(float_tx)
    db.session.commit()

    return jsonify({
        "message": f"✅ {amount} RWF successfully sent to {agent.first_name} ({agent_mobile})"
    }), 200

# HeadQuater's Balance
@admin_bp.route('/admin/hq-balance', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_hq_balance():
    hq_wallet = HeadquartersWallet.query.first()
    if not hq_wallet:
        return jsonify({"error": "HQ Wallet not found"}), 404

    return jsonify({"balance": round(hq_wallet.balance, 2)}), 200

@admin_bp.route('/admin/float-history', methods=['GET'])
@jwt_required()
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
def get_user_auth_logs():
    logs = UserAuthLog.query.order_by(UserAuthLog.auth_timestamp.desc()).limit(50).all()
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
def unlock_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.locked_until = None
    db.session.commit()

    return jsonify({"message": "✅ User account unlocked"}), 200

# Admin View all transactions
@admin_bp.route("/admin/all-transactions", methods=["GET"])
@jwt_required()
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




# ✅ ROUTE (cleaned + safe)
@admin_bp.route("/admin/reverse-transfer/<int:transaction_id>", methods=["POST"])
@jwt_required()
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
        timestamp=datetime.utcnow()
    )

    db.session.add(reversal)

    admin_user = db.session.get(User, get_jwt_identity())
    rt_log = RealTimeLog(
        user_id=admin_user.id,
        action=f"🔁 Reversal initiated: TX #{transaction.id} — {transaction.amount} RWF back to sender",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Admin HQ"),
        location="Headquarters",
        risk_alert=True
    )
    db.session.add(rt_log)
    db.session.commit()

    # ✅ 10-second test delay (increase in prod)
    app = current_app._get_current_object()
    print("🌀 Scheduling finalize_reversal in 10 seconds...")

    threading.Timer(10, finalize_reversal, args=(app, reversal.id, sender_wallet.id, transaction.amount)).start()

    return jsonify({
        "message": "✅ Reversal initiated. Refund will be processed shortly.",
        "reversed_transaction_id": reversal.id
    }), 200

