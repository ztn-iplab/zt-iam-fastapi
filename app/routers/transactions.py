import json
import threading
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import SessionLocal, get_db
from app.models import RealTimeLog, SIMCard, Transaction, User, Wallet
from app.security import get_jwt_identity, verify_session_fingerprint
from utils.email_alerts import send_alert_email
from utils.totp import verify_totp_code
from utils.user_trust_engine import evaluate_trust

router = APIRouter(prefix="/api", tags=["Transactions"])


def _update_transaction_status(transaction_id: int, new_status: str) -> None:
    time.sleep(10)
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).get(transaction_id)
        if transaction:
            transaction.status = new_status
            db.commit()
    finally:
        db.close()


class TransactionCreate(BaseModel):
    amount: float
    transaction_type: str
    totp: str
    device_info: str | None = None
    location: str | None = None
    recipient_mobile: str | None = None
    agent_mobile: str | None = None


class TransactionUpdate(BaseModel):
    status: str | None = None
    location: str | None = None
    device_info: str | None = None
    transaction_metadata: str | None = None


class WithdrawalRequest(BaseModel):
    amount: float


class VerifyOtpPayload(BaseModel):
    otp: str


@router.post("/transactions", dependencies=[Depends(verify_session_fingerprint)])
def create_transaction(
    payload: TransactionCreate, request: Request, db: Session = Depends(get_db)
):
    user_id = int(get_jwt_identity(request))

    amount = payload.amount
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be a positive number")

    transaction_type = payload.transaction_type.lower()
    sender_wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not sender_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if transaction_type == "deposit":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Deposits are not allowed for regular users")

    if not payload.totp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP code is required")

    user = db.query(User).get(user_id)
    if not user or not user.otp_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TOTP secret not configured for user")

    if not verify_totp_code(user.otp_secret, payload.totp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired TOTP code")

    ip_address = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else None)
    context = {
        "amount": amount,
        "device_info": payload.device_info,
        "ip_address": ip_address,
        "location": payload.location,
        "scope": "transaction",
    }
    risk_score = evaluate_trust(user, context, tenant=None)
    fraud_flag = risk_score >= 0.7

    if transaction_type == "withdrawal":
        if sender_wallet.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        agent_mobile = payload.agent_mobile
        if not agent_mobile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent mobile number is required")

        agent_sim = db.query(SIMCard).filter_by(mobile_number=agent_mobile).first()
        if not agent_sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        assigned_agent = db.query(User).get(agent_sim.user_id)
        if not assigned_agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent user not found")

        transaction_metadata = {
            "initiated_by": "user",
            "approved_by_agent": False,
            "assigned_agent_id": assigned_agent.id,
            "assigned_agent_mobile": agent_mobile,
            "assigned_agent_name": f"{assigned_agent.first_name} {assigned_agent.last_name}".strip(),
        }

        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            status="pending",
            location=payload.location,
            device_info=payload.device_info,
            transaction_metadata=json.dumps(transaction_metadata),
            fraud_flag=fraud_flag,
            risk_score=risk_score,
            tenant_id=1,
        )

        db.add(transaction)

        log_msg = f"{transaction_type.title()} of {amount} RWF"
        if fraud_flag:
            log_msg = f"Suspicious {log_msg} flagged"

        db.add(
            RealTimeLog(
                user_id=user.id,
                action=log_msg,
                ip_address=ip_address,
                device_info=payload.device_info,
                location=payload.location or "Unknown",
                risk_alert=fraud_flag,
                tenant_id=1,
            )
        )

        subject = "Fraud Alert: Suspicious Transaction Detected"
        body = f"""
A suspicious transaction has been flagged.

User ID: {user.id}
Amount: {amount} RWF
Type: {transaction_type}
Risk Score: {risk_score}
IP: {ip_address}
Device: {payload.device_info}
Location: {payload.location}
"""
        send_alert_email(subject, body)
        db.commit()

        return {
            "message": "Withdrawal request submitted. Awaiting agent approval.",
            "transaction_id": transaction.id,
            "status": transaction.status,
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "assigned_agent": f"{assigned_agent.first_name} {assigned_agent.last_name} ({agent_mobile})",
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "updated_balance": sender_wallet.balance,
            "location": transaction.location,
            "device_info": transaction.device_info,
            "fraud_flag": transaction.fraud_flag,
            "risk_score": transaction.risk_score,
        }

    if transaction_type == "transfer":
        recipient_mobile = payload.recipient_mobile
        if not recipient_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient mobile number is required for transfers",
            )

        recipient_sim = db.query(SIMCard).filter_by(mobile_number=recipient_mobile).first()
        if not recipient_sim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

        recipient_user = db.query(User).get(recipient_sim.user_id)
        if not recipient_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")

        recipient_wallet = db.query(Wallet).filter_by(user_id=recipient_user.id).first()
        if not recipient_wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient wallet not found")

        if sender_wallet.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

        sender_wallet.balance -= amount
        recipient_wallet.balance += amount

        transaction_metadata = {
            "recipient_mobile": recipient_mobile,
            "recipient_id": recipient_user.id,
            "recipient_name": f"{recipient_user.first_name} {recipient_user.last_name}".strip(),
            "sender_id": user_id,
        }

        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            status="pending",
            location=payload.location,
            device_info=payload.device_info,
            transaction_metadata=json.dumps(transaction_metadata),
            fraud_flag=fraud_flag,
            risk_score=risk_score,
            tenant_id=1,
        )

        db.add(transaction)

        log_msg = f"{transaction_type.title()} of {amount} RWF"
        if fraud_flag:
            log_msg = f"Suspicious {log_msg} flagged"

        db.add(
            RealTimeLog(
                user_id=user.id,
                action=log_msg,
                ip_address=ip_address,
                device_info=payload.device_info,
                location=payload.location or "Unknown",
                risk_alert=fraud_flag,
                tenant_id=1,
            )
        )

        db.commit()
        threading.Thread(
            target=_update_transaction_status, args=(transaction.id, "completed")
        ).start()

        return {
            "message": f"{amount} RWF transferred to {recipient_user.first_name} {recipient_user.last_name} ({recipient_mobile}).",
            "transaction_id": transaction.id,
            "status": transaction.status,
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "updated_balance": sender_wallet.balance,
            "location": transaction.location,
            "device_info": transaction.device_info,
            "fraud_flag": transaction.fraud_flag,
            "risk_score": transaction.risk_score,
        }

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type")


