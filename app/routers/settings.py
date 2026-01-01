from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RealTimeLog, User, UserAccessControl, UserRole
from app.security import get_jwt_identity, verify_session_fingerprint
from utils.email_alerts import send_admin_alert
from utils.location import get_ip_location

router = APIRouter(prefix="/settings", tags=["Settings"])
templates = Jinja2Templates(directory="templates")


class ProfileUpdate(BaseModel):
    country: str


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(verify_session_fingerprint)])
def settings_home(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = "user"
    if access:
        role_obj = db.query(UserRole).get(access.role_id)
        if role_obj:
            role = role_obj.role_name.lower()
    dashboard_urls = {
        "admin": "/admin/dashboard",
        "agent": "/agent/dashboard",
        "user": "/user/dashboard",
    }
    dashboard_url = dashboard_urls.get(role, "/user/dashboard")
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "user": user, "role": role, "dashboard_url": dashboard_url},
    )


@router.get("/change-password", response_class=HTMLResponse, dependencies=[Depends(verify_session_fingerprint)])
def change_password(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})


@router.get("/reset-totp", response_class=HTMLResponse, dependencies=[Depends(verify_session_fingerprint)])
def reset_totp(request: Request):
    return templates.TemplateResponse("reset_totp.html", {"request": request})


@router.get("/reset-webauthn", response_class=HTMLResponse, dependencies=[Depends(verify_session_fingerprint)])
def reset_webauthn(request: Request):
    return templates.TemplateResponse("reset_webauthn.html", {"request": request})


@router.post("/update-profile", dependencies=[Depends(verify_session_fingerprint)])
def update_profile(
    payload: ProfileUpdate, request: Request, db: Session = Depends(get_db)
):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_country = payload.country.strip()
    if not new_country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Country is required"
        )

    user.country = new_country
    db.add(
        RealTimeLog(
            user_id=user.id,
            action=f"Updated profile info (country: {new_country})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "Profile updated successfully."}


@router.post("/request-deletion", dependencies=[Depends(verify_session_fingerprint)])
def request_account_deletion(request: Request, db: Session = Depends(get_db)):
    user_id = get_jwt_identity(request)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.deletion_requested:
        return {"message": "Your account deletion is already under review."}

    user.deletion_requested = True
    db.add(
        RealTimeLog(
            user_id=user.id,
            action="Requested account deletion",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            risk_alert=True,
            tenant_id=1,
        )
    )
    send_admin_alert(
        user=user,
        event_type="account_deletion_request",
        ip_address=request.client.host if request.client else None,
        location=get_ip_location(request.client.host if request.client else ""),
        device_info=request.headers.get("User-Agent", ""),
    )
    db.commit()
    return {
        "message": "Account deletion request submitted. Admins will review it shortly."
    }
