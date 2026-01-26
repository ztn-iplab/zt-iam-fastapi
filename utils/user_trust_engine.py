# user_trust_engine.py

from datetime import datetime, timedelta
from math import pow

from app.models import TenantTrustPolicyFile, UserAuthLog


class BaseTrustEngine:
    def __init__(self, user, context):
        self.user = user
        self.context = context
        self.factors = []
        self._factor_keys = set()
        self.baseline_score = self._compute_baseline_score()
        self.score = self.baseline_score
        self.minimum_score = self.baseline_score
        self.confidence = self._compute_confidence()
        self.last_evaluation = datetime.utcnow()

    def _compute_baseline_score(self):
        base_risk = 0.15
        prior = self.user.trust_score if self.user.trust_score is not None else base_risk
        last_login = self.user.last_login or self.user.created_at
        if last_login:
            age_days = max(0, (datetime.utcnow() - last_login).days)
            half_life_days = 7
            decay = pow(0.5, age_days / half_life_days)
            prior = base_risk + (prior - base_risk) * decay
        return max(base_risk, min(prior, 1.0))

    def _compute_confidence(self):
        signal_keys = ("device_info", "ip_address", "location", "amount", "device_enrolled")
        signals = sum(1 for key in signal_keys if self.context.get(key) is not None)
        return min(1.0, 0.4 + (signals * 0.12))

    def _add_factor(self, key, weight, title, guidance, evidence=None):
        if key in self._factor_keys:
            return
        self._factor_keys.add(key)
        if weight <= 0:
            return
        self.score += weight
        self.factors.append(
            {
                "key": key,
                "weight": round(weight, 2),
                "title": title,
                "guidance": guidance,
                "evidence": evidence or {},
            }
        )

    def finalize(self):
        score = min(max(self.score, self.minimum_score), 1.0)
        return round(score, 2)

    def run(self):
        self.rule_large_transaction()
        self.rule_odd_hours()
        self.rule_new_device_or_ip()
        self.rule_location_change()
        self.rule_recent_failures()
        self.rule_account_age()
        self.rule_login_velocity()
        self.rule_identity_unverified()
        self.rule_missing_device_binding()
        return self.finalize()

    def rule_large_transaction(self):
        amount = self.context.get("amount")
        if amount is None:
            return
        avg_amount = 10000
        if amount > avg_amount * 3:
            self._add_factor(
                "large_transaction",
                0.4,
                "Unusual transaction size",
                "Verify the recipient and consider a smaller test transfer first.",
                {"amount": amount},
            )

    def rule_odd_hours(self):
        hour = datetime.utcnow().hour
        if hour in [1, 2, 3, 4]:
            self._add_factor(
                "odd_hours",
                0.2,
                "Unusual login time",
                "If this is you, proceed; otherwise reset your password immediately.",
                {"hour": hour},
            )

    def rule_new_device_or_ip(self):
        device_info = self.context.get("device_info")
        ip_address = self.context.get("ip_address")
        recent_logs = (
            UserAuthLog.query.filter_by(user_id=self.user.id)
            .order_by(UserAuthLog.auth_timestamp.desc())
            .limit(5)
            .all()
        )

        if device_info and not any(log.device_info == device_info for log in recent_logs):
            self._add_factor(
                "new_device",
                0.2,
                "New device detected",
                "Approve the login only if this is your device.",
            )
        if ip_address and not any(log.ip_address == ip_address for log in recent_logs):
            self._add_factor(
                "new_ip",
                0.2,
                "New network detected",
                "If this IP is unfamiliar, change your password.",
                {"ip_address": ip_address},
            )

    def rule_location_change(self):
        location = (self.context.get("location") or "").strip()
        if not location or location == "Unknown":
            return
        last = (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="success")
            .order_by(UserAuthLog.auth_timestamp.desc())
            .first()
        )
        if last and last.location and last.location != location:
            self._add_factor(
                "location_change",
                0.2,
                "Location change detected",
                "If this location is unexpected, secure your account.",
                {"location": location},
            )

    def rule_recent_failures(self):
        window = datetime.utcnow() - timedelta(minutes=15)
        failures = (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="failed")
            .filter(UserAuthLog.auth_timestamp >= window)
            .count()
        )
        if failures >= 3:
            self._add_factor(
                "recent_failures",
                0.35,
                "Multiple failed login attempts",
                "If this wasn't you, reset your password and review recent activity.",
                {"failed_attempts": failures},
            )

    def rule_account_age(self):
        if not self.user.created_at:
            return
        if self.user.created_at >= datetime.utcnow() - timedelta(days=7):
            self._add_factor(
                "new_account",
                0.15,
                "New account",
                "Complete profile verification to improve trust.",
            )

    def rule_login_velocity(self):
        window = datetime.utcnow() - timedelta(hours=1)
        logins = (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="success")
            .filter(UserAuthLog.auth_timestamp >= window)
            .count()
        )
        if logins >= 5:
            self._add_factor(
                "login_velocity",
                0.2,
                "High login activity",
                "If this wasn’t you, sign out of other sessions.",
                {"login_count": logins},
            )

    def rule_identity_unverified(self):
        if not self.user.identity_verified:
            self._add_factor(
                "identity_unverified",
                0.1,
                "Identity not verified",
                "Verify your identity to reduce future risk checks.",
            )

    def rule_missing_device_binding(self):
        device_enrolled = self.context.get("device_enrolled")
        if device_enrolled is False:
            self._add_factor(
                "device_not_bound",
                0.25,
                "No trusted device bound",
                "Enroll a trusted device for stronger protection.",
            )


