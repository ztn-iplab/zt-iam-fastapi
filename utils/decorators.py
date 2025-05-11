from functools import wraps
from flask import jsonify, redirect, url_for, request, flash
from flask_jwt_extended import get_jwt_identity
from models.models import db, User, UserAccessControl, UserRole, RealTimeLog
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from utils.security import get_request_fingerprint
from utils.location import get_ip_location
from datetime import datetime
import json

def role_required(required_roles, json_response=True):
    """
    Decorator to restrict access to specific roles.
    
    Parameters:
      required_roles (list): List of allowed roles.
      json_response (bool): If True, returns a JSON error message; if False, redirects.
    
    Usage examples:
      @role_required(["admin"], json_response=False)
      @role_required(["admin", "agent"])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                if json_response or request.is_json:
                    return jsonify({"error": "Unauthorized access"}), 403
                else:
                    return redirect(url_for('login'))
            user_access = UserAccessControl.query.filter_by(user_id=user_id).first()
            if not user_access:
                if json_response or request.is_json:
                    return jsonify({"error": "User has no assigned role"}), 403
                else:
                    return redirect(url_for('unauthorized'))
            user_role = UserRole.query.get(user_access.role_id)
            if not user_role or user_role.role_name not in required_roles:
                if json_response or request.is_json:
                    return jsonify({"error": "Access denied: Insufficient permissions"}), 403
                else:
                    return redirect(url_for('unauthorized'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ✅ TOTP Setup Enforcement
def require_totp_setup(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = User.query.get(get_jwt_identity())
        if not user or not user.otp_secret:
            flash("🔐 Please set up your TOTP to continue.")
            return redirect(url_for('user.show_totp_setup'))
        return view_func(*args, **kwargs)
    return wrapped
    
def session_protected():
    """Decorator to enforce fingerprint-based session integrity."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            token_data = get_jwt()
            token_fp = token_data.get("fp")
            request_fp = get_request_fingerprint()
            user_id = token_data.get("sub")

            if token_fp != request_fp:
                # ✅ Attempt to resolve role (optional but useful for admin logs)
                role = "unknown"
                try:
                    user = User.query.get(user_id)
                    if user:
                        access = UserAccessControl.query.filter_by(user_id=user.id).first()
                        if access:
                            role_obj = UserRole.query.get(access.role_id)
                            if role_obj:
                                role = role_obj.role_name
                except:
                    pass  # Avoid breaking logging if DB errors occur

                # ✅ Log suspicious activity
                db.session.add(RealTimeLog(
                    user_id=user_id,
                    action=f"🚨 Session hijack attempt on {role} account (fingerprint mismatch)",
                    ip_address=request.remote_addr,
                    device_info=request.headers.get("User-Agent", "Unknown"),
                    location=get_ip_location(request.remote_addr),
                    metadata=json.dumps({
                        "expected_fp": token_fp,
                        "actual_fp": request_fp
                    }),
                    timestamp=datetime.utcnow(),
                    risk_alert=True,
                    tenant_id=1 
                ))
                db.session.commit()

                return jsonify({"error": "Session fingerprint mismatch. Access denied."}), 401

            return fn(*args, **kwargs)
        return wrapper
    return decorator