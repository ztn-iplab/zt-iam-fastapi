import hashlib
import json
import random
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_full_mfa, role_required
from app.models import PendingSIMSwap, RealTimeLog, SIMCard, Transaction, User, UserAccessControl, UserRole, Wallet
from app.security import get_jwt_identity, verify_session_fingerprint
from utils.email_alerts import send_sim_swap_verification_email
from utils.totp import verify_totp_code

router = APIRouter(tags=["Agent"])
templates = Jinja2Templates(directory="templates")

WITHDRAWAL_EXPIRY_MINUTES = 5


def _generate_unique_mobile_number(db: Session, network_provider: str) -> str:
    prefix = "078" if network_provider == "MTN" else "073"
    while True:
        new_number = prefix + str(random.randint(1000000, 9999999))
        existing_number = db.query(SIMCard).filter_by(mobile_number=new_number).first()
        if not existing_number:
            return new_number


def _generate_unique_iccid(db: Session) -> str:
    while True:
        new_iccid = "8901" + str(random.randint(100000000000, 999999999999))
        existing_iccid = db.query(SIMCard).filter_by(iccid=new_iccid).first()
        if not existing_iccid:
            return new_iccid


def _expire_pending_withdrawals(db: Session) -> int:
    now = datetime.utcnow()
    expired_count = 0

    pending = db.query(Transaction).filter_by(transaction_type="withdrawal", status="pending").all()
    for tx in pending:
        if tx.timestamp and now - tx.timestamp > timedelta(minutes=WITHDRAWAL_EXPIRY_MINUTES):
            tx.status = "expired"
            expired_count += 1

    if expired_count:
        db.commit()
    return expired_count


@router.post("/agent/generate_sim", dependencies=[Depends(verify_session_fingerprint)])
def generate_sim(payload: dict, db: Session = Depends(get_db)):
    network_provider = payload.get("network_provider")
    if not network_provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Network provider is required.")
    if network_provider not in ["MTN", "Airtel"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid network provider. Choose MTN or Airtel.",
        )

    mobile_number = _generate_unique_mobile_number(db, network_provider)
    iccid = _generate_unique_iccid(db)

    return {
        "success": True,
        "message": f"{network_provider} SIM generated successfully.",
        "mobile_number": mobile_number,
        "iccid": iccid,
    }


@router.post("/agent/register_sim", dependencies=[Depends(verify_session_fingerprint)])
def register_sim(payload: dict, request: Request, db: Session = Depends(get_db)):
    logged_in_user = int(get_jwt_identity(request))
    agent = db.query(User).get(logged_in_user)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    user_access = db.query(UserAccessControl).filter_by(user_id=logged_in_user).first()
    if not user_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized. Agent role required."
        )

    user_role = db.query(UserRole).get(user_access.role_id)
    if not user_role or user_role.role_name != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized. Only agents can register SIMs.",
        )

    iccid = payload.get("iccid")
    mobile_number = payload.get("mobile_number")
    network_provider = payload.get("network_provider")
    if not iccid or not mobile_number or not network_provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required SIM details.")
    if network_provider not in ["MTN", "Airtel"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid network provider. Choose MTN or Airtel.",
        )

    existing_sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if existing_sim:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This ICCID is already registered.")

    new_sim = SIMCard(
        iccid=iccid,
        mobile_number=mobile_number,
        network_provider=network_provider,
        status="unregistered",
        registered_by=str(agent.id),
    )
    db.add(new_sim)
    db.commit()

    return {
        "success": True,
        "message": f"{network_provider} SIM registered successfully.",
        "mobile_number": new_sim.mobile_number,
        "iccid": new_sim.iccid,
    }


@router.get("/agent/sim-registrations", dependencies=[Depends(verify_session_fingerprint)])
def fetch_sim_registration_history(request: Request, db: Session = Depends(get_db)):
    agent_id = str(get_jwt_identity(request))
    sims = (
        db.query(SIMCard)
        .filter_by(registered_by=agent_id)
        .order_by(SIMCard.registration_date.desc())
        .all()
    )

    sim_list = []
    for sim in sims:
        if sim.status == "active":
            status_class = "text-success"
        elif sim.status == "suspended":
            status_class = "text-danger"
        elif sim.status == "swapped":
            status_class = "text-warning"
        else:
            status_class = "text-muted"

        if sim.user_id:
            active_sim = db.query(SIMCard).filter_by(user_id=sim.user_id, status="active").first()
            display_mobile = active_sim.mobile_number if active_sim else sim.mobile_number
        else:
            display_mobile = sim.mobile_number

        sim_list.append(
            {
                "iccid": sim.iccid,
                "mobile_number": display_mobile,
                "network_provider": sim.network_provider,
                "status": sim.status,
                "status_class": status_class,
                "timestamp": sim.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
                "registered_user": f"{sim.user.first_name} {sim.user.last_name}"
                if sim.user
                else "Not Linked",
            }
        )

    return {"sims": sim_list}


