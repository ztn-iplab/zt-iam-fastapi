# user_trust_engine.py

import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
from math import log, pow
from pathlib import Path

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
        base_risk = 0.0
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

    def _recent_success_logs(self, limit=5):
        return (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="success")
            .order_by(UserAuthLog.auth_timestamp.desc())
            .limit(limit)
            .all()
        )

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
                0.12,
                "Unusual login time",
                "If this is you, proceed; otherwise reset your password immediately.",
                {"hour": hour},
            )

    def rule_new_device_or_ip(self):
        device_info = self.context.get("device_info")
        ip_address = self.context.get("ip_address")
        recent_logs = self._recent_success_logs(limit=5)
        # Do not penalize first-time logins for "new device/network" without baseline history.
        if not recent_logs:
            return

        if device_info and not any(log.device_info == device_info for log in recent_logs):
            self._add_factor(
                "new_device",
                0.12,
                "New device detected",
                "Approve the login only if this is your device.",
            )
        if ip_address and not any(log.ip_address == ip_address for log in recent_logs):
            self._add_factor(
                "new_ip",
                0.12,
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
                0.05,
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
                0.12,
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
            recent_logs = self._recent_success_logs(limit=5)
            if not recent_logs:
                recent_logs = []

            if recent_logs and device_info and not any(log.device_info == device_info for log in recent_logs):
                weight = rules["new_device_or_ip"].get("weight", 0.2)
                self._add_factor(
                    "new_device",
                    weight,
                    "New device detected",
                    "Approve the login only if this is your device.",
                )
            if recent_logs and ip_address and not any(log.ip_address == ip_address for log in recent_logs):
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


DEFAULT_PROBABILISTIC_MODEL = {
    "version": "2026-03-02",
    "base_rate": 0.08,
    "prior_weight": 0.35,
    "feature_likelihood_ratios": {
        "large_transaction": 4.0,
        "odd_hours": 1.6,
        "new_device": 2.2,
        "new_ip": 1.9,
        "location_change": 2.4,
        "recent_failures": 3.8,
        "new_account": 1.3,
        "login_velocity": 1.8,
        "identity_unverified": 1.7,
        "device_not_bound": 2.0,
        "known_device": 0.72,
        "known_network": 0.8,
        "identity_verified": 0.78,
        "device_enrolled": 0.68,
    },
}


def _clamp_probability(value: float) -> float:
    return min(max(float(value), 1e-6), 1.0 - 1e-6)


def _odds_from_probability(probability: float) -> float:
    p = _clamp_probability(probability)
    return p / (1.0 - p)


@lru_cache(maxsize=1)
def _load_probabilistic_model() -> dict:
    configured_path = os.getenv("ZT_PROB_TRUST_MODEL_PATH", "").strip()
    if configured_path:
        candidate = Path(configured_path)
    else:
        candidate = Path(__file__).resolve().parents[1] / "config" / "trust_probabilistic_model.json"

    if candidate.exists():
        try:
            loaded = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return loaded
        except Exception:
            pass
    return DEFAULT_PROBABILISTIC_MODEL


class ProbabilisticTrustEngine(BaseTrustEngine):
    _FEATURE_INFO = {
        "large_transaction": ("Unusual transaction size", "Verify recipient and amount before proceeding."),
        "odd_hours": ("Unusual login time", "If unexpected, reset credentials and review recent activity."),
        "new_device": ("New device detected", "Approve only if this device belongs to you."),
        "new_ip": ("New network detected", "Confirm this network is trusted."),
        "location_change": ("Location change detected", "Secure the account if this location is unfamiliar."),
        "recent_failures": ("Recent failed attempts", "Multiple failures indicate active credential abuse."),
        "new_account": ("New account", "New accounts receive stricter checks until behavior stabilizes."),
        "login_velocity": ("High login velocity", "Unusual rapid logins may indicate account sharing or abuse."),
        "identity_unverified": ("Identity unverified", "Complete identity verification to reduce risk."),
        "device_not_bound": ("No trusted device bound", "Enroll a device key to reduce risk and step-up frequency."),
        "known_device": ("Known device", "Historical device consistency lowered risk."),
        "known_network": ("Known network", "Historical network consistency lowered risk."),
        "identity_verified": ("Identity verified", "Verified identity lowered risk."),
        "device_enrolled": ("Trusted device enrolled", "Bound device key lowered risk."),
    }

    def _active_features(self) -> tuple[dict, dict]:
        recent_logs = self._recent_success_logs(limit=5)
        has_history = bool(recent_logs)
        device_info = self.context.get("device_info")
        ip_address = self.context.get("ip_address")
        location = (self.context.get("location") or "").strip()
        amount = self.context.get("amount")
        now = datetime.utcnow()

        last_success = recent_logs[0] if has_history else None

        failures_window = now - timedelta(minutes=15)
        recent_failures = (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="failed")
            .filter(UserAuthLog.auth_timestamp >= failures_window)
            .count()
        )
        success_window = now - timedelta(hours=1)
        recent_successes = (
            UserAuthLog.query.filter_by(user_id=self.user.id, auth_status="success")
            .filter(UserAuthLog.auth_timestamp >= success_window)
            .count()
        )

        features = {
            "large_transaction": bool(amount is not None and amount > 30000),
            "odd_hours": bool(now.hour in {1, 2, 3, 4}),
            "new_device": bool(
                has_history and device_info and not any(log.device_info == device_info for log in recent_logs)
            ),
            "new_ip": bool(has_history and ip_address and not any(log.ip_address == ip_address for log in recent_logs)),
            "location_change": bool(
                has_history
                and last_success
                and last_success.location
                and location
                and location != "Unknown"
                and location != last_success.location
            ),
            "recent_failures": bool(recent_failures >= 3),
            "new_account": bool(
                self.user.created_at and self.user.created_at >= datetime.utcnow() - timedelta(days=7)
            ),
            "login_velocity": bool(recent_successes >= 5),
            "identity_unverified": bool(not self.user.identity_verified),
            "device_not_bound": bool(self.context.get("device_enrolled") is False),
            "known_device": bool(
                has_history and device_info and any(log.device_info == device_info for log in recent_logs)
            ),
            "known_network": bool(
                has_history and ip_address and any(log.ip_address == ip_address for log in recent_logs)
            ),
            "identity_verified": bool(self.user.identity_verified),
            "device_enrolled": bool(self.context.get("device_enrolled") is True),
        }

        evidence = {
            "recent_failures": {"failed_attempts_15m": recent_failures},
            "login_velocity": {"success_logins_1h": recent_successes},
            "location_change": {"location": location},
            "new_ip": {"ip_address": ip_address},
            "large_transaction": {"amount": amount},
        }
        return features, evidence

    def run(self):
        model = _load_probabilistic_model()
        lrs = model.get("feature_likelihood_ratios", {})
        base_rate = float(model.get("base_rate", 0.08))
        base_odds = _odds_from_probability(base_rate)
        odds = base_odds

        prior_weight = min(max(float(model.get("prior_weight", 0.35)), 0.0), 1.0)
        prior_prob = _clamp_probability(self.baseline_score)
        prior_odds = _odds_from_probability(prior_prob)
        if base_odds > 0:
            odds *= pow(prior_odds / base_odds, prior_weight)

        features, evidence = self._active_features()
        for feature, active in features.items():
            if not active:
                continue
            lr = float(lrs.get(feature, 1.0))
            if lr <= 0:
                continue
            odds *= lr
            title, guidance = self._FEATURE_INFO.get(feature, (feature.replace("_", " ").title(), ""))
            self.factors.append(
                {
                    "key": feature,
                    "weight": round(log(lr), 3),
                    "title": title,
                    "guidance": guidance,
                    "evidence": evidence.get(feature, {}),
                }
            )

        probability = odds / (1.0 + odds)
        self.score = min(max(probability, 0.0), 1.0)
        self.minimum_score = 0.0
        return round(self.score, 2)


def _risk_level(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


def evaluate_trust_details(user, context, tenant=None):
    mode = os.getenv("ZT_TRUST_ENGINE_MODE", "probabilistic").strip().lower()

    if tenant and hasattr(tenant, "custom_trust_logic") and callable(tenant.custom_trust_logic):
        try:
            score = tenant.custom_trust_logic(user, context)
            score = max(0.0, min(float(score), 1.0))
            return {"score": round(score, 2), "level": _risk_level(score), "factors": []}
        except Exception:
            pass

    if tenant and mode == "policy":
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

    if mode == "rules":
        engine = BaseTrustEngine(user, context)
    else:
        try:
            engine = ProbabilisticTrustEngine(user, context)
        except Exception:
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
