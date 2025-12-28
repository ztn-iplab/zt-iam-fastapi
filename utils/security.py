import base64
import hashlib
import os
import re
import secrets
from datetime import datetime

import pyotp

from utils.location import get_ip_location


def is_strong_password(password):
    # At least 8 chars, 1 upper, 1 lower, 1 digit, 1 special
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )

# Generate a secure random token (for password resets, TOTP resets, etc.)
def generate_token():
    return secrets.token_urlsafe(32)


# Securely hash a token before saving it to the DB
def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


# Verify that a raw token matches the hashed token from the DB
def verify_token(token, hashed):
    return hash_token(token) == hashed


# TOTP Verification: Verifies the TOTP input against the user's secret
def verify_totp(user, otp_input):
    if not user.otp_secret:
        return False
    try:
        return pyotp.TOTP(user.otp_secret).verify(otp_input)
    except Exception:
        return False


# Placeholder for fallback verification (SMS/WebAuthn/Device Fingerprint)
def verify_secondary_method(user, request_obj=None):
    """
    For ZTN-based secondary verification fallback. You can enhance this:
    - WebAuthn verification (recommended)
    - Compare known device/browser
    - IP or geolocation match
    - Admin approval
    """
    try:
        req = request_obj or _resolve_request()
        if not req:
            return False
        headers = getattr(req, "headers", {}) or {}
        user_ip = (
            headers.get("X-Real-IP")
            or headers.get("X-Forwarded-For")
            or getattr(req, "remote_addr", None)
            or (req.client.host if getattr(req, "client", None) else None)
        )
        user_agent = headers.get("User-Agent", "")
        _ = get_ip_location(user_ip or "")

        if user.trusted_ip == user_ip and user.trusted_device in user_agent:
            return True
    except Exception:
        return False
    return False

def generate_challenge():
    return base64.b64encode(os.urandom(32)).decode("utf-8")

def _resolve_request():
    try:
        from flask import has_request_context, request as flask_request
    except Exception:
        return None

    if not has_request_context():
        return None
    return flask_request


def get_request_fingerprint(tenant_id=None, request_obj=None):
    req = request_obj or _resolve_request()
    if not req:
        return "no-request-context"

    headers = getattr(req, "headers", {}) or {}
    ip = (
        headers.get("X-Real-IP")
        or headers.get("X-Forwarded-For")
        or getattr(req, "remote_addr", None)
        or (req.client.host if getattr(req, "client", None) else None)
        or "unknown"
    )

    ua = headers.get("User-Agent", "unknown").lower().strip()
    tenant_str = str(tenant_id) if tenant_id else "unknown-tenant"

    raw_fp = f"{tenant_str}|{ip}|{ua}"
    return hashlib.sha256(raw_fp.encode()).hexdigest()


def generate_custom_api_key(tenant_name):
    # Sanitize tenant name (remove special chars), uppercase, and shorten
    prefix = re.sub(r'\W+', '', tenant_name).upper()[:12]
    suffix = secrets.token_hex(6)  # 12 hex chars
    return f"{prefix}-{suffix}"
