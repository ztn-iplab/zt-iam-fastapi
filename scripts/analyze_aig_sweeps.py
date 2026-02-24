#!/usr/bin/env python3
import argparse
import csv
import json
import math
import ssl
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


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


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class ApiClient:
    def __init__(self, base_url: str, api_key: str, insecure: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        ctx = ssl._create_unverified_context() if insecure else None
        handlers = []
        if ctx:
            handlers.append(request.HTTPSHandler(context=ctx))
        self.opener = request.build_opener(*handlers)

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        suffix = ""
        if params:
            suffix = "?" + parse.urlencode({k: v for k, v in params.items() if v is not None})
        req = request.Request(
            f"{self.base_url}{path}{suffix}",
            headers={"X-API-Key": self.api_key},
            method="GET",
        )
        try:
            with self.opener.open(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if raw else {}
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                body = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                body = {"raw": raw}
            return exc.code, body


@dataclass
class Obs:
    id: int
    user_id: int | None
    correlation_id: str | None
    session_id: str | None
    observed_at: datetime
    source_family: str | None
    source_name: str | None
    signal_key: str | None
    evidence_value: float
    weight: float | None
    reliability: float | None


@dataclass
class Dec:
    id: int
    user_id: int | None
    correlation_id: str | None
    session_id: str | None
    action_name: str | None
    decision_time: datetime
    threshold: float | None
    alpha: float | None
    decay_lambda: float | None
    delta_t_seconds: float | None
    metadata_json: dict[str, Any]
    ground_truth_allow: bool | None


def parse_list(s: str) -> list[float]:
    vals = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        vals.append(float(part))
    return vals


def parse_str_list(s: str) -> list[str]:
    vals = []
    for part in s.split(","):
        part = part.strip()
        if part:
            vals.append(part)
    return vals


def weighted_c_obs(
    obs_rows: list[Obs],
    *,
    family_weights: dict[str, float],
    use_reliability: bool,
) -> float | None:
    if not obs_rows:
        return None
    weighted_sum = 0.0
    total_weight = 0.0
    for o in obs_rows:
        e = clamp01(o.evidence_value)
        w = 1.0 if o.weight is None else max(0.0, float(o.weight))
        fam = (o.source_family or "").strip().lower()
        w *= max(0.0, float(family_weights.get(fam, 1.0)))
        if use_reliability:
            rel = 1.0 if o.reliability is None else clamp01(float(o.reliability))
            w *= rel
        weighted_sum += w * e
        total_weight += w
    if total_weight > 0:
        return clamp01(weighted_sum / total_weight)
    return clamp01(sum(clamp01(o.evidence_value) for o in obs_rows) / len(obs_rows))


def load_trace_from_api(client: ApiClient, experiment_run_id: str | None, correlation_id: str | None) -> dict[str, Any]:
    status, body = client.get_json(
        "/aig/traces/export",
        {"experiment_run_id": experiment_run_id, "correlation_id": correlation_id, "limit_per_stream": 10000},
    )
    if status != 200:
        raise RuntimeError(f"trace export failed: status={status} body={body}")
    return body


def normalize_trace(data: dict[str, Any]) -> tuple[list[Obs], list[Dec]]:
    obs: list[Obs] = []
    for row in data.get("observations", []):
        dt = parse_dt(row.get("observed_at"))
        if dt is None:
            continue
        obs.append(
            Obs(
                id=int(row["id"]),
                user_id=row.get("user_id"),
                correlation_id=row.get("correlation_id"),
                session_id=row.get("session_id"),
                observed_at=dt,
                source_family=row.get("source_family"),
                source_name=row.get("source_name"),
                signal_key=row.get("signal_key"),
                evidence_value=float(row.get("evidence_value") or 0.0),
                weight=(None if row.get("weight") is None else float(row["weight"])),
                reliability=(None if row.get("reliability") is None else float(row["reliability"])),
            )
        )

    decs: list[Dec] = []
    for row in data.get("decisions", []):
        dt = parse_dt(row.get("decision_time"))
        if dt is None:
            continue
        md = row.get("metadata_json") or {}
        if not isinstance(md, dict):
            md = {}
        if md.get("seeded") is True:
            gta = None
        else:
            gta = md.get("ground_truth_allow")
        if isinstance(gta, str):
            gta = gta.strip().lower() in {"1", "true", "yes", "y"}
        elif not isinstance(gta, bool):
            gta = None
        decs.append(
            Dec(
                id=int(row["id"]),
                user_id=row.get("user_id"),
                correlation_id=row.get("correlation_id"),
                session_id=row.get("session_id"),
                action_name=row.get("action_name"),
                decision_time=dt,
                threshold=(None if row.get("threshold") is None else float(row["threshold"])),
                alpha=(None if row.get("alpha") is None else float(row["alpha"])),
                decay_lambda=(None if row.get("decay_lambda") is None else float(row["decay_lambda"])),
                delta_t_seconds=(None if row.get("delta_t_seconds") is None else float(row["delta_t_seconds"])),
                metadata_json=md,
                ground_truth_allow=gta,
            )
        )
    return obs, decs


def filter_obs_for_decision(obs_by_corr: dict[str, list[Obs]], dec: Dec, window_seconds: int) -> list[Obs]:
    if dec.correlation_id and dec.correlation_id in obs_by_corr:
        source = obs_by_corr[dec.correlation_id]
    else:
        source = []
    lower = dec.decision_time.timestamp() - max(0, window_seconds)
    upper = dec.decision_time.timestamp()
    return [o for o in source if lower <= o.observed_at.timestamp() <= upper]


def recompute_predictions(
    observations: list[Obs],
    decisions: list[Dec],
    *,
    theta: float,
    alpha: float,
    decay_lambda: float,
    family_weights: dict[str, float],
    use_reliability: bool,
    include_families: set[str] | None,
) -> list[dict[str, Any]]:
    obs_by_corr: dict[str, list[Obs]] = defaultdict(list)
    for o in observations:
        if o.correlation_id:
            obs_by_corr[o.correlation_id].append(o)
    for corr in obs_by_corr:
        obs_by_corr[corr].sort(key=lambda x: (x.observed_at, x.id))

    scored: list[dict[str, Any]] = []
    state_c: dict[tuple[Any, ...], float] = {}
    state_t: dict[tuple[Any, ...], datetime] = {}

    decs = sorted(decisions, key=lambda d: (d.decision_time, d.id))
    for d in decs:
        state_key = (d.user_id, d.correlation_id or d.session_id, d.action_name)
        md = d.metadata_json or {}
        window_seconds = int(md.get("window_seconds", 300))
        obs_rows = filter_obs_for_decision(obs_by_corr, d, window_seconds)
        if include_families is not None:
            obs_rows = [o for o in obs_rows if (o.source_family or "").strip().lower() in include_families]
        c_obs = weighted_c_obs(obs_rows, family_weights=family_weights, use_reliability=use_reliability)

        if state_key in state_c and state_key in state_t:
            c_prev = state_c[state_key]
            dt_seconds = max(0.0, (d.decision_time - state_t[state_key]).total_seconds())
        else:
            c_prev = clamp01(float(md.get("c_prev", 1.0)))
            if d.delta_t_seconds is not None:
                dt_seconds = max(0.0, float(d.delta_t_seconds))
            else:
                dt_seconds = 0.0

        c_decay = clamp01(c_prev * math.exp(-decay_lambda * dt_seconds))
        if c_obs is None:
            c_value = c_decay
            reason = "no_recent_observations"
        else:
            c_value = clamp01(alpha * c_obs + (1.0 - alpha) * c_decay)
            reason = "threshold_met" if c_value >= theta else "below_threshold"

        pred_allow = c_value >= theta
        pred_decision = "allow" if pred_allow else "step_up"
        scored.append(
            {
                "decision_id": d.id,
                "scenario": md.get("scenario"),
                "series_type": md.get("series_type"),
                "phase_index": md.get("phase_index"),
                "correlation_id": d.correlation_id,
                "action_name": d.action_name,
                "decision_time": d.decision_time.isoformat(),
                "ground_truth_allow": d.ground_truth_allow,
                "pred_allow": pred_allow,
                "pred_decision": pred_decision,
                "c_obs": c_obs,
                "c_decay": c_decay,
                "c_value": c_value,
                "obs_count": len(obs_rows),
                "theta": theta,
                "alpha": alpha,
                "decay_lambda": decay_lambda,
                "w_telecom": family_weights.get("telecom", 1.0),
                "w_device": family_weights.get("device", 1.0),
                "w_interaction": family_weights.get("interaction", 1.0),
                "use_reliability": use_reliability,
                "ablation": ("all" if include_families is None else "+".join(sorted(include_families))),
                "reason": reason,
            }
        )
        state_c[state_key] = c_value
        state_t[state_key] = d.decision_time

    return scored


def summarize(scored: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [r for r in scored if isinstance(r.get("ground_truth_allow"), bool)]
    tp = tn = fp = fn = 0
    for r in labeled:
        gt = bool(r["ground_truth_allow"])
        pred = bool(r["pred_allow"])
        if gt and pred:
            tp += 1
        elif gt and not pred:
            fn += 1
        elif not gt and pred:
            fp += 1
        else:
            tn += 1
    total = len(labeled)
    benign_total = tp + fn
    attack_total = fp + tn
    frr = (fn / benign_total) if benign_total else None
    far = (fp / attack_total) if attack_total else None
    acc = ((tp + tn) / total) if total else None

    # Progression detection delay (in phase steps) for labeled takeover series.
    by_corr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in scored:
        corr = r.get("correlation_id")
        if corr:
            by_corr[corr].append(r)
    delays = []
    for corr, items in by_corr.items():
        items.sort(key=lambda x: (x.get("phase_index") is None, x.get("phase_index"), x["decision_id"]))
        compromised = [i for i in items if i.get("series_type") == "takeover_progression" and i.get("phase_index") is not None and int(i["phase_index"]) >= 2]
        if not compromised:
            continue
        first_comp = min(int(i["phase_index"]) for i in compromised)
        first_detect = None
        for i in compromised:
            if not i["pred_allow"]:
                first_detect = int(i["phase_index"])
                break
        if first_detect is None:
            delays.append(None)
        else:
            delays.append(first_detect - first_comp)

    detectable = [d for d in delays if d is not None]
    return {
        "labeled_total": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": acc,
        "false_accept_rate": far,
        "false_reject_rate": frr,
        "takeover_series": len(delays),
        "takeover_detected_series": len(detectable),
        "avg_detection_phase_delay": (sum(detectable) / len(detectable)) if detectable else None,
        "max_detection_phase_delay": (max(detectable) if detectable else None),
    }


def ablation_to_include_families(name: str) -> set[str] | None:
    key = name.strip().lower()
    if key in {"all", "none"}:
        return None
    mapping = {
        "telecom_only": {"telecom"},
        "device_only": {"device"},
        "interaction_only": {"interaction"},
        "no_telecom": {"device", "interaction"},
        "no_device": {"telecom", "interaction"},
        "no_interaction": {"telecom", "device"},
        "telecom+interaction": {"telecom", "interaction"},
        "telecom+device": {"telecom", "device"},
        "device+interaction": {"device", "interaction"},
    }
    if key not in mapping:
        raise ValueError(f"Unsupported ablation '{name}'")
    return mapping[key]


def write_threshold_curve_svg(summary_rows: list[dict[str, Any]], path: Path) -> None:
    if not summary_rows:
        return
    # Select a non-threshold parameter bundle using best FAR/FRR/ACC across rows.
    def rank_key(r: dict[str, Any]):
        return (
            1.0 if r.get("false_accept_rate") is None else float(r["false_accept_rate"]),
            1.0 if r.get("false_reject_rate") is None else float(r["false_reject_rate"]),
            -(0.0 if r.get("accuracy") is None else float(r["accuracy"])),
        )

    best_row = min(summary_rows, key=rank_key)
    bundle_key = (
        best_row.get("alpha"),
        best_row.get("decay_lambda"),
        best_row.get("w_telecom"),
        best_row.get("w_device"),
        best_row.get("w_interaction"),
        best_row.get("use_reliability"),
        best_row.get("ablation"),
    )
    rows = [
        r for r in summary_rows
        if (
            r.get("alpha"),
            r.get("decay_lambda"),
            r.get("w_telecom"),
            r.get("w_device"),
            r.get("w_interaction"),
            r.get("use_reliability"),
            r.get("ablation"),
        ) == bundle_key
    ]
    rows.sort(key=lambda r: float(r["theta"]))
    if not rows:
        return

    width = 900
    height = 460
    ml, mr, mt, mb = 70, 20, 30, 80
    cw = width - ml - mr
    ch = height - mt - mb

    def x_of(theta: float) -> float:
        t_min = float(rows[0]["theta"])
        t_max = float(rows[-1]["theta"])
        if t_max == t_min:
            return ml + cw / 2
        return ml + ((theta - t_min) / (t_max - t_min)) * cw

    def y_of(val: float) -> float:
        return mt + ch - clamp01(val) * ch

    def path_for(metric_key: str) -> str:
        pts = []
        for r in rows:
            val = r.get(metric_key)
            if val is None:
                continue
            pts.append((x_of(float(r["theta"])), y_of(float(val))))
        if not pts:
            return ""
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)

    far_path = path_for("false_accept_rate")
    frr_path = path_for("false_reject_rate")
    acc_path = path_for("accuracy")

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt+ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt+ch}' x2='{ml+cw}' y2='{mt+ch}' stroke='#222'/>",
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        y = y_of(tick)
        lines.append(f"<line x1='{ml-4}' y1='{y:.1f}' x2='{ml+cw}' y2='{y:.1f}' stroke='#eee'/>")
        lines.append(f"<text x='{ml-8}' y='{y+4:.1f}' font-size='16' text-anchor='end' fill='#222'>{tick:.2f}</text>")
    for r in rows:
        x = x_of(float(r["theta"]))
        lines.append(f"<line x1='{x:.1f}' y1='{mt+ch}' x2='{x:.1f}' y2='{mt+ch+5}' stroke='#222'/>")
        lines.append(
            f"<text x='{x:.1f}' y='{mt+ch+20}' font-size='16' text-anchor='middle' fill='#222'>{float(r['theta']):.2f}</text>"
        )
    if far_path:
        lines.append(f"<path d='{far_path}' fill='none' stroke='#C0392B' stroke-width='2.5'/>")
    if frr_path:
        lines.append(f"<path d='{frr_path}' fill='none' stroke='#2E86C1' stroke-width='2.5'/>")
    if acc_path:
        lines.append(f"<path d='{acc_path}' fill='none' stroke='#117A65' stroke-width='2.5' stroke-dasharray='6 4'/>")
    subtitle = (
        f"alpha={best_row['alpha']}, lambda={best_row['decay_lambda']}, "
        f"wT={best_row['w_telecom']}, wD={best_row['w_device']}, wI={best_row['w_interaction']}, "
        f"rel={best_row['use_reliability']}, ablation={best_row['ablation']}"
    )
    lines.append(f"<text x='{ml}' y='18' font-size='18' fill='#222'>AIg Sweep: FAR/FRR/ACC vs threshold</text>")
    lines.append(f"<text x='{ml}' y='34' font-size='15' fill='#555'>{subtitle}</text>")
    legend_y = height - 22
    legend = [("#C0392B", "FAR"), ("#2E86C1", "FRR"), ("#117A65", "ACC")]
    x = ml
    for color, label in legend:
        lines.append(f"<line x1='{x}' y1='{legend_y}' x2='{x+18}' y2='{legend_y}' stroke='{color}' stroke-width='2.5'/>")
        lines.append(f"<text x='{x+24}' y='{legend_y+4}' font-size='16' fill='#222'>{label}</text>")
        x += 90
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def _match_bundle(row: dict[str, Any], stats: dict[str, Any]) -> bool:
    keys = [
        "theta",
        "alpha",
        "decay_lambda",
        "w_telecom",
        "w_device",
        "w_interaction",
        "use_reliability",
        "ablation",
    ]
    return all(row.get(k) == stats.get(k) for k in keys)


def write_trajectory_svg(pred_rows: list[dict[str, Any]], best_stats: dict[str, Any] | None, path: Path) -> None:
    if not best_stats:
        return
    rows = [r for r in pred_rows if _match_bundle(r, best_stats)]
    if not rows:
        return
    candidates = [r for r in rows if r.get("scenario") == "takeover_progression"]
    if not candidates:
        candidates = rows

    by_corr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in candidates:
        corr = str(r.get("correlation_id") or "unknown")
        by_corr[corr].append(r)
    corr, series = max(by_corr.items(), key=lambda kv: len(kv[1]))
    series.sort(key=lambda r: (r.get("phase_index") is None, r.get("phase_index"), r.get("decision_id")))
    if not series:
        return

    width = 980
    height = 480
    ml, mr, mt, mb = 70, 20, 35, 90
    cw = width - ml - mr
    ch = height - mt - mb

    n = len(series)
    x_positions = [ml + (0 if n == 1 else (i / (n - 1)) * cw) for i in range(n)]

    def y_of(v: float | None) -> float | None:
        if v is None:
            return None
        return mt + ch - clamp01(float(v)) * ch

    def build_path(vals: list[float | None]) -> str:
        pts = []
        for x, v in zip(x_positions, vals):
            y = y_of(v)
            if y is None:
                continue
            pts.append((x, y))
        if not pts:
            return ""
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)

    c_vals = [r.get("c_value") for r in series]
    c_obs = [r.get("c_obs") for r in series]
    c_decay = [r.get("c_decay") for r in series]
    theta = float(best_stats.get("theta", 0.5))
    y_theta = y_of(theta) or (mt + ch / 2)

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt+ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt+ch}' x2='{ml+cw}' y2='{mt+ch}' stroke='#222'/>",
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        y = mt + ch - tick * ch
        lines.append(f"<line x1='{ml}' y1='{y:.1f}' x2='{ml+cw}' y2='{y:.1f}' stroke='#eee'/>")
        lines.append(f"<text x='{ml-8}' y='{y+4:.1f}' font-size='16' text-anchor='end' fill='#222'>{tick:.2f}</text>")

    # threshold line
    lines.append(f"<line x1='{ml}' y1='{y_theta:.1f}' x2='{ml+cw}' y2='{y_theta:.1f}' stroke='#555' stroke-dasharray='6 4'/>")
    lines.append(f"<text x='{ml+cw-4}' y='{y_theta-6:.1f}' font-size='15' text-anchor='end' fill='#555'>theta={theta:.2f}</text>")

    colors = {"c_value": "#117A65", "c_obs": "#2E86C1", "c_decay": "#AF601A"}
    paths = {
        "c_value": build_path(c_vals),
        "c_obs": build_path(c_obs),
        "c_decay": build_path(c_decay),
    }
    for key, d in paths.items():
        if d:
            dash = "" if key != "c_decay" else " stroke-dasharray='5 4'"
            lines.append(f"<path d='{d}' fill='none' stroke='{colors[key]}' stroke-width='2.5'{dash}/>")

    # points + labels
    for idx, (x, row) in enumerate(zip(x_positions, series), start=1):
        y = y_of(row.get("c_value"))
        if y is None:
            continue
        pred_allow = bool(row.get("pred_allow"))
        gt = row.get("ground_truth_allow")
        fill = "#1E8449" if pred_allow else "#C0392B"
        stroke = "#000" if isinstance(gt, bool) and gt != pred_allow else "none"
        lines.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4' fill='{fill}' stroke='{stroke}' stroke-width='1'/>")
        phase = row.get("phase_index")
        lbl = f"p{phase}" if phase is not None else f"{idx}"
        lines.append(f"<text x='{x:.1f}' y='{mt+ch+20}' font-size='16' text-anchor='middle' fill='#222'>{lbl}</text>")
        decision_lbl = "A" if pred_allow else "S"
        lines.append(f"<text x='{x:.1f}' y='{y-8:.1f}' font-size='14' text-anchor='middle' fill='#222'>{decision_lbl}</text>")

    title = f"AIg C(t) Trajectory ({best_stats.get('ablation')}, corr={corr[-10:]})"
    subtitle = (
        f"alpha={best_stats.get('alpha')}, lambda={best_stats.get('decay_lambda')}, "
        f"wT={best_stats.get('w_telecom')}, wD={best_stats.get('w_device')}, wI={best_stats.get('w_interaction')}, "
        f"rel={best_stats.get('use_reliability')}"
    )
    lines.append(f"<text x='{ml}' y='18' font-size='18' fill='#222'>{title}</text>")
    lines.append(f"<text x='{ml}' y='33' font-size='15' fill='#555'>{subtitle}</text>")

    legend = [("C(t)", colors["c_value"]), ("C_obs", colors["c_obs"]), ("C_decay", colors["c_decay"])]
    lx = ml
    ly = height - 25
    for label, color in legend:
        lines.append(f"<line x1='{lx}' y1='{ly}' x2='{lx+18}' y2='{ly}' stroke='{color}' stroke-width='2.5'/>")
        lines.append(f"<text x='{lx+24}' y='{ly+4}' font-size='16' fill='#222'>{label}</text>")
        lx += 110
    lines.append("<text x='650' y='459' font-size='15' fill='#555'>Point labels: A=allow, S=step_up; black outline = mismatch vs ground truth</text>")
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = [
        "theta",
        "alpha",
        "decay_lambda",
        "w_telecom",
        "w_device",
        "w_interaction",
        "use_reliability",
        "ablation",
        "labeled_total",
        "tp",
        "tn",
        "fp",
        "fn",
        "accuracy",
        "false_accept_rate",
        "false_reject_rate",
        "takeover_series",
        "takeover_detected_series",
        "avg_detection_phase_delay",
        "max_detection_phase_delay",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fields})


