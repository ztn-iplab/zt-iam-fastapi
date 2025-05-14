import secrets
import hashlib
import pyotp
from datetime import datetime
from flask import request
from utils.location import get_ip_location
import os
import base64
import re


def is_strong_password(password):
    # At least 8 chars, 1 upper, 1 lower, 1 digit, 1 special
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )

# ✅ Generate a secure random token (for password resets, TOTP resets, etc.)
def generate_token():
    return secrets.token_urlsafe(32)


# ✅ Securely hash a token before saving it to the DB
def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


# ✅ Verify that a raw token matches the hashed token from the DB
def verify_token(token, hashed):
    return hash_token(token) == hashed


# ✅ TOTP Verification: Verifies the TOTP input against the user's secret
def verify_totp(user, otp_input):
    if not user.otp_secret:
        return False
    try:
        return pyotp.TOTP(user.otp_secret).verify(otp_input)
    except Exception:
        return False


# 🧠 Placeholder for fallback verification (SMS/WebAuthn/Device Fingerprint)
def verify_secondary_method(user):
    """
    For ZTN-based secondary verification fallback. You can enhance this:
    - WebAuthn verification (recommended)
    - Compare known device/browser
    - IP or geolocation match
    - Admin approval
    """
    try:
        user_ip = request.remote_addr
        user_agent = request.user_agent.string
        location = get_ip_location(user_ip)

        # TODO: Replace with real secondary auth like WebAuthn or SMS
        if user.trusted_ip == user_ip and user.trusted_device in user_agent:
            return True
    except:
        pass
    return False

def generate_challenge():
    return base64.b64encode(os.urandom(32)).decode("utf-8")




import hashlib
from flask import request, has_request_context

def get_request_fingerprint():
    if not has_request_context():
        return "no-request-context"

    # 🛡 Trust real client IP forwarded by NGINX
    ip = (
        request.headers.get("X-Real-IP")
        or request.headers.get("X-Forwarded-For")
        or request.remote_addr
        or "unknown"
    )

    ua = request.headers.get("User-Agent", "unknown").lower().strip()

    raw_fp = f"{ip}|{ua}"
    return hashlib.sha256(raw_fp.encode()).hexdigest()


