#!/usr/bin/env python3
import argparse
import csv
import json
import random
import ssl
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


RNG = random.Random(2026)
JITTER = 0.0


def _j(value: float, scale: float | None = None) -> float:
    amt = JITTER if scale is None else scale
    if amt <= 0:
        return float(value)
    return max(0.0, min(1.0, float(value) + RNG.uniform(-amt, amt)))


class ApiClient:
    def __init__(self, base_url: str, api_key: str, insecure: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        ctx = ssl._create_unverified_context() if insecure else None
        handlers = []
        if ctx:
            handlers.append(request.HTTPSHandler(context=ctx))
        self.opener = request.build_opener(*handlers)
        self.max_retries = 3
        self.retry_base_sleep = 0.75

    def request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        for attempt in range(self.max_retries + 1):
            data = json.dumps(payload).encode("utf-8") if payload is not None else None
            req = request.Request(
                f"{self.base_url}{path}",
                data=data,
                method=method,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                },
            )
            try:
                with self.opener.open(req, timeout=10) as resp:
                    raw = resp.read().decode("utf-8")
                    return resp.status, json.loads(raw) if raw else {}
            except error.HTTPError as exc:
                raw = exc.read().decode("utf-8")
                try:
                    body = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    body = {"raw": raw}
                if exc.code == 429 and attempt < self.max_retries:
                    time.sleep(self.retry_base_sleep * (2 ** attempt))
                    continue
                return exc.code, body

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        suffix = ""
        if params:
            suffix = "?" + parse.urlencode({k: v for k, v in params.items() if v is not None})
        return self.request_json("GET", f"{path}{suffix}")

    def post_json(self, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        return self.request_json("POST", path, payload)


@dataclass
class DecisionRow:
    experiment_run_id: str
    scenario: str
    correlation_id: str
    action_index: int
    expected_allow: bool
    observed_decision: str
    c_obs: float | None
    c_decay: float | None
    c_value: float | None
    threshold: float
    alpha: float
    decay_lambda: float
    observation_count: int
    reason: str
    step_up_required: bool
    http_status: int
    pass_expectation: bool


def ensure_ok(status: int, body: dict[str, Any], context: str) -> dict[str, Any]:
    if status != 200:
        raise RuntimeError(f"{context} failed: status={status} body={body}")
    return body


def post_observations(client: ApiClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    status, body = client.post_json("/aig/observations/batch", {"observations": rows})
    ensure_ok(status, body, "observations/batch")


def post_telecom_events(client: ApiClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    status, body = client.post_json("/aig/telecom/events/batch", {"events": rows})
    ensure_ok(status, body, "telecom/events/batch")


def seed_decision(client: ApiClient, row: dict[str, Any]) -> None:
    status, body = client.post_json("/aig/decisions", row)
    ensure_ok(status, body, "seed decision")


def authorize(client: ApiClient, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    return client.post_json("/aig/authorize", payload)


def export_trace(client: ApiClient, *, correlation_id: str | None, experiment_run_id: str | None) -> dict[str, Any]:
    status, body = client.get_json(
        "/aig/traces/export",
        {"correlation_id": correlation_id, "experiment_run_id": experiment_run_id},
    )
    return ensure_ok(status, body, "trace export")


def make_obs(
    *,
    t: datetime,
    user_id: int,
    corr: str,
    run_id: str,
    actor_label: str,
    source_family: str,
    source_name: str,
    signal_key: str,
    evidence_value: float,
    weight: float | None = None,
    reliability: float | None = None,
    session_id: str | None = None,
    session_label: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "observed_at": iso_z(t),
        "source_family": source_family,
        "source_name": source_name,
        "signal_key": signal_key,
        "evidence_value": evidence_value,
        "weight": weight,
        "reliability": reliability,
        "session_id": session_id,
        "session_label": session_label,
        "correlation_id": corr,
        "experiment_run_id": run_id,
        "actor_label": actor_label,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "metadata_json": metadata or {},
    }


def make_tel_event(
    *,
    t: datetime,
    user_id: int,
    corr: str,
    run_id: str,
    actor_label: str,
    event_type: str,
    source_type: str = "simulator",
    source_independent: bool = True,
    source_confidence: float = 0.9,
    source_weight_hint: float | None = 0.6,
    mobile_number: str = "+15550001111",
    old_iccid: str | None = None,
    new_iccid: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "event_type": event_type,
        "event_time": iso_z(t),
        "mobile_number": mobile_number,
        "old_iccid": old_iccid,
        "new_iccid": new_iccid,
        "source_type": source_type,
        "source_independent": source_independent,
        "source_confidence": source_confidence,
        "source_weight_hint": source_weight_hint,
        "correlation_id": corr,
        "experiment_run_id": run_id,
        "actor_label": actor_label,
        "metadata_json": metadata or {},
    }


def run_single_authorize(
    client: ApiClient,
    *,
    scenario: str,
    corr: str,
    run_id: str,
    user_id: int,
    action_index: int,
    expected_allow: bool,
    threshold: float,
    alpha: float,
    decay_lambda: float,
    metadata: dict[str, Any],
    action_name: str = "view_patient_record",
    action_class: str = "ehr_read",
    resource_type: str = "patient",
    resource_id: str = "42",
    initial_c: float | None = None,
) -> DecisionRow:
    payload = {
        "action_name": action_name,
        "action_class": action_class,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "user_id": user_id,
        "session_id": corr,
        "correlation_id": corr,
        "experiment_run_id": run_id,
        "threshold": threshold,
        "alpha": alpha,
        "decay_lambda": decay_lambda,
        "window_seconds": 3600,
        "on_below_threshold": "step_up",
        "metadata_json": {
            "scenario": scenario,
            "action_index": action_index,
            "ground_truth_allow": expected_allow,
            **metadata,
        },
    }
    if initial_c is not None:
        payload["initial_c"] = initial_c

    status, body = authorize(client, payload)
    observed_decision = (body.get("decision") or f"http_{status}").strip().lower()
    pass_expectation = (observed_decision == "allow") == expected_allow if status == 200 else False
    return DecisionRow(
        experiment_run_id=run_id,
        scenario=scenario,
        correlation_id=corr,
        action_index=action_index,
        expected_allow=expected_allow,
        observed_decision=observed_decision,
        c_obs=body.get("c_obs"),
        c_decay=body.get("c_decay"),
        c_value=body.get("c_value"),
        threshold=float(body.get("threshold") or threshold),
        alpha=float(body.get("alpha") or alpha),
        decay_lambda=float(body.get("decay_lambda") or decay_lambda),
        observation_count=int(body.get("observation_count") or 0),
        reason=str(body.get("reason") or ""),
        step_up_required=bool(body.get("step_up_required")),
        http_status=status,
        pass_expectation=pass_expectation,
    )


def scenario_benign_high(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "benign_high_interaction"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    t0 = utc_now()
    obs = [
        make_obs(
            t=t0 - timedelta(seconds=35),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="interaction",
            source_name="hms_browser_telemetry",
            signal_key="page_view",
            evidence_value=_j(0.80, 0.05),
            weight=0.3,
            reliability=0.6,
            session_id=f"browser-{uuid.uuid4().hex[:8]}",
            session_label="benign",
            resource_type="hms_page",
            resource_id="/patients/view",
        ),
        make_obs(
            t=t0 - timedelta(seconds=18),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="interaction",
            source_name="hms_browser_telemetry",
            signal_key="click",
            evidence_value=_j(0.85, 0.05),
            weight=0.3,
            reliability=0.6,
            resource_type="hms_page",
            resource_id="/patients/view",
        ),
        make_obs(
            t=t0 - timedelta(seconds=5),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="interaction",
            source_name="hms_browser_telemetry",
            signal_key="scroll",
            evidence_value=_j(0.75, 0.05),
            weight=0.3,
            reliability=0.6,
            resource_type="hms_page",
            resource_id="/patients/view",
        ),
    ]
    post_observations(client, obs)
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=0,
            expected_allow=True,
            threshold=0.70,
            alpha=0.70,
            decay_lambda=0.001,
            metadata={"ground_truth": "benign"},
        )
    ]


def scenario_benign_telecom_noise(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "benign_with_telecom_noise"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    t0 = utc_now()
    tel = [
        make_tel_event(
            t=t0 - timedelta(seconds=90),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            event_type="network_reattach",
            source_confidence=0.7,
            source_weight_hint=0.2,
            metadata={"note": "benign cellular handoff"},
        )
    ]
    obs = [
        make_obs(
            t=t0 - timedelta(seconds=60),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="telecom",
            source_name="carrier-sim",
            signal_key="recent_swap_window",
            evidence_value=_j(0.30, 0.04),
            weight=0.5,
            reliability=0.9,
        ),
        make_obs(
            t=t0 - timedelta(seconds=20),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="interaction",
            source_name="hms_browser_telemetry",
            signal_key="page_view",
            evidence_value=_j(0.78, 0.05),
            weight=0.3,
            reliability=0.6,
            resource_type="hms_page",
            resource_id="/appointments",
        ),
        make_obs(
            t=t0 - timedelta(seconds=4),
            user_id=user_id,
            corr=corr,
            run_id=run_id,
            actor_label="doctor_legit",
            source_family="interaction",
            source_name="hms_browser_telemetry",
            signal_key="click",
            evidence_value=_j(0.80, 0.05),
            weight=0.3,
            reliability=0.6,
            resource_type="hms_page",
            resource_id="/appointments",
        ),
    ]
    post_telecom_events(client, tel)
    post_observations(client, obs)
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=0,
            expected_allow=True,
            threshold=0.65,
            alpha=0.70,
            decay_lambda=0.001,
            metadata={"ground_truth": "benign"},
            action_name="manage_appointments",
            resource_id="appointments",
        )
    ]


def scenario_benign_pause_resume(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "benign_pause_resume_short"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    now = utc_now()
    seed_decision(
        client,
        {
            "user_id": user_id,
            "decision_time": iso_z(now - timedelta(seconds=60)),
            "action_name": "view_patient_record",
            "action_class": "ehr_read",
            "resource_type": "patient",
            "resource_id": "42",
            "session_id": corr,
            "correlation_id": corr,
            "experiment_run_id": run_id,
            "c_obs": 0.92,
            "c_decay": 0.92,
            "c_value": 0.92,
            "threshold": 0.70,
            "alpha": 0.7,
            "decay_lambda": 0.001,
            "delta_t_seconds": 0.0,
            "decision": "allow",
            "reason": "seeded_prior_for_pause_resume",
            "step_up_required": False,
            "observation_count": 0,
            "metadata_json": {"scenario": scenario, "seeded": True},
        },
    )
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=1,
            expected_allow=True,
            threshold=0.70,
            alpha=0.70,
            decay_lambda=0.001,
            metadata={"ground_truth": "benign_pause", "idle_seconds": 60},
        )
    ]


def scenario_benign_device_consistent(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "benign_device_consistent"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    t0 = utc_now()
    post_observations(
        client,
        [
            make_obs(
                t=t0 - timedelta(seconds=12),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="doctor_legit",
                source_family="device",
                source_name="zt_iam_device_binding",
                signal_key="known_device_key_match",
                evidence_value=_j(0.95, 0.03),
                weight=0.6,
                reliability=0.95,
                metadata={"attested": True},
            ),
            make_obs(
                t=t0 - timedelta(seconds=7),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="doctor_legit",
                source_family="interaction",
                source_name="hms_browser_telemetry",
                signal_key="click",
                evidence_value=_j(0.72, 0.06),
                weight=0.3,
                reliability=0.6,
                resource_type="hms_page",
                resource_id="/patients/view",
            ),
        ],
    )
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=0,
            expected_allow=True,
            threshold=0.70,
            alpha=0.70,
            decay_lambda=0.001,
            metadata={"ground_truth": "benign", "device_consistent": True},
        )
    ]


