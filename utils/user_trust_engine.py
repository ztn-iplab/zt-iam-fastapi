# user_trust_engine.py
from datetime import datetime
from models.models import UserAuthLog

class BaseTrustEngine:
    def __init__(self, user, context):
        self.user = user
        self.context = context
        self.score = 0.0

    def run(self):
        self.rule_large_transaction()
        self.rule_odd_hours()
        self.rule_new_device_or_ip()
        self.rule_geo_trust()
        return round(min(self.score, 1.0), 2)

    def rule_large_transaction(self):
        amount = self.context.get("amount")
        if amount is None:
            return  # This tenant or action has nothing to do with transactions
        avg_amount = 10000
        if amount > avg_amount * 3:
            self.score += 0.4


    def rule_odd_hours(self):
        hour = datetime.utcnow().hour
        if hour in [1, 2, 3, 4]:
            self.score += 0.2

    def rule_new_device_or_ip(self):
        device_info = self.context.get("device_info")
        ip_address = self.context.get("ip_address")
        recent_logs = UserAuthLog.query.filter_by(user_id=self.user.id).order_by(
            UserAuthLog.auth_timestamp.desc()
        ).limit(5).all()

        if device_info and not any(log.device_info == device_info for log in recent_logs):
            self.score += 0.2
        if ip_address and not any(log.ip_address == ip_address for log in recent_logs):
            self.score += 0.2

    def rule_geo_trust(self):
        if self.user.trust_score < 0.3:
            self.score += 0.2


def evaluate_trust(user, context, tenant=None):
    # Hook for tenant-defined custom logic
    if tenant and hasattr(tenant, "custom_trust_logic") and callable(tenant.custom_trust_logic):
        try:
            return tenant.custom_trust_logic(user, context)
        except Exception as e:
            print(f"⚠️ Failed to use custom trust logic: {e}")

    # Default logic
    return BaseTrustEngine(user, context).run()