def write_predictions_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = [
        "theta",
        "alpha",
        "decay_lambda",
        "w_telecom",
        "w_device",
        "w_interaction",
        "use_reliability",
        "ablation",
        "decision_id",
        "scenario",
        "series_type",
        "phase_index",
        "correlation_id",
        "action_name",
        "decision_time",
        "ground_truth_allow",
        "pred_allow",
        "pred_decision",
        "c_obs",
        "c_decay",
        "c_value",
        "obs_count",
        "reason",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline AIg parameter sweep analysis")
    parser.add_argument("--base-url", default="https://localhost/api/v1")
    parser.add_argument("--api-key")
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--experiment-run-id")
    parser.add_argument("--correlation-id")
    parser.add_argument("--trace-json", help="Use local exported trace JSON instead of API")
    parser.add_argument("--thresholds", default="0.55,0.65,0.75,0.85")
    parser.add_argument("--alphas", default="0.5,0.7,0.85")
    parser.add_argument("--lambdas", default="0.0001,0.001,0.005")
    parser.add_argument("--w-telecoms", default="0.5,1.0,1.5")
    parser.add_argument("--w-devices", default="0.5,1.0,1.5")
    parser.add_argument("--w-interactions", default="0.5,1.0,1.5")
    parser.add_argument("--reliability-modes", default="off,on")
    parser.add_argument(
        "--ablations",
        default="all,telecom_only,device_only,interaction_only,no_telecom,no_device,no_interaction",
        help="Comma-separated ablation presets",
    )
    parser.add_argument("--output-dir", default="experiments/aig_sweep")
    args = parser.parse_args()

    if not args.trace_json and not args.api_key:
        raise SystemExit("--api-key is required unless --trace-json is provided")
    if not args.trace_json and not (args.experiment_run_id or args.correlation_id):
        raise SystemExit("Provide --experiment-run-id or --correlation-id (or use --trace-json)")

    if args.trace_json:
        data = json.loads(Path(args.trace_json).read_text(encoding="utf-8"))
        run_label = args.experiment_run_id or args.correlation_id or Path(args.trace_json).stem
    else:
        client = ApiClient(args.base_url, args.api_key, insecure=args.insecure)
        data = load_trace_from_api(client, args.experiment_run_id, args.correlation_id)
        run_label = args.experiment_run_id or args.correlation_id or "trace"

    observations, decisions = normalize_trace(data)
    decisions = [d for d in decisions if isinstance(d.ground_truth_allow, bool)]
    if not decisions:
        raise SystemExit("No labeled decisions found in trace metadata (ground_truth_allow missing)")

    thresholds = parse_list(args.thresholds)
    alphas = parse_list(args.alphas)
    lambdas = parse_list(args.lambdas)
    w_telecoms = parse_list(args.w_telecoms)
    w_devices = parse_list(args.w_devices)
    w_interactions = parse_list(args.w_interactions)
    reliability_modes = [m.strip().lower() for m in parse_str_list(args.reliability_modes)]
    ablations = parse_str_list(args.ablations)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_out = out_dir / f"{run_label}_predictions.csv"
    sum_out = out_dir / f"{run_label}_summary.csv"
    json_out = out_dir / f"{run_label}_best.json"
    svg_out = out_dir / f"{run_label}_threshold_curve.svg"
    traj_svg_out = out_dir / f"{run_label}_trajectory.svg"

    all_pred_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    best = None
    best_all = None

    for theta in thresholds:
        for alpha in alphas:
            for lam in lambdas:
                for wt in w_telecoms:
                    for wd in w_devices:
                        for wi in w_interactions:
                            family_weights = {
                                "telecom": float(wt),
                                "device": float(wd),
                                "interaction": float(wi),
                            }
                            for rel_mode in reliability_modes:
                                use_reliability = rel_mode in {"on", "true", "1", "yes"}
                                for ablation_name in ablations:
                                    include_families = ablation_to_include_families(ablation_name)
                                    scored = recompute_predictions(
                                        observations,
                                        decisions,
                                        theta=float(theta),
                                        alpha=float(alpha),
                                        decay_lambda=float(lam),
                                        family_weights=family_weights,
                                        use_reliability=use_reliability,
                                        include_families=include_families,
                                    )
                                    stats = summarize(scored)
                                    stats.update(
                                        {
                                            "theta": float(theta),
                                            "alpha": float(alpha),
                                            "decay_lambda": float(lam),
                                            "w_telecom": float(wt),
                                            "w_device": float(wd),
                                            "w_interaction": float(wi),
                                            "use_reliability": use_reliability,
                                            "ablation": ablation_name,
                                        }
                                    )
                                    summary_rows.append(stats)
                                    for r in scored:
                                        all_pred_rows.append(r)
                                    key = (
                                        1.0 if stats["false_accept_rate"] is None else stats["false_accept_rate"],
                                        1.0 if stats["false_reject_rate"] is None else stats["false_reject_rate"],
                                        -(0.0 if stats["accuracy"] is None else stats["accuracy"]),
                                    )
                                    if best is None or key < best["rank_key"]:
                                        best = {"rank_key": key, "stats": stats}
                                    if ablation_name == "all" and (best_all is None or key < best_all["rank_key"]):
                                        best_all = {"rank_key": key, "stats": stats}

    write_predictions_csv(all_pred_rows, pred_out)
    write_summary_csv(summary_rows, sum_out)
    write_threshold_curve_svg(summary_rows, svg_out)
    write_trajectory_svg(all_pred_rows, best_all["stats"] if best_all else None, traj_svg_out)
    if best:
        json_out.write_text(json.dumps(best["stats"], indent=2), encoding="utf-8")

    print(f"Labeled decisions: {len(decisions)}")
    combos = (
        len(thresholds)
        * len(alphas)
        * len(lambdas)
        * len(w_telecoms)
        * len(w_devices)
        * len(w_interactions)
        * len(reliability_modes)
        * len(ablations)
    )
    print(f"Parameter combinations: {combos}")
    print(f"Wrote {pred_out}")
    print(f"Wrote {sum_out}")
    print(f"Wrote {svg_out}")
    print(f"Wrote {traj_svg_out}")
    if best:
        print("Best (ranked by FAR, FRR, accuracy):")
        print(json.dumps(best["stats"], indent=2))
        print(f"Wrote {json_out}")
    if best_all:
        print("Best full-sensor config (ablation=all):")
        print(json.dumps(best_all["stats"], indent=2))


if __name__ == "__main__":
    main()