def scenario_takeover_device_mismatch(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "takeover_device_mismatch"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    t0 = utc_now()
    post_observations(
        client,
        [
            make_obs(
                t=t0 - timedelta(seconds=18),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="device",
                source_name="zt_iam_device_binding",
                signal_key="known_device_key_match",
                evidence_value=_j(0.10, 0.03),
                weight=0.6,
                reliability=0.95,
                metadata={"attested": False, "device_unknown": True},
            ),
            make_obs(
                t=t0 - timedelta(seconds=11),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="interaction",
                source_name="hms_browser_telemetry",
                signal_key="page_view",
                evidence_value=_j(0.55, 0.08),
                weight=0.3,
                reliability=0.6,
            ),
            make_obs(
                t=t0 - timedelta(seconds=5),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="telecom",
                source_name="carrier-sim",
                signal_key="line_rebound_after_swap",
                evidence_value=_j(0.20, 0.05),
                weight=0.4,
                reliability=0.9,
            ),
        ],
    )
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=0,
            expected_allow=False,
            threshold=0.65,
            alpha=0.75,
            decay_lambda=0.001,
            metadata={"ground_truth": "takeover", "device_mismatch": True, "compromised": True},
        )
    ]


def scenario_takeover_swap_low(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "takeover_recent_swap_low_interaction"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    t0 = utc_now()
    post_telecom_events(
        client,
        [
            make_tel_event(
                t=t0 - timedelta(seconds=30),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker_after_sim_swap",
                event_type="sim_swap_completed",
                old_iccid="ICCID-OLD-001",
                new_iccid="ICCID-NEW-777",
                metadata={"simulator": "attack_scenario"},
            )
        ],
    )
    post_observations(
        client,
        [
            make_obs(
                t=t0 - timedelta(seconds=25),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="telecom",
                source_name="carrier-sim",
                signal_key="recent_swap_window",
                evidence_value=_j(0.10, 0.04),
                weight=0.6,
                reliability=0.95,
            ),
            make_obs(
                t=t0 - timedelta(seconds=20),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="interaction",
                source_name="hms_browser_telemetry",
                signal_key="page_view",
                evidence_value=_j(0.20, 0.05),
                weight=0.3,
                reliability=0.6,
            ),
            make_obs(
                t=t0 - timedelta(seconds=8),
                user_id=user_id,
                corr=corr,
                run_id=run_id,
                actor_label="attacker",
                source_family="interaction",
                source_name="hms_browser_telemetry",
                signal_key="click",
                evidence_value=_j(0.15, 0.05),
                weight=0.3,
                reliability=0.6,
            ),
        ],
    )
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=0,
            expected_allow=False,
            threshold=0.65,
            alpha=0.80,
            decay_lambda=0.001,
            metadata={"ground_truth": "takeover", "compromised": True},
        )
    ]


