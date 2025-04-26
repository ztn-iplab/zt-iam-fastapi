# utils/logging_helpers.py

from models.models import db, RealTimeLog, UserAuthLog

def log_realtime_event(user, action, ip_address, device_info, location, risk_alert=False):
    """Log an action into RealTimeLog with automatic tenant_id."""
    db.session.add(RealTimeLog(
        user_id=user.id if user else None,
        tenant_id=user.tenant_id if user else 1,  # fallback to 1 if user is missing (like admin ops)
        action=action,
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        risk_alert=risk_alert
    ))

def log_auth_event(user, method, status, ip_address, device_info, location, failed_attempts=0):
    """Log an auth attempt into UserAuthLog with automatic tenant_id."""
    db.session.add(UserAuthLog(
        user_id=user.id,
        tenant_id=user.tenant_id,
        auth_method=method,
        auth_status=status,
        ip_address=ip_address,
        device_info=device_info,
        location=location,
        failed_attempts=failed_attempts
    ))