@router.get("/transactions", dependencies=[Depends(verify_session_fingerprint)])
def get_transactions(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    transactions = (
        db.query(Transaction)
        .filter(
            (Transaction.user_id == user_id)
            | (Transaction.transaction_metadata.contains(f'\"recipient_id\": {user_id}'))
        )
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    transaction_list = []
    for tx in transactions:
        try:
            metadata = json.loads(tx.transaction_metadata) if tx.transaction_metadata else {}
            recipient_mobile = metadata.get("recipient_mobile", "N/A")
            recipient_id = metadata.get("recipient_id")
            agent_mobile = metadata.get("assigned_agent_mobile") or metadata.get(
                "deposited_by_mobile", "N/A"
            )

            if isinstance(agent_mobile, str) and agent_mobile.startswith("SWP_"):
                assigned_agent_id = metadata.get("assigned_agent_id")
                if assigned_agent_id:
                    active_sim = (
                        db.query(SIMCard)
                        .filter_by(user_id=assigned_agent_id, status="active")
                        .first()
                    )
                    if active_sim:
                        agent_mobile = active_sim.mobile_number

                deposited_by_mobile = metadata.get("deposited_by_mobile")
                if deposited_by_mobile and deposited_by_mobile.startswith("SWP_"):
                    deposited_sim = (
                        db.query(SIMCard)
                        .filter_by(user_id=user_id, status="active")
                        .first()
                    )
                    if deposited_sim:
                        agent_mobile = deposited_sim.mobile_number

            sender_sim = (
                db.query(SIMCard).filter_by(user_id=tx.user_id, status="active").first()
            )
            sender_mobile = sender_sim.mobile_number if sender_sim else "Unknown"

            if tx.transaction_type == "deposit":
                label = f"Deposit from Agent {agent_mobile}"
            elif tx.transaction_type == "transfer":
                if tx.user_id == user_id:
                    label = f"Transfered to {recipient_mobile}"
                elif recipient_id == user_id:
                    label = f"Received from {sender_mobile}"
                else:
                    label = "Transfer"
            elif tx.transaction_type == "withdrawal":
                if tx.status == "pending":
                    label = f"Withdrawal (Pending Agent Approval - {agent_mobile})"
                elif tx.status == "rejected":
                    label = f"Withdrawal (Rejected by Agent {agent_mobile})"
                elif tx.status == "expired":
                    label = f"Withdrawal (Expired - Not Approved in Time)"
                else:
                    label = f"Withdrawal (Approved by Agent {agent_mobile})"
            elif tx.transaction_type == "reversal":
                label = "Transfer Reversed"
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
                    "details": metadata,
                }
            )
        except Exception:
            continue

    return {"transactions": transaction_list}


@router.put("/transactions/{transaction_id}", dependencies=[Depends(verify_session_fingerprint)])
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = int(get_jwt_identity(request))
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or unauthorized"
        )

    if payload.status is not None:
        transaction.status = payload.status
    if payload.location is not None:
        transaction.location = payload.location
    if payload.device_info is not None:
        transaction.device_info = payload.device_info
    if payload.transaction_metadata is not None:
        transaction.transaction_metadata = payload.transaction_metadata

    db.commit()
    return {"message": "Transaction updated successfully"}


@router.delete("/transactions/{transaction_id}", dependencies=[Depends(verify_session_fingerprint)])
def delete_transaction(transaction_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or unauthorized"
        )

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@router.post("/user/initiated-withdrawal", dependencies=[Depends(verify_session_fingerprint)])
def user_initiate_withdrawal(
    payload: WithdrawalRequest, request: Request, db: Session = Depends(get_db)
):
    user_id = int(get_jwt_identity(request))
    amount = payload.amount
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than zero")

    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    if wallet.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")

    withdrawal_request = Transaction(
        user_id=user_id,
        amount=amount,
        transaction_type="withdrawal",
        status="pending",
        transaction_metadata=json.dumps({"initiated_by": "user", "approved_by_agent": False}),
    )
    db.add(withdrawal_request)
    db.commit()

    return {"message": "Withdrawal request submitted. Awaiting agent approval.", "transaction_id": withdrawal_request.id}


@router.post("/verify-transaction-otp", dependencies=[Depends(verify_session_fingerprint)])
def verify_transaction_otp(
    payload: VerifyOtpPayload, request: Request, db: Session = Depends(get_db)
):
    user_id = int(get_jwt_identity(request))
    user = db.query(User).get(user_id)
    if not user or not user.otp_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TOTP not set up")

    if not verify_totp_code(user.otp_secret, payload.otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")

    return {"message": "Transaction authorized"}
