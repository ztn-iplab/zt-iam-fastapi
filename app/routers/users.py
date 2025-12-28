from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_full_mfa, require_totp_setup
from app.models import SIMCard, User, UserAccessControl, UserRole
from app.security import get_jwt_identity, verify_session_fingerprint

router = APIRouter(tags=["Users"])
templates = Jinja2Templates(directory="templates")


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None
    country: Optional[str] = None
    identity_verified: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    country: Optional[str] = None
    identity_verified: Optional[bool] = None
    password: Optional[str] = None


@router.get(
    "/user/dashboard",
    response_class=HTMLResponse,
    dependencies=[
        Depends(verify_session_fingerprint),
        Depends(require_totp_setup),
        Depends(require_full_mfa),
    ],
)
def user_dashboard(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "user": user})


@router.post("/users", dependencies=[Depends(verify_session_fingerprint)])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    new_user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        country=payload.country,
        identity_verified=payload.identity_verified,
        tenant_id=1,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "first_name": new_user.first_name,
        "email": new_user.email,
        "country": new_user.country,
        "identity_verified": new_user.identity_verified,
    }


@router.get("/user", dependencies=[Depends(verify_session_fingerprint)])
def get_user(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role = "user"
    user_access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    if user_access:
        user_role = db.query(UserRole).get(user_access.role_id)
        if user_role:
            role = user_role.role_name

    sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = sim.mobile_number if sim else None

    return {
        "id": user.id,
        "mobile_number": mobile_number,
        "first_name": user.first_name,
        "email": user.email,
        "country": user.country,
        "identity_verified": user.identity_verified,
        "trust_score": user.trust_score,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "role": role,
        "wallet": None if role == "admin" else (
            None
            if not user.wallet
            else {
                "balance": user.wallet.balance,
                "currency": user.wallet.currency,
                "last_transaction_at": user.wallet.last_transaction_at.isoformat()
                if user.wallet.last_transaction_at
                else None,
            }
        ),
    }


@router.put("/user", dependencies=[Depends(verify_session_fingerprint)])
def update_user(
    payload: UserUpdate, request: Request, db: Session = Depends(get_db)
):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.country is not None:
        user.country = payload.country
    if payload.identity_verified is not None:
        user.identity_verified = payload.identity_verified
    if payload.password:
        user.password = payload.password

    db.commit()
    return {"message": "User updated successfully"}


@router.delete("/user", dependencies=[Depends(verify_session_fingerprint)])
def delete_user(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/user/profile", dependencies=[Depends(verify_session_fingerprint)])
def profile(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = sim.mobile_number if sim else None

    return {
        "id": user.id,
        "mobile_number": mobile_number,
        "first_name": user.first_name,
        "country": user.country,
        "identity_verified": user.identity_verified,
    }


@router.post("/user/request_deletion", dependencies=[Depends(verify_session_fingerprint)])
def request_deletion(request: Request):
    _ = get_jwt_identity(request)
    return {
        "message": "Your account deletion request has been submitted. An administrator will review your request shortly."
    }


@router.get("/user-info/{mobile_number}", dependencies=[Depends(verify_session_fingerprint)])
def get_user_info(mobile_number: str, request: Request, db: Session = Depends(get_db)):
    _ = get_jwt_identity(request)
    sim = db.query(SIMCard).filter_by(mobile_number=mobile_number).first()
    if not sim or not sim.user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this mobile number.",
        )

    user = sim.user
    return {
        "id": user.id,
        "mobile_number": sim.mobile_number,
        "name": f"{user.first_name} {user.last_name or ''}".strip() or "Unknown",
    }


@router.get(
    "/setup-totp",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_session_fingerprint)],
)
def show_totp_setup(request: Request):
    return templates.TemplateResponse("setup_totp.html", {"request": request})
