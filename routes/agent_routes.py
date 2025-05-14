from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Wallet, Transaction, SIMCard, UserAccessControl, UserRole, RealTimeLog, TenantUser, Tenant, PendingSIMSwap
from utils.decorators import role_required,session_protected
import random
import json
from datetime import datetime, timedelta
from utils.auth_decorators import require_full_mfa
from utils.decorators import session_protected
import secrets
import hashlib
from utils.email_alerts import send_sim_swap_verification_email


agent_bp = Blueprint("agent", __name__)

# A function to generate a unique mobile number
def generate_unique_mobile_number(network_provider):
    """Generate a mobile number based on the selected network provider."""
    prefix = "078" if network_provider == "MTN" else "073"  # MTN → 078, Airtel → 073

    while True:
        new_number = prefix + str(random.randint(1000000, 9999999))  # Ensures 10-digit number
        existing_number = SIMCard.query.filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number

# A function to generate a unique SIM Serial Number (ICCID)
def generate_unique_iccid():
    """Generate a unique SIM Serial Number (ICCID)."""
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = SIMCard.query.filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid


#✅ Function to control transaction life time
WITHDRAWAL_EXPIRY_MINUTES = 5  # Make sure it's the same as the one used in approval route

def expire_pending_withdrawals():
    now = datetime.utcnow()
    expired_count = 0

    pending = Transaction.query.filter_by(
        transaction_type="withdrawal",
        status="pending"
    ).all()

    for tx in pending:
        if tx.timestamp and now - tx.timestamp > timedelta(minutes=WITHDRAWAL_EXPIRY_MINUTES):
            tx.status = "expired"
            expired_count += 1

    if expired_count > 0:
        db.session.commit()
    return expired_count

# ✅ Function to generate a new sim card
@agent_bp.route("/agent/generate_sim", methods=["POST"])
@jwt_required()
@session_protected()
def generate_sim():
    """Generate a unique SIM number and ICCID but do not register it yet."""
    data = request.get_json()
    network_provider = data.get("network_provider")

    if not network_provider:
        return jsonify({"success": False, "error": "❌ Network provider is required."}), 400

    if network_provider not in ["MTN", "Airtel"]:
        return jsonify({"success": False, "error": "❌ Invalid network provider. Choose MTN or Airtel."}), 400

    # ✅ Generate unique mobile number & ICCID
    mobile_number = generate_unique_mobile_number(network_provider)
    iccid = generate_unique_iccid()

    return jsonify({
        "success": True,
        "message": f"✅ {network_provider} SIM generated successfully!",
        "mobile_number": mobile_number,
        "iccid": iccid
    }), 200


# ✅ API: Register SIM Card (Agents Only)
@agent_bp.route("/agent/register_sim", methods=["POST"])
@jwt_required()
@session_protected()
def register_sim():
    logged_in_user = get_jwt_identity()
    agent = User.query.get(logged_in_user)

    # ✅ Check if the user is an agent
    user_access = UserAccessControl.query.filter_by(user_id=logged_in_user).first()
    if not user_access:
        return jsonify({"success": False, "error": "❌ Unauthorized. Agent role required."}), 403

    user_role = UserRole.query.get(user_access.role_id)
    if not user_role or user_role.role_name != "agent":
        return jsonify({"success": False, "error": "❌ Unauthorized. Only agents can register SIMs."}), 403

    data = request.get_json()
    iccid = data.get("iccid")
    mobile_number = data.get("mobile_number")
    network_provider = data.get("network_provider")

    if not iccid or not mobile_number or not network_provider:
        return jsonify({"success": False, "error": "❌ Missing required SIM details."}), 400

    if network_provider not in ["MTN", "Airtel"]:
        return jsonify({"success": False, "error": "❌ Invalid network provider. Choose MTN or Airtel."}), 400

    # ✅ Ensure the ICCID is unique before saving
    existing_sim = SIMCard.query.filter_by(iccid=iccid).first()
    if existing_sim:
        return jsonify({"success": False, "error": "❌ This ICCID is already registered."}), 400

    # ✅ Save the SIM with the agent's `user_id`
    new_sim = SIMCard(
        iccid=iccid,
        mobile_number=mobile_number,
        network_provider=network_provider,
        status="unregistered",
        registered_by=agent.id
    )

    db.session.add(new_sim)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"✅ {network_provider} SIM registered successfully!",
        "mobile_number": new_sim.mobile_number,
        "iccid": new_sim.iccid
    }), 201