@router.get(
    "/agent/dashboard",
    response_class=HTMLResponse,
    dependencies=[
        Depends(verify_session_fingerprint),
        Depends(role_required(["agent"])),
        Depends(require_full_mfa),
    ],
)
def agent_dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return templates.TemplateResponse(
        "agent_dashboard.html",
        {"request": request, "user": user, "dashboard_url": "/agent/dashboard"},
    )


@router.post(
    "/agent/transaction",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["agent"]))],
)
def process_agent_transaction(payload: dict, request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    try:
        amount = float(payload.get("amount"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount")

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than zero"
        )

    transaction_type = payload.get("transaction_type")
    recipient_mobile = payload.get("recipient_mobile")
    if not transaction_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction type is required")

    agent = db.query(User).get(user_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent_wallet = db.query(Wallet).filter_by(user_id=agent.id).first()
    if not agent_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent wallet not found")

    totp_code = payload.get("totp")
    if not totp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP code is required")
    if not agent.otp_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="TOTP not configured for this agent"
        )
    if not verify_totp_code(agent.otp_secret, totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired TOTP code")

    transaction_metadata = {}
    rt_log = None
    recipient_wallet = None

    if transaction_type == "deposit":
        if not recipient_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient mobile is required for deposits",
            )

        recipient_sim = db.query(SIMCard).filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient SIM not found")

        recipient = db.query(User).get(recipient_sim.user_id)
        if not recipient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")

        recipient_wallet = db.query(Wallet).filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient wallet not found")

        if recipient.id == agent.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agents cannot deposit into their own accounts",
            )

        if agent_wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance for deposit"
            )

        agent_wallet.balance -= amount
        recipient_wallet.balance += amount

        deposited_by_mobile = agent.sim_cards[0].mobile_number if agent.sim_cards else "N/A"
        transaction_metadata = {
            "deposited_by_mobile": deposited_by_mobile,
            "recipient_mobile": recipient_mobile,
            "recipient_name": f"{recipient.first_name} {recipient.last_name}",
        }

        new_transaction = Transaction(
            user_id=recipient.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1,
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"Agent deposited {amount} RWF to {recipient.first_name} ({recipient_mobile})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )

    elif transaction_type == "transfer":
        if not recipient_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient mobile is required for transfers",
            )

        recipient_sim = db.query(SIMCard).filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient SIM not found")

        recipient = db.query(User).get(recipient_sim.user_id)
        if not recipient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")

        recipient_wallet = db.query(Wallet).filter_by(user_id=recipient.id).first()
        if not recipient_wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient wallet not found")

        if agent_wallet.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        agent_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = {
            "transfer_by": "Agent",
            "recipient_mobile": recipient_mobile,
            "recipient_name": f"{recipient.first_name} {recipient.last_name}",
        }

        new_transaction = Transaction(
            user_id=agent.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1,
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"Agent transferred {amount} RWF to {recipient.first_name} ({recipient_mobile})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )

    elif transaction_type == "withdrawal":
        if agent_wallet.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        agent_wallet.balance -= amount

        transaction_metadata = {"withdrawal_method": "Agent Processed"}

        new_transaction = Transaction(
            user_id=agent.id,
            amount=amount,
            transaction_type=transaction_type,
            status="completed",
            transaction_metadata=json.dumps(transaction_metadata),
            tenant_id=1,
        )

        rt_log = RealTimeLog(
            user_id=agent.id,
            action=f"Agent withdrew {amount} RWF from own float",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type")

    db.add(new_transaction)
    if rt_log:
        db.add(rt_log)
    db.commit()

    updated_balance = agent_wallet.balance
    if transaction_type == "deposit" and recipient_wallet:
        updated_balance = recipient_wallet.balance

    return {
        "message": f"{transaction_type.capitalize()} successful",
        "updated_balance": updated_balance,
        "recipient_mobile": recipient_mobile if transaction_type != "withdrawal" else None,
        "recipient_name": transaction_metadata.get("recipient_name", "N/A"),
    }


@router.get(
    "/agent/transactions",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["agent"]))],
)
def get_agent_transactions(request: Request, db: Session = Depends(get_db)):
    agent_id = int(get_jwt_identity(request))

    agent_sims = (
        db.query(SIMCard)
        .filter(SIMCard.user_id == agent_id, SIMCard.status.in_(["active", "swapped"]))
        .all()
    )
    agent_mobiles = [sim.mobile_number for sim in agent_sims if sim.mobile_number]

    conditions = [Transaction.user_id == agent_id]
    conditions.append(Transaction.transaction_metadata.contains(f'"assigned_agent_id": {agent_id}'))
    for mobile in agent_mobiles:
        conditions.append(Transaction.transaction_metadata.contains(f'"deposited_by_mobile": "{mobile}"'))

    transactions = db.query(Transaction).filter(or_(*conditions)).order_by(Transaction.timestamp.desc()).all()

    transaction_list = []
    for tx in transactions:
        try:
            metadata = json.loads(tx.transaction_metadata or "{}")
            involved = False
            if tx.user_id == agent_id:
                involved = True
            elif metadata.get("assigned_agent_id") and int(metadata.get("assigned_agent_id")) == agent_id:
                involved = True
            elif metadata.get("deposited_by_mobile") in agent_mobiles:
                involved = True

            if not involved:
                continue

            if tx.transaction_type in ["deposit", "transfer"]:
                recipient_mobile = metadata.get("recipient_mobile", "N/A")
            elif tx.transaction_type == "withdrawal":
                recipient_user_id = tx.user_id
                active_sim = (
                    db.query(SIMCard)
                    .filter_by(user_id=recipient_user_id, status="active")
                    .first()
                )
                recipient_mobile = active_sim.mobile_number if active_sim else "N/A"
            else:
                recipient_mobile = "Self"

            admin_msg = metadata.get("admin_message")
            if tx.transaction_type == "withdrawal":
                if tx.status == "pending":
                    label = "User withdrawal pending approval"
                elif tx.status == "rejected":
                    label = "User withdrawal rejected"
                elif tx.status == "expired":
                    label = "User withdrawal expired"
                else:
                    label = "User withdrawal approved"
            elif tx.transaction_type == "float":
                label = f"Float from admin: {admin_msg}" if admin_msg else "Float from admin"
            elif tx.transaction_type == "transfer" and tx.user_id == agent_id:
                label = f"Transfer to {recipient_mobile}"
            elif tx.transaction_type == "transfer":
                label = f"Transfer from {recipient_mobile}"
            elif tx.transaction_type == "deposit":
                label = f"Deposit to {recipient_mobile}"
            else:
                label = tx.transaction_type.capitalize()

            status_class = ""
            if tx.status == "rejected":
                status_class = "text-danger"
            elif tx.status == "pending":
                status_class = "text-warning"
            elif tx.status == "completed":
                status_class = "text-success"
            elif tx.status == "expired":
                status_class = "text-muted"

            transaction_list.append(
                {
                    "transaction_id": tx.id,
                    "amount": tx.amount,
                    "transaction_type": tx.transaction_type,
                    "label": label,
                    "status": tx.status,
                    "status_class": status_class,
                    "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "recipient_mobile": recipient_mobile,
                }
            )
        except Exception:
            continue

    return {"transactions": transaction_list}


