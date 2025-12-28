import hashlib
import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RealTimeLog, User, UserAccessControl, UserRole
from utils.location import get_ip_location

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHMS = ["HS256"]
ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")


def _extract_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    return request.cookies.get(ACCESS_COOKIE_NAME)


def decode_access_token(request: Request) -> dict:
    token = _extract_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid token: {exc}",
        ) from exc


def get_jwt_identity(request: Request) -> str:
    payload = decode_access_token(request)
    return str(payload.get("sub", ""))


def get_request_fingerprint(request: Request, tenant_id: Optional[int] = None) -> str:
    ip = (
        request.headers.get("X-Real-IP")
        or request.headers.get("X-Forwarded-For")
        or (request.client.host if request.client else None)
        or "unknown"
    )
    ua = request.headers.get("User-Agent", "unknown").lower().strip()
    tenant_str = str(tenant_id) if tenant_id else "unknown-tenant"
    raw_fp = f"{tenant_str}|{ip}|{ua}"
    return hashlib.sha256(raw_fp.encode()).hexdigest()


def verify_session_fingerprint(
    request: Request, db: Session = Depends(get_db)
) -> None:
    payload = decode_access_token(request)
    token_fp = payload.get("fp")
    if not token_fp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session fingerprint missing. Please log in again.",
        )

    user_id = payload.get("sub")
    request_fp = get_request_fingerprint(request)

    if token_fp == request_fp:
        return

    role = "unknown"
    if user_id:
        user = db.query(User).get(user_id)
        if user:
            access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
            if access:
                role_obj = db.query(UserRole).get(access.role_id)
                if role_obj:
                    role = role_obj.role_name

    db.add(
        RealTimeLog(
            user_id=user_id,
            action=f"Session hijack attempt on {role} account (fingerprint mismatch)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session fingerprint mismatch. Access denied.",
    )
