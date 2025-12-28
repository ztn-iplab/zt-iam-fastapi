from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import UserAccessControl, UserRole
from app.security import get_jwt_identity, verify_session_fingerprint

router = APIRouter(prefix="/api", tags=["Roles"])


class RoleAssign(BaseModel):
    user_id: int
    role_id: int
    access_level: str = "read"


@router.get("/roles", dependencies=[Depends(verify_session_fingerprint)])
def get_roles(request: Request, db: Session = Depends(get_db)):
    _ = get_jwt_identity(request)
    roles = db.query(UserRole).all()
    return [
        {
            "id": role.id,
            "role_name": role.role_name,
            "permissions": role.permissions if hasattr(role, "permissions") else None,
        }
        for role in roles
    ]


@router.get("/user/{user_id}", dependencies=[Depends(verify_session_fingerprint)])
def get_user_role(user_id: int, request: Request, db: Session = Depends(get_db)):
    _ = get_jwt_identity(request)
    user_access = db.query(UserAccessControl).filter_by(user_id=user_id).first()
    if not user_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no assigned role"
        )
    user_role = db.query(UserRole).get(user_access.role_id)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User role not found"
        )
    return {"user_id": user_id, "role": user_role.role_name}


@router.post("/assign_role", dependencies=[Depends(verify_session_fingerprint)])
def assign_role(payload: RoleAssign, request: Request, db: Session = Depends(get_db)):
    _ = get_jwt_identity(request)
    user_access = db.query(UserAccessControl).filter_by(user_id=payload.user_id).first()
    if user_access:
        user_access.role_id = payload.role_id
        user_access.access_level = payload.access_level
    else:
        user_access = UserAccessControl(
            user_id=payload.user_id,
            role_id=payload.role_id,
            access_level=payload.access_level,
        )
        db.add(user_access)

    db.commit()
    return {
        "message": "Role assigned successfully",
        "user_id": payload.user_id,
        "role_id": payload.role_id,
    }