@router.get(
    "/agent/wallet",
    dependencies=[Depends(verify_session_fingerprint), Depends(role_required(["agent"]))],
)
def agent_wallet(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return {"balance": wallet.balance, "currency": wallet.currency, "can_deposit": False}


@router.get("/agent/dashboard/data", dependencies=[Depends(role_required(["agent"]))])
def agent_dashboard_data(request: Request, db: Session = Depends(get_db)):
    agent_id = int(get_jwt_identity(request))
    agent = db.query(User).get(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    total_transactions = (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.user_id == agent.id,
                Transaction.transaction_metadata.like(
                    f'%\"deposited_by\": \"Agent\", \"agent_id\": {agent.id}%'
                ),
            )
        )
        .count()
    )

    total_sims = db.query(SIMCard).filter_by(registered_by=str(agent.id)).count()

    total_deposits = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.transaction_type == "deposit",
            Transaction.transaction_metadata.like(
                f'%\"deposited_by\": \"Agent\", \"agent_id\": {agent.id}%'
            ),
        )
        .scalar()
        or 0
    )

    total_withdrawals = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == agent.id, Transaction.transaction_type == "withdrawal")
        .scalar()
        or 0
    )

    total_transfers = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == agent.id, Transaction.transaction_type == "transfer")
        .scalar()
        or 0
    )

    return {
        "total_transactions": total_transactions,
        "total_sims": total_sims,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers,
    }


