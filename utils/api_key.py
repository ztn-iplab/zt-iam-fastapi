from datetime import datetime, timedelta
from flask import request, jsonify, g
from models.models import db, Tenant, RealTimeLog
from utils.location import get_ip_location
import secrets

# 📊 Trust Engine Configs
ERROR_LIMIT = 10
SCORE_DECAY_HOURS = 6
WARN_THRESHOLD = 0.5
BLOCK_THRESHOLD = 1.0

# 🎚️ Plan-specific Rate Limits
PLAN_RATE_LIMITS = {
    "basic": 100,
    "premium": 1000,
    "enterprise": 5000
}

# 🔓 Trusted tenants (bypass all abuse logic)
TRUST_ENGINE_BYPASS_TENANTS = ["MasterTenant", "MinistryOfHealth"]

def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401

        tenant = Tenant.query.filter_by(api_key=api_key).first()
        if not tenant:
            return jsonify({"error": "Invalid API key"}), 403

        now = datetime.utcnow()

        # ✅ Bypass trust engine for whitelisted tenants (safe for dev/testing)
        # if tenant.name in TRUST_ENGINE_BYPASS_TENANTS:
        #     tenant.last_api_access = now
        #     db.session.commit()
        #     g.tenant = tenant
        #     return func(*args, **kwargs)

        # 🔐 Plan-based dynamic rate limits
        plan = (tenant.plan or "basic").lower()
        rate_limit = PLAN_RATE_LIMITS.get(plan, 100)

        # ✅ Initialize fields safely
        tenant.api_score = getattr(tenant, 'api_score', 0.0) or 0.0
        tenant.api_request_count = getattr(tenant, 'api_request_count', 0) or 0
        tenant.api_error_count = getattr(tenant, 'api_error_count', 0) or 0

        # ♻️ Decay score on window expiry
        if not tenant.api_last_reset or (now - tenant.api_last_reset > timedelta(hours=SCORE_DECAY_HOURS)):
            tenant.api_request_count = 0
            tenant.api_error_count = 0
            tenant.api_score = max(tenant.api_score - 0.2, 0.0)
            tenant.api_last_reset = now

        # ⛔ Suspended or expired
        if not tenant.is_active:
            return jsonify({"error": "This API key has been suspended"}), 403
        if tenant.api_key_expires_at and tenant.api_key_expires_at < now:
            return jsonify({"error": "API key has expired. Please renew or upgrade your plan."}), 403

        # ✅ Record usage
        tenant.last_api_access = now
        tenant.api_request_count += 1

        if tenant.api_request_count > rate_limit:
            tenant.api_score += 0.1

        # 🚨 Auto-suspend if abusive
        if tenant.api_score >= BLOCK_THRESHOLD:
            tenant.is_active = False
            db.session.add(tenant)
            db.session.add(RealTimeLog(
                tenant_id=tenant.id,
                user_id=None,
                action=f"🚫 Auto-suspended API Key due to abuse: {tenant.name}",
                ip_address=request.remote_addr,
                device_info=request.user_agent.string,
                location=get_ip_location(request.remote_addr)
            ))
            db.session.commit()
            return jsonify({"error": "API key suspended due to repeated abuse"}), 403

        # ✅ Save usage stats
        db.session.add(tenant)
        db.session.commit()
        g.tenant = tenant

        try:
            return func(*args, **kwargs)
        except Exception as e:
            tenant.api_error_count += 1
            if tenant.api_error_count >= ERROR_LIMIT:
                tenant.api_score += 0.1
            db.session.commit()
            raise e

    wrapper.__name__ = func.__name__
    return wrapper




def generate_api_key():
    return secrets.token_hex(32)
