import os

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, UserAccessControl, UserRole
from app.security import get_jwt_identity


def _webauthn_allowed() -> bool:
    return os.getenv("ZT_DISABLE_WEBAUTHN", "").lower() not in {"1", "true", "yes"}


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def require_totp_setup(
    request: Request, user: User = Depends(get_current_user)
) -> None:
    if not user.otp_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOTP setup required",
        )


def require_full_mfa(request: Request) -> None:
    if not request.session.get("mfa_totp_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOTP verification required",
        )
    if _webauthn_allowed() and request.session.get("mfa_webauthn_required"):
        if request.session.get("mfa_webauthn_verified"):
            return
        if not request.session.get("mfa_webauthn_has_credentials"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="WebAuthn setup required",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Passkey or biometric authentication required",
        )


def role_required(required_roles: list[str]):
    def checker(
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> None:
        access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
        if not access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no assigned role")
        role = db.query(UserRole).get(access.role_id)
        if not role or role.role_name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Insufficient permissions"
            )

    return checker
