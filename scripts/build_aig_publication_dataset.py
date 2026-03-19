#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge per-campaign AIg calibration CSVs into one publication-ready ML dataset"
    )
    parser.add_argument(
        "--campaign-root",
        default="experiments/aig_corpus_20260309",
        help="Root directory containing campaign folders",
    )
    parser.add_argument(
        "--campaign",
        action="append",
        default=[],
        help="Campaign specification in the form campaign_id:split (repeatable)",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Output directory for the frozen publication dataset bundle",
    )
    parser.add_argument(
        "--dataset-name",
        default="aig_publication_dataset",
        help="Base name for the merged dataset files",
    )
    return parser.parse_args()


def default_campaigns() -> list[tuple[str, str]]:
    return [
        ("aigcorpus-20260309-trainA", "train"),
        ("aigcorpus-20260309-trainB", "train"),
        ("aigcorpus-20260309-devA", "dev"),
        ("aigcorpus-20260309-testA", "test"),
    ]


def parse_campaign_specs(values: list[str]) -> list[tuple[str, str]]:
    if not values:
        return default_campaigns()
    items: list[tuple[str, str]] = []
    for value in values:
        if ":" not in value:
            raise SystemExit(f"Invalid --campaign value '{value}'. Expected campaign_id:split")
        campaign_id, split = value.split(":", 1)
        campaign_id = campaign_id.strip()
        split = split.strip().lower()
        if split not in {"train", "dev", "test"}:
            raise SystemExit(f"Invalid split '{split}' for campaign '{campaign_id}'")
        items.append((campaign_id, split))
    return items


def load_rows(csv_path: Path, *, campaign_id: str, split: str) -> list[dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            enriched = {
                "campaign_id": campaign_id,
                "split": split,
                **row,
            }
            rows.append(enriched)
        return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit("No rows found to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(
    path: Path,
    *,
    dataset_csv: str,
    manifest_json: str,
    split_counts: Counter[str],
    scenario_counts: Counter[str],
) -> None:
    lines = [
        "# AIg Publication Dataset",
        "",
        "This bundle contains the frozen AIg calibration dataset prepared for ML experiments and artifact sharing.",
        "",
        "## Files",
        "",
        f"- `{dataset_csv}`: merged row-level dataset",
        f"- `{manifest_json}`: dataset manifest with split and campaign metadata",
        "",
        "## Columns",
        "",
        "- `campaign_id`: source campaign",
        "- `split`: frozen split label (`train`, `dev`, `test`)",
        "- `session_id`: session/correlation identifier",
        "- `action_id`: protected-action decision identifier",
        "- `scenario`: scenario family label",
        "- `action_name`: action under evaluation",
        "- `delta_t_minutes`: time since previous decision point",
        "- `prev_confidence`: previous AIg confidence state",
        "- `e_telecom`: telecom consistency score",
        "- `e_device`: device consistency score",
        "- `e_timing`: reconstructed timing-consistency score",
        "- `e_ordering`: reconstructed ordering-consistency score",
        "- `session_step_index`: 1-based decision position within the session",
        "- `recent_conf_mean_3`: mean previous-confidence value over the prior 3 decisions",
        "- `recent_conf_slope_3`: current previous-confidence minus the prior-3 mean",
        "- `recent_delta_mean_3`: mean inter-decision gap over the prior 3 decisions",
        "- `recent_telecom_mean_3`: mean telecom evidence over the prior 3 decisions",
        "- `recent_device_mean_3`: mean device evidence over the prior 3 decisions",
        "- `recent_timing_mean_3`: mean timing evidence over the prior 3 decisions",
        "- `recent_ordering_mean_3`: mean ordering evidence over the prior 3 decisions",
        "- `steps_since_strong_telecom`: decisions since the last strong telecom reinforcement (`e_telecom >= 0.8`)",
        "- `minutes_since_strong_telecom`: elapsed minutes since the last strong telecom reinforcement",
        "- `aig_label`: target label (`1` preserved, `0` violated)",
        "- `manual_allow`: manual-policy decision",
        "- `manual_threshold`: threshold used by the manual policy",
        "- `manual_c_value`: manual confidence value at decision time",
        "",
        "## Split counts",
        "",
    ]
    for split, count in sorted(split_counts.items()):
        lines.append(f"- `{split}`: {count} rows")
    lines.extend(["", "## Scenario counts", ""])
    for scenario, count in sorted(scenario_counts.items()):
        lines.append(f"- `{scenario}`: {count} rows")
    lines.extend(
        [
            "",
            "## Reproducibility note",
            "",
            "This publication bundle is derived from per-campaign calibration CSVs rather than raw trace JSON files.",
            "The raw traces may be retained privately for audit or regeneration, but this bundle is the shareable ML-ready dataset.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    campaign_root = Path(args.campaign_root)
    if not campaign_root.is_absolute():
        campaign_root = repo_root / campaign_root
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir

    campaign_specs = parse_campaign_specs(args.campaign)
    all_rows: list[dict[str, str]] = []
    campaigns_payload: list[dict[str, str | int]] = []

    for campaign_id, split in campaign_specs:
        dataset_csv = campaign_root / campaign_id / "calibration" / "aig_calibration_dataset.csv"
        if not dataset_csv.exists():
            raise SystemExit(f"Calibration dataset not found for campaign '{campaign_id}': {dataset_csv}")
        rows = load_rows(dataset_csv, campaign_id=campaign_id, split=split)
        all_rows.extend(rows)
        campaigns_payload.append(
            {
                "campaign_id": campaign_id,
                "split": split,
                "dataset_csv": f"<CAMPAIGN_ROOT>/{campaign_id}/calibration/aig_calibration_dataset.csv",
                "rows": len(rows),
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_csv_name = f"{args.dataset_name}.csv"
    manifest_name = f"{args.dataset_name}_manifest.json"
    readme_name = "README.md"

    dataset_csv_path = out_dir / dataset_csv_name
    write_csv(dataset_csv_path, all_rows)

    split_counts = Counter(row["split"] for row in all_rows)
    scenario_counts = Counter(row["scenario"] for row in all_rows)
    label_counts = Counter(row["aig_label"] for row in all_rows)

    manifest = {
        "dataset_name": args.dataset_name,
        "row_count": len(all_rows),
        "split_counts": dict(split_counts),
        "scenario_counts": dict(scenario_counts),
        "label_counts": dict(label_counts),
        "campaigns": campaigns_payload,
        "columns": list(all_rows[0].keys()) if all_rows else [],
        "notes": [
            "Paths are sanitized for portability.",
            "The merged dataset is intended as the publication-ready ML table.",
            "Per-campaign calibration CSVs remain the immediate source material.",
        ],
    }
    (out_dir / manifest_name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    write_readme(
        out_dir / readme_name,
        dataset_csv=dataset_csv_name,
        manifest_json=manifest_name,
        split_counts=split_counts,
        scenario_counts=scenario_counts,
    )

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
