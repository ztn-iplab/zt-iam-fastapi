from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Transaction, Wallet, User
import json
import threading
import time

transaction_bp = Blueprint('transaction', __name__)

def update_transaction_status(app, transaction_id, new_status):
    """
    Background function that updates a transaction's status.
    This function pushes an application context so that Flask-SQLAlchemy can be used.
    """
    time.sleep(10)  # Simulated delay (10 seconds)
    with app.app_context():
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            transaction.status = new_status
            db.session.commit()

import threading
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Wallet, Transaction, SIMCard

transaction_bp = Blueprint("transaction", __name__)

import threading
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, Wallet, Transaction, SIMCard

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    logged_in_user = int(get_jwt_identity())  # Get the logged-in user's ID
    data = request.get_json()

    # ✅ Validate required fields
    if not data.get('amount') or not data.get('transaction_type'):
        return jsonify({"error": "Amount and transaction type are required"}), 400

    # ✅ Validate amount (should be a positive number)
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    transaction_type = data['transaction_type'].lower()  # Normalize transaction type

    # ✅ Fetch the sender's wallet
    sender_wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not sender_wallet:
        return jsonify({"error": "Wallet not found"}), 404

    # ✅ Users are not allowed to deposit
    if transaction_type == "deposit":
        return jsonify({"error": "Deposits are not allowed for regular users"}), 403

    transaction_metadata = {}  # ✅ Initialize metadata

    # ✅ Process withdrawals
    if transaction_type == "withdrawal":
        if sender_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        sender_wallet.balance -= amount
        status = "completed"

        # ✅ Store metadata for withdrawal
        transaction_metadata = {
            "withdrawal_method": "Self-Service"
        }

    # ✅ Process transfers
    elif transaction_type == "transfer":
        recipient_mobile = data.get('recipient_mobile')
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile number is required for transfers"}), 400

        # ✅ Find recipient SIM card
        recipient_sim = SIMCard.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            return jsonify({"error": "Recipient not found"}), 404

        # ✅ Fetch recipient user using SIM card
        recipient_user = User.query.get(recipient_sim.user_id)
        if not recipient_user:
            return jsonify({"error": "Recipient user not found"}), 404

        # ✅ Fetch recipient's wallet
        recipient_wallet = Wallet.query.filter_by(user_id=recipient_user.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        # ✅ Ensure the sender has enough funds
        if sender_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        # ✅ Deduct from sender and credit recipient
        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        status = "pending"  # Transfers start as "pending"

        # ✅ Store metadata for transfer
        transaction_metadata = {
            "recipient_mobile": recipient_mobile,
            "recipient_id": recipient_user.id
        }

    else:
        return jsonify({"error": "Invalid transaction type"}), 400

    # ✅ Convert metadata to JSON string
    transaction_metadata_str = json.dumps(transaction_metadata)

    # ✅ Create transaction record
    transaction = Transaction(
        user_id=logged_in_user,
        amount=amount,
        transaction_type=transaction_type,
        status=status,
        location=data.get('location'),
        device_info=data.get('device_info'),
        transaction_metadata=transaction_metadata_str,
        fraud_flag=data.get('fraud_flag', False),
        risk_score=data.get('risk_score', 0)
    )

    db.session.add(transaction)
    db.session.commit()

    # ✅ For transfers, simulate async verification
    if transaction_type == "transfer":
        app = current_app._get_current_object()
        threading.Thread(target=update_transaction_status, args=(app, transaction.id, "completed")).start()

    return jsonify({
        "id": transaction.id,
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "status": transaction.status,  # Initially "pending" for transfers
        "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
        "location": transaction.location,
        "device_info": transaction.device_info,
        "fraud_flag": transaction.fraud_flag,
        "risk_score": transaction.risk_score,
        "transaction_metadata": transaction_metadata,  # ✅ Return as a parsed JSON object
        "updated_balance": sender_wallet.balance
    }), 201

# Get Transactions (Only User-Specific)
@transaction_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    logged_in_user = int(get_jwt_identity())

    # Fetch only transactions belonging to the logged-in user
    transactions = Transaction.query.filter_by(user_id=logged_in_user).all()

    return jsonify([{
    "id": transaction.id,
    "user_id": transaction.user_id,
    "amount": transaction.amount,
    "transaction_type": transaction.transaction_type,
    "status": transaction.status,
    "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
    "location": transaction.location,
    "device_info": transaction.device_info,
    "fraud_flag": transaction.fraud_flag,
    "risk_score": transaction.risk_score,
    "recipient_mobile": (
        "Self" if transaction.transaction_type in ["deposit", "withdrawal"]
        else json.loads(transaction.transaction_metadata).get("recipient_mobile") if transaction.transaction_metadata else "N/A"
    )
} for transaction in transactions]), 200

# Update a specific transaction (only if it belongs to the logged-in user)
@transaction_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    logged_in_user = int(get_jwt_identity())
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != logged_in_user:
        return jsonify({"error": "Transaction not found or unauthorized"}), 404

    data = request.get_json()
    # Allow updating some non-critical fields (e.g., status, location, device_info, metadata)
    if 'status' in data:
        transaction.status = data['status']
    if 'location' in data:
        transaction.location = data['location']
    if 'device_info' in data:
        transaction.device_info = data['device_info']
    if 'transaction_metadata' in data:
        transaction.transaction_metadata = data['transaction_metadata']

    db.session.commit()
    return jsonify({"message": "Transaction updated successfully"}), 200

# Delete a specific transaction (only if it belongs to the logged-in user)
@transaction_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    logged_in_user = int(get_jwt_identity())
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != logged_in_user:
        return jsonify({"error": "Transaction not found or unauthorized"}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted successfully"}), 200

    
