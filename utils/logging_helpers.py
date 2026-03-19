from app.models import RealTimeLog, Tenant, UserAuthLog


def log_realtime_event(db, user, action, ip_address, device_info, location, risk_alert=False):
    """Log an action into RealTimeLog with a safe tenant fallback.

    If no user is available and there is no tenant yet (fresh DB), skip logging
    instead of raising a foreign-key error.
    """
    tenant_id = user.tenant_id if user else None
    if tenant_id is None:
        first_tenant = db.query(Tenant.id).order_by(Tenant.id.asc()).first()
        tenant_id = first_tenant[0] if first_tenant else None
    if tenant_id is None:
        return

    db.add(
        RealTimeLog(
            user_id=user.id if user else None,
            tenant_id=tenant_id,
            action=action,
            ip_address=ip_address,
            device_info=device_info,
            location=location,
            risk_alert=risk_alert,
        )
    )

def log_auth_event(db, user, method, status, ip_address, device_info, location, failed_attempts=0):
    """Log an auth attempt into UserAuthLog with automatic tenant_id."""
    db.add(UserAuthLog(
        user_id=user.id,
        tenant_id=user.tenant_id,
        auth_method=method,
        auth_status=status,
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        failed_attempts=failed_attempts
    ))
