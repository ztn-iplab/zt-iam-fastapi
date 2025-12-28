import json
import random
import threading
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from app.db import SessionLocal, get_db
from app.deps import require_full_mfa, role_required
from app.models import (
    HeadquartersWallet,
    RealTimeLog,
    SIMCard,
    Tenant,
    TenantPasswordHistory,
    TenantTrustPolicyFile,
    TenantUser,
    Transaction,
    User,
    UserAccessControl,
    UserAuthLog,
    UserRole,
    Wallet,
    WebAuthnCredential,
)
from app.security import get_jwt_identity, verify_session_fingerprint
from utils.email_alerts import send_rotated_api_key_email, send_tenant_api_key_email
from utils.location import get_ip_location
from utils.security import generate_custom_api_key, is_strong_password

router = APIRouter(tags=["Admin"])
templates = Jinja2Templates(directory="templates")

ZTN_MASTER_TENANT_ID = 1


def _finalize_reversal(reversal_id: int, sender_wallet_id: int, amount: float) -> None:
    db = SessionLocal()
    try:
        reversal_tx = db.query(Transaction).get(reversal_id)
        sender_wallet = db.query(Wallet).get(sender_wallet_id)

        if not reversal_tx or not sender_wallet:
            return
        if reversal_tx.status != "pending":
            return

        sender_wallet.balance += float(amount)
        reversal_tx.status = "completed"

        try:
            tx_meta = json.loads(reversal_tx.transaction_metadata or "{}")
            original_tx_id = tx_meta.get("reversal_of_transaction_id", "Unknown")
        except Exception:
            original_tx_id = "Unknown"

        db.add(
            RealTimeLog(
                user_id=reversal_tx.user_id,
                action=f"Reversal completed: {amount} RWF refunded to sender for TX #{original_tx_id}",
                ip_address="System",
                device_info="Auto Processor",
                location="Headquarters",
                risk_alert=False,
                tenant_id=1,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _generate_unique_mobile_number(db: Session) -> str:
    while True:
        new_number = "0787" + str(random.randint(100000, 999999))
        existing_number = db.query(SIMCard).filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number


def _generate_unique_iccid(db: Session) -> str:
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = db.query(SIMCard).filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid


@router.get(
    "/admin/dashboard",
    response_class=HTMLResponse,
    dependencies=[
        Depends(verify_session_fingerprint),
        Depends(role_required(["admin"])),
        Depends(require_full_mfa),
    ],
)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    role = db.query(UserRole).get(user_access.role_id).role_name if user_access else "Unknown"

    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    admin_user = {"first_name": user.first_name, "full_name": full_name, "role": role}
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": admin_user})


@router.get(
    "/admin/users",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    users_list = []
    for u in users:
        primary_sim = db.query(SIMCard).filter_by(user_id=u.id, status="active").first()
        access = (
            db.query(UserAccessControl)
            .join(UserRole, UserAccessControl.role_id == UserRole.id)
            .filter(
                UserAccessControl.user_id == u.id,
                UserAccessControl.tenant_id == ZTN_MASTER_TENANT_ID,
                UserRole.tenant_id == ZTN_MASTER_TENANT_ID,
            )
            .first()
        )
        if not access or not access.role:
            continue

        role_name = access.role.role_name
        is_locked = u.locked_until is not None and u.locked_until > datetime.utcnow()
        users_list.append(
            {
                "id": u.id,
                "name": f"{u.first_name} {u.last_name or ''}".strip(),
                "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",
                "email": u.email,
                "role": role_name,
                "is_locked": is_locked,
                "locked_until": u.locked_until.isoformat() if u.locked_until else None,
            }
        )
    return users_list


@router.post("/admin/assign_role", dependencies=[Depends(role_required(["admin"]))])
def assign_role(payload: dict, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role = db.query(UserRole).get(payload.get("role_id"))
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role ID")

    if role.tenant_id != ZTN_MASTER_TENANT_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cross-tenant role assignment is not allowed",
        )

    user_access = db.query(UserAccessControl).filter_by(
        user_id=user.id, tenant_id=ZTN_MASTER_TENANT_ID
    ).first()

    if user_access:
        user_access.role_id = role.id
        user_access.access_level = payload.get("access_level", "read")
    else:
        db.add(
            UserAccessControl(
                user_id=user.id,
                role_id=role.id,
                tenant_id=ZTN_MASTER_TENANT_ID,
                access_level=payload.get("access_level", "read"),
            )
        )

    user_sim = db.query(SIMCard).filter_by(user_id=user.id, status="active").first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"
    admin_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=admin_id,
            tenant_id=ZTN_MASTER_TENANT_ID,
            action=f"Assigned role '{role.role_name}' to user {user.first_name} {user.last_name} ({mobile_number})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
        )
    )
    db.commit()
    return {"message": f"Role '{role.role_name}' assigned to user with mobile {mobile_number}"}


@router.put(
    "/admin/suspend_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def suspend_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user_id = int(get_jwt_identity(request))
    if current_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins are not allowed to suspend their own accounts.",
        )

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    user.deletion_requested = True

    admin_user = db.query(User).get(current_user_id)
    user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    db.add(
        RealTimeLog(
            user_id=admin_user.id,
            action=f"Suspended user {user.first_name} {user.last_name} ({mobile_number}) and marked for deletion.",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "User has been suspended and marked for deletion."}


@router.put(
    "/admin/verify_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def verify_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = True
    user.deletion_requested = False

    admin_id = int(get_jwt_identity(request))
    admin_user = db.query(User).get(admin_id)

    user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    db.add(
        RealTimeLog(
            user_id=admin_user.id if admin_user else None,
            action=f"Verified and reactivated user {user.first_name} {user.last_name} ({mobile_number})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "User account has been activated and verified."}


@router.delete(
    "/admin/delete_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user_id = int(get_jwt_identity(request))
    if current_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins are not allowed to delete their own accounts.",
        )

    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.deletion_requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not requested account deletion.",
        )

    user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    admin_user = db.query(User).get(current_user_id)
    db.add(
        RealTimeLog(
            user_id=admin_user.id if admin_user else None,
            action=f"Deleted user {user.first_name} {user.last_name} ({mobile_number}) and all associated records",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=True,
            tenant_id=1,
        )
    )

    db.query(Wallet).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(Transaction).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(UserAuthLog).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(SIMCard).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(UserAccessControl).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(RealTimeLog).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()

    return {
        "message": f"User with mobile {mobile_number} and all related data have been permanently deleted."
    }


@router.put(
    "/admin/edit_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def edit_user(user_id: int, payload: dict, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    changes = []
    if "first_name" in payload:
        user.first_name = payload["first_name"]
        changes.append("first_name")
    if "last_name" in payload:
        user.last_name = payload["last_name"]
        changes.append("last_name")
    if "email" in payload:
        existing_email = db.query(User).filter_by(email=payload["email"]).first()
        if existing_email and existing_email.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = payload["email"]
        changes.append("email")

    if "mobile_number" in payload:
        existing_sim = db.query(SIMCard).filter_by(mobile_number=payload["mobile_number"]).first()
        if existing_sim and existing_sim.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Mobile number already in use"
            )

        user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
        if user_sim:
            user_sim.mobile_number = payload["mobile_number"]
            changes.append("mobile_number")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No SIM card linked to this user"
            )

    if changes:
        admin_id = int(get_jwt_identity(request))
        user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
        mobile_number = user_sim.mobile_number if user_sim else "N/A"

        db.add(
            RealTimeLog(
                user_id=admin_id,
                action=(
                    "Edited user "
                    f"{user.first_name} {user.last_name} ({mobile_number}) "
                    f"- Fields updated: {', '.join(changes)}"
                ),
                ip_address=request.client.host if request.client else None,
                device_info=request.headers.get("User-Agent", "Admin Panel"),
                location="Headquarters",
                risk_alert=False,
                tenant_id=1,
            )
        )

    db.commit()
    return {"message": "User updated successfully."}


@router.get(
    "/admin/edit_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_edit_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name or "",
        "email": user.email,
        "mobile_number": user_sim.mobile_number if user_sim else "",
    }


@router.get(
    "/admin/generate_sim",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def generate_sim(request: Request, db: Session = Depends(get_db)):
    new_iccid = _generate_unique_iccid(db)
    new_mobile_number = _generate_unique_mobile_number(db)

    new_sim = SIMCard(
        iccid=new_iccid,
        mobile_number=new_mobile_number,
        network_provider="MTN Rwanda",
        status="unregistered",
        registered_by="Admin",
    )
    db.add(new_sim)

    admin_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=admin_id,
            action=f"Admin generated SIM: {new_iccid} with mobile {new_mobile_number}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    return {"iccid": new_sim.iccid, "mobile_number": new_sim.mobile_number}


@router.get(
    "/admin/view_user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def view_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    primary_sim = db.query(SIMCard).filter_by(user_id=user.id, status="active").first()
    access = db.query(UserAccessControl).filter_by(
        user_id=user.id, tenant_id=ZTN_MASTER_TENANT_ID
    ).first()
    user_role = db.query(UserRole).get(access.role_id) if access else None
    role_name = user_role.role_name if user_role else "N/A"

    admin_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=admin_id,
            action=f"Viewed profile of {user.first_name} {user.last_name or ''} ({primary_sim.mobile_number if primary_sim else 'N/A'})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin Panel"),
            location="Headquarters",
            risk_alert=False,
            tenant_id=ZTN_MASTER_TENANT_ID,
        )
    )
    db.commit()

    return {
        "id": user.id,
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "mobile_number": primary_sim.mobile_number if primary_sim else "N/A",
        "email": user.email,
        "role": role_name,
        "is_verified": user.identity_verified,
        "is_suspended": not user.is_active,
        "can_assign_role": True,
        "can_suspend": not user.is_active,
        "can_verify": not user.identity_verified,
        "can_delete": True,
        "can_edit": True,
    }


@router.post(
    "/admin/fund-agent",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def fund_agent(payload: dict, request: Request, db: Session = Depends(get_db)):
    admin_id = int(get_jwt_identity(request))
    agent_mobile = payload.get("agent_mobile")
    raw_amount = payload.get("amount")
    device_info = payload.get("device_info")
    location = payload.get("location")

    if not agent_mobile or raw_amount is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing agent mobile or amount."
        )

    try:
        amount = Decimal(str(raw_amount))
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount.")
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be a valid number.")

    hq_wallet = db.query(HeadquartersWallet).first()
    if not hq_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HQ Wallet not found")

    hq_balance = Decimal(str(hq_wallet.balance or 0))
    if hq_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient HQ funds. Available: {hq_balance} RWF, Requested: {amount} RWF",
        )

    agent_sim = db.query(SIMCard).filter_by(mobile_number=agent_mobile).first()
    if not agent_sim or not agent_sim.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Agent SIM is not assigned to any user."
        )

    agent = db.query(User).get(agent_sim.user_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent user not found.")

    agent_wallet = db.query(Wallet).filter_by(user_id=agent.id).first()
    if not agent_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent wallet not found")

    hq_wallet.balance = float(hq_wallet.balance or 0) - float(amount)
    agent_wallet.balance += float(amount)

    float_tx = Transaction(
        user_id=agent.id,
        amount=float(amount),
        transaction_type="float_received",
        status="completed",
        location=json.dumps(location),
        device_info=json.dumps(device_info),
        transaction_metadata=json.dumps(
            {"from_admin": admin_id, "approved_by": "admin", "float_source": "HQ Wallet"}
        ),
        fraud_flag=False,
        risk_score=0.0,
        tenant_id=1,
    )
    db.add(float_tx)

    db.add(
        RealTimeLog(
            user_id=admin_id,
            action=f"Funded agent {agent.first_name} ({agent_mobile}) with {amount} RWF from HQ Wallet",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent"),
            location=json.dumps(location),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": f"{amount} RWF successfully sent to {agent.first_name} ({agent_mobile})"}


@router.get(
    "/admin/hq-balance",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_hq_balance(db: Session = Depends(get_db)):
    hq_wallet = db.query(HeadquartersWallet).first()
    if not hq_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HQ Wallet not found")
    return {"balance": round(float(hq_wallet.balance or 0), 2)}


@router.get(
    "/admin/float-history",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def float_history(db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction)
        .filter_by(transaction_type="float_received")
        .order_by(Transaction.timestamp.desc())
        .limit(20)
        .all()
    )
    result = []
    for tx in transactions:
        agent = db.query(User).get(tx.user_id)
        sim = db.query(SIMCard).filter_by(user_id=agent.id).first() if agent else None
        result.append(
            {
                "timestamp": tx.timestamp,
                "amount": tx.amount,
                "agent_name": f"{agent.first_name} {agent.last_name}" if agent else "Unknown",
                "agent_mobile": sim.mobile_number if sim else "N/A",
            }
        )
    return {"transfers": result}


@router.get(
    "/admin/flagged-transactions",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_flagged_transactions(db: Session = Depends(get_db)):
    flagged = db.query(Transaction).filter_by(fraud_flag=True).order_by(Transaction.timestamp.desc()).all()
    result = []
    for tx in flagged:
        user = db.query(User).get(tx.user_id)
        result.append(
            {
                "id": tx.id,
                "user": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "amount": tx.amount,
                "type": tx.transaction_type,
                "risk_score": tx.risk_score,
                "status": tx.status,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M"),
            }
        )
    return result


@router.get(
    "/admin/real-time-logs",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_real_time_logs(db: Session = Depends(get_db)):
    logs = db.query(RealTimeLog).order_by(RealTimeLog.timestamp.desc()).limit(50).all()
    result = []
    for log in logs:
        result.append(
            {
                "user": f"{log.user.first_name} {log.user.last_name}" if log.user else "Unknown",
                "action": log.action,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M"),
                "ip": log.ip_address,
                "location": log.location,
                "device": log.device_info,
                "risk_alert": log.risk_alert,
            }
        )
    return result


@router.get(
    "/admin/user-auth-logs",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_user_auth_logs(db: Session = Depends(get_db)):
    logs = db.query(UserAuthLog).order_by(UserAuthLog.auth_timestamp.desc()).limit(100).all()
    result = []
    for log in logs:
        user = db.query(User).get(log.user_id)
        result.append(
            {
                "user": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "method": log.auth_method,
                "status": log.auth_status,
                "timestamp": log.auth_timestamp.strftime("%Y-%m-%d %H:%M"),
                "ip": log.ip_address,
                "device": log.device_info,
                "location": log.location,
                "fails": log.failed_attempts,
            }
        )
    return result


@router.patch(
    "/admin/unlock-user/{user_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def unlock_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.locked_until = None
    db.commit()

    admin_id = int(get_jwt_identity(request))
    user_sim = db.query(SIMCard).filter_by(user_id=user.id).first()
    mobile_number = user_sim.mobile_number if user_sim else "N/A"

    db.add(
        RealTimeLog(
            user_id=admin_id,
            action=f"Unlocked user account for {user.first_name} {user.last_name} ({mobile_number})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location="Admin Panel",
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()
    return {"message": "User account unlocked"}


@router.get(
    "/admin/all-transactions",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def all_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(Transaction.timestamp.desc()).all()
    result = []
    for tx in transactions:
        user = db.query(User).get(tx.user_id)
        result.append(
            {
                "id": tx.id,
                "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "transaction_type": tx.transaction_type,
                "amount": tx.amount,
                "status": tx.status,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return {"transactions": result}


@router.post(
    "/admin/reverse-transfer/{transaction_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def reverse_transfer(transaction_id: int, request: Request, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction or transaction.transaction_type != "transfer" or transaction.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This transaction is not eligible for reversal."
        )

    try:
        metadata = json.loads(transaction.transaction_metadata or "{}")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid metadata: {exc}"
        ) from exc

    existing_reversal = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_type == "reversal",
            Transaction.transaction_metadata.contains(
                f'"reversal_of_transaction_id": {transaction.id}'
            ),
        )
        .first()
    )
    if existing_reversal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This transaction has already been reversed."
        )

    time_since_tx = datetime.utcnow() - transaction.timestamp
    if time_since_tx.total_seconds() > 86400:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This transaction is too old to be reversed."
        )

    sender_id = transaction.user_id
    recipient_id = metadata.get("recipient_id")
    if not recipient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing recipient info in metadata."
        )

    sender_wallet = db.query(Wallet).filter_by(user_id=sender_id).first()
    recipient_wallet = db.query(Wallet).filter_by(user_id=recipient_id).first()
    if not sender_wallet or not recipient_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One of the wallets is missing")
    if recipient_wallet.balance < transaction.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipient does not have sufficient balance for reversal",
        )

    recipient_wallet.balance -= transaction.amount
    reversal_metadata = {
        "reversal_of_transaction_id": transaction.id,
        "original_sender": sender_id,
        "original_recipient": recipient_id,
        "reversed_by_admin": int(get_jwt_identity(request)),
        "delayed_refund": True,
    }

    reversal = Transaction(
        user_id=sender_id,
        amount=transaction.amount,
        transaction_type="reversal",
        status="pending",
        transaction_metadata=json.dumps(reversal_metadata),
        timestamp=datetime.utcnow(),
        tenant_id=1,
    )
    db.add(reversal)

    admin_user = db.query(User).get(int(get_jwt_identity(request)))
    db.add(
        RealTimeLog(
            user_id=admin_user.id if admin_user else None,
            action=f"Reversal initiated: TX #{transaction.id} - {transaction.amount} RWF back to sender",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Admin HQ"),
            location="Headquarters",
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()

    threading.Timer(
        10, _finalize_reversal, args=(reversal.id, sender_wallet.id, transaction.amount)
    ).start()

    return {"message": "Reversal initiated. Refund will be processed shortly.", "reversed_transaction_id": reversal.id}


@router.get("/api/admin/metrics", dependencies=[Depends(verify_session_fingerprint)])
def admin_dashboard_metrics(request: Request, db: Session = Depends(get_db)):
    def daterange(start_date, end_date):
        for n in range((end_date - start_date).days + 1):
            yield start_date + timedelta(n)

    from_str = request.query_params.get("from")
    to_str = request.query_params.get("to")

    now = datetime.utcnow()
    default_from = (now - timedelta(days=7)).date()
    default_to = now.date()

    try:
        start_date = datetime.strptime(from_str, "%Y-%m-%d").date() if from_str else default_from
        end_date = datetime.strptime(to_str, "%Y-%m-%d").date() if to_str else default_to
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")

    login_methods = {
        "password": db.query(UserAuthLog).filter_by(auth_method="password", auth_status="success").count(),
        "totp": db.query(UserAuthLog).filter_by(auth_method="totp", auth_status="success").count(),
        "webauthn": db.query(UserAuthLog).filter_by(auth_method="webauthn", auth_status="success").count(),
    }

    failures = (
        db.query(func.date(UserAuthLog.auth_timestamp).label("day"), func.count().label("count"))
        .filter(
            UserAuthLog.auth_status == "failed",
            func.date(UserAuthLog.auth_timestamp) >= start_date,
            func.date(UserAuthLog.auth_timestamp) <= end_date,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    failure_dict = {r.day.strftime("%Y-%m-%d"): r.count for r in failures}
    padded_dates = [d.strftime("%Y-%m-%d") for d in daterange(start_date, end_date)]
    padded_counts = [failure_dict.get(d, 0) for d in padded_dates]
    auth_failures = {"dates": padded_dates, "counts": padded_counts}

    actor_query = text(
        """
        SELECT
            CASE
                WHEN transaction_metadata::json->>'initiated_by' = 'user' THEN 'user'
                WHEN transaction_metadata::json->>'transfer_by' = 'Agent' THEN 'agent'
                WHEN transaction_metadata::json->>'withdrawal_method' = 'Agent Processed' THEN 'agent'
                ELSE 'admin'
            END AS actor,
            COUNT(*) AS count
        FROM transactions
        GROUP BY actor
        """
    )
    actor_results = db.execute(actor_query).fetchall()
    actor_counts = {row[0]: row[1] for row in actor_results}
    transaction_sources = [
        actor_counts.get("user", 0),
        actor_counts.get("agent", 0),
        actor_counts.get("admin", 0),
    ]

    flagged = {
        "flagged": db.query(Transaction).filter(Transaction.risk_score >= 0.7).count(),
        "clean": db.query(Transaction).filter(Transaction.risk_score < 0.7).count(),
    }

    user_states = {
        "active": db.query(User).filter_by(is_active=True).count(),
        "inactive": db.query(User).filter_by(is_active=False).count(),
        "suspended": db.query(User).filter(User.locked_until.isnot(None)).count(),
        "unverified": db.query(User).filter_by(identity_verified=False).count(),
    }

    sim_stats = {
        "new": db.query(SIMCard).filter(SIMCard.status == "active").count(),
        "swapped": db.query(SIMCard).filter(SIMCard.status == "swapped").count(),
        "suspended": db.query(SIMCard).filter(SIMCard.status == "suspended").count(),
    }

    multi_failures = (
        db.query(UserAuthLog.user_id, func.count().label("fail_count"))
        .filter(
            UserAuthLog.auth_status == "failed",
            UserAuthLog.auth_timestamp >= datetime.utcnow() - timedelta(days=1),
        )
        .group_by(UserAuthLog.user_id)
        .having(func.count() >= 3)
        .all()
    )
    flagged_users = (
        db.query(Transaction.user_id, func.count().label("flagged_count"))
        .filter(Transaction.risk_score >= 0.7)
        .group_by(Transaction.user_id)
        .having(func.count() >= 1)
        .all()
    )
    anomalies = {
        "multiple_failed_logins": [{"user_id": u.user_id, "count": u.fail_count} for u in multi_failures],
        "frequent_flagged_users": [{"user_id": u.user_id, "count": u.flagged_count} for u in flagged_users],
    }

    logs = [
        {"location": log.location or "Unknown"}
        for log in db.query(RealTimeLog)
        .filter(func.date(RealTimeLog.timestamp) >= start_date, func.date(RealTimeLog.timestamp) <= end_date)
        .limit(1000)
        .all()
    ]

    return {
        "login_methods": login_methods,
        "auth_failures": auth_failures,
        "transaction_sources": transaction_sources,
        "flagged": flagged,
        "user_states": user_states,
        "sim_stats": sim_stats,
        "anomalies": anomalies,
        "logs": logs,
    }


@router.post(
    "/admin/register-tenant",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def register_tenant(payload: dict, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(int(get_jwt_identity(request)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    if not user_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

    user_role = db.query(UserRole).get(user_access.role_id)
    if not user_role or user_role.role_name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can register tenants."
        )

    name = payload.get("name")
    contact_email = payload.get("contact_email")
    custom_api_key = payload.get("api_key")
    admin_info = payload.get("admin_user")

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant name is required.")
    if not contact_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Contact email is required."
        )
    if db.query(Tenant).filter_by(name=name).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A tenant with this name already exists."
        )

    tenant_api_key = custom_api_key or generate_custom_api_key(name)

    new_tenant = Tenant(name=name, api_key=tenant_api_key, contact_email=contact_email)
    db.add(new_tenant)
    db.flush()

    if admin_info:
        required_fields = ["mobile_number", "first_name", "email", "password"]
        for field in required_fields:
            if not admin_info.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Admin user {field} is required."
                )

        sim_card = (
            db.query(SIMCard)
            .filter_by(mobile_number=admin_info["mobile_number"], status="active")
            .first()
        )
        if not sim_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mobile number not valid or not active"
            )

        linked_user = db.query(User).get(sim_card.user_id)
        if not linked_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not linked to any user")

        if db.query(TenantUser).filter_by(tenant_id=new_tenant.id, user_id=linked_user.id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user already exists under this tenant."
            )

        if not is_strong_password(admin_info["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin password does not meet security requirements.",
            )

        tenant_user = TenantUser(
            tenant_id=new_tenant.id,
            user_id=linked_user.id,
            company_email=admin_info["email"],
            password_hash=generate_password_hash(admin_info["password"]),
        )
        db.add(tenant_user)

        admin_role = db.query(UserRole).filter_by(role_name="admin", tenant_id=new_tenant.id).first()
        if not admin_role:
            admin_role = UserRole(role_name="admin", tenant_id=new_tenant.id)
            db.add(admin_role)
            db.flush()

        db.add(
            UserAccessControl(
                user_id=linked_user.id,
                role_id=admin_role.id,
                access_level="full",
                tenant_id=new_tenant.id,
            )
        )

        db.add(
            RealTimeLog(
                user_id=linked_user.id,
                action=f"Initial Admin User Registered for Tenant: {name}",
                ip_address=request.client.host if request.client else None,
                device_info=request.headers.get("User-Agent", ""),
                location=get_ip_location(request.client.host if request.client else ""),
                tenant_id=new_tenant.id,
                risk_alert=False,
            )
        )

    db.add(
        RealTimeLog(
            user_id=user.id,
            action=f"Registered new Tenant: {name}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            tenant_id=new_tenant.id,
        )
    )
    db.commit()

    email_sent = False
    try:
        send_tenant_api_key_email(name, tenant_api_key, contact_email)
        email_sent = True
    except Exception:
        email_sent = False

    return {
        "message": "Tenant and Admin registered successfully.",
        "tenant_id": new_tenant.id,
        "api_key": tenant_api_key,
        "email_sent": email_sent,
    }


@router.post(
    "/admin/rotate-api-key/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def rotate_api_key(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    admin_user = db.query(User).get(int(get_jwt_identity(request)))
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    tenant = db.query(Tenant).get(tenant_id)
    if not tenant or tenant.name.lower() == "dummytenant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rotate key for this tenant."
        )

    old_key = tenant.api_key
    new_key = generate_custom_api_key(tenant.name)
    tenant.api_key = new_key
    tenant.api_key_rotated_at = datetime.utcnow()

    db.add(
        RealTimeLog(
            user_id=admin_user.id,
            action=f"Rotated API Key for Tenant: {tenant.name}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
            tenant_id=tenant.id,
        )
    )
    db.commit()

    try:
        send_rotated_api_key_email(tenant.name, new_key, tenant.contact_email)
    except Exception:
        pass

    return {"message": "API key rotated successfully."}


@router.get(
    "/admin/tenants",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def list_tenants(db: Session = Depends(get_db)):
    tenants = (
        db.query(Tenant)
        .filter(Tenant.name != "Master Tenant")
        .order_by(Tenant.created_at.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "name": t.name,
            "contact_email": t.contact_email,
            "plan": t.plan,
            "is_active": t.is_active,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            "last_api_access": t.last_api_access.strftime("%Y-%m-%d %H:%M:%S")
            if t.last_api_access
            else None,
            "api_score": float(t.api_score) if t.api_score is not None else 0.0,
        }
        for t in tenants
    ]


@router.post(
    "/admin/toggle-tenant/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def toggle_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = not tenant.is_active
    db.commit()
    return {"message": f"Tenant {'enabled' if tenant.is_active else 'suspended'}."}


@router.delete(
    "/admin/delete-tenant/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    try:
        tenant_user_ids = [
            tu.id
            for tu in db.query(TenantUser.id).filter_by(tenant_id=tenant_id).all()
        ]

        if tenant_user_ids:
            db.query(TenantPasswordHistory).filter(
                TenantPasswordHistory.tenant_user_id.in_(tenant_user_ids)
            ).delete(synchronize_session=False)

        db.query(UserAccessControl).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.query(WebAuthnCredential).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.query(TenantTrustPolicyFile).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.query(UserAuthLog).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.query(RealTimeLog).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.query(TenantUser).filter_by(tenant_id=tenant_id).delete(synchronize_session=False)
        db.delete(tenant)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant due to internal error",
        )

    return {"message": f"Tenant '{tenant.name}' deleted successfully"}


@router.put(
    "/admin/update-tenant/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def update_tenant(tenant_id: int, payload: dict, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).get(int(get_jwt_identity(request)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_access = db.query(UserAccessControl).filter_by(user_id=user.id).first()
    user_role = db.query(UserRole).get(user_access.role_id) if user_access else None
    if not user_role or user_role.role_name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update tenants."
        )

    tenant = db.query(Tenant).get(tenant_id)
    if not tenant or tenant.name.lower() == "mastertenant":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found or not editable.")

    new_email = payload.get("contact_email")
    new_plan = payload.get("plan")

    plan_changed = False
    if new_email:
        tenant.contact_email = new_email.strip()
    if new_plan and new_plan.strip().lower() != tenant.plan.lower():
        tenant.plan = new_plan.strip().lower()
        plan_changed = True

    if plan_changed:
        if tenant.plan == "premium":
            tenant.api_key_expires_at = datetime.utcnow() + timedelta(days=90)
        elif tenant.plan == "enterprise":
            tenant.api_key_expires_at = datetime.utcnow() + timedelta(days=365)
        else:
            tenant.api_key_expires_at = None

        tenant.api_score = 0.0
        tenant.api_request_count = 0
        tenant.api_error_count = 0
        tenant.api_last_reset = datetime.utcnow()

    db.commit()
    return {"message": "Tenant updated successfully."}


@router.post(
    "/admin/reset-trust-score/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def reset_trust_score(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    tenant.api_score = 0.0
    tenant.api_error_count = 0
    tenant.api_request_count = 0
    tenant.api_last_reset = datetime.utcnow()
    tenant.is_active = True
    db.commit()

    db.add(
        RealTimeLog(
            user_id=int(get_jwt_identity(request)),
            tenant_id=tenant.id,
            action=f"Trust score reset for tenant: {tenant.name}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else ""),
        )
    )
    db.commit()

    return {"message": f"Trust score reset for {tenant.name}."}


@router.get(
    "/admin/tenant-details/{tenant_id}",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["admin"]))],
)
def get_tenant_details(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return {
        "id": tenant.id,
        "name": tenant.name,
        "contact_email": tenant.contact_email,
        "plan": tenant.plan,
        "created_at": tenant.created_at.isoformat(),
        "last_api_access": tenant.last_api_access.isoformat() if tenant.last_api_access else "Never",
        "api_key_expires_at": tenant.api_key_expires_at.isoformat()
        if tenant.api_key_expires_at
        else "Never",
        "api_request_count": tenant.api_request_count,
        "api_error_count": tenant.api_error_count,
        "api_score": round(tenant.api_score or 0.0, 2),
        "is_active": tenant.is_active,
    }
