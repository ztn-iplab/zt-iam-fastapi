from flask import request, jsonify, g
from models.models import Tenant

def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401
        tenant = Tenant.query.filter_by(api_key=api_key).first()
        if not tenant:
            return jsonify({"error": "Invalid API key"}), 403
        g.tenant = tenant
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

import secrets

def generate_api_key():
    return secrets.token_hex(32)
