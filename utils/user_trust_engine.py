# user_trust_engine.py

from datetime import datetime, timedelta
import json
from models.models import UserAuthLog, TenantTrustPolicyFile

# -------------------------------
# BaseTrustEngine – Default Rules
# -------------------------------

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
            return
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


# -------------------------------
# JSONPolicyTrustEngine – Per Tenant
# -------------------------------

class JSONPolicyTrustEngine(BaseTrustEngine):
    def __init__(self, user, context, tenant):
        super().__init__(user, context)
        self.tenant = tenant

    def run(self):
        policy_file = TenantTrustPolicyFile.query.filter_by(
            tenant_id=self.tenant.id
        ).first()

        if not policy_file:
            print("📂 No tenant policy found. Using BaseTrustEngine.")
            return super().run()

        config = policy_file.config_json  #  Already stored as JSON in DB

        if not isinstance(config, dict):
            print("⚠️ Invalid config format. Using BaseTrustEngine.")
            return super().run()

        rules = config.get("rules", {})
        score = 0.0
        ctx = self.context

        #  Odd Hours
        if rules.get("odd_hours", {}).get("enabled"):
            hour = (datetime.utcnow().hour + 9) % 24  # Adjust to JST
            # hour = datetime.utcnow().hour
            if hour in rules["odd_hours"].get("hours", [1, 2, 3, 4]):
                print("📌 odd hours triggered")
                score += rules["odd_hours"].get("weight", 0.2)


        #  New Device/IP
        if rules.get("new_device_or_ip", {}).get("enabled"):
            device_info = ctx.get("device_info")
            ip_address = ctx.get("ip_address")
            recent_logs = UserAuthLog.query.filter_by(user_id=self.user.id).order_by(
                UserAuthLog.auth_timestamp.desc()
            ).limit(5).all()

            if device_info and not any(log.device_info == device_info for log in recent_logs):
                score += rules["new_device_or_ip"].get("weight", 0.2)
            if ip_address and not any(log.ip_address == ip_address for log in recent_logs):
                print("📌 new device rule triggered")
                score += rules["new_device_or_ip"].get("weight", 0.2)

        #  Geo Trust
        if rules.get("geo_trust", {}).get("enabled"):
            min_score = rules["geo_trust"].get("min_trust_score", 0.3)
            if self.user.trust_score < min_score:
                print("📌 geo_trust triggered")
                score += rules["geo_trust"].get("weight", 0.2)

        #  Login Frequency Rule
        if rules.get("login_frequency", {}).get("enabled"):
            threshold = rules["login_frequency"].get("threshold", 3)
            weight = rules["login_frequency"].get("weight", 0.2)

            since = datetime.utcnow() - timedelta(hours=24)
            login_count = UserAuthLog.query.filter_by(
                user_id=self.user.id,
                auth_method="password",
                auth_status="success"
            ).filter(UserAuthLog.auth_timestamp >= since).count()

            if login_count >= threshold:
                print(f"📌 login_frequency triggered with count={login_count}")
                score += weight


        return round(min(score, 1.0), 2)


# -------------------------------
# Trust Evaluation Entry Point
# -------------------------------

def evaluate_trust(user, context, tenant=None):
    #  Optional custom callable hook
    if tenant and hasattr(tenant, "custom_trust_logic") and callable(tenant.custom_trust_logic):
        try:
            score = tenant.custom_trust_logic(user, context)
            print(f"📊 Trust Score (Callable Logic): {score}")
            return score
        except Exception as e:
            print(f"⚠️ Failed to use custom trust logic: {e}")

    #  Use tenant.id to load policy if present
    if tenant:
        policy_file = TenantTrustPolicyFile.query.filter_by(tenant_id=tenant.id).first()
        if policy_file:
            try:
                score = JSONPolicyTrustEngine(user, context, tenant).run()
                print(f"📊 Trust Score (JSON Policy): {score}")
                return score
            except Exception as e:
                print(f"⚠️ JSONPolicyTrustEngine failed: {e}")
        else:
            print("📂 No tenant policy found. Using BaseTrustEngine.")
    else:
        print("⚠️ No tenant provided. Using BaseTrustEngine.")

    #  Fallback
    score = BaseTrustEngine(user, context).run()
    print(f"📊 Trust Score (Base Engine Fallback): {score}")
    return score
