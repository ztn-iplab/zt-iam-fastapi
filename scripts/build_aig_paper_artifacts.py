#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from shutil import copyfile
from typing import Any


def _f(v: Any, default: float = 0.0) -> float:
    if v in (None, ""):
        return default
    return float(v)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _best_full_sensor(summary_rows: list[dict[str, str]]) -> dict[str, str] | None:
    rows = [r for r in summary_rows if (r.get("ablation") or "") == "all"]
    if not rows:
        return None
    def key(r):
        far = _f(r.get("false_accept_rate"), 1.0)
        frr = _f(r.get("false_reject_rate"), 1.0)
        acc = _f(r.get("accuracy"), 0.0)
        return (far, frr, -acc)
    return min(rows, key=key)


def _bundle_match(row: dict[str, str], ref: dict[str, str]) -> bool:
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
    return all((row.get(k) or "") == (ref.get(k) or "") for k in keys)


def _write_svg(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_fig2_confidence_evolution(pred_rows: list[dict[str, str]], best_all: dict[str, str], out_path: Path) -> None:
    candidates = [r for r in pred_rows if _bundle_match(r, best_all)]
    # Prefer takeover progression, else any multi-point series.
    by_corr: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in candidates:
        by_corr[r.get("correlation_id", "")].append(r)

    selected = None
    for corr, rows in by_corr.items():
        if any((r.get("scenario") or "") == "takeover_progression" for r in rows):
            selected = (corr, rows)
            break
    if not selected:
        selected = max(by_corr.items(), key=lambda kv: len(kv[1]))
    corr, rows = selected
    rows.sort(key=lambda r: (_f(r.get("phase_index"), 999), int(r.get("decision_id") or 0)))

    width, height = 980, 520
    ml, mr, mt, mb = 70, 20, 40, 120
    cw, ch = width - ml - mr, height - mt - mb
    n = len(rows)
    xs = [ml + (0 if n == 1 else (i / (n - 1)) * cw) for i in range(n)]
    theta = _f(best_all.get("theta"), 0.5)

    def y(v: float) -> float:
        return mt + ch - max(0.0, min(1.0, v)) * ch

    def path_for(key: str) -> str:
        pts = []
        for x, r in zip(xs, rows):
            rv = r.get(key)
            if rv in (None, ""):
                continue
            pts.append((x, y(float(rv))))
        if not pts:
            return ""
        return "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)

    c_path = path_for("c_value")
    obs_path = path_for("c_obs")
    dec_path = path_for("c_decay")

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt+ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt+ch}' x2='{ml+cw}' y2='{mt+ch}' stroke='#222'/>",
        f"<text x='{ml}' y='20' font-size='22' fill='#222'>Evolution of AIg confidence over time</text>",
        "<text x='70' y='37' font-size='16' fill='#555'>Reinforcing observations increase confidence; lack of evidence causes decay. Actions requiring AIg require C(t) ≥ θ.</text>",
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = y(tick)
        lines.append(f"<line x1='{ml}' y1='{yy:.1f}' x2='{ml+cw}' y2='{yy:.1f}' stroke='#eee'/>")
        lines.append(f"<text x='{ml-8}' y='{yy+4:.1f}' font-size='16' text-anchor='end' fill='#222'>{tick:.2f}</text>")
    ytheta = y(theta)
    lines.append(f"<line x1='{ml}' y1='{ytheta:.1f}' x2='{ml+cw}' y2='{ytheta:.1f}' stroke='#7D3C98' stroke-width='2' stroke-dasharray='6 4'/>")
    lines.append(f"<text x='{ml+cw-4}' y='{ytheta-8:.1f}' font-size='16' text-anchor='end' fill='#7D3C98'>θ = {theta:.2f}</text>")

    if dec_path:
        lines.append(f"<path d='{dec_path}' fill='none' stroke='#AF601A' stroke-width='2' stroke-dasharray='5 4'/>")
    if obs_path:
        lines.append(f"<path d='{obs_path}' fill='none' stroke='#2E86C1' stroke-width='2'/>")
    if c_path:
        lines.append(f"<path d='{c_path}' fill='none' stroke='#117A65' stroke-width='3'/>")

    # Observation markers and action outcomes
    lane_y = mt + ch + 38
    lines.append(f"<text x='{ml-8}' y='{lane_y+4}' font-size='15' text-anchor='end' fill='#555'>Actions</text>")
    for idx, (x, r) in enumerate(zip(xs, rows), start=1):
        decision = (r.get("pred_decision") or "").lower()
        pred_allow = (r.get("pred_allow") or "").lower() == "true"
        gt_allow = (r.get("ground_truth_allow") or "").lower() == "true"
        cval = r.get("c_value")
        yy = y(float(cval)) if cval not in (None, "") else y(0)
        fill = "#1E8449" if pred_allow else "#C0392B"
        stroke = "#111" if pred_allow != gt_allow else "none"
        lines.append(f"<circle cx='{x:.1f}' cy='{yy:.1f}' r='4.5' fill='{fill}' stroke='{stroke}' stroke-width='1'/>")
        lines.append(f"<circle cx='{x:.1f}' cy='{lane_y:.1f}' r='5' fill='{fill}'/>")
        lines.append(f"<text x='{x:.1f}' y='{lane_y+18:.1f}' font-size='15' text-anchor='middle' fill='#222'>{idx}</text>")
        obs_count = int(float(r.get('obs_count') or 0))
        lines.append(f"<text x='{x:.1f}' y='{yy-9:.1f}' font-size='14' text-anchor='middle' fill='#333'>n={obs_count}</text>")
        if decision == "step_up":
            lines.append(f"<text x='{x:.1f}' y='{lane_y-10:.1f}' font-size='14' text-anchor='middle' fill='#C0392B'>step-up</text>")

    # Small annotations
    lines.append(f"<text x='{ml}' y='{height-48}' font-size='16' fill='#222'>Example series: {rows[0].get('scenario','')} ({corr[-10:]})</text>")
    lines.append(f"<text x='{ml}' y='{height-30}' font-size='15' fill='#555'>Green points/markers = allow, red = step-up, black outline = mismatch vs ground truth label.</text>")
    lx = ml
    ly = height - 12
    for label, color, dash in [("C(t)", "#117A65", ""), ("C_obs", "#2E86C1", ""), ("C_decay", "#AF601A", " stroke-dasharray='5 4'")]:
        lines.append(f"<line x1='{lx}' y1='{ly-4}' x2='{lx+18}' y2='{ly-4}' stroke='{color}' stroke-width='2'{dash}/>")
        lines.append(f"<text x='{lx+24}' y='{ly}' font-size='15' fill='#222'>{label}</text>")
        lx += 110
    lines.append("</svg>")
    _write_svg(out_path, lines)


