from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, User, RealTimeLog
from utils.location import get_ip_location
from utils.decorators import role_required, session_protected

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET'])
@jwt_required()
@session_protected()
def settings():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return render_template('settings.html', user=user)

@settings_bp.route('/change-password')
@jwt_required()
@session_protected()
def change_password():
    return render_template('change_password.html')

@settings_bp.route('/reset-totp')
@jwt_required()
@session_protected()
def reset_totp():
    return render_template('reset_totp.html')

@settings_bp.route('/reset-webauthn')
@jwt_required()
@session_protected()
def reset_webauthn():
    return render_template('reset_webauthn.html')



@settings_bp.route('/settings/update-profile', methods=['POST'])
@jwt_required()
@session_protected()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    new_country = data.get('country', '').strip()
    if not new_country:
        return jsonify({"error": "Country is required"}), 400

    user.country = new_country

    db.session.add(RealTimeLog(
        user_id=user.id,
        action=f"📝 Updated profile info (country: {new_country})",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=False
    ))

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200

@settings_bp.route('/settings/request-deletion', methods=['POST'])
@jwt_required()
@session_protected()
def request_account_deletion():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.deletion_requested:
        return jsonify({"message": "Your account deletion is already under review."}), 200

    user.deletion_requested = True

    db.session.add(RealTimeLog(
        user_id=user.id,
        action="🧨 Requested account deletion",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string,
        location=get_ip_location(request.remote_addr),
        risk_alert=True
    ))

    # Optional: Notify admins
    from utils.email_alerts import send_admin_alert
    send_admin_alert(
        user=user,
        event_type="account_deletion_request",
        ip_address=request.remote_addr,
        location=get_ip_location(request.remote_addr),
        device_info=request.user_agent.string
    )

    db.session.commit()
    return jsonify({"message": "Account deletion request submitted. Admins will review it shortly."}), 200

@settings_bp.route('/')
@jwt_required()
@session_protected()
def settings_home():
    user = User.query.get(get_jwt_identity())
    role = 'user'  # or 'admin' or 'agent', however you determine this

    # If you're using a User.role field:
    role = user.role

    return render_template('settings.html', user=user, role=role)
