#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, roc_auc_score


EXPECTED_ORDER = {"page_view": 0, "click": 1, "scroll": 2}


@dataclass
class CalibrationRow:
    session_id: str
    action_id: int
    scenario: str
    action_name: str
    delta_t_minutes: float
    prev_confidence: float
    e_telecom: float
    e_device: float
    e_timing: float
    e_ordering: float
    session_step_index: int
    recent_conf_mean_3: float
    recent_conf_slope_3: float
    recent_delta_mean_3: float
    recent_telecom_mean_3: float
    recent_device_mean_3: float
    recent_timing_mean_3: float
    recent_ordering_mean_3: float
    steps_since_strong_telecom: int
    minutes_since_strong_telecom: float
    aig_label: int
    manual_allow: bool
    manual_threshold: float
    manual_c_value: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and evaluate the AIg calibration dataset from merged traces")
    parser.add_argument("--trace-json", required=True, help="Merged AIg trace export JSON")
    parser.add_argument("--output-dir", required=True, help="Directory for calibration outputs")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Session-level train split ratio applied within each scenario",
    )
    return parser.parse_args()


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def load_trace(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def weighted_mean(observations: list[dict[str, Any]]) -> float:
    if not observations:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0.0
    for obs in observations:
        weight = float(obs.get("weight") or 1.0)
        reliability = float(obs.get("reliability") or 1.0)
        w = max(0.0, weight) * clamp01(reliability)
        weighted_sum += w * clamp01(float(obs.get("evidence_value") or 0.0))
        total_weight += w
    if total_weight <= 0:
        return statistics.fmean(clamp01(float(obs.get("evidence_value") or 0.0)) for obs in observations)
    return clamp01(weighted_sum / total_weight)


def timing_score(interaction_obs: list[dict[str, Any]], decision_time: datetime | None) -> float:
    if not interaction_obs or decision_time is None:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0.0
    for obs in interaction_obs:
        observed_at = parse_dt(obs.get("observed_at"))
        if observed_at is None:
            continue
        age_seconds = max(0.0, (decision_time - observed_at).total_seconds())
        recency = math.exp(-(age_seconds / 60.0))
        weight = float(obs.get("weight") or 1.0) * clamp01(float(obs.get("reliability") or 1.0)) * recency
        weighted_sum += weight * clamp01(float(obs.get("evidence_value") or 0.0))
        total_weight += weight
    if total_weight <= 0:
        return weighted_mean(interaction_obs)
    return clamp01(weighted_sum / total_weight)


def ordering_score(interaction_obs: list[dict[str, Any]]) -> float:
    if not interaction_obs:
        return 0.0
    ordered = sorted(
        interaction_obs,
        key=lambda obs: (
            parse_dt(obs.get("observed_at")) or datetime.min.replace(tzinfo=timezone.utc),
            int(obs.get("id") or 0),
        ),
    )
    avg_evidence = weighted_mean(ordered)
    if len(ordered) == 1:
        return avg_evidence
    good = 0
    total = 0
    for left, right in zip(ordered, ordered[1:]):
        l_rank = EXPECTED_ORDER.get(str(left.get("signal_key") or "").strip(), 99)
        r_rank = EXPECTED_ORDER.get(str(right.get("signal_key") or "").strip(), 99)
        good += int(l_rank <= r_rank)
        total += 1
    if total == 0:
        return avg_evidence
    return clamp01((good / total) * avg_evidence)


def build_dataset(trace: dict[str, Any]) -> list[CalibrationRow]:
    obs_by_id = {int(obs["id"]): obs for obs in trace.get("observations", []) if obs.get("id") is not None}
    rows_by_session: dict[str, list[CalibrationRow]] = {}
    decisions = [
        decision
        for decision in trace.get("decisions", [])
        if not ((decision.get("metadata_json") or {}).get("seeded"))
    ]
    decisions.sort(
        key=lambda decision: (
            str((decision.get("metadata_json") or {}).get("scenario") or "unknown"),
            str(decision.get("correlation_id") or decision.get("session_id") or ""),
            parse_dt(decision.get("decision_time")) or datetime.min.replace(tzinfo=timezone.utc),
            int(decision.get("id") or 0),
        )
    )
    for decision in decisions:
        md = decision.get("metadata_json") or {}
        ground_truth_allow = md.get("ground_truth_allow")
        if not isinstance(ground_truth_allow, bool):
            continue
        observation_ids = md.get("observation_ids_used") or []
        observations = [obs_by_id[oid] for oid in observation_ids if oid in obs_by_id]
        telecom_obs = [obs for obs in observations if obs.get("source_family") == "telecom"]
        device_obs = [obs for obs in observations if obs.get("source_family") == "device"]
        interaction_obs = [obs for obs in observations if obs.get("source_family") == "interaction"]
        decision_time = parse_dt(decision.get("decision_time"))
        session_id = str(decision.get("correlation_id") or decision.get("session_id") or "")
        session_rows = rows_by_session.setdefault(session_id, [])
        prev_rows = session_rows[-3:]
        strong_indices = [idx for idx, row in enumerate(session_rows) if row.e_telecom >= 0.8]
        last_strong_index = strong_indices[-1] if strong_indices else None
        step_index = len(session_rows) + 1
        delta_minutes = max(0.0, float(decision.get("delta_t_seconds") or 0.0) / 60.0)
        prev_confidence = clamp01(float(md.get("c_prev") or 1.0))
        e_telecom = weighted_mean(telecom_obs)
        e_device = weighted_mean(device_obs)
        e_timing = timing_score(interaction_obs, decision_time)
        e_ordering = ordering_score(interaction_obs)

        def recent_mean(values: list[float]) -> float:
            return float(statistics.fmean(values)) if values else 0.0

        recent_conf_values = [row.prev_confidence for row in prev_rows]
        recent_delta_values = [row.delta_t_minutes for row in prev_rows]
        recent_telecom_values = [row.e_telecom for row in prev_rows]
        recent_device_values = [row.e_device for row in prev_rows]
        recent_timing_values = [row.e_timing for row in prev_rows]
        recent_ordering_values = [row.e_ordering for row in prev_rows]

        row = CalibrationRow(
            session_id=session_id,
            action_id=int(decision["id"]),
            scenario=str(md.get("scenario") or "unknown"),
            action_name=str(decision.get("action_name") or ""),
            delta_t_minutes=delta_minutes,
            prev_confidence=prev_confidence,
            e_telecom=e_telecom,
            e_device=e_device,
            e_timing=e_timing,
            e_ordering=e_ordering,
            session_step_index=step_index,
            recent_conf_mean_3=recent_mean(recent_conf_values),
            recent_conf_slope_3=prev_confidence - recent_mean(recent_conf_values) if recent_conf_values else 0.0,
            recent_delta_mean_3=recent_mean(recent_delta_values),
            recent_telecom_mean_3=recent_mean(recent_telecom_values),
            recent_device_mean_3=recent_mean(recent_device_values),
            recent_timing_mean_3=recent_mean(recent_timing_values),
            recent_ordering_mean_3=recent_mean(recent_ordering_values),
            steps_since_strong_telecom=(len(session_rows) - last_strong_index) if last_strong_index is not None else len(session_rows),
            minutes_since_strong_telecom=(
                sum(item.delta_t_minutes for item in session_rows[last_strong_index + 1 :]) + delta_minutes
                if last_strong_index is not None
                else sum(item.delta_t_minutes for item in session_rows) + delta_minutes
            ),
            aig_label=int(ground_truth_allow),
            manual_allow=str(decision.get("decision") or "").strip().lower() == "allow",
            manual_threshold=float(decision.get("threshold") or 0.5),
            manual_c_value=float(decision.get("c_value") or 0.0),
        )
        session_rows.append(row)

    rows: list[CalibrationRow] = []
    for session_rows in rows_by_session.values():
        rows.extend(session_rows)
    return rows


def stratified_session_split(rows: list[CalibrationRow], seed: int, train_ratio: float) -> tuple[set[str], set[str]]:
    rng = random.Random(seed)
    by_scenario: dict[str, list[str]] = {}
    for row in rows:
        by_scenario.setdefault(row.scenario, [])
        if row.session_id not in by_scenario[row.scenario]:
            by_scenario[row.scenario].append(row.session_id)
    train_sessions: set[str] = set()
    eval_sessions: set[str] = set()
    for scenario, sessions in sorted(by_scenario.items()):
        local = list(sessions)
        rng.shuffle(local)
        train_count = max(1, min(len(local) - 1, round(len(local) * train_ratio)))
        train_sessions.update(local[:train_count])
        eval_sessions.update(local[train_count:])
    return train_sessions, eval_sessions


def feature_matrix(rows: list[CalibrationRow]) -> tuple[np.ndarray, np.ndarray]:
    x = np.array(
        [
            [
                row.e_telecom,
                row.e_device,
                row.e_timing,
                row.e_ordering,
                row.session_step_index,
                row.recent_conf_mean_3,
                row.recent_conf_slope_3,
                row.recent_delta_mean_3,
                row.recent_telecom_mean_3,
                row.recent_device_mean_3,
                row.recent_timing_mean_3,
                row.recent_ordering_mean_3,
                row.steps_since_strong_telecom,
                row.minutes_since_strong_telecom,
                row.delta_t_minutes,
                row.prev_confidence,
            ]
            for row in rows
        ],
        dtype=float,
    )
    y = np.array([row.aig_label for row in rows], dtype=int)
    return x, y


def choose_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    best_threshold = 0.5
    best_key = (-1.0, -1.0, -1.0)
    for threshold in [i / 100.0 for i in range(20, 81)]:
        y_pred = (y_prob >= threshold).astype(int)
        benign_total = int((y_true == 1).sum())
        attack_total = int((y_true == 0).sum())
        benign_allow = int(((y_true == 1) & (y_pred == 1)).sum())
        attack_block = int(((y_true == 0) & (y_pred == 0)).sum())
        continuity = benign_allow / benign_total if benign_total else 0.0
        blocking = attack_block / attack_total if attack_total else 0.0
        f1 = f1_score(y_true, y_pred, zero_division=0)
        key = (blocking + continuity, f1, blocking)
        if key > best_key:
            best_key = key
            best_threshold = threshold
    return best_threshold


def classification_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "AUROC": float(roc_auc_score(y_true, y_prob)),
        "AUPRC": float(average_precision_score(y_true, y_prob)),
        "F1-score": float(f1_score(y_true, y_pred, zero_division=0)),
        "Brier score": float(brier_score_loss(y_true, y_prob)),
    }