def scenario_idle_decay(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "idle_decay_stepup"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    now = utc_now()
    seeded_at = now - timedelta(hours=2)
    seed_decision(
        client,
        {
            "user_id": user_id,
            "decision_time": iso_z(seeded_at),
            "action_name": "view_patient_record",
            "action_class": "ehr_read",
            "resource_type": "patient",
            "resource_id": "42",
            "session_id": corr,
            "correlation_id": corr,
            "experiment_run_id": run_id,
            "c_obs": 0.95,
            "c_decay": 0.95,
            "c_value": 0.95,
            "threshold": 0.7,
            "alpha": 0.7,
            "decay_lambda": 0.001,
            "delta_t_seconds": 0.0,
            "decision": "allow",
            "reason": "seeded_prior_for_decay",
            "step_up_required": False,
            "observation_count": 0,
            "metadata_json": {"scenario": scenario, "seeded": True},
        },
    )
    return [
        run_single_authorize(
            client,
            scenario=scenario,
            corr=corr,
            run_id=run_id,
            user_id=user_id,
            action_index=1,
            expected_allow=False,
            threshold=0.70,
            alpha=0.70,
            decay_lambda=0.001,
            metadata={"ground_truth": "benign_idle", "idle_seconds": 7200},
        )
    ]


def scenario_takeover_progression(client: ApiClient, run_id: str, user_id: int) -> list[DecisionRow]:
    scenario = "takeover_progression"
    corr = f"{scenario}-{uuid.uuid4().hex[:10]}"
    now = utc_now()
    seed_decision(
        client,
        {
            "user_id": user_id,
            "decision_time": iso_z(now - timedelta(minutes=5)),
            "action_name": "view_patient_record",
            "action_class": "ehr_read",
            "resource_type": "patient",
            "resource_id": "42",
            "session_id": corr,
            "correlation_id": corr,
            "experiment_run_id": run_id,
            "c_obs": 0.90,
            "c_decay": 0.90,
            "c_value": 0.90,
            "threshold": 0.65,
            "alpha": 0.75,
            "decay_lambda": 0.001,
            "delta_t_seconds": 0.0,
            "decision": "allow",
            "reason": "seeded_prior_for_progression",
            "step_up_required": False,
            "observation_count": 0,
            "metadata_json": {"scenario": scenario, "seeded": True},
        },
    )

    rows: list[DecisionRow] = []
    phases = [
        # expected_allow, interaction_score, telecom_score (lower is riskier)
        (True, _j(0.72, 0.05), _j(0.55, 0.05)),
        (True, _j(0.62, 0.05), _j(0.40, 0.05)),
        (False, _j(0.40, 0.05), _j(0.20, 0.04)),
        (False, _j(0.25, 0.05), _j(0.10, 0.04)),
    ]
    for idx, (expected_allow, interaction_e, telecom_e) in enumerate(phases):
        t = utc_now()
        if idx == 0:
            post_telecom_events(
                client,
                [
                    make_tel_event(
                        t=t - timedelta(seconds=20),
                        user_id=user_id,
                        corr=corr,
                        run_id=run_id,
                        actor_label="transition",
                        event_type="sim_swap_completed",
                        old_iccid="ICCID-OLD-PROG",
                        new_iccid="ICCID-NEW-PROG",
                        metadata={"phase": idx},
                    )
                ],
            )
        post_observations(
            client,
            [
                make_obs(
                    t=t - timedelta(seconds=4),
                    user_id=user_id,
                    corr=corr,
                    run_id=run_id,
                    actor_label="mixed",
                    source_family="telecom",
                    source_name="carrier-sim",
                    signal_key="recent_swap_window",
                    evidence_value=telecom_e,
                    weight=0.6,
                    reliability=0.95,
                    metadata={"phase": idx},
                ),
                make_obs(
                    t=t - timedelta(seconds=2),
                    user_id=user_id,
                    corr=corr,
                    run_id=run_id,
                    actor_label="mixed",
                    source_family="interaction",
                    source_name="hms_browser_telemetry",
                    signal_key="click",
                    evidence_value=interaction_e,
                    weight=0.3,
                    reliability=0.6,
                    metadata={"phase": idx},
                ),
            ],
        )
        rows.append(
            run_single_authorize(
                client,
                scenario=scenario,
                corr=corr,
                run_id=run_id,
                user_id=user_id,
                action_index=idx + 1,
                expected_allow=expected_allow,
                threshold=0.65,
                alpha=0.75,
                decay_lambda=0.001,
                metadata={
                    "ground_truth": "takeover_progression",
                    "phase_index": idx,
                    "compromised": (idx >= 2),
                    "series_type": "takeover_progression",
                },
            )
        )
        time.sleep(0.05)
    return rows


def write_csv(rows: list[DecisionRow], output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "experiment_run_id",
                "scenario",
                "correlation_id",
                "action_index",
                "expected_allow",
                "observed_decision",
                "c_obs",
                "c_decay",
                "c_value",
                "threshold",
                "alpha",
                "decay_lambda",
                "observation_count",
                "reason",
                "step_up_required",
                "http_status",
                "pass_expectation",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r.experiment_run_id,
                    r.scenario,
                    r.correlation_id,
                    r.action_index,
                    str(r.expected_allow).lower(),
                    r.observed_decision,
                    r.c_obs,
                    r.c_decay,
                    r.c_value,
                    r.threshold,
                    r.alpha,
                    r.decay_lambda,
                    r.observation_count,
                    r.reason,
                    str(r.step_up_required).lower(),
                    r.http_status,
                    str(r.pass_expectation).lower(),
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate labeled AIg experiment traces")
    parser.add_argument("--base-url", default="https://localhost/api/v1")
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each scenario generator N times for larger traces")
    parser.add_argument("--jitter", type=float, default=0.03, help="Random evidence jitter amplitude in [0,1]")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for reproducible jitter")
    parser.add_argument("--output-csv", default="experiments/aig_scenarios.csv")
    parser.add_argument("--export-dir", default="experiments/aig_traces")
    parser.add_argument("--export-combined", action="store_true", help="Export combined trace for experiment_run_id")
    args = parser.parse_args()

    global RNG, JITTER
    RNG = random.Random(args.seed)
    JITTER = max(0.0, min(0.5, float(args.jitter)))

    client = ApiClient(args.base_url, args.api_key, insecure=args.insecure)
    run_id = f"aigexp-{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}-{uuid.uuid4().hex[:6]}"
    print(f"experiment_run_id={run_id}")

    all_rows: list[DecisionRow] = []
    generators = [
        scenario_benign_high,
        scenario_benign_telecom_noise,
        scenario_benign_pause_resume,
        scenario_benign_device_consistent,
        scenario_takeover_swap_low,
        scenario_takeover_device_mismatch,
        scenario_idle_decay,
        scenario_takeover_progression,
    ]
    for rep in range(max(1, args.repeats)):
        for fn in generators:
            rows = fn(client, run_id, args.user_id)
            all_rows.extend(rows)
            print(f"{fn.__name__}[rep={rep+1}]: {len(rows)} decision(s)")

    write_csv(all_rows, args.output_csv)
    print(f"Wrote {args.output_csv}")

    if args.export_combined:
        export = export_trace(client, correlation_id=None, experiment_run_id=run_id)
        out_dir = Path(args.export_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{run_id}.json"
        out_file.write_text(json.dumps(export, indent=2), encoding="utf-8")
        print(f"Wrote {out_file}")

    passes = sum(1 for r in all_rows if r.pass_expectation)
    print(f"Expectation match: {passes}/{len(all_rows)}")
    if passes != len(all_rows):
        sys.exit(2)


if __name__ == "__main__":
    main()