def build_takeover_timeline(trace: dict[str, Any], out_path: Path) -> None:
    telecom = trace.get("telecom_events", []) or []
    obs = trace.get("observations", []) or []
    dec = trace.get("decisions", []) or []
    # choose takeover progression correlation if present
    candidate_corrs = []
    for d in dec:
        md = d.get("metadata_json") or {}
        if isinstance(md, dict) and (md.get("series_type") == "takeover_progression" or d.get("action_name") == "view_patient_record"):
            candidate_corrs.append(d.get("correlation_id"))
    corr = next((c for c in candidate_corrs if c), None)
    if corr is None and dec:
        corr = dec[0].get("correlation_id")
    if corr is None:
        raise RuntimeError("No decisions found in trace for takeover timeline")

    telecom = [t for t in telecom if t.get("correlation_id") == corr]
    obs = [o for o in obs if o.get("correlation_id") == corr]
    dec = [d for d in dec if d.get("correlation_id") == corr]
    if not dec:
        raise RuntimeError("No decisions for selected correlation")

    def t_of(item, key):
        v = item.get(key)
        if not v:
            return None
        return v

    # use lexical time order (ISO timestamps)
    all_times = sorted(
        [x for x in [*(t_of(i, "event_time") for i in telecom), *(t_of(i, "observed_at") for i in obs), *(t_of(i, "decision_time") for i in dec)] if x]
    )
    tmin = all_times[0]
    tmax = all_times[-1]
    # map to evenly spaced positions (sufficient for figure)
    unique_times = sorted(set(all_times))
    time_index = {t: i for i, t in enumerate(unique_times)}

    width, height = 1100, 500
    ml, mr, mt, mb = 120, 20, 40, 70
    cw, ch = width - ml - mr, height - mt - mb
    lanes = [("Telecom", 0), ("Observations", 1), ("Protected Actions", 2), ("Outcome", 3)]
    lane_gap = ch / (len(lanes) - 1 if len(lanes) > 1 else 1)

    def x_of(t: str) -> float:
        if len(unique_times) == 1:
            return ml + cw / 2
        return ml + (time_index[t] / (len(unique_times) - 1)) * cw

    def y_lane(i: int) -> float:
        return mt + i * lane_gap

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        "<text x='20' y='20' font-size='22' fill='#222'>Takeover timeline (AIg evidence and enforcement)</text>",
        "<text x='20' y='37' font-size='16' fill='#555'>Telecom takeover indicators and observation degradation precede step-up on protected actions.</text>",
    ]
    for name, idx in lanes:
        y = y_lane(idx)
        lines.append(f"<line x1='{ml}' y1='{y:.1f}' x2='{ml+cw}' y2='{y:.1f}' stroke='#ddd'/>")
        lines.append(f"<text x='{ml-10}' y='{y+4:.1f}' font-size='16' text-anchor='end' fill='#222'>{name}</text>")
    for t in unique_times:
        x = x_of(t)
        lines.append(f"<line x1='{x:.1f}' y1='{mt-5}' x2='{x:.1f}' y2='{mt+ch+5}' stroke='#f2f2f2'/>")

    # telecom events
    for e in telecom:
        t = e.get("event_time")
        if not t:
            continue
        x = x_of(t)
        y = y_lane(0)
        et = e.get("event_type", "event")
        color = "#C0392B" if "swap" in et else "#AF601A"
        lines.append(f"<rect x='{x-8:.1f}' y='{y-8:.1f}' width='16' height='16' fill='{color}' rx='3'/>")
        lines.append(f"<text x='{x:.1f}' y='{y-12:.1f}' font-size='14' text-anchor='middle' fill='#333'>{et}</text>")

    # observations (telecom/device/interaction)
    fam_color = {"telecom": "#1F618D", "device": "#117864", "interaction": "#7D6608"}
    for o in obs:
        t = o.get("observed_at")
        if not t:
            continue
        x = x_of(t)
        y = y_lane(1)
        fam = (o.get("source_family") or "other").lower()
        val = _f(o.get("evidence_value"))
        r = 3 + 4 * max(0, min(1, val))
        color = fam_color.get(fam, "#566573")
        lines.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r:.1f}' fill='{color}' opacity='0.85'/>")

    # actions/decisions
    action_points = []
    for d in dec:
        t = d.get("decision_time")
        if not t:
            continue
        x = x_of(t)
        y = y_lane(2)
        action_points.append((x, d))
        lines.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5' fill='#34495E'/>")
        lines.append(f"<text x='{x:.1f}' y='{y-10:.1f}' font-size='14' text-anchor='middle' fill='#333'>{d.get('action_name','action')}</text>")
    for x, d in action_points:
        y = y_lane(3)
        decision = (d.get("decision") or "").lower()
        color = {"allow": "#1E8449", "step_up": "#D35400", "deny": "#C0392B"}.get(decision, "#566573")
        lines.append(f"<rect x='{x-10:.1f}' y='{y-8:.1f}' width='20' height='16' fill='{color}' rx='3'/>")
        cval = d.get("c_value")
        label = decision or "?"
        if cval not in (None, ""):
            label += f" (C={float(cval):.2f})"
        lines.append(f"<text x='{x:.1f}' y='{y+22:.1f}' font-size='14' text-anchor='middle' fill='#333'>{label}</text>")
        # connector
        lines.append(f"<line x1='{x:.1f}' y1='{y_lane(2)+6:.1f}' x2='{x:.1f}' y2='{y-8:.1f}' stroke='#aaa'/>")

    # x labels
    for t in unique_times:
        x = x_of(t)
        short = t.split("T", 1)[-1][:8] if "T" in t else t
        lines.append(f"<text x='{x:.1f}' y='{height-20}' font-size='14' text-anchor='middle' fill='#555'>{short}</text>")

    # legend
    lx, ly = ml, height - 46
    legend = [
        ("Telecom event", "#C0392B"),
        ("Telecom obs", fam_color["telecom"]),
        ("Device obs", fam_color["device"]),
        ("Interaction obs", fam_color["interaction"]),
        ("step_up", "#D35400"),
        ("allow", "#1E8449"),
    ]
    for name, color in legend:
        lines.append(f"<rect x='{lx}' y='{ly-10}' width='12' height='12' fill='{color}'/>")
        lines.append(f"<text x='{lx+18}' y='{ly}' font-size='15' fill='#222'>{name}</text>")
        lx += 120
    lines.append("</svg>")
    _write_svg(out_path, lines)