def compare_manual_vs_learned(eval_rows: list[CalibrationRow], learned_prob: np.ndarray, threshold: float) -> dict[str, dict[str, float]]:
    y_true = np.array([row.aig_label for row in eval_rows], dtype=int)
    manual_pred = np.array([1 if row.manual_allow else 0 for row in eval_rows], dtype=int)
    learned_pred = (learned_prob >= threshold).astype(int)

    def summarize(pred: np.ndarray) -> dict[str, float]:
        benign_total = int((y_true == 1).sum())
        attack_total = int((y_true == 0).sum())
        false_step_up = int(((y_true == 1) & (pred == 0)).sum())
        blocked = int(((y_true == 0) & (pred == 0)).sum())
        continuity = int(((y_true == 1) & (pred == 1)).sum())
        return {
            "false_step_up_rate_benign": false_step_up / benign_total if benign_total else 0.0,
            "takeover_blocking_rate": blocked / attack_total if attack_total else 0.0,
            "task_completion_continuity": continuity / benign_total if benign_total else 0.0,
        }

    manual = summarize(manual_pred)
    learned = summarize(learned_pred)

    return {"manual": manual, "learned": learned}


def write_dataset_csv(rows: list[CalibrationRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "session_id",
                "action_id",
                "scenario",
                "action_name",
                "delta_t_minutes",
                "prev_confidence",
                "e_telecom",
                "e_device",
                "e_timing",
                "e_ordering",
                "session_step_index",
                "recent_conf_mean_3",
                "recent_conf_slope_3",
                "recent_delta_mean_3",
                "recent_telecom_mean_3",
                "recent_device_mean_3",
                "recent_timing_mean_3",
                "recent_ordering_mean_3",
                "steps_since_strong_telecom",
                "minutes_since_strong_telecom",
                "aig_label",
                "manual_allow",
                "manual_threshold",
                "manual_c_value",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.session_id,
                    row.action_id,
                    row.scenario,
                    row.action_name,
                    round(row.delta_t_minutes, 6),
                    round(row.prev_confidence, 6),
                    round(row.e_telecom, 6),
                    round(row.e_device, 6),
                    round(row.e_timing, 6),
                    round(row.e_ordering, 6),
                    row.session_step_index,
                    round(row.recent_conf_mean_3, 6),
                    round(row.recent_conf_slope_3, 6),
                    round(row.recent_delta_mean_3, 6),
                    round(row.recent_telecom_mean_3, 6),
                    round(row.recent_device_mean_3, 6),
                    round(row.recent_timing_mean_3, 6),
                    round(row.recent_ordering_mean_3, 6),
                    row.steps_since_strong_telecom,
                    round(row.minutes_since_strong_telecom, 6),
                    row.aig_label,
                    int(row.manual_allow),
                    round(row.manual_threshold, 6),
                    round(row.manual_c_value, 6),
                ]
            )