class JSONPolicyTrustEngine(BaseTrustEngine):
    def __init__(self, user, context, tenant):
        super().__init__(user, context)
        self.tenant = tenant

    def run(self):
        policy_file = TenantTrustPolicyFile.query.filter_by(tenant_id=self.tenant.id).first()

        if not policy_file:
            return super().run()

        config = policy_file.config_json
        if not isinstance(config, dict):
            return super().run()

        rules = config.get("rules", {})
        ctx = self.context

        if rules.get("odd_hours", {}).get("enabled"):
            hour = (datetime.utcnow().hour + 9) % 24
            if hour in rules["odd_hours"].get("hours", [1, 2, 3, 4]):
                weight = rules["odd_hours"].get("weight", 0.2)
                self._add_factor(
                    "odd_hours",
                    weight,
                    "Unusual login time",
                    "If this is you, proceed; otherwise secure your account.",
                    {"hour": hour},
                )

        if rules.get("new_device_or_ip", {}).get("enabled"):
            device_info = ctx.get("device_info")
            ip_address = ctx.get("ip_address")
            recent_logs = (
                UserAuthLog.query.filter_by(user_id=self.user.id)
                .order_by(UserAuthLog.auth_timestamp.desc())
                .limit(5)
                .all()
            )

            if device_info and not any(log.device_info == device_info for log in recent_logs):
                weight = rules["new_device_or_ip"].get("weight", 0.2)
                self._add_factor(
                    "new_device",
                    weight,
                    "New device detected",
                    "Approve the login only if this is your device.",
                )
            if ip_address and not any(log.ip_address == ip_address for log in recent_logs):
                weight = rules["new_device_or_ip"].get("weight", 0.2)
                self._add_factor(
                    "new_ip",
                    weight,
                    "New network detected",
                    "If this IP is unfamiliar, change your password.",
                    {"ip_address": ip_address},
                )

        if rules.get("geo_trust", {}).get("enabled"):
            min_score = rules["geo_trust"].get("min_trust_score", 0.3)
            if self.user.trust_score < min_score:
                weight = rules["geo_trust"].get("weight", 0.2)
                self._add_factor(
                    "geo_trust",
                    weight,
                    "Location trust below threshold",
                    "Confirm your location before proceeding.",
                )

        if rules.get("login_frequency", {}).get("enabled"):
            threshold = rules["login_frequency"].get("threshold", 3)
            weight = rules["login_frequency"].get("weight", 0.2)

            since = datetime.utcnow() - timedelta(hours=24)
            login_count = (
                UserAuthLog.query.filter_by(
                    user_id=self.user.id,
                    auth_method="password",
                    auth_status="success",
                )
                .filter(UserAuthLog.auth_timestamp >= since)
                .count()
            )

            if login_count >= threshold:
                self._add_factor(
                    "login_frequency",
                    weight,
                    "Unusual login frequency",
                    "Consider changing your password if this wasn’t you.",
                    {"login_count": login_count},
                )

        return self.finalize()


def _risk_level(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


def evaluate_trust_details(user, context, tenant=None):
    if tenant and hasattr(tenant, "custom_trust_logic") and callable(tenant.custom_trust_logic):
        try:
            score = tenant.custom_trust_logic(user, context)
            score = max(0.0, min(float(score), 1.0))
            return {"score": round(score, 2), "level": _risk_level(score), "factors": []}
        except Exception:
            pass

    if tenant:
        policy_file = TenantTrustPolicyFile.query.filter_by(tenant_id=tenant.id).first()
        if policy_file:
            try:
                engine = JSONPolicyTrustEngine(user, context, tenant)
                score = engine.run()
                return {
                    "score": score,
                    "level": _risk_level(score),
                    "factors": engine.factors,
                    "confidence": engine.confidence,
                    "baseline": round(engine.baseline_score, 2),
                }
            except Exception:
                pass

    engine = BaseTrustEngine(user, context)
    score = engine.run()
    return {
        "score": score,
        "level": _risk_level(score),
        "factors": engine.factors,
        "confidence": engine.confidence,
        "baseline": round(engine.baseline_score, 2),
    }


def evaluate_trust(user, context, tenant=None):
    return evaluate_trust_details(user, context, tenant)["score"]