# ✅ API: Fetch SIM Registration History
@agent_bp.route("/agent/sim-registrations", methods=["GET"])
@jwt_required()
@session_protected()
def fetch_sim_registration_history():
    agent_id = get_jwt_identity()

    # ✅ Fetch only SIMs registered by the agent
    sims = SIMCard.query.filter_by(registered_by=agent_id).order_by(SIMCard.registration_date.desc()).all()

    sim_list = []
    for sim in sims:
        # ✅ Determine status color class
        if sim.status == "active":
            status_class = "text-success"
        elif sim.status == "suspended":
            status_class = "text-danger"
        elif sim.status == "swapped":
            status_class = "text-warning"
        else:
            status_class = "text-muted"

        # ✅ If the SIM was swapped, show the real current mobile number
        if sim.mobile_number.startswith("SWP_") and sim.user_id:
            active_sim = SIMCard.query.filter_by(user_id=sim.user_id, status="active").first()
            display_mobile = active_sim.mobile_number if active_sim else sim.mobile_number
        else:
            display_mobile = sim.mobile_number

        sim_list.append({
            "iccid": sim.iccid,
            "mobile_number": display_mobile,
            "network_provider": sim.network_provider,
            "status": sim.status,
            "status_class": status_class,
            "timestamp": sim.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
            "registered_user": f"{sim.user.first_name} {sim.user.last_name}" if sim.user else "Not Linked"
        })

    return jsonify({"sims": sim_list}), 200




# ✅ Agent Dashboard (HTML Page)
@agent_bp.route("/agent/dashboard", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["agent"])
@require_full_mfa
def agent_dashboard():
    """Render Agent Dashboard"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return render_template("agent_dashboard.html", user=user)

# ✅ Agent Transaction
@agent_bp.route("/agent/transaction", methods=["POST"])
@jwt_required()
@session_protected()
@role_required(["agent"])
def process_agent_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    transaction_type = data.get("transaction_type")
    recipient_mobile = data.get("recipient_mobile", None)

    if not transaction_type:
        return jsonify({"error": "Transaction type is required"}), 400

    agent = db.session.get(User, user_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    agent_wallet = Wallet.query.filter_by(user_id=agent.id).first()
    if not agent_wallet:
        return jsonify({"error": "Agent wallet not found"}), 404

    from utils.totp import verify_totp_code
    totp_code = data.get("totp")
    if not totp_code:
        return jsonify({"error": "TOTP code is required"}), 400

    if not agent.otp_secret:
        return jsonify({"error": "TOTP not configured for this agent"}), 403

    if not verify_totp_code(agent.otp_secret, totp_code):
        return jsonify({"error": "Invalid or expired TOTP code"}), 401

    transaction_metadata = {}
    rt_log = None

    if transaction_type == "deposit":
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile is required for deposits"}), 400

        recipient_sim = SIMCard.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            return jsonify({"error": "Recipient SIM not found"}), 404

        recipient = User.query.get(recipient_sim.user_id)
        if not recipient:
            return jsonify({"error": "Recipient user not found"}), 404

        recipient_wallet = Wallet.query.filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        if recipient.id == agent.id:
            return jsonify({"error": "Agents cannot deposit into their own accounts"}), 403

        if agent_wallet.balance < amount:
            return jsonify({"error": "Insufficient balance for deposit"}), 400

        print(f"✅ Agent deposit: {amount} RWF to {recipient.first_name} ({recipient_mobile})")
        agent_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = {
            "deposited_by_mobile": agent.sim_cards[0].mobile_number if agent.sim_cards else "N/A",
            "recipient_mobile": recipient_mobile,
            "recipient_name": f"{recipient.first_name} {recipient.last_name}"
        }

        new_transaction = Transaction(
            user_id=recipient.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"🧾 Agent deposited {amount} RWF to {recipient.first_name} ({recipient_mobile})",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=data.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1
        )

    elif transaction_type == "transfer":
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile is required for transfers"}), 400

        recipient_sim = SIMCard.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            return jsonify({"error": "Recipient SIM not found"}), 404

        recipient = User.query.get(recipient_sim.user_id)
        if not recipient:
            return jsonify({"error": "Recipient user not found"}), 404

        recipient_wallet = Wallet.query.filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        if agent_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        print(f"✅ Agent transfer: {amount} RWF to {recipient.first_name} ({recipient_mobile})")
        agent_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = {
            "transfer_by": "Agent",
            "recipient_mobile": recipient_mobile,
            "recipient_name": f"{recipient.first_name} {recipient.last_name}"
        }

        new_transaction = Transaction(
            user_id=agent.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"🔁 Agent transferred {amount} RWF to {recipient.first_name} ({recipient_mobile})",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=data.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1
        )

    elif transaction_type == "withdrawal":
        if agent_wallet.balance < amount:
            return jsonify({"error": "Insufficient balance"}), 400

        print(f"✅ Agent withdrawal: {amount} RWF")
        agent_wallet.balance -= amount

        transaction_metadata = {
            "withdrawal_method": "Agent Processed"
        }

        new_transaction = Transaction(
            user_id=agent.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"💸 Agent withdrew {amount} RWF from own float",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=data.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1
        )

    else:
        return jsonify({"error": "Invalid transaction type"}), 400

    # ✅ Commit Transaction and Real-Time Log
    db.session.add(new_transaction)
    if rt_log:
        db.session.add(rt_log)
    db.session.commit()

    return jsonify({
        "message": f"{transaction_type.capitalize()} successful",
        "updated_balance": (
            agent_wallet.balance if transaction_type != "deposit" else recipient_wallet.balance
        ),
        "recipient_mobile": recipient_mobile if transaction_type != "withdrawal" else None,
        "recipient_name": transaction_metadata.get("recipient_name", "N/A")
    }), 200


# ✅ API: Fetch Agent's Transaction History
@agent_bp.route('/agent/transactions', methods=['GET'])
@jwt_required()
@session_protected()
@role_required(['agent'])
def get_agent_transactions():
    agent_id = int(get_jwt_identity())

    # ✅ Get all SIMs (active + swapped) for historical tracking
    agent_sims = SIMCard.query.filter(
        SIMCard.user_id == agent_id,
        SIMCard.status.in_(["active", "swapped"])
    ).all()
    agent_mobiles = [sim.mobile_number for sim in agent_sims if sim.mobile_number]

    # ✅ Query transactions agent is involved in
    transactions = Transaction.query.filter(
        db.or_(
            Transaction.user_id == agent_id,
            Transaction.transaction_metadata.contains(f'"assigned_agent_id": {agent_id}'),
            *[
                Transaction.transaction_metadata.contains(f'"deposited_by_mobile": "{mobile}"')
                for mobile in agent_mobiles
            ]
        )
    ).order_by(Transaction.timestamp.desc()).all()

    transaction_list = []
    for tx in transactions:
        try:
            metadata = json.loads(tx.transaction_metadata or "{}")

            # ✅ Determine if agent was involved
            involved = False
            if tx.user_id == agent_id:
                involved = True
            elif metadata.get("assigned_agent_id") and int(metadata.get("assigned_agent_id")) == agent_id:
                involved = True
            elif metadata.get("deposited_by_mobile") in agent_mobiles:
                involved = True

            if not involved:
                continue

            # ✅ Determine recipient mobile
            if tx.transaction_type in ["deposit", "transfer"]:
                recipient_mobile = metadata.get("recipient_mobile", "N/A")
            elif tx.transaction_type == "withdrawal":
                recipient_user_id = tx.user_id
                active_sim = SIMCard.query.filter_by(user_id=recipient_user_id, status="active").first()
                recipient_mobile = active_sim.mobile_number if active_sim else "N/A"
            else:
                recipient_mobile = "Self"

            # ✅ Build descriptive label
            admin_msg = metadata.get("admin_message")
            if tx.transaction_type == "withdrawal":
                if tx.status == "pending":
                    label = "User Withdrawal Pending Approval"
                elif tx.status == "rejected":
                    label = "User Withdrawal Rejected"
                elif tx.status == "expired":
                    label = "User Withdrawal Expired"
                else:
                    label = "User Withdrawal Approved"
            elif tx.transaction_type == "float":
                label = f"Float from Admin: {admin_msg}" if admin_msg else "Float from Admin"
            elif tx.transaction_type == "transfer" and tx.user_id == agent_id:
                label = f"Transfer to {recipient_mobile}"
            elif tx.transaction_type == "transfer":
                label = f"Transfer from {recipient_mobile}"
            elif tx.transaction_type == "deposit":
                label = f"Deposit to {recipient_mobile}"
            else:
                label = tx.transaction_type.capitalize()

            # ✅ Determine status class for UI
            status_class = ""
            if tx.status == "rejected":
                status_class = "text-danger"
            elif tx.status == "pending":
                status_class = "text-warning"
            elif tx.status == "completed":
                status_class = "text-success"
            elif tx.status == "expired":
                status_class = "text-muted"

            # ✅ Final output structure
            transaction_list.append({
                "transaction_id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "label": label,
                "status": tx.status,
                "status_class": status_class,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "recipient_mobile": recipient_mobile
            })

        except Exception as e:
            print(f"❌ Error processing transaction ID {tx.id}: {e}")
            continue

    return jsonify({"transactions": transaction_list}), 200



# ✅ API: Fetch Agent Wallet Info
@agent_bp.route("/agent/wallet", methods=["GET"])
@jwt_required()
@session_protected()
@role_required(["agent"])
def agent_wallet():
    """Return agent's wallet balance, ensuring deposits are restricted"""
    user_id = get_jwt_identity()
    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    return jsonify({
        "balance": wallet.balance,
        "currency": wallet.currency,
        "can_deposit": False  # ✅ Agents cannot deposit into their own wallets
    }), 200


