#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ATTACK_DECISIONS = {"step_up", "deny", "block"}


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def parse_int(value: str | None, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def safe_rate(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return num / den


def evaluate(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts = {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "n": 0}
    by_scenario: dict[str, dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "n": 0}
    )

    progression_by_corr: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        expected_allow = parse_bool(row.get("expected_allow"))
        observed = str(row.get("observed_decision") or "").strip().lower()
        predicted_attack = observed in ATTACK_DECISIONS
        ground_attack = not expected_allow
        scenario = str(row.get("scenario") or "").strip() or "unknown"

        c = by_scenario[scenario]
        c["n"] += 1
        counts["n"] += 1
        if ground_attack and predicted_attack:
            c["tp"] += 1
            counts["tp"] += 1
        elif ground_attack and (not predicted_attack):
            c["fn"] += 1
            counts["fn"] += 1
        elif (not ground_attack) and predicted_attack:
            c["fp"] += 1
            counts["fp"] += 1
        else:
            c["tn"] += 1
            counts["tn"] += 1

        if scenario == "takeover_progression":
            corr = str(row.get("correlation_id") or "").strip()
            if corr:
                progression_by_corr[corr].append(
                    {
                        "action_index": parse_int(row.get("action_index"), 0),
                        "ground_attack": ground_attack,
                        "predicted_attack": predicted_attack,
                    }
                )

    scenario_metrics: dict[str, dict[str, Any]] = {}
    for scenario, c in sorted(by_scenario.items()):
        far = safe_rate(c["fp"], c["fp"] + c["tn"])
        frr = safe_rate(c["fn"], c["fn"] + c["tp"])
        scenario_metrics[scenario] = {
            **c,
            "false_accept_rate": far,
            "false_reject_rate": frr,
            "accuracy": safe_rate(c["tp"] + c["tn"], c["n"]),
        }

    far = safe_rate(counts["fp"], counts["fp"] + counts["tn"])
    frr = safe_rate(counts["fn"], counts["fn"] + counts["tp"])
    acc = safe_rate(counts["tp"] + counts["tn"], counts["n"])

    progression_delays: list[int] = []
    progression_misses = 0
    for _, seq in progression_by_corr.items():
        seq = sorted(seq, key=lambda x: x["action_index"])
        compromise_idx = None
        for item in seq:
            if item["ground_attack"]:
                compromise_idx = item["action_index"]
                break
        if compromise_idx is None:
            continue
        detect_idx = None
        for item in seq:
            if item["action_index"] >= compromise_idx and item["predicted_attack"]:
                detect_idx = item["action_index"]
                break
        if detect_idx is None:
            progression_misses += 1
        else:
            progression_delays.append(max(0, detect_idx - compromise_idx))

    progression_series = len(progression_by_corr)
    progression_detected = len(progression_delays)

    return {
        "canonical_definition": {
            "ground_truth_attack": "expected_allow == false",
            "predicted_attack": "observed_decision in {'step_up','deny','block'}",
            "FAR": "FP / (FP + TN) over benign-labeled actions",
            "FRR": "FN / (FN + TP) over attack-labeled actions",
        },
        "overall": {
            **counts,
            "false_accept_rate": far,
            "false_reject_rate": frr,
            "accuracy": acc,
        },
        "takeover_progression": {
            "series_count": progression_series,
            "detected_series": progression_detected,
            "missed_series": progression_misses,
            "detection_rate": safe_rate(progression_detected, progression_series),
            "mean_detection_delay_phases": (
                sum(progression_delays) / len(progression_delays) if progression_delays else None
            ),
            "max_detection_delay_phases": (max(progression_delays) if progression_delays else None),
            "delays": progression_delays,
        },
        "by_scenario": scenario_metrics,
    }


def write_summary_csv(result: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    overall = result["overall"]
    progression = result["takeover_progression"]
    rows = [
        ("Total actions", overall["n"]),
        ("TP", overall["tp"]),
        ("TN", overall["tn"]),
        ("FP", overall["fp"]),
        ("FN", overall["fn"]),
        ("FAR", round(overall["false_accept_rate"], 6)),
        ("FRR", round(overall["false_reject_rate"], 6)),
        ("Accuracy", round(overall["accuracy"], 6)),
        ("Takeover progression series", progression["series_count"]),
        ("Takeover progression detected", progression["detected_series"]),
        ("Takeover progression misses", progression["missed_series"]),
        ("Takeover progression detection rate", round(progression["detection_rate"], 6)),
        (
            "Mean detection delay (phases)",
            "" if progression["mean_detection_delay_phases"] is None else round(progression["mean_detection_delay_phases"], 6),
        ),
        (
            "Max detection delay (phases)",
            "" if progression["max_detection_delay_phases"] is None else progression["max_detection_delay_phases"],
        ),
    ]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(["Metric", "Value"])
        w.writerows(rows)


def write_scenario_csv(result: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "scenario",
            "n",
            "tp",
            "tn",
            "fp",
            "fn",
            "false_accept_rate",
            "false_reject_rate",
            "accuracy",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for scenario, m in sorted(result["by_scenario"].items()):
            w.writerow(
                {
                    "scenario": scenario,
                    "n": m["n"],
                    "tp": m["tp"],
                    "tn": m["tn"],
                    "fp": m["fp"],
                    "fn": m["fn"],
                    "false_accept_rate": round(m["false_accept_rate"], 6),
                    "false_reject_rate": round(m["false_reject_rate"], 6),
                    "accuracy": round(m["accuracy"], 6),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Canonical evaluation of AIg campaign outputs from aggregate_decisions.csv"
    )
    parser.add_argument("--aggregate-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    aggregate_path = Path(args.aggregate_csv)
    if not aggregate_path.exists():
        raise SystemExit(f"aggregate csv not found: {aggregate_path}")

    with aggregate_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit("aggregate csv is empty")

    result = evaluate(rows)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "canonical_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_summary_csv(result, out_dir / "canonical_summary.csv")
    write_scenario_csv(result, out_dir / "canonical_by_scenario.csv")

    print(json.dumps(result["overall"], indent=2))
    print(json.dumps(result["takeover_progression"], indent=2))
    print(f"Wrote {out_dir / 'canonical_metrics.json'}")
    print(f"Wrote {out_dir / 'canonical_summary.csv'}")
    print(f"Wrote {out_dir / 'canonical_by_scenario.csv'}")


if __name__ == "__main__":
    main()
