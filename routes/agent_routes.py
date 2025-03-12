from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Wallet, Transaction, SIMCard
from utils.decorators import role_required
import random

agent_bp = Blueprint("agent", __name__)

# A function to generate a unique mobile number
def generate_unique_mobile_number():
    """Generate a mobile number that does not exist in the database."""
    while True:
        new_number = "0787" + str(random.randint(100000, 999999))  # Example format
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

# ✅ API: Register SIM Card (Agents Only)
@agent_bp.route("/agent/register_sim", methods=["POST"])
@jwt_required()
def register_sim():
    logged_in_user = get_jwt_identity()
    agent = User.query.get(logged_in_user)

    # Only agents should be able to register SIMs
    if not agent or agent.user_access_control.role != "agent":
        return jsonify({"error": "Unauthorized. Only agents can register SIMs."}), 403

    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate unique mobile number and ICCID
    mobile_number = generate_unique_mobile_number()
    iccid = generate_unique_iccid()

    # Create the SIM card
    new_sim = SIMCard(
        iccid=iccid,
        mobile_number=mobile_number,
        network_provider="MTN Rwanda",  # Example telecom
        status="active",
        registered_by="Agent",
        user_id=user.id
    )

    db.session.add(new_sim)
    db.session.commit()

    return jsonify({
        "message": "SIM card registered successfully",
        "user_id": user.id,
        "mobile_number": new_sim.mobile_number,
        "iccid": new_sim.iccid
    }), 201

# ✅ API: Fetch SIM Registration History
@agent_bp.route("/agent/sim-registrations", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def fetch_sim_registration_history():
    """Fetch all SIM cards registered by the agent"""
    agent_id = get_jwt_identity()

    # ✅ Get SIMs registered by this agent
    sims = SIMCard.query.filter_by(registered_by="Agent").order_by(SIMCard.registration_date.desc()).all()

    sim_list = [
        {
            "iccid": sim.iccid,
            "mobile_number": sim.mobile_number,
            "network_provider": sim.network_provider,
            "status": sim.status,
            "timestamp": sim.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
            "registered_user": f"{sim.user.first_name} {sim.user.last_name}" if sim.user else "Not Linked"
        }
        for sim in sims
    ]

    return jsonify({"sims": sim_list}), 200



# ✅ Agent Dashboard (HTML Page)
@agent_bp.route("/agent/dashboard", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_dashboard():
    """Render Agent Dashboard"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return render_template("agent_dashboard.html", user=user)

# ✅ API: Fetch Agent Dashboard Data (Transactions + SIM Registrations Count)
@agent_bp.route("/agent/dashboard/data", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_dashboard_data():
    """Return JSON data for agent dashboard"""
    agent_id = get_jwt_identity()
    agent = db.session.get(User, agent_id)

    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    # ✅ Get total transactions done by this agent
    total_transactions = Transaction.query.filter_by(user_id=agent.id).count()

    # ✅ Get total SIMs registered by this agent
    total_sims = SIMCard.query.filter_by(registered_by="Agent").count()

    # ✅ Get total deposits, withdrawals, and transfers
    total_deposits = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=agent.id, transaction_type="deposit").scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=agent.id, transaction_type="withdrawal").scalar() or 0
    total_transfers = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=agent.id, transaction_type="transfer").scalar() or 0

    return jsonify({
        "total_transactions": total_transactions,
        "total_sims": total_sims,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers
    }), 200


# ✅ API: Fetch Agent's Transaction History
import json

@agent_bp.route("/agent/transactions", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_transactions():
    """Return agent's transaction history with deposit restriction and recipient details"""
    agent_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=agent_id).order_by(Transaction.timestamp.desc()).all()

    transaction_list = []
    for tx in transactions:
        # ✅ Ensure transaction_metadata is parsed correctly
        metadata = json.loads(tx.transaction_metadata) if tx.transaction_metadata else {}

        # ✅ Prevent agents from making deposits (filter deposits out)
        if tx.transaction_type == "deposit":
            continue  # Skip deposits, agents cannot deposit into their own accounts

        # ✅ Show recipient number only for transfers & deposits to other accounts
        recipient_mobile = metadata.get("recipient_mobile") if tx.transaction_type in ["transfer", "deposit"] else "Self"

        transaction_list.append({
            "amount": tx.amount,
            "transaction_type": tx.transaction_type,
            "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "recipient_mobile": recipient_mobile
        })

    return jsonify({"transactions": transaction_list}), 200


@agent_bp.route("/agent/transaction", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def process_agent_transaction():
    """Handle transactions (Deposit for users, Withdrawal, Transfer) with strict validation"""
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

    # ✅ Fetch Agent & Wallet
    agent = db.session.get(User, user_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    agent_wallet = Wallet.query.filter_by(user_id=agent.id).first()
    if not agent_wallet:
        return jsonify({"error": "Agent wallet not found"}), 404

    # ✅ Handle Deposits (Agent can deposit into user accounts, not their own)
    if transaction_type == "deposit":
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile is required for deposits"}), 400

        recipient = User.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient:
            return jsonify({"error": "Recipient not found"}), 404

        if recipient.id == agent.id:
            return jsonify({"error": "Agents cannot deposit into their own accounts"}), 403

        recipient_wallet = Wallet.query.filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        # ✅ Process Deposit into the User's Account
        recipient_wallet.balance += amount

        transaction_metadata = json.dumps({
            "deposited_by": "Agent",
            "recipient_mobile": recipient_mobile
        })

    # ✅ Handle Transfers (Agent sending money to another user)
    elif transaction_type == "transfer":
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile is required for transfers"}), 400

        recipient = User.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient:
            return jsonify({"error": "Recipient not found"}), 404

        recipient_wallet = Wallet.query.filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        if agent_wallet.balance < amount:
            return jsonify({"error": "Insufficient balance for transfer"}), 400

        # ✅ Process Transfer
        agent_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = json.dumps({
            "transfer_by": "Agent",
            "recipient_mobile": recipient_mobile
        })

    # ✅ Handle Withdrawals (Agent withdrawing from their own wallet)
    elif transaction_type == "withdrawal":
        if agent_wallet.balance < amount:
            return jsonify({"error": "Insufficient balance"}), 400
        agent_wallet.balance -= amount

        transaction_metadata = json.dumps({
            "withdrawal_method": "Agent Processed"
        })

    else:
        return jsonify({"error": "Invalid transaction type"}), 400

    # ✅ Save Transaction
    new_transaction = Transaction(
        user_id=agent.id if transaction_type != "deposit" else recipient.id,  # Deposits are recorded under the recipient
        amount=amount,
        transaction_type=transaction_type,
        status="completed",
        transaction_metadata=transaction_metadata
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({
        "message": f"{transaction_type.capitalize()} successful",
        "updated_balance": agent_wallet.balance if transaction_type != "deposit" else recipient_wallet.balance
    }), 200


# ✅ API: Fetch Agent Wallet Info
@agent_bp.route("/agent/wallet", methods=["GET"])
@jwt_required()
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





