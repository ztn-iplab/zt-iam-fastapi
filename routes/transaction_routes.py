from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Transaction, Wallet, User, SIMCard, RealTimeLog
from utils.totp import verify_totp_code # Import your OTP logic
from utils.location import get_ip_location  
import pyotp
from datetime import datetime
import json
import threading
import time
import json
from utils.fraud_engine import calculate_risk_score
from utils.email_alerts import send_alert_email
from utils.decorators import role_required, session_protected

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
@session_protected()
def create_transaction():
    logged_in_user = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('amount') or not data.get('transaction_type'):
        return jsonify({"error": "Amount and transaction type are required"}), 400

    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number"}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount format"}), 400

    transaction_type = data['transaction_type'].lower()
    sender_wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not sender_wallet:
        return jsonify({"error": "Wallet not found"}), 404

    transaction_metadata = {}

    if transaction_type == "deposit":
        return jsonify({"error": "Deposits are not allowed for regular users"}), 403

    totp_code = data.get('totp')
    if not totp_code:
        return jsonify({"error": "TOTP code is required"}), 400

    user = User.query.get(logged_in_user)
    if not user or not user.otp_secret:
        return jsonify({"error": "TOTP secret not configured for user"}), 403

    if not verify_totp_code(user.otp_secret, totp_code):
        return jsonify({"error": "Invalid or expired TOTP code"}), 401

    ip_address = request.remote_addr or data.get('ip_address')
    risk_score = calculate_risk_score(user, amount, data.get('location'), data.get('device_info'), ip_address)
    fraud_flag = risk_score >= 0.7

    # ✅ Withdrawal
    if transaction_type == "withdrawal":
        if sender_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        agent_mobile = data.get("agent_mobile")
        if not agent_mobile:
            return jsonify({"error": "Agent mobile number is required"}), 400

        agent_sim = SIMCard.query.filter_by(mobile_number=agent_mobile).first()
        if not agent_sim:
            return jsonify({"error": "Agent not found"}), 404

        assigned_agent = User.query.get(agent_sim.user_id)
        if not assigned_agent:
            return jsonify({"error": "Agent user not found"}), 404

        status = "pending"
        transaction_metadata = {
            "initiated_by": "user",
            "approved_by_agent": False,
            "assigned_agent_id": assigned_agent.id,
            "assigned_agent_mobile": agent_mobile,
            "assigned_agent_name": f"{assigned_agent.first_name} {assigned_agent.last_name}".strip()
        }

        transaction = Transaction(
            user_id=logged_in_user,
            amount=amount,
            transaction_type=transaction_type,
            status=status,
            location=data.get('location'),
            device_info=data.get('device_info'),
            transaction_metadata=json.dumps(transaction_metadata),
            fraud_flag=fraud_flag,
            risk_score=risk_score,
            tenant_id=1
        )

        db.session.add(transaction)

        # ✅ Real-time log
        log_msg = f"{transaction_type.title()} of {amount} RWF"
        if fraud_flag:
            log_msg = f"⚠️ Suspicious {log_msg} flagged"

        rt_log = RealTimeLog(
            user_id=user.id,
            action=log_msg,
            ip_address=ip_address,
            device_info=data.get('device_info'),
            location=data.get('location', 'Unknown'),
            risk_alert=fraud_flag,
            tenant_id=1
        )
        db.session.add(rt_log)

        # ✅ Send Email
        subject = "🚨 Fraud Alert: Suspicious Transaction Detected"
        body = f"""
        A suspicious transaction has been flagged.

        User ID: {user.id}
        Amount: {amount} RWF
        Type: {transaction_type}
        Risk Score: {risk_score}
        IP: {ip_address}
        Device: {data.get('device_info')}
        Location: {data.get('location')}

        Please log in to the admin dashboard to review.
        """
        send_alert_email(subject, body)

        db.session.commit()

        return jsonify({
            "message": "✅ Withdrawal request submitted. Awaiting agent approval.",
            "transaction_id": transaction.id,
            "status": transaction.status,
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "assigned_agent": f"{assigned_agent.first_name} {assigned_agent.last_name} ({agent_mobile})",
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "updated_balance": sender_wallet.balance,
            "location": transaction.location,
            "device_info": transaction.device_info,
            "fraud_flag": transaction.fraud_flag,
            "risk_score": transaction.risk_score
        }), 200

    # ✅ Transfer
    elif transaction_type == "transfer":
        recipient_mobile = data.get('recipient_mobile')
        if not recipient_mobile:
            return jsonify({"error": "Recipient mobile number is required for transfers"}), 400

        recipient_sim = SIMCard.query.filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            return jsonify({"error": "Recipient not found"}), 404

        recipient_user = User.query.get(recipient_sim.user_id)
        if not recipient_user:
            return jsonify({"error": "Recipient user not found"}), 404

        recipient_wallet = Wallet.query.filter_by(user_id=recipient_user.id).first()
        if not recipient_wallet:
            return jsonify({"error": "Recipient wallet not found"}), 404

        if sender_wallet.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        sender_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = {
            "recipient_mobile": recipient_mobile,
            "recipient_id": recipient_user.id,
            "recipient_name": f"{recipient_user.first_name} {recipient_user.last_name}".strip(),
            "sender_id": logged_in_user
        }

        transaction = Transaction(
            user_id=logged_in_user,
            amount=amount,
            transaction_type=transaction_type,
            status="pending",
            location=data.get('location'),
            device_info=data.get('device_info'),
            transaction_metadata=json.dumps(transaction_metadata),
            fraud_flag=fraud_flag,
            risk_score=risk_score,
            tenant_id=1
        )

        db.session.add(transaction)

        # ✅ Real-time log
        log_msg = f"{transaction_type.title()} of {amount} RWF"
        if fraud_flag:
            log_msg = f"⚠️ Suspicious {log_msg} flagged"

        rt_log = RealTimeLog(
            user_id=user.id,
            action=log_msg,
            ip_address=ip_address,
            device_info=data.get('device_info'),
            location=data.get('location', 'Unknown'),
            risk_alert=fraud_flag,
            tenant_id=1
        )
        db.session.add(rt_log)

        db.session.commit()

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
@session_protected()
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

            # ✅ Normalize any swapped agent mobile
            if isinstance(agent_mobile, str) and agent_mobile.startswith("SWP_"):
                assigned_agent_id = metadata.get("assigned_agent_id")
                if assigned_agent_id:
                    active_sim = SIMCard.query.filter_by(user_id=assigned_agent_id, status="active").first()
                    if active_sim:
                        agent_mobile = active_sim.mobile_number

                # Or try looking up who deposited
                deposited_by_mobile = metadata.get("deposited_by_mobile")
                if deposited_by_mobile and deposited_by_mobile.startswith("SWP_"):
                    deposited_sim = SIMCard.query.filter_by(user_id=logged_in_user, status="active").first()
                    if deposited_sim:
                        agent_mobile = deposited_sim.mobile_number

            # ✅ Fetch sender mobile number (for transfer receiver label)
            sender_sim = SIMCard.query.filter_by(user_id=tx.user_id, status="active").first()
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

            elif tx.transaction_type == "reversal":
                label = "🔁 Transfer Reversed"

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
@session_protected()
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
@session_protected()
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
@session_protected()
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


@transaction_bp.route('/verify-transaction-otp', methods=['POST'])
@jwt_required()
@session_protected()
def verify_transaction_otp():
    data = request.get_json()
    otp_input = data.get('otp')
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user.otp_secret:
        return jsonify({"error": "TOTP not set up"}), 403

    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(otp_input, valid_window=1):
        return jsonify({"error": "Invalid or expired OTP"}), 401

    # ✅ OTP is valid — proceed to finalize the transaction
    # You can re-use the `transaction_data` from earlier or include it in this request

    # Example placeholder:
    return jsonify({"message": "✅ Transaction authorized!"}), 200