@router.get("/agent/profile", dependencies=[Depends(role_required(["agent"]))])
def agent_profile(request: Request, db: Session = Depends(get_db)):
    current_user_id = int(get_jwt_identity(request))
    user = db.query(User).get(current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    latest_sim = (
        db.query(SIMCard).filter_by(user_id=user.id).order_by(SIMCard.registration_date.desc()).first()
    )
    mobile_number = latest_sim.mobile_number if latest_sim else "Not Assigned"

    return {
        "id": user.id,
        "mobile_number": mobile_number,
        "first_name": user.first_name or "Unknown",
        "last_name": user.last_name or "",
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "country": user.country or "N/A",
        "identity_verified": user.identity_verified,
        "role": "agent",
    }


@router.get("/agent/view_sim/{iccid}")
def view_sim(iccid: str, db: Session = Depends(get_db)):
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")

    return {
        "iccid": sim.iccid,
        "mobile_number": sim.mobile_number,
        "network_provider": sim.network_provider,
        "status": sim.status,
        "registration_date": sim.registration_date.strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.post("/agent/activate_sim", dependencies=[Depends(verify_session_fingerprint)])
def activate_sim(payload: dict, request: Request, db: Session = Depends(get_db)):
    iccid = payload.get("iccid")
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")

    sim.status = "active"
    db.commit()

    agent_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Activated SIM ICCID: {iccid}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": "SIM activated successfully."}


@router.post("/agent/suspend_sim")
def suspend_sim(payload: dict, request: Request, db: Session = Depends(get_db)):
    iccid = payload.get("iccid")
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")

    sim.status = "suspended"
    db.commit()

    agent_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Suspended SIM ICCID: {iccid}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": "SIM suspended successfully."}


@router.post("/agent/reactivate_sim", dependencies=[Depends(role_required(["agent"]))])
def reactivate_sim(payload: dict, request: Request, db: Session = Depends(get_db)):
    iccid = payload.get("iccid")
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")
    if sim.status != "suspended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only suspended SIMs can be re-activated"
        )

    sim.status = "active"
    db.commit()

    agent_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Re-activated suspended SIM ICCID: {iccid}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": "SIM re-activated successfully."}


@router.delete("/agent/delete_sim")
def delete_sim(payload: dict, request: Request, db: Session = Depends(get_db)):
    iccid = payload.get("iccid")
    sim = db.query(SIMCard).filter_by(iccid=iccid).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")
    if sim.status != "unregistered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete an activated SIM.")

    db.delete(sim)
    db.commit()

    agent_id = int(get_jwt_identity(request))
    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Deleted SIM ICCID: {iccid}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location=payload.get("location", "Unknown"),
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": "SIM deleted successfully."}