def build_ablation_summary(summary_rows: list[dict[str, str]], out_path: Path) -> None:
    # Best accuracy row per ablation
    by_ablation: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in summary_rows:
        ab = r.get("ablation") or "unknown"
        by_ablation[ab].append(r)
    selected = []
    for ab, rows in by_ablation.items():
        row = min(
            rows,
            key=lambda r: (
                _f(r.get("false_accept_rate"), 1.0),
                _f(r.get("false_reject_rate"), 1.0),
                -_f(r.get("accuracy"), 0.0),
            ),
        )
        selected.append((ab, row))
    selected.sort(key=lambda t: (_f(t[1].get("false_accept_rate"), 1.0), _f(t[1].get("false_reject_rate"), 1.0)))

    width, height = 1100, 520
    ml, mr, mt, mb = 70, 20, 35, 120
    cw, ch = width - ml - mr, height - mt - mb
    n = len(selected)
    if n == 0:
        return
    group_w = cw / n
    bar_w = group_w * 0.22

    def y(v: float) -> float:
        return mt + ch - max(0, min(1, v)) * ch

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        "<text x='20' y='20' font-size='22' fill='#222'>AIg source ablation performance (best per ablation)</text>",
        "<text x='20' y='37' font-size='16' fill='#555'>Bars show FAR, FRR, and Accuracy for the best-tuned configuration within each ablation.</text>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt+ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt+ch}' x2='{ml+cw}' y2='{mt+ch}' stroke='#222'/>",
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = y(tick)
        lines.append(f"<line x1='{ml}' y1='{yy:.1f}' x2='{ml+cw}' y2='{yy:.1f}' stroke='#eee'/>")
        lines.append(f"<text x='{ml-8}' y='{yy+4:.1f}' font-size='16' text-anchor='end' fill='#222'>{tick:.2f}</text>")
    colors = [("#C0392B", "false_accept_rate"), ("#2E86C1", "false_reject_rate"), ("#117A65", "accuracy")]
    for i, (ab, r) in enumerate(selected):
        gx = ml + i * group_w
        for j, (color, key) in enumerate(colors):
            val = _f(r.get(key), 0.0)
            x = gx + group_w * 0.1 + j * (bar_w + group_w * 0.04)
            yy = y(val)
            h = mt + ch - yy
            lines.append(f"<rect x='{x:.1f}' y='{yy:.1f}' width='{bar_w:.1f}' height='{h:.1f}' fill='{color}'/>")
        label = ab.replace("_", " ")
        lines.append(f"<text x='{gx + group_w/2:.1f}' y='{mt+ch+18:.1f}' font-size='14' text-anchor='middle' fill='#222'>{label}</text>")
    lx, ly = ml, height - 24
    for color, key in colors:
        lines.append(f"<rect x='{lx}' y='{ly-10}' width='12' height='12' fill='{color}'/>")
        lines.append(f"<text x='{lx+18}' y='{ly}' font-size='15' fill='#222'>{key}</text>")
        lx += 160
    lines.append("</svg>")
    _write_svg(out_path, lines)


