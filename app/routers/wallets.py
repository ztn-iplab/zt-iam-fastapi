from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Wallet
from app.security import get_jwt_identity, verify_session_fingerprint

router = APIRouter(prefix="/api", tags=["Wallets"])


class WalletUpdate(BaseModel):
    balance: Optional[float] = None
    currency: Optional[str] = None


@router.get("/wallets", dependencies=[Depends(verify_session_fingerprint)])
def get_wallet(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    return {
        "user_id": wallet.user_id,
        "balance": wallet.balance,
        "currency": wallet.currency,
    }


@router.put("/wallets", dependencies=[Depends(verify_session_fingerprint)])
def update_wallet(
    payload: WalletUpdate, request: Request, db: Session = Depends(get_db)
):
    user_id = int(get_jwt_identity(request))

    if payload.balance is not None and (payload.balance < 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid balance value. It must be a non-negative number.",
        )

    if payload.currency and len(payload.currency) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid currency. It must be a 3-letter currency code.",
        )

    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    if payload.balance is not None:
        wallet.balance = payload.balance
    if payload.currency:
        wallet.currency = payload.currency

    db.commit()

    return {
        "user_id": wallet.user_id,
        "balance": wallet.balance,
        "currency": wallet.currency,
    }


@router.delete("/wallets", dependencies=[Depends(verify_session_fingerprint)])
def delete_wallet(request: Request, db: Session = Depends(get_db)):
    user_id = int(get_jwt_identity(request))
    wallet = db.query(Wallet).filter_by(user_id=user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    db.delete(wallet)
    db.commit()
    return {"message": "Wallet deleted successfully"}
