from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RealTimeLog, Tenant
from utils.location import get_ip_location

ERROR_LIMIT = 10
SCORE_DECAY_HOURS = 6
BLOCK_THRESHOLD = 1.0

PLAN_RATE_LIMITS = {
    "basic": 100,
    "premium": 1000,
    "enterprise": 5000,
}


def require_api_key(request: Request, db: Session = Depends(get_db)) -> Tenant:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    tenant = db.query(Tenant).filter_by(api_key=api_key).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    now = datetime.utcnow()
    plan = (tenant.plan or "basic").lower()
    rate_limit = PLAN_RATE_LIMITS.get(plan, 100)

    tenant.api_score = getattr(tenant, "api_score", 0.0) or 0.0
    tenant.api_request_count = getattr(tenant, "api_request_count", 0) or 0
    tenant.api_error_count = getattr(tenant, "api_error_count", 0) or 0

    if not tenant.api_last_reset or (now - tenant.api_last_reset > timedelta(hours=SCORE_DECAY_HOURS)):
        tenant.api_request_count = 0
        tenant.api_error_count = 0
        tenant.api_score = max(tenant.api_score - 0.2, 0.0)
        tenant.api_last_reset = now

    if not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This API key has been suspended")
    if tenant.api_key_expires_at and tenant.api_key_expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has expired. Please renew or upgrade your plan.",
        )

    tenant.last_api_access = now
    tenant.api_request_count += 1

    if tenant.api_request_count > rate_limit:
        tenant.api_score += 0.1

    if tenant.api_score >= BLOCK_THRESHOLD:
        tenant.is_active = False
        db.add(
            RealTimeLog(
                tenant_id=tenant.id,
                user_id=None,
                action=f"Auto-suspended API Key due to abuse: {tenant.name}",
                ip_address=request.client.host if request.client else None,
                device_info=request.headers.get("User-Agent", ""),
                location=get_ip_location(request.client.host if request.client else ""),
                risk_alert=True,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key suspended due to repeated abuse",
        )

    db.add(tenant)
    db.commit()
    return tenant