def build_weight_heatmap(summary_rows: list[dict[str, str]], out_path: Path) -> None:
    rows = [r for r in summary_rows if (r.get("ablation") or "") == "all"]
    if not rows:
        return
    # use best alpha/lambda/theta/w_device/use_reliability and map accuracy over wT x wI
    best = _best_full_sensor(rows)
    if not best:
        return
    subset = [
        r for r in rows
        if (r.get("theta"), r.get("alpha"), r.get("decay_lambda"), r.get("w_device"), r.get("use_reliability"))
        == (best.get("theta"), best.get("alpha"), best.get("decay_lambda"), best.get("w_device"), best.get("use_reliability"))
    ]
    wts = sorted({r.get("w_telecom") for r in subset}, key=lambda x: _f(x))
    wis = sorted({r.get("w_interaction") for r in subset}, key=lambda x: _f(x))
    cell = {(r.get("w_telecom"), r.get("w_interaction")): _f(r.get("accuracy"), 0.0) for r in subset}
    if not wts or not wis:
        return
    width, height = 700, 520
    ml, mr, mt, mb = 120, 20, 60, 80
    cw, ch = width - ml - mr, height - mt - mb
    cell_w = cw / len(wis)
    cell_h = ch / len(wts)
    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        "<text x='20' y='22' font-size='22' fill='#222'>AIg weight tuning heatmap (full-sensor)</text>",
        f"<text x='20' y='40' font-size='15' fill='#555'>Accuracy at theta={best['theta']}, alpha={best['alpha']}, lambda={best['decay_lambda']}, w_device={best['w_device']}, reliability={best['use_reliability']}</text>",
    ]
    for i, wt in enumerate(wts):
        yy = mt + i * cell_h
        lines.append(f"<text x='{ml-8}' y='{yy + cell_h/2 + 4:.1f}' font-size='15' text-anchor='end' fill='#222'>{wt}</text>")
    for j, wi in enumerate(wis):
        xx = ml + j * cell_w
        lines.append(f"<text x='{xx + cell_w/2:.1f}' y='{mt-8}' font-size='15' text-anchor='middle' fill='#222'>{wi}</text>")
    lines.append(f"<text x='{ml-60}' y='{mt + ch/2:.1f}' font-size='16' text-anchor='middle' fill='#222' transform='rotate(-90 {ml-60},{mt + ch/2:.1f})'>w_telecom</text>")
    lines.append(f"<text x='{ml + cw/2:.1f}' y='{height-24}' font-size='16' text-anchor='middle' fill='#222'>w_interaction</text>")
    for i, wt in enumerate(wts):
        for j, wi in enumerate(wis):
            acc = cell.get((wt, wi), 0.0)
            # green scale
            shade = int(255 - (acc * 140))
            fill = f"rgb({shade},{255 - int(acc*60)},{shade})"
            x = ml + j * cell_w
            y = mt + i * cell_h
            lines.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{cell_w:.1f}' height='{cell_h:.1f}' fill='{fill}' stroke='#fff'/>")
            lines.append(f"<text x='{x+cell_w/2:.1f}' y='{y+cell_h/2+4:.1f}' font-size='15' text-anchor='middle' fill='#111'>{acc:.2f}</text>")
    lines.append("</svg>")
    _write_svg(out_path, lines)