def write_table_csv(path: Path, rows: list[tuple[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Metric", "Value"])
        writer.writerows(rows)


def write_comparison_svg(comparison: dict[str, dict[str, float]], path: Path) -> None:
    metrics = [
        ("False step-up rate", "false_step_up_rate_benign"),
        ("Takeover blocking rate", "takeover_blocking_rate"),
        ("Task completion continuity", "task_completion_continuity"),
    ]
    width, height = 980, 500
    ml, mr, mt, mb = 88, 28, 96, 84
    cw, ch = width - ml - mr, height - mt - mb
    group_w = cw / len(metrics)
    bar_w = 70
    colors = {"manual": "#A04000", "learned": "#117A65"}
    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' style=\"font-family: 'Times New Roman', serif;\">",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<text x='{ml}' y='38' font-size='32' font-weight='700' fill='#222'>Manual vs learned AIg calibration</text>",
        f"<text x='{ml}' y='68' font-size='21' fill='#555'>Held-out session split; timing/ordering reconstructed from interaction sub-signals.</text>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt+ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt+ch}' x2='{ml+cw}' y2='{mt+ch}' stroke='#222'/>",
    ]
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = mt + ch - (tick * ch)
        lines.append(f"<line x1='{ml}' y1='{y:.1f}' x2='{ml+cw}' y2='{y:.1f}' stroke='#eee'/>")
        lines.append(f"<text x='{ml-10}' y='{y+6:.1f}' font-size='19' text-anchor='end' fill='#222'>{tick:.2f}</text>")
    for idx, (label, key) in enumerate(metrics):
        gx = ml + idx * group_w + (group_w / 2)
        for offset, name in [(-bar_w / 2, "manual"), (bar_w / 2, "learned")]:
            value = comparison[name][key]
            bh = value * ch
            x = gx + offset - (bar_w / 2)
            y = mt + ch - bh
            value_y = max(82.0, y - 10.0)
            lines.append(
                f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w}' height='{bh:.1f}' fill='{colors[name]}' opacity='0.9'/>"
            )
            lines.append(
                f"<text x='{x + bar_w/2:.1f}' y='{value_y:.1f}' font-size='21' font-weight='700' text-anchor='middle' fill='#222'>{value:.3f}</text>"
            )
        lines.append(f"<text x='{gx:.1f}' y='{mt+ch+34:.1f}' font-size='21' text-anchor='middle' fill='#222'>{label}</text>")
    lx = ml
    ly = height - 24
    for name, color in [("manual", colors["manual"]), ("learned", colors["learned"])]:
        lines.append(f"<rect x='{lx}' y='{ly-14}' width='22' height='14' fill='{color}'/>")
        lines.append(f"<text x='{lx+34}' y='{ly}' font-size='20' fill='#222'>{name}</text>")
        lx += 138
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    trace_path = Path(args.trace_json).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    trace = load_trace(trace_path)
    rows = build_dataset(trace)
    if not rows:
        raise SystemExit("No calibration rows found in trace")

    train_sessions, eval_sessions = stratified_session_split(rows, seed=args.seed, train_ratio=args.train_ratio)
    train_rows = [row for row in rows if row.session_id in train_sessions]
    eval_rows = [row for row in rows if row.session_id in eval_sessions]

    x_train, y_train = feature_matrix(train_rows)
    x_eval, y_eval = feature_matrix(eval_rows)

    model = LogisticRegression(max_iter=2000, solver="lbfgs", random_state=args.seed)
    model.fit(x_train, y_train)
    train_prob = model.predict_proba(x_train)[:, 1]
    eval_prob = model.predict_proba(x_eval)[:, 1]
    threshold = choose_threshold(y_train, train_prob)
    metrics = classification_metrics(y_eval, eval_prob, threshold)
    comparison = compare_manual_vs_learned(eval_rows, eval_prob, threshold)

    dataset_csv = out_dir / "aig_calibration_dataset.csv"
    write_dataset_csv(rows, dataset_csv)

    benign_records = sum(row.aig_label == 1 for row in rows)
    violation_records = sum(row.aig_label == 0 for row in rows)
    total_observation_points = sum(
        len((decision.get("metadata_json") or {}).get("observation_ids_used") or [])
        for decision in trace.get("decisions", [])
        if not (decision.get("metadata_json") or {}).get("seeded")
    )

    table7_rows = [
        ("Total observation records", total_observation_points),
        ("Benign records", benign_records),
        ("AIg-violation records", violation_records),
        ("Training records", len(train_rows)),
        ("Evaluation records", len(eval_rows)),
        ("Validation protocol", "70/30 session-level split within each scenario (seed=2026)"),
    ]
    write_table_csv(out_dir / "table7_calibration_split.csv", table7_rows)

    table8_rows = [(key, f"{value:.4f}") for key, value in metrics.items()]
    table8_rows.append(("Decision threshold", f"{threshold:.2f}"))
    write_table_csv(out_dir / "table8_calibration_results.csv", table8_rows)

    table9_rows = [
        ("False step-up rate (benign) - manual", f"{comparison['manual']['false_step_up_rate_benign']:.4f}"),
        ("False step-up rate (benign) - learned", f"{comparison['learned']['false_step_up_rate_benign']:.4f}"),
        ("Takeover blocking rate - manual", f"{comparison['manual']['takeover_blocking_rate']:.4f}"),
        ("Takeover blocking rate - learned", f"{comparison['learned']['takeover_blocking_rate']:.4f}"),
        ("Task completion continuity - manual", f"{comparison['manual']['task_completion_continuity']:.4f}"),
        ("Task completion continuity - learned", f"{comparison['learned']['task_completion_continuity']:.4f}"),
    ]
    write_table_csv(out_dir / "table9_manual_vs_learned.csv", table9_rows)

    feature_names = [
        "e_telecom",
        "e_device",
        "e_timing",
        "e_ordering",
        "session_step_index",
        "recent_conf_mean_3",
        "recent_conf_slope_3",
        "recent_delta_mean_3",
        "recent_telecom_mean_3",
        "recent_device_mean_3",
        "recent_timing_mean_3",
        "recent_ordering_mean_3",
        "steps_since_strong_telecom",
        "minutes_since_strong_telecom",
        "delta_t_minutes",
        "prev_confidence",
    ]
    table10_rows = [(name, f"{coef:.4f}") for name, coef in zip(feature_names, model.coef_[0], strict=True)]
    table10_rows.append(("Intercept beta0", f"{model.intercept_[0]:.4f}"))
    write_table_csv(out_dir / "table10_learned_coefficients.csv", table10_rows)

    write_comparison_svg(comparison, out_dir / "fig6_manual_vs_learned.svg")

    summary = {
        "input_trace": str(trace_path),
        "dataset_csv": str(dataset_csv),
        "notes": {
            "timing_inference": "e_timing is reconstructed as a recency-weighted interaction score because the runtime engine logs family-level interaction evidence.",
            "ordering_inference": "e_ordering is reconstructed from page_view->click->scroll progression within each decision window.",
        },
        "table7": {key: value for key, value in table7_rows},
        "table8": {key: value for key, value in table8_rows},
        "table9": {key: value for key, value in table9_rows},
        "table10": {key: value for key, value in table10_rows},
    }
    (out_dir / "calibration_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
