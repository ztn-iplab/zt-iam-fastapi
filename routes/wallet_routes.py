from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, Wallet
from utils.decorators import role_required, session_protected

wallet_bp = Blueprint('wallet', __name__)

# Get Wallet (Only the Logged-in User)
@wallet_bp.route('/wallets', methods=['GET'])
@jwt_required()
@session_protected()
def get_wallet():
    logged_in_user = int(get_jwt_identity())

    # Fetch wallet for the logged-in user only
    wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    return jsonify({
        "user_id": wallet.user_id,
        "balance": wallet.balance,
        "currency": wallet.currency
    }), 200

# Update Wallet Balance (Only for the Logged-in User)
@wallet_bp.route('/wallets', methods=['PUT'])
@jwt_required()
@session_protected()
def update_wallet():
    logged_in_user = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate the data
    balance = data.get('balance')
    currency = data.get('currency')
    
    if balance is not None and (not isinstance(balance, (int, float)) or balance < 0):
        return jsonify({"error": "Invalid balance value. It must be a non-negative number."}), 400
    
    if currency and len(currency) != 3:
        return jsonify({"error": "Invalid currency. It must be a 3-letter currency code."}), 400

    wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    wallet.balance = balance if balance is not None else wallet.balance
    wallet.currency = currency if currency else wallet.currency
    db.session.commit()
    
    return jsonify({
        "user_id": wallet.user_id,
        "balance": wallet.balance,
        "currency": wallet.currency
    }), 200

# DELETE endpoint: Delete the wallet for the logged-in user
@wallet_bp.route('/wallets', methods=['DELETE'])
@jwt_required()
@session_protected()
def delete_wallet():
    logged_in_user = int(get_jwt_identity())
    wallet = Wallet.query.filter_by(user_id=logged_in_user).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    db.session.delete(wallet)
    db.session.commit()
    return jsonify({"message": "Wallet deleted successfully"}), 200