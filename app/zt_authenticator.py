import base64
import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import jwt
import qrcode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.jwt import JWT_ALGORITHM, JWT_SECRET


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_pepper() -> str:
    return os.getenv("ZT_TOTP_PEPPER") or (JWT_SECRET or "")


def generate_nonce() -> str:
    return secrets.token_urlsafe(32)


def build_device_proof_message(nonce: str, device_id: str, rp_id: str, otp: str) -> bytes:
    payload = f"{nonce}|{device_id}|{rp_id}|{otp}"
    return payload.encode("utf-8")


def verify_p256_signature(public_key_b64: str, message: bytes, signature_b64: str) -> bool:
    try:
        public_key_bytes = base64.b64decode(public_key_b64)
        signature_bytes = base64.b64decode(signature_b64)
    except (ValueError, TypeError):
        return False

    try:
        key = serialization.load_der_public_key(public_key_bytes)
        if not isinstance(key, ec.EllipticCurvePublicKey):
            return False
        key.verify(signature_bytes, message, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError):
        return False


def hash_otp(otp: str) -> str:
    pepper = _get_pepper()
    data = (otp + pepper).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def generate_recovery_codes(count: int = 8) -> list[str]:
    return [secrets.token_hex(4) for _ in range(count)]


def hash_recovery_code(code: str) -> str:
    pepper = _get_pepper()
    data = (code + pepper).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def issue_enroll_token(payload: dict, ttl_minutes: int = 10) -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET_KEY is required for enrollment tokens")
    body = payload.copy()
    body["purpose"] = "zt_enroll"
    body["exp"] = _utcnow() + timedelta(minutes=ttl_minutes)
    return jwt.encode(body, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_enroll_token(token: str) -> dict:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET_KEY is required for enrollment tokens")
    data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if data.get("purpose") != "zt_enroll":
        raise ValueError("Invalid enrollment token")
    return data


def build_enrollment_payload(
    *,
    email: str,
    rp_id: str,
    rp_display_name: str,
    issuer: str,
    account_name: str,
    device_label: str,
    enroll_token: str,
    api_base_url: str,
) -> dict[str, Any]:
    return {
        "type": "zt_totp_enroll",
        "email": email,
        "rp_id": rp_id,
        "rp_display_name": rp_display_name,
        "issuer": issuer,
        "account_name": account_name,
        "device_label": device_label,
        "enroll_token": enroll_token,
        "api_base_url": api_base_url,
    }


def generate_enrollment_qr(payload: dict[str, Any]) -> str:
    qr = qrcode.make(json.dumps(payload))
    buffer = base64.b64encode(_qr_to_png(qr))
    return f"data:image/png;base64,{buffer.decode()}"


def build_enrollment_code(payload: dict[str, Any]) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    return f"ZTENROLL:{encoded.rstrip('=')}"


_ENROLL_CODE_STORE: dict[str, tuple[dict[str, Any], datetime]] = {}


def issue_enrollment_code(payload: dict[str, Any], ttl_minutes: int = 10) -> str:
    code = base64.b32encode(os.urandom(5)).decode("ascii").rstrip("=")
    expires_at = _utcnow() + timedelta(minutes=ttl_minutes)
    _ENROLL_CODE_STORE[code] = (payload, expires_at)
    return code


def resolve_enrollment_code(code: str) -> Optional[dict[str, Any]]:
    entry = _ENROLL_CODE_STORE.get(code)
    if not entry:
        return None
    payload, expires_at = entry
    if expires_at < _utcnow():
        _ENROLL_CODE_STORE.pop(code, None)
        return None
    return payload


def _qr_to_png(qr) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()


def resolve_rp_id(request, fallback_name: str) -> str:
    host = getattr(request.url, "hostname", None)
    base_url = os.getenv("PUBLIC_BASE_URL")
    if base_url:
        try:
            parsed = urlparse(base_url)
            if parsed.hostname:
                if host in {"localhost", "127.0.0.1", "localhost.localdomain.com"}:
                    return parsed.hostname
                if not host:
                    return parsed.hostname
        except Exception:
            pass
    if host:
        return host
    return fallback_name


def resolve_api_base_url(
    request,
    default_path: str,
    override_env: str = "ZT_AUTH_API_BASE_URL",
) -> str:
    explicit = os.getenv(override_env)
    if explicit:
        return explicit.rstrip("/")
    base_url = os.getenv("PUBLIC_BASE_URL")
    if base_url:
        return base_url.rstrip("/") + default_path
    return str(request.base_url).rstrip("/") + default_path
