from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from models.models import db, SIMRegistration

agent_bp = Blueprint("agent", __name__)

#Simcard Registration
@agent_bp.route("/api/agent/register_sim", methods=["POST"])
@jwt_required()
def register_sim():
    """Agent registers a new SIM card for a user."""
    data = request.get_json()

    if not data.get("mobile_number"):
        return jsonify({"error": "Mobile number is required"}), 400

    # Corrected query using db.session.get()
    user = db.session.get(User, data["mobile_number"])  
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if SIM is already registered
    existing_sim = db.session.get(SIMRegistration, user.id)  
    if existing_sim:
        return jsonify({"error": "SIM card already registered"}), 400

    # Register SIM using user's details
    new_sim = SIMRegistration(
        user_id=user.id,
        registration_timestamp=datetime.utcnow(),
        verified_by="agent",
        status="pending"
    )
    db.session.add(new_sim)
    db.session.commit()

    return jsonify({
        "message": "SIM card registered successfully!",
        "user_name": f"{user.first_name} {user.last_name}",
        "mobile_number": user.mobile_number
    }), 201



#Agent Transactions
@agent_bp.route("/api/agent/process_transaction", methods=["POST"])
@jwt_required()
def process_transaction():
    """Agent processes a transaction on behalf of a user."""
    data = request.get_json()

    if not data.get("amount") or not data.get("transaction_type"):
        return jsonify({"error": "Amount and transaction type are required"}), 400

    new_transaction = Transaction(
        user_id=get_jwt_identity(),
        amount=float(data["amount"]),
        transaction_type=data["transaction_type"],
        status="pending"
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Transaction submitted for processing!"}), 201

#View pending transactions
@agent_bp.route("/api/agent/pending_transactions", methods=["GET"])
@jwt_required()
def get_pending_transactions():
    """Fetch transactions that need verification."""
    transactions = Transaction.query.filter_by(status="pending").all()
    
    tx_list = [{"id": tx.id, "amount": tx.amount, "status": tx.status} for tx in transactions]

    return jsonify({"transactions": tx_list}), 200
