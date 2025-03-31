from functools import wraps
from flask import jsonify, redirect, url_for, request, flash
from flask_jwt_extended import get_jwt_identity
from models.models import db, User, UserAccessControl, UserRole

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
