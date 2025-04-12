from functools import wraps
from flask import session, jsonify

def require_full_mfa(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("mfa_totp_verified"):
            return jsonify({"error": "TOTP verification required"}), 403
        if not session.get("mfa_webauthn_verified"):
            return jsonify({"error": "Passkey or biometric authentication required"}), 401
        return view_func(*args, **kwargs)
    return wrapper