# ✅ API: Fetch Agent Dashboard Data (Transactions + SIM Registrations Count)
@agent_bp.route("/agent/dashboard/data", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_dashboard_data():
    """Return JSON data for agent dashboard, ensuring deposits into user accounts are counted."""
    agent_id = get_jwt_identity()
    agent = db.session.get(User, agent_id)

    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    # ✅ Count transactions made by this agent (withdrawal, transfer, deposits into user accounts)
    total_transactions = Transaction.query.filter(
        (Transaction.user_id == agent.id) | 
        (Transaction.transaction_metadata.like(f'%\"deposited_by\": \"Agent\", \"agent_id\": {agent.id}%'))
    ).count()

    # ✅ Get total SIMs registered by this agent
    total_sims = SIMCard.query.filter_by(registered_by=str(agent.id)).count()

    # ✅ Get total deposits made BY THE AGENT into user accounts
    total_deposits = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == "deposit",
        Transaction.transaction_metadata.like(f'%\"deposited_by\": \"Agent\", \"agent_id\": {agent.id}%')
    ).scalar() or 0

    # ✅ Get total withdrawals by the agent
    total_withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == agent.id,
        Transaction.transaction_type == "withdrawal"
    ).scalar() or 0

    # ✅ Get total transfers by the agent
    total_transfers = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == agent.id,
        Transaction.transaction_type == "transfer"
    ).scalar() or 0

    return jsonify({
        "total_transactions": total_transactions,
        "total_sims": total_sims,
        "total_deposits": total_deposits,  # ✅ Now counts deposits made by agents
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers
    }), 200



# ✅ API: Fetch Agent Profile (Ensure Name is Returned)
@agent_bp.route('/agent/profile', methods=['GET'])
@jwt_required()
@role_required(["agent"])
def agent_profile():
    """Fetch agent profile data, ensuring mobile number is fetched correctly"""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Fetch the most recently assigned SIM card for the agent
    latest_sim = SIMCard.query.filter_by(user_id=user.id).order_by(SIMCard.registration_date.desc()).first()
    mobile_number = latest_sim.mobile_number if latest_sim else "Not Assigned"  # ✅ Fix: Fetch mobile from SIMCard

    return jsonify({
        "id": user.id,
        "mobile_number": mobile_number,  # ✅ Fetch mobile from SIMCard
        "first_name": user.first_name or "Unknown",
        "last_name": user.last_name or "",
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "country": user.country or "N/A",
        "identity_verified": user.identity_verified,
        "role": "agent"
    }), 200


@agent_bp.route("/agent/view_sim/<iccid>", methods=["GET"])
@jwt_required()
def view_sim(iccid):
    sim = SIMCard.query.filter_by(iccid=iccid).first()
    if not sim:
        return jsonify({"error": "SIM not found"}), 404

    return jsonify({
        "iccid": sim.iccid,
        "mobile_number": sim.mobile_number,
        "network_provider": sim.network_provider,
        "status": sim.status,
        "registration_date": sim.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
    }), 200


@agent_bp.route("/agent/activate_sim", methods=["POST"])
@jwt_required()
@session_protected()
def activate_sim():
    
    data = request.get_json()
    iccid = data.get("iccid")

    sim = SIMCard.query.filter_by(iccid=iccid).first()
    if not sim:
        return jsonify({"error": "SIM not found"}), 404

    sim.status = "active"
    db.session.commit()

    # ✅ Log the SIM activation to RealTimeLog
    agent_id = get_jwt_identity()
    
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"📲 Activated SIM ICCID: {iccid}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=data.get("location", "Unknown"),
        risk_alert=False,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({"message": "✅ SIM activated successfully!"}), 200



@agent_bp.route("/agent/suspend_sim", methods=["POST"])
@jwt_required()
def suspend_sim():
    data = request.get_json()
    iccid = data.get("iccid")

    sim = SIMCard.query.filter_by(iccid=iccid).first()
    if not sim:
        return jsonify({"error": "SIM not found"}), 404

    sim.status = "suspended"
    db.session.commit()

    # ✅ Log to RealTimeLog
    agent_id = get_jwt_identity()
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"⚠️ Suspended SIM ICCID: {iccid}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=data.get("location", "Unknown"),
        risk_alert=True,  # 🚨 Mark as sensitive
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({"message": "⚠️ SIM suspended successfully!"}), 200

# Reactivate sim
@agent_bp.route("/agent/reactivate_sim", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def reactivate_sim():
    data = request.get_json()
    iccid = data.get("iccid")

    sim = SIMCard.query.filter_by(iccid=iccid).first()
    if not sim:
        return jsonify({"error": "SIM not found"}), 404

    if sim.status != "suspended":
        return jsonify({"error": "Only suspended SIMs can be re-activated"}), 400

    sim.status = "active"
    db.session.commit()

    # ✅ Log the action
    agent_id = get_jwt_identity()
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"🔄 Re-activated suspended SIM ICCID: {iccid}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=data.get("location", "Unknown"),
        risk_alert=False,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({"message": "🔄 SIM re-activated successfully!"}), 200


@agent_bp.route("/agent/delete_sim", methods=["DELETE"])
@jwt_required()
def delete_sim():
    data = request.get_json()
    iccid = data.get("iccid")

    sim = SIMCard.query.filter_by(iccid=iccid).first()
    if not sim:
        return jsonify({"error": "SIM not found"}), 404

    if sim.status != "unregistered":
        return jsonify({"error": "Cannot delete an activated SIM."}), 400

    db.session.delete(sim)
    db.session.commit()

    # ✅ Log SIM deletion in RealTimeLog
    agent_id = get_jwt_identity()
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"🗑️ Deleted SIM ICCID: {iccid}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location=data.get("location", "Unknown"),
        risk_alert=True,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({"message": "🗑️ SIM deleted successfully!"}), 200


# ✅ AGENT VIEWS PENDING WITHDRAWALS 
@agent_bp.route("/agent/pending-withdrawals", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def get_pending_withdrawals():
    agent_id = int(get_jwt_identity())

    pending_withdrawals = Transaction.query.filter_by(
        transaction_type="withdrawal",
        status="pending"
    ).order_by(Transaction.timestamp.desc()).all()

    result = []
    for tx in pending_withdrawals:
        try:
            metadata = json.loads(tx.transaction_metadata or "{}")
            assigned_agent_id_raw = metadata.get("assigned_agent_id")

            assigned_agent_id = int(assigned_agent_id_raw) if assigned_agent_id_raw is not None else -1

            print(f"🧾 Transaction ID: {tx.id}")
            print(f"🔑 Assigned Agent ID in Metadata: {assigned_agent_id} (type: {type(assigned_agent_id)})")
            print(f"👤 Logged-in Agent ID: {agent_id} (type: {type(agent_id)})")

            if assigned_agent_id != agent_id:
                print("⛔ Skipping — this withdrawal is not assigned to this agent.\n")
                continue  # 🔐 Do not show unassigned transactions

            user = User.query.get(tx.user_id)

            result.append({
                "transaction_id": tx.id,
                "amount": tx.amount,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "user_id": user.id if user else None,
                "agent_mobile": metadata.get("assigned_agent_mobile"),
                "metadata": metadata
            })

            print("✅ Included in result ✅\n")

        except Exception as e:
            print(f"❌ Skipping transaction ID {tx.id}: Metadata parsing error - {e}")
            continue

    return jsonify({"pending_withdrawals": result}), 200
    

# ✅ AGENT APPROVES WITHDRAWAL
@agent_bp.route("/agent/approve-withdrawal/<int:transaction_id>", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def approve_user_withdrawal(transaction_id):
    agent_id = int(get_jwt_identity())
    transaction = Transaction.query.get(transaction_id)

    if not transaction or transaction.transaction_type != "withdrawal" or transaction.status != "pending":
        return jsonify({"error": "Invalid or already processed withdrawal request"}), 400

    metadata = json.loads(transaction.transaction_metadata or "{}")
    assigned_agent_id = int(metadata.get("assigned_agent_id", -1))

    if assigned_agent_id != agent_id:
        return jsonify({"error": "You are not authorized to approve this withdrawal"}), 403

    now = datetime.utcnow()
    if transaction.timestamp and now - transaction.timestamp > timedelta(minutes=WITHDRAWAL_EXPIRY_MINUTES):
        transaction.status = "expired"

        # ✅ Real-time log for expiration
        rt_log = RealTimeLog(
            user_id=agent_id,
            action=f"⏳ Withdrawal request of {transaction.amount} RWF for User {transaction.user_id} expired",
            ip_address=request.remote_addr,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location="Agent location",  # or data.get("location") if passed
            risk_alert=True,
            tenant_id=1
        )
        db.session.add(rt_log)
        db.session.commit()

        return jsonify({"error": "⏳ This withdrawal request has expired and can no longer be approved."}), 403

    user_wallet = Wallet.query.filter_by(user_id=transaction.user_id).first()
    if not user_wallet:
        return jsonify({"error": "User wallet not found"}), 404

    if user_wallet.balance < transaction.amount:
        return jsonify({"error": "Insufficient user balance"}), 400

    user_wallet.balance -= transaction.amount
    transaction.status = "completed"

    metadata["approved_by_agent"] = True
    metadata["approved_by"] = agent_id
    metadata["approved_at"] = now.isoformat()
    transaction.transaction_metadata = json.dumps(metadata)

    db.session.commit()

    # ✅ Real-time log for approval
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"✅ Approved withdrawal of {transaction.amount} RWF for User {transaction.user_id}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location="Agent location",  # or data.get("location") if passed
        risk_alert=False,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({
        "message": "✅ Withdrawal approved and processed.",
        "user_id": transaction.user_id,
        "withdrawn_amount": transaction.amount,
        "updated_balance": user_wallet.balance,
        "approved_by": agent_id
    }), 200



# ✅ AGENT Rejects WITHDRAWAL
@agent_bp.route("/agent/reject-withdrawal/<int:transaction_id>", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def reject_user_withdrawal(transaction_id):
    agent_id = int(get_jwt_identity())
    transaction = Transaction.query.get(transaction_id)

    if not transaction or transaction.transaction_type != "withdrawal" or transaction.status != "pending":
        return jsonify({"error": "Invalid or already processed withdrawal request"}), 400

    metadata = json.loads(transaction.transaction_metadata or "{}")
    assigned_agent_id = int(metadata.get("assigned_agent_id", -1))

    if assigned_agent_id != agent_id:
        return jsonify({"error": "You are not authorized to reject this withdrawal"}), 403

    transaction.status = "rejected"
    metadata["rejected_by_agent"] = True
    metadata["rejected_by"] = agent_id
    metadata["rejected_at"] = datetime.utcnow().isoformat()
    transaction.transaction_metadata = json.dumps(metadata)

    db.session.commit()

    # ✅ Log to RealTimeLog
    rt_log = RealTimeLog(
        user_id=agent_id,
        action=f"❌ Rejected withdrawal of {transaction.amount} RWF for User {transaction.user_id}",
        ip_address=request.remote_addr,
        device_info=request.headers.get("User-Agent", "Unknown"),
        location="Agent location",  # Or data.get("location") if passed
        risk_alert=True,
        tenant_id=1
    )
    db.session.add(rt_log)
    db.session.commit()

    return jsonify({
        "message": "❌ Withdrawal rejected successfully.",
        "transaction_id": transaction.id,
        "status": "rejected"
    }), 200


# SIM SWAPPING
# @agent_bp.route("/agent/swap-sim", methods=["POST"])
# @jwt_required()
# @role_required(["agent"])
# def swap_sim():
#     data = request.get_json()

#     old_iccid = data.get("old_iccid")
#     new_iccid = data.get("new_iccid")
#     network_provider = data.get("network_provider")
#     location = data.get("location", "Unknown")

#     if not old_iccid or not new_iccid or not network_provider:
#         return jsonify({"error": "Missing required fields"}), 400

#     agent_id = int(get_jwt_identity())

#     # ✅ 1. Validate old SIM
#     old_sim = SIMCard.query.filter_by(iccid=old_iccid).first()
#     if not old_sim or old_sim.status != "active":
#         return jsonify({"error": "Old SIM not found or not active"}), 404

#     # ✅ 2. Validate new SIM
#     new_sim = SIMCard.query.filter_by(iccid=new_iccid).first()
#     if not new_sim:
#         return jsonify({"error": "The selected new ICCID does not exist in the system."}), 404
#     if new_sim.status != "unregistered":
#         return jsonify({"error": "The selected ICCID is not available for activation."}), 400

#     # ✅ 3. Enforce same network provider
#     if old_sim.network_provider != new_sim.network_provider:
#         return jsonify({
#             "error": f"SIM swap denied: Cannot swap from {old_sim.network_provider} to {new_sim.network_provider}."
#         }), 400

#     # ✅ 4. Prevent frequent swaps of same number
#     recent_swap = SIMCard.query.filter_by(
#         mobile_number=old_sim.mobile_number,
#         status="swapped"
#     ).order_by(SIMCard.registration_date.desc()).first()

#     if recent_swap:
#         time_since_last = datetime.utcnow() - recent_swap.registration_date
#         if time_since_last.total_seconds() < 120:
#             return jsonify({"error": "SIM was recently swapped. Please wait before swapping again."}), 429

#     # ✅ 5. Backup mobile number
#     old_mobile_number = old_sim.mobile_number

#     # ✅ 6. Mark old SIM as swapped
#     old_sim.status = "swapped"
#     old_sim.mobile_number = f"SWP_{int(datetime.utcnow().timestamp())}"

#     # ✅ 7. Assign new SIM
#     new_sim.status = "active"
#     new_sim.user_id = old_sim.user_id
#     new_sim.mobile_number = old_mobile_number
#     new_sim.registration_date = datetime.utcnow()
#     new_sim.registered_by = str(agent_id)  # For tracking in history

#     # ✅ 8. Log real-time
#     rt_log = RealTimeLog(
#         user_id=agent_id,
#         action=f"🔄 SIM swapped for {old_mobile_number}: {old_iccid} ➡️ {new_iccid}",
#         ip_address=request.remote_addr,
#         device_info=request.headers.get("User-Agent", "Unknown"),
#         location=location,
#         risk_alert=True,
#         tenant_id=1
#     )

#     db.session.add(rt_log)
#     db.session.commit()

#     return jsonify({
#         "message": "🔄 SIM swap successful",
#         "mobile_number": old_mobile_number,
#         "old_iccid": old_iccid,
#         "new_iccid": new_iccid
#     }), 200

@agent_bp.route("/agent/request-sim-swap", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def request_sim_swap():
    data = request.get_json()
    old_iccid = data.get("old_iccid")
    new_iccid = data.get("new_iccid")
    location = data.get("location", "Unknown")
    agent_id = get_jwt_identity()

    # Step 1: Validate both SIMs
    old_sim = SIMCard.query.filter_by(iccid=old_iccid).first()
    new_sim = SIMCard.query.filter_by(iccid=new_iccid).first()

    if not old_sim or not new_sim:
        return jsonify({"error": "SIM not found"}), 404
    if old_sim.status != "active" or new_sim.status != "unregistered":
        return jsonify({"error": "SIM status invalid"}), 400
    if old_sim.network_provider != new_sim.network_provider:
        return jsonify({"error": "Mismatched network providers"}), 400

    user_id = old_sim.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found for old SIM"}), 404

    # Step 2: Generate token and save pending swap
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    pending = PendingSIMSwap(
        token_hash=token_hash,
        user_id=user_id,
        old_iccid=old_iccid,
        new_iccid=new_iccid,
        requested_by=str(agent_id),
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db.session.add(pending)
    db.session.commit()

    # Step 3: Send email
    send_sim_swap_verification_email(user, raw_token)

    return jsonify({
        "message": "🔐 A verification email has been sent to the user. Awaiting approval."
    }), 200