def build_usability_figure(usability: dict[str, Any], out_path: Path) -> None:
    metrics = {k: v for k, v in usability.items() if not str(k).startswith("_")}
    ordered = [
        "Participants",
        "Sessions observed",
        "Total protected actions",
        "Actions requiring step-up verification",
        "Successful recoveries after step-up",
        "Incomplete tasks",
        "Session terminations due to AIg",
    ]
    width, height = 860, 420
    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        "<text x='20' y='26' font-size='22' fill='#222'>AIg usability study summary</text>",
        "<text x='20' y='44' font-size='16' fill='#555'>Aggregated metrics computed from AIg decision traces (session-tagged HMS runs).</text>",
    ]
    x_metric, x_val = 30, 700
    y0, row_h = 80, 42
    lines.append(f"<rect x='20' y='{y0-24}' width='{width-40}' height='{len(ordered)*row_h + 34}' fill='#fafafa' stroke='#ddd' rx='8'/>")
    lines.append(f"<text x='{x_metric}' y='{y0}' font-size='17' font-weight='bold' fill='#222'>Metric</text>")
    lines.append(f"<text x='{x_val}' y='{y0}' font-size='17' font-weight='bold' fill='#222'>Observed Value</text>")
    for i, k in enumerate(ordered):
        y = y0 + 28 + i * row_h
        if i > 0:
            lines.append(f"<line x1='28' y1='{y-18}' x2='{width-28}' y2='{y-18}' stroke='#e6e6e6'/>")
        val = metrics.get(k, 0)
        lines.append(f"<text x='{x_metric}' y='{y}' font-size='17' fill='#222'>{k}</text>")
        lines.append(f"<text x='{x_val}' y='{y}' font-size='17' fill='#111'>{val}</text>")
    lines.append("</svg>")
    _write_svg(out_path, lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build manuscript-ready AIg SVG figures and tables bundle")
    parser.add_argument("--run-id", required=True, help="Experiment run id prefix used in aig_sweep/aig_traces filenames")
    parser.add_argument("--base-dir", default="experiments")
    parser.add_argument("--out-dir", default="experiments/paper_artifacts")
    parser.add_argument("--usability-json", help="Path to usability JSON (from analyze_aig_usability.py)")
    args = parser.parse_args()

    base = Path(args.base_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    summary_csv = base / "aig_sweep" / f"{args.run_id}_summary.csv"
    pred_csv = base / "aig_sweep" / f"{args.run_id}_predictions.csv"
    trace_json = base / "aig_traces" / f"{args.run_id}.json"
    threshold_svg = base / "aig_sweep" / f"{args.run_id}_threshold_curve.svg"
    trajectory_svg = base / "aig_sweep" / f"{args.run_id}_trajectory.svg"
    best_json = base / "aig_sweep" / f"{args.run_id}_best.json"

    summary_rows = _load_csv(summary_csv)
    pred_rows = _load_csv(pred_csv)
    trace = _load_json(trace_json)
    best_all = _best_full_sensor(summary_rows)
    if not best_all:
        raise SystemExit("Could not determine best full-sensor row from summary CSV")

    # Figure 2
    build_fig2_confidence_evolution(pred_rows, best_all, out / "fig2_aig_confidence_evolution.svg")
    # Figure 4 placeholder replacement (takeover timeline)
    build_takeover_timeline(trace, out / "fig4_takeover_timeline.svg")
    # Additional figures
    build_ablation_summary(summary_rows, out / "fig_ablation_summary.svg")
    build_weight_heatmap(summary_rows, out / "fig_weight_heatmap.svg")

    if threshold_svg.exists():
        copyfile(threshold_svg, out / "fig_threshold_tradeoff.svg")
    if trajectory_svg.exists():
        copyfile(trajectory_svg, out / "fig_ct_trajectory.svg")
    if best_json.exists():
        copyfile(best_json, out / "best_overall.json")

    # Usability table / figure if available
    if args.usability_json:
        usability = _load_json(Path(args.usability_json))
        build_usability_figure(usability, out / "fig_usability_summary.svg")
        # copy raw table files if sibling files exist
        ujson = Path(args.usability_json)
        for sibling_name in ("aig_usability_table.tex", "aig_usability_table.csv"):
            sib = ujson.parent / sibling_name
            if sib.exists():
                copyfile(sib, out / sibling_name)

    # Produce sanitized trace bundle for safe sharing (best effort).
    redacted_out = out / f"{args.run_id}.sanitized.json"
    redact_script = Path(__file__).with_name("redact_aig_trace.py")
    if redact_script.exists():
        try:
            subprocess.run(
                [
                    "python3",
                    str(redact_script),
                    "--trace-json",
                    str(trace_json),
                    "--output",
                    str(redacted_out),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            pass

    manifest = {
        "run_id": args.run_id,
        "files": sorted([p.name for p in out.glob("*")]),
        "best_full_sensor": {
            "theta": best_all.get("theta"),
            "alpha": best_all.get("alpha"),
            "decay_lambda": best_all.get("decay_lambda"),
            "w_telecom": best_all.get("w_telecom"),
            "w_device": best_all.get("w_device"),
            "w_interaction": best_all.get("w_interaction"),
            "use_reliability": best_all.get("use_reliability"),
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(f"Wrote bundle to {out}")


if __name__ == "__main__":
    main()
