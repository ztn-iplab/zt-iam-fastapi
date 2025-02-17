from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Transaction, Wallet

transaction_bp = Blueprint('transaction', __name__)

# Create a Transaction & Update Wallet Balance (Only for the Logged-in User)
@transaction_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    logged_in_user = int(get_jwt_identity())  # Cast back to integer
    data = request.get_json()

    # Validate required fields
    if not data.get('amount') or not data.get('transaction_type'):
        return jsonify({"error": "Amount and transaction type are required"}), 400

    # Validate amount (should be a positive number)
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    transaction_type = data['transaction_type'].lower()  # Normalize transaction type

    # Fetch user's wallet
    wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    # Handle different transaction types
    if transaction_type == "deposit":
        wallet.balance += amount  # Increase balance on deposit
    elif transaction_type in ["withdrawal", "payment"]:
        if wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        wallet.balance -= amount  # Deduct balance on withdrawal/payment
    else:
        return jsonify({"error": "Invalid transaction type"}), 400

    # Create the transaction with all fields
    transaction = Transaction(
        user_id=logged_in_user,  # Automatically assign to logged-in user
        amount=amount,
        transaction_type=transaction_type,
        status=data.get('status', 'pending'),  # Default to "pending"
        location=data.get('location'),
        device_info=data.get('device_info'),
        transaction_metadata=data.get('transaction_metadata'),
        fraud_flag=data.get('fraud_flag', False),  # Default to False if not provided
        risk_score=data.get('risk_score', 0)  # Default to 0 if not provided
    )

    # Explicitly add both wallet and transaction to the session before commit
    db.session.add(wallet)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
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
        "transaction_metadata": transaction.transaction_metadata,
        "updated_balance": wallet.balance  # This is just returned in the JSON response
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
        "transaction_metadata": transaction.transaction_metadata
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