from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models.models import db, User, UserAccessControl, UserRole

def role_required(required_roles):
    """
    Decorator to restrict access to specific roles.
    Usage:
        @role_required(["admin"])  # Only admins can access
        @role_required(["admin", "agent"])  # Both admins & agents can access
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()  # Extract user ID from JWT
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return jsonify({"error": "Unauthorized access"}), 403

            # Get user's role
            user_access = UserAccessControl.query.filter_by(user_id=user_id).first()
            if not user_access:
                return jsonify({"error": "User has no assigned role"}), 403

            user_role = UserRole.query.get(user_access.role_id)
            if not user_role or user_role.role_name not in required_roles:
                return jsonify({"error": "Access denied: Insufficient permissions"}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator