#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def load_trace_files(files: list[Path]) -> list[dict[str, Any]]:
    traces = []
    for p in files:
        traces.append(json.loads(p.read_text(encoding="utf-8")))
    return traces


def discover_trace_files(trace_dir: Path, pattern: str) -> list[Path]:
    return sorted(trace_dir.glob(pattern))


@dataclass
class Decision:
    decision_id: int
    decision_time: datetime
    decision: str
    correlation_id: str | None
    action_name: str | None
    metadata: dict[str, Any]


def _truthy(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "y"}
    return False


def flatten_decisions(traces: list[dict[str, Any]]) -> list[Decision]:
    out: list[Decision] = []
    for trace in traces:
        for row in trace.get("decisions", []):
            md = row.get("metadata_json") or {}
            if not isinstance(md, dict):
                md = {}
            if md.get("seeded") is True:
                continue
            t = parse_dt(row.get("decision_time"))
            if t is None:
                continue
            out.append(
                Decision(
                    decision_id=int(row["id"]),
                    decision_time=t,
                    decision=str(row.get("decision") or "").strip().lower(),
                    correlation_id=row.get("correlation_id"),
                    action_name=row.get("action_name"),
                    metadata=md,
                )
            )
    out.sort(key=lambda d: (d.decision_time, d.decision_id))
    return out


def participant_key(dec: Decision) -> str | None:
    md = dec.metadata
    for key in ("participant_id", "actor_label"):
        v = md.get(key)
        if v not in (None, ""):
            return str(v)
    return None


def session_key(dec: Decision) -> str | None:
    return dec.correlation_id or None


def find_recoveries(decisions: list[Decision], timeout_seconds: int) -> tuple[int, set[int]]:
    by_session: dict[str, list[Decision]] = defaultdict(list)
    for d in decisions:
        if d.correlation_id:
            by_session[d.correlation_id].append(d)
    recovered_stepup_ids: set[int] = set()

    for _, sess in by_session.items():
        sess.sort(key=lambda d: (d.decision_time, d.decision_id))
        for i, d in enumerate(sess):
            if d.decision != "step_up":
                continue
            deadline = d.decision_time.timestamp() + timeout_seconds
            for j in range(i + 1, len(sess)):
                nxt = sess[j]
                if nxt.decision_time.timestamp() > deadline:
                    break
                # same action or same route/scenario is best-effort acceptable
                same_action = (nxt.action_name == d.action_name) or (
                    nxt.metadata.get("hms_route") == d.metadata.get("hms_route")
                )
                if same_action and nxt.decision == "allow":
                    recovered_stepup_ids.add(d.decision_id)
                    break
    return len(recovered_stepup_ids), recovered_stepup_ids


def compute_metrics(traces: list[dict[str, Any]], recovery_timeout_seconds: int) -> dict[str, Any]:
    decisions = flatten_decisions(traces)
    participants = {k for d in decisions if (k := participant_key(d))}
    sessions = {k for d in decisions if (k := session_key(d))}

    protected_actions = len(decisions)
    step_ups = [d for d in decisions if d.decision == "step_up"]
    denies = [d for d in decisions if d.decision == "deny"]
    recoveries_count, recovered_stepup_ids = find_recoveries(decisions, recovery_timeout_seconds)
    incomplete_tasks = max(0, len(step_ups) - recoveries_count - len([d for d in step_ups if d.decision_id in recovered_stepup_ids]))
    # "incomplete tasks" is best measured via task markers; until then, use unrecovered step-ups
    incomplete_tasks = max(0, len(step_ups) - recoveries_count)

    terminations_due_to_aig = len(denies)

    return {
        "Participants": len(participants),
        "Sessions observed": len(sessions),
        "Total protected actions": protected_actions,
        "Actions requiring step-up verification": len(step_ups),
        "Successful recoveries after step-up": recoveries_count,
        "Incomplete tasks": incomplete_tasks,
        "Session terminations due to AIg": terminations_due_to_aig,
        "_notes": {
            "recovery_timeout_seconds": recovery_timeout_seconds,
            "participant_key_priority": ["metadata_json.participant_id", "metadata_json.actor_label"],
            "incomplete_tasks_definition": "step_up decisions without a subsequent allow in the same session/action within timeout",
            "termination_definition": "deny decisions",
        },
    }


def write_csv_table(metrics: dict[str, Any], out_path: Path) -> None:
    rows = [(k, v) for k, v in metrics.items() if not k.startswith("_")]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Metric", "Observed Value"])
        for k, v in rows:
            w.writerow([k, v])


def write_latex_table(metrics: dict[str, Any], out_path: Path) -> None:
    ordered = [
        "Participants",
        "Sessions observed",
        "Total protected actions",
        "Actions requiring step-up verification",
        "Successful recoveries after step-up",
        "Incomplete tasks",
        "Session terminations due to AIg",
    ]
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Summary of the user interaction study under AIg enforcement.}",
        r"\label{tab:usability}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{6pt}",
        r"\renewcommand{\arraystretch}{1.2}",
        "",
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"\textbf{Metric} & \textbf{Observed Value} \\",
        r"\midrule",
    ]
    for key in ordered:
        lines.append(rf"{key} & {metrics.get(key, 0)} \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(metrics: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def parse_expected(items: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Expected metric must be NAME=VALUE, got: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = int(v.strip())
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute usability-study table metrics from AIg trace exports")
    parser.add_argument("--trace-json", action="append", default=[], help="Trace JSON file (repeatable)")
    parser.add_argument("--trace-dir", help="Directory containing trace JSON files")
    parser.add_argument("--glob", default="*.json", help="Glob pattern when using --trace-dir")
    parser.add_argument("--recovery-timeout-seconds", type=int, default=600)
    parser.add_argument("--output-dir", default="experiments/usability")
    parser.add_argument("--expected", action="append", default=[], help="Validate metric, e.g. 'Participants=45'")
    args = parser.parse_args()

    files: list[Path] = []
    files.extend(Path(p) for p in args.trace_json)
    if args.trace_dir:
        files.extend(discover_trace_files(Path(args.trace_dir), args.glob))
    files = sorted({p.resolve() for p in files if p.exists()})
    if not files:
        raise SystemExit("No trace files provided/found")

    traces = load_trace_files(files)
    metrics = compute_metrics(traces, recovery_timeout_seconds=args.recovery_timeout_seconds)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_table(metrics, out_dir / "aig_usability_table.csv")
    write_latex_table(metrics, out_dir / "aig_usability_table.tex")
    write_json(metrics, out_dir / "aig_usability_table.json")

    print(json.dumps({k: v for k, v in metrics.items() if not k.startswith("_")}, indent=2))
    print(f"Wrote {out_dir / 'aig_usability_table.csv'}")
    print(f"Wrote {out_dir / 'aig_usability_table.tex'}")
    print(f"Wrote {out_dir / 'aig_usability_table.json'}")

    if args.expected:
        expected = parse_expected(args.expected)
        mismatches = []
        for k, exp in expected.items():
            got = metrics.get(k)
            if got != exp:
                mismatches.append((k, exp, got))
        if mismatches:
            print("Validation mismatches:")
            for k, exp, got in mismatches:
                print(f"- {k}: expected {exp}, got {got}")
            raise SystemExit(2)
        print("Validation passed against expected metrics.")


if __name__ == "__main__":
    main()

