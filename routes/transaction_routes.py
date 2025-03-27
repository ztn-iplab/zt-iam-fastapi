from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Transaction, Wallet, User, SIMCard
import json
import threading
import time
import threading
import json


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

    transaction_metadata = {}  # ✅ Initialize metadata

    # ❌ Block deposit for users
    if transaction_type == "deposit":
        return jsonify({"error": "Deposits are not allowed for regular users"}), 403

    # ✅ Handle withdrawals (user-initiated, agent must approve)
    elif transaction_type == "withdrawal":
        if sender_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        agent_mobile = data.get("agent_mobile")
        if not agent_mobile:
            return jsonify({"error": "Agent mobile number is required to process withdrawal"}), 400

        # ✅ Find the agent by mobile
        agent_sim = SIMCard.query.filter_by(mobile_number=agent_mobile).first()
        if not agent_sim:
            return jsonify({"error": "Agent not found"}), 404

        assigned_agent = User.query.get(agent_sim.user_id)
        if not assigned_agent:
            return jsonify({"error": "Agent user not found"}), 404

        # ✅ Store metadata
        status = "pending"
        transaction_metadata = {
            "initiated_by": "user",
            "approved_by_agent": False,
            "assigned_agent_id": assigned_agent.id,
            "assigned_agent_mobile": agent_mobile,
            "assigned_agent_name": f"{assigned_agent.first_name} {assigned_agent.last_name}".strip()
        }

        transaction_metadata_str = json.dumps(transaction_metadata)

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

        return jsonify({
            "message": f"✅ Withdrawal request submitted. Awaiting approval from agent {assigned_agent.first_name} {assigned_agent.last_name} ({agent_mobile}).",
            "transaction_id": transaction.id,
            "status": transaction.status,
            "assigned_agent": f"{assigned_agent.first_name} {assigned_agent.last_name} ({agent_mobile})",
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "updated_balance": sender_wallet.balance,
            "location": transaction.location,
            "device_info": transaction.device_info,
            "fraud_flag": transaction.fraud_flag,
            "risk_score": transaction.risk_score
        }), 200

    # ✅ Handle transfers
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
            "recipient_id": recipient_user.id,
            "recipient_name": f"{recipient_user.first_name} {recipient_user.last_name}".strip(),
            "sender_id": logged_in_user
        }

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
        app = current_app._get_current_object()
        threading.Thread(target=update_transaction_status, args=(app, transaction.id, "completed")).start()

        return jsonify({
            "message": f"✅ {amount} RWF transferred to {recipient_user.first_name} {recipient_user.last_name} ({recipient_mobile}).",
            "transaction_id": transaction.id,
            "status": transaction.status,
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "updated_balance": sender_wallet.balance,
            "location": transaction.location,
            "device_info": transaction.device_info,
            "fraud_flag": transaction.fraud_flag,
            "risk_score": transaction.risk_score
        }), 200

    else:
        return jsonify({"error": "Invalid transaction type"}), 400
     
# The Transactions history
@transaction_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    logged_in_user = int(get_jwt_identity())

    transactions = Transaction.query.filter(
        (Transaction.user_id == logged_in_user) |
        (Transaction.transaction_metadata.contains(f'"recipient_id": {logged_in_user}'))
    ).order_by(Transaction.timestamp.desc()).all()

    transaction_list = []
    for tx in transactions:
        try:
            metadata = json.loads(tx.transaction_metadata) if tx.transaction_metadata else {}

            recipient_mobile = metadata.get("recipient_mobile", "N/A")
            recipient_id = metadata.get("recipient_id")
            agent_mobile = metadata.get("assigned_agent_mobile") or metadata.get("deposited_by_mobile", "N/A")
            initiated_by = metadata.get("initiated_by", None)
            approved_by_agent = metadata.get("approved_by_agent", None)

            # ✅ Fetch sender mobile number (for transfer receiver label)
            sender_sim = SIMCard.query.filter_by(user_id=tx.user_id).first()
            sender_mobile = sender_sim.mobile_number if sender_sim else "Unknown"

            # ✅ Labeling logic based on transaction type
            if tx.transaction_type == "deposit":
                label = f"Deposit from Agent {agent_mobile}"

            elif tx.transaction_type == "transfer":
                if tx.user_id == logged_in_user:
                    label = f"Transfered to {recipient_mobile}"
                elif recipient_id == logged_in_user:
                    label = f"Received from {sender_mobile}"
                else:
                    label = "Transfer"

            elif tx.transaction_type == "withdrawal":
                if tx.status == "pending":
                    label = f"Withdrawal (Pending Agent Approval - {agent_mobile})"
                elif tx.status == "rejected":
                    label = f"Withdrawal (❌ Rejected by Agent {agent_mobile})"
                elif tx.status == "expired":
                    label = f"Withdrawal (⏳ Expired - Not Approved in Time)"
                else:
                    label = f"Withdrawal (✅ Approved by Agent {agent_mobile})"
            else:
                label = tx.transaction_type.capitalize()

            # ✅ Optional: style class based on status
            status_class = ""
            if tx.status == "rejected":
                status_class = "text-danger"
            elif tx.status == "pending":
                status_class = "text-warning"
            elif tx.status == "completed":
                status_class = "text-success"
            elif tx.status == "expired":
                status_class = "text-muted"

            transaction_list.append({
                "transaction_id": tx.id,
                "amount": tx.amount,
                "transaction_type": tx.transaction_type,
                "label": label,
                "status": tx.status,
                "status_class": status_class,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "details": metadata
            })

        except Exception as e:
            print(f"❌ Error processing transaction metadata: {e}")
            continue

    return jsonify({"transactions": transaction_list}), 200


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

# Under agent approval withdraws
# ✅ USER INITIATES WITHDRAWAL
@transaction_bp.route('/user/initiated-withdrawal', methods=['POST'])
@jwt_required()
def user_initiate_withdrawal():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount format"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    if wallet.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Don't deduct balance yet — wait for agent approval
    withdrawal_request = Transaction(
        user_id=user_id,
        amount=amount,
        transaction_type="withdrawal",
        status="pending",
        transaction_metadata=json.dumps({
            "initiated_by": "user",
            "approved_by_agent": False
        })
    )
    db.session.add(withdrawal_request)
    db.session.commit()

    return jsonify({
        "message": "Withdrawal request submitted. Awaiting agent approval.",
        "transaction_id": withdrawal_request.id
    }), 200
