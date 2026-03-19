#!/usr/bin/env python3
"""Train a probabilistic trust model from auth logs.

This script estimates feature likelihood ratios:
LR(feature) = P(feature | risky) / P(feature | safe)
with Laplace smoothing, and writes a JSON model consumed by
utils/user_trust_engine.py.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.db import SessionLocal
from app.models import Device, DeviceKey, User, UserAuthLog


FEATURES = [
    "large_transaction",
    "odd_hours",
    "new_device",
    "new_ip",
    "location_change",
    "recent_failures",
    "new_account",
    "login_velocity",
    "identity_unverified",
    "device_not_bound",
    "known_device",
    "known_network",
    "identity_verified",
    "device_enrolled",
]

RISK_FEATURES = {
    "large_transaction",
    "odd_hours",
    "new_device",
    "new_ip",
    "location_change",
    "recent_failures",
    "new_account",
    "login_velocity",
    "identity_unverified",
    "device_not_bound",
}

PROTECTIVE_FEATURES = {
    "known_device",
    "known_network",
    "identity_verified",
    "device_enrolled",
}


@dataclass
class TrainingStats:
    total_risky: int = 0
    total_safe: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train probabilistic trust model from auth logs")
    parser.add_argument(
        "--output",
        default="config/trust_probabilistic_model.json",
        help="Output JSON model path",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Laplace smoothing alpha",
    )
    parser.add_argument(
        "--base-rate-floor",
        type=float,
        default=0.02,
        help="Minimum base risky-event rate",
    )
    parser.add_argument(
        "--base-rate-ceiling",
        type=float,
        default=0.35,
        help="Maximum base risky-event rate",
    )
    return parser.parse_args()


def _norm(value: str | None) -> str:
    return (value or "").strip()


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        users = {u.id: u for u in db.query(User).all()}

        enrolled_user_ids = {
            row[0]
            for row in (
                db.query(Device.user_id)
                .join(DeviceKey, DeviceKey.device_id == Device.id)
                .distinct()
                .all()
            )
            if row and row[0] is not None
        }

        logs = (
            db.query(UserAuthLog)
            .filter(UserAuthLog.auth_method == "password")
            .order_by(UserAuthLog.user_id.asc(), UserAuthLog.auth_timestamp.asc())
            .all()
        )

        feature_counts_risky = defaultdict(int)
        feature_counts_safe = defaultdict(int)
        stats = TrainingStats()

        success_history = defaultdict(lambda: deque(maxlen=20))
        fail_history_15m = defaultdict(deque)
        success_history_1h = defaultdict(deque)

        for log in logs:
            user = users.get(log.user_id)
            if not user or not log.auth_timestamp:
                continue

            ts = log.auth_timestamp
            uid = log.user_id

            failures = fail_history_15m[uid]
            while failures and failures[0] < ts - timedelta(minutes=15):
                failures.popleft()

            recent_successes = success_history_1h[uid]
            while recent_successes and recent_successes[0] < ts - timedelta(hours=1):
                recent_successes.popleft()

            success_logs = list(success_history[uid])
            has_history = bool(success_logs)

            device_info = _norm(log.device_info)
            ip_address = _norm(log.ip_address)
            location = _norm(log.location)
            known_devices = {item[0] for item in success_logs if item[0]}
            known_ips = {item[1] for item in success_logs if item[1]}
            last_location = success_logs[-1][2] if has_history else ""

            features = {
                "large_transaction": False,
                "odd_hours": ts.hour in {1, 2, 3, 4},
                "new_device": has_history and bool(device_info) and device_info not in known_devices,
                "new_ip": has_history and bool(ip_address) and ip_address not in known_ips,
                "location_change": has_history
                and bool(last_location)
                and bool(location)
                and location != "Unknown"
                and location != last_location,
                "recent_failures": len(failures) >= 3,
                "new_account": bool(user.created_at and user.created_at >= ts - timedelta(days=7)),
                "login_velocity": len(recent_successes) >= 5,
                "identity_unverified": not bool(user.identity_verified),
                "device_not_bound": uid not in enrolled_user_ids,
                "known_device": has_history and bool(device_info) and device_info in known_devices,
                "known_network": has_history and bool(ip_address) and ip_address in known_ips,
                "identity_verified": bool(user.identity_verified),
                "device_enrolled": uid in enrolled_user_ids,
            }

            risky = log.auth_status != "success"
            if risky:
                stats.total_risky += 1
                target = feature_counts_risky
            else:
                stats.total_safe += 1
                target = feature_counts_safe

            for feature, active in features.items():
                if active:
                    target[feature] += 1

            if risky:
                failures.append(ts)
            else:
                recent_successes.append(ts)
                success_history[uid].append((device_info, ip_address, location))

        if stats.total_risky == 0 or stats.total_safe == 0:
            raise RuntimeError("Need both risky and safe auth log samples to train model")

        alpha = max(args.alpha, 1e-6)
        model = {
            "version": datetime.now(UTC).strftime("%Y-%m-%d"),
            "base_rate": min(
                max(stats.total_risky / (stats.total_risky + stats.total_safe), args.base_rate_floor),
                args.base_rate_ceiling,
            ),
            "prior_weight": 0.35,
            "smoothing_alpha": alpha,
            "training": {
                "samples": stats.total_risky + stats.total_safe,
                "risky_samples": stats.total_risky,
                "safe_samples": stats.total_safe,
            },
            "feature_likelihood_ratios": {},
        }

        for feature in FEATURES:
            p_feat_risky = (feature_counts_risky[feature] + alpha) / (stats.total_risky + (2.0 * alpha))
            p_feat_safe = (feature_counts_safe[feature] + alpha) / (stats.total_safe + (2.0 * alpha))
            lr = p_feat_risky / p_feat_safe
            if feature in RISK_FEATURES and lr < 1.0:
                lr = 1.0 / max(lr, 1e-6)
            if feature in PROTECTIVE_FEATURES and lr > 1.0:
                lr = 1.0 / lr
            model["feature_likelihood_ratios"][feature] = round(float(lr), 4)

        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = Path(__file__).resolve().parents[1] / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

        print(f"Wrote model to {output_path}")
        print(json.dumps(model["training"], indent=2))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