@router.get("/agent/pending-withdrawals", dependencies=[Depends(role_required(["agent"]))])
def get_pending_withdrawals(request: Request, db: Session = Depends(get_db)):
    agent_id = int(get_jwt_identity(request))
    _expire_pending_withdrawals(db)

    pending_withdrawals = (
        db.query(Transaction)
        .filter_by(transaction_type="withdrawal", status="pending")
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    result = []
    for tx in pending_withdrawals:
        try:
            metadata = json.loads(tx.transaction_metadata or "{}")
            assigned_agent_id_raw = metadata.get("assigned_agent_id")
            assigned_agent_id = int(assigned_agent_id_raw) if assigned_agent_id_raw is not None else -1
            if assigned_agent_id != agent_id:
                continue

            user = db.query(User).get(tx.user_id)
            result.append(
                {
                    "transaction_id": tx.id,
                    "amount": tx.amount,
                    "timestamp": tx.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                    "user_id": user.id if user else None,
                    "agent_mobile": metadata.get("assigned_agent_mobile"),
                    "metadata": metadata,
                }
            )
        except Exception:
            continue

    return {"pending_withdrawals": result}


@router.post("/agent/approve-withdrawal/{transaction_id}", dependencies=[Depends(role_required(["agent"]))])
def approve_user_withdrawal(transaction_id: int, request: Request, db: Session = Depends(get_db)):
    agent_id = int(get_jwt_identity(request))
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction or transaction.transaction_type != "withdrawal" or transaction.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already processed withdrawal request",
        )

    metadata = json.loads(transaction.transaction_metadata or "{}")
    assigned_agent_id = int(metadata.get("assigned_agent_id", -1))
    if assigned_agent_id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to approve this withdrawal",
        )

    now = datetime.utcnow()
    if transaction.timestamp and now - transaction.timestamp > timedelta(minutes=WITHDRAWAL_EXPIRY_MINUTES):
        transaction.status = "expired"
        db.add(
            RealTimeLog(
                user_id=agent_id,
                action=f"Withdrawal request of {transaction.amount} RWF for User {transaction.user_id} expired",
                ip_address=request.client.host if request.client else None,
                device_info=request.headers.get("User-Agent", "Unknown"),
                location="Agent location",
                risk_alert=True,
                tenant_id=1,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This withdrawal request has expired and can no longer be approved.",
        )

    user_wallet = db.query(Wallet).filter_by(user_id=transaction.user_id).first()
    if not user_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User wallet not found")
    if user_wallet.balance < transaction.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient user balance")

    user_wallet.balance -= transaction.amount
    transaction.status = "completed"
    metadata["approved_by_agent"] = True
    metadata["approved_by"] = agent_id
    metadata["approved_at"] = now.isoformat()
    transaction.transaction_metadata = json.dumps(metadata)
    db.commit()

    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Approved withdrawal of {transaction.amount} RWF for User {transaction.user_id}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location="Agent location",
            risk_alert=False,
            tenant_id=1,
        )
    )
    db.commit()

    return {
        "message": "Withdrawal approved and processed.",
        "user_id": transaction.user_id,
        "withdrawn_amount": transaction.amount,
        "updated_balance": user_wallet.balance,
        "approved_by": agent_id,
    }


@router.post("/agent/reject-withdrawal/{transaction_id}", dependencies=[Depends(role_required(["agent"]))])
def reject_user_withdrawal(transaction_id: int, request: Request, db: Session = Depends(get_db)):
    agent_id = int(get_jwt_identity(request))
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction or transaction.transaction_type != "withdrawal" or transaction.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already processed withdrawal request",
        )

    metadata = json.loads(transaction.transaction_metadata or "{}")
    assigned_agent_id = int(metadata.get("assigned_agent_id", -1))
    if assigned_agent_id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to reject this withdrawal",
        )

    transaction.status = "rejected"
    metadata["rejected_by_agent"] = True
    metadata["rejected_by"] = agent_id
    metadata["rejected_at"] = datetime.utcnow().isoformat()
    transaction.transaction_metadata = json.dumps(metadata)
    db.commit()

    db.add(
        RealTimeLog(
            user_id=agent_id,
            action=f"Rejected withdrawal of {transaction.amount} RWF for User {transaction.user_id}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", "Unknown"),
            location="Agent location",
            risk_alert=True,
            tenant_id=1,
        )
    )
    db.commit()

    return {"message": "Withdrawal rejected successfully.", "transaction_id": transaction.id, "status": "rejected"}


@router.post("/agent/request-sim-swap", dependencies=[Depends(role_required(["agent"]))])
def request_sim_swap(payload: dict, request: Request, db: Session = Depends(get_db)):
    old_iccid = payload.get("old_iccid")
    new_iccid = payload.get("new_iccid")
    agent_id = int(get_jwt_identity(request))

    old_sim = db.query(SIMCard).filter_by(iccid=old_iccid).first()
    new_sim = db.query(SIMCard).filter_by(iccid=new_iccid).first()
    if not old_sim or not new_sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SIM not found")
    if old_sim.status != "active" or new_sim.status != "unregistered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SIM status invalid")
    if old_sim.network_provider != new_sim.network_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Mismatched network providers"
        )

    user_id = old_sim.user_id
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for old SIM")

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    pending = PendingSIMSwap(
        token_hash=token_hash,
        user_id=user_id,
        old_iccid=old_iccid,
        new_iccid=new_iccid,
        requested_by=str(agent_id),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(pending)
    db.commit()

    send_sim_swap_verification_email(user, raw_token)

    return {"message": "A verification email has been sent to the user. Awaiting approval."}
