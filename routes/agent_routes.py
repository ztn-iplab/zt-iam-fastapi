from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Wallet, Transaction, SIMRegistration
from utils.decorators import role_required

agent_bp = Blueprint("agent", __name__)

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
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    total_transactions = Transaction.query.filter_by(user_id=user.id).count()
    total_sims = SIMRegistration.query.filter_by(user_id=user.id).count()
    total_deposits = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user.id, transaction_type="deposit").scalar() or 0
    total_withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user.id, transaction_type="withdrawal").scalar() or 0
    total_transfers = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user.id, transaction_type="transfer").scalar() or 0

    return jsonify({
        "total_transactions": total_transactions,
        "total_sims": total_sims,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers
    }), 200


# ✅ API: Fetch Agent's Transaction History
@agent_bp.route("/agent/transactions", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_transactions():
    """Return agent's transaction history"""
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()

    transaction_list = []
    for tx in transactions:
        # Ensure transaction_metadata is parsed correctly
        metadata = json.loads(tx.transaction_metadata) if tx.transaction_metadata else {}

        transaction_list.append({
            "amount": tx.amount,
            "transaction_type": tx.transaction_type,
            "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "recipient_mobile": metadata.get("recipient_mobile") if tx.transaction_type == "transfer" else "Self"
        })

    return jsonify({"transactions": transaction_list}), 200

# ✅ API: Process Transactions with Validations
@agent_bp.route("/agent/transaction", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def process_agent_transaction():
    """Handle transactions (Deposit, Withdrawal, Transfer) with validation"""
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

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    wallet = Wallet.query.filter_by(user_id=user.id).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    if transaction_type == "withdrawal" and wallet.balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    if transaction_type == "transfer":
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile is required for transfers"}), 400

        recipient = User.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient:
            return jsonify({"error": "Recipient not found"}), 404

        recipient_wallet = Wallet.query.filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        if wallet.balance < amount:
            return jsonify({"error": "Insufficient balance for transfer"}), 400

        wallet.balance -= amount
        recipient_wallet.balance += amount

    elif transaction_type == "deposit":
        wallet.balance += amount

    elif transaction_type == "withdrawal":
        wallet.balance -= amount

    new_transaction = Transaction(
        user_id=user.id,
        amount=amount,
        transaction_type=transaction_type,
        status="completed"
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({
        "message": "Transaction successful",
        "updated_balance": wallet.balance
    }), 200

# ✅ API: Fetch Agent Wallet Info
@agent_bp.route("/agent/wallet", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def agent_wallet():
    """Return agent's wallet balance"""
    user_id = get_jwt_identity()
    wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    return jsonify({
        "balance": wallet.balance,
        "currency": wallet.currency
    }), 200

# ✅ API: Fetch Agent Profile (Ensure Name is Returned)
@agent_bp.route('/agent/profile', methods=['GET'])
@jwt_required()
@role_required(["agent"])
def agent_profile():
    """Fetch agent profile data"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "mobile_number": user.mobile_number,
        "first_name": user.first_name or "Unknown",
        "last_name": user.last_name or "",
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "country": user.country or "N/A",
        "identity_verified": user.identity_verified
    }), 200

# ✅ API: Agent SIM Registration
@agent_bp.route("/agent/register_sim", methods=["POST"])
@jwt_required()
@role_required(["agent"])
def register_sim():
    """Agent registers a new SIM card for a user."""
    data = request.get_json()

    if not data.get("mobile_number"):
        return jsonify({"error": "Mobile number is required"}), 400

    user = User.query.filter_by(mobile_number=data["mobile_number"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    existing_sim = SIMRegistration.query.filter_by(user_id=user.id).first()
    if existing_sim:
        return jsonify({"error": "SIM card already registered"}), 400

    new_sim = SIMRegistration(
        user_id=user.id,
        registration_timestamp=db.func.current_timestamp(),
        verified_by="agent",
        status="pending"
    )
    db.session.add(new_sim)
    db.session.commit()

    return jsonify({"message": "SIM card registered successfully!"}), 201

    
# ✅ API: Fetch SIM Registration History
@agent_bp.route("/agent/sim-registrations", methods=["GET"])
@jwt_required()
@role_required(["agent"])
def fetch_sim_registration_history():
    """Fetch all SIM cards registered by the agent"""
    user_id = get_jwt_identity()
    
    sims = SIMRegistration.query.filter_by(user_id=user_id).order_by(SIMRegistration.registration_timestamp.desc()).all()

    sim_list = [
        {
            "mobile_number": sim.user.mobile_number,
            "timestamp": sim.registration_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": sim.status
        }
        for sim in sims
    ]

    return jsonify({"sims": sim_list}), 200
