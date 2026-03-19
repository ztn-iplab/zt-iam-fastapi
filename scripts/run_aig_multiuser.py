#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


@dataclass
class UserRunResult:
    synthetic_user_id: int
    iam_user_id: int
    seed: int
    returncode: int
    duration_s: float
    experiment_run_id: str | None
    stdout_tail: str
    stderr_tail: str
    csv_path: str
    trace_path: str | None


def is_usable_run(result: UserRunResult) -> bool:
    # run_aig_scenarios.py uses rc=2 for expectation mismatch; the trace is still usable.
    if result.returncode not in (0, 2):
        return False
    return Path(result.csv_path).exists()


def parse_experiment_run_id(stdout: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith("experiment_run_id="):
            return line.split("=", 1)[1].strip()
    return None


def tail_text(text: str, max_lines: int = 20) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def run_one(
    *,
    repo_root: Path,
    python_exe: str,
    base_url: str,
    api_key: str,
    insecure: bool,
    synthetic_user_id: int,
    iam_user_id: int,
    repeats: int,
    jitter: float,
    seed: int,
    export_combined: bool,
    campaign_dir: Path,
) -> UserRunResult:
    user_dir = campaign_dir / f"user_{synthetic_user_id:04d}"
    user_dir.mkdir(parents=True, exist_ok=True)
    out_csv = user_dir / "aig_scenarios.csv"
    export_dir = user_dir / "traces"
    export_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        python_exe,
        str(repo_root / "scripts" / "run_aig_scenarios.py"),
        "--base-url",
        base_url,
        "--api-key",
        api_key,
        "--user-id",
        str(iam_user_id),
        "--repeats",
        str(repeats),
        "--jitter",
        str(jitter),
        "--seed",
        str(seed),
        "--output-csv",
        str(out_csv),
        "--export-dir",
        str(export_dir),
    ]
    if insecure:
        cmd.append("--insecure")
    if export_combined:
        cmd.append("--export-combined")

    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    duration_s = time.perf_counter() - started
    exp_id = parse_experiment_run_id(proc.stdout)
    trace_path = None
    if exp_id:
        candidate = export_dir / f"{exp_id}.json"
        if candidate.exists():
            trace_path = str(candidate)
    return UserRunResult(
        synthetic_user_id=synthetic_user_id,
        iam_user_id=iam_user_id,
        seed=seed,
        returncode=proc.returncode,
        duration_s=duration_s,
        experiment_run_id=exp_id,
        stdout_tail=tail_text(proc.stdout),
        stderr_tail=tail_text(proc.stderr),
        csv_path=str(out_csv),
        trace_path=trace_path,
    )


def merge_csvs(results: list[UserRunResult], out_csv: Path) -> int:
    rows_written = 0
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    handle = out_csv.open("w", newline="", encoding="utf-8")
    try:
        for r in results:
            p = Path(r.csv_path)
            if not is_usable_run(r) or not p.exists():
                continue
            with p.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    continue
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=["campaign_user_id", *reader.fieldnames])
                    writer.writeheader()
                for row in reader:
                    row = {"campaign_user_id": r.synthetic_user_id, **row}
                    writer.writerow(row)
                    rows_written += 1
    finally:
        handle.close()
    return rows_written


def merge_traces(results: list[UserRunResult], out_json: Path) -> dict[str, Any]:
    merged = {
        "tenant_id": None,
        "filters": {"campaign_merge": True},
        "counts": {"telecom_events": 0, "observations": 0, "decisions": 0},
        "telecom_events": [],
        "observations": [],
        "decisions": [],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    for r in results:
        if not is_usable_run(r) or not r.trace_path:
            continue
        p = Path(r.trace_path)
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if merged["tenant_id"] is None:
            merged["tenant_id"] = data.get("tenant_id")
        for key in ("telecom_events", "observations", "decisions"):
            items = data.get(key) or []
            for item in items:
                if isinstance(item, dict):
                    item = dict(item)
                    item.setdefault("metadata_json", {})
                    if isinstance(item["metadata_json"], dict):
                        item["metadata_json"].setdefault("campaign_user_id", r.synthetic_user_id)
                merged[key].append(item)
    for key in ("telecom_events", "observations", "decisions"):
        merged["counts"][key] = len(merged[key])
    out_json.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def write_manifest(results: list[UserRunResult], manifest_path: Path, aggregate_csv: Path, merged_trace: Path | None) -> dict[str, Any]:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    full_successes = [r for r in results if r.returncode == 0]
    usable_runs = [r for r in results if is_usable_run(r)]
    failures = [r for r in results if not is_usable_run(r)]
    expectation_mismatches = [r for r in results if r.returncode == 2]
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_users": len(results),
        "successes": len(full_successes),
        "usable_runs": len(usable_runs),
        "expectation_mismatches": len(expectation_mismatches),
        "failures": len(failures),
        "aggregate_csv": str(aggregate_csv),
        "merged_trace_json": str(merged_trace) if merged_trace else None,
        "runs": [
            {
                "synthetic_user_id": r.synthetic_user_id,
                "iam_user_id": r.iam_user_id,
                "seed": r.seed,
                "returncode": r.returncode,
                "duration_s": round(r.duration_s, 3),
                "experiment_run_id": r.experiment_run_id,
                "csv_path": r.csv_path,
                "trace_path": r.trace_path,
                "stdout_tail": r.stdout_tail,
                "stderr_tail": r.stderr_tail,
            }
            for r in results
        ],
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run many automated AIg scenario users and aggregate outputs")
    parser.add_argument("--base-url", default="https://localhost/api/v1")
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--insecure", action="store_true")
    parser.add_argument("--users", type=int, default=50, help="Number of synthetic users to run")
    parser.add_argument("--start-user-id", type=int, default=1000, help="Synthetic campaign user index (for manifests only)")
    parser.add_argument("--iam-user-id", type=int, default=1, help="Existing IAM user_id used for DB-backed inserts")
    parser.add_argument(
        "--participants-csv",
        default=None,
        help="CSV with participant_no and user_id columns (e.g., experiments/participants/ztiam_demo_participants.csv)",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--jitter", type=float, default=0.03)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--no-export-combined", action="store_true")
    parser.add_argument("--campaign-id", default=None)
    parser.add_argument("--output-root", default="experiments/aig_multiuser")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    python_exe = sys.executable or "python3"
    campaign_id = args.campaign_id or f"aigmulti-{utc_stamp()}-{uuid.uuid4().hex[:6]}"
    campaign_dir = (repo_root / args.output_root / campaign_id).resolve()
    campaign_dir.mkdir(parents=True, exist_ok=True)
    print(f"campaign_id={campaign_id}")
    print(f"campaign_dir={campaign_dir}")

    export_combined = not args.no_export_combined
    futures = []
    results: list[UserRunResult] = []

    user_targets: list[tuple[int, int]] = []
    if args.participants_csv:
        participants_path = Path(args.participants_csv)
        if not participants_path.is_absolute():
            participants_path = (repo_root / participants_path).resolve()
        if not participants_path.exists():
            raise SystemExit(f"participants csv not found: {participants_path}")
        with participants_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"participant_no", "user_id"}
            missing = [k for k in required if k not in (reader.fieldnames or [])]
            if missing:
                raise SystemExit(
                    f"participants csv missing required columns: {', '.join(missing)}"
                )
            for row in reader:
                try:
                    synthetic_user_id = int(row["participant_no"])
                    iam_user_id = int(row["user_id"])
                except (TypeError, ValueError):
                    continue
                user_targets.append((synthetic_user_id, iam_user_id))
        user_targets.sort(key=lambda x: x[0])
        if args.users > 0:
            user_targets = user_targets[: args.users]
    else:
        for idx in range(args.users):
            synthetic_user_id = args.start_user_id + idx
            user_targets.append((synthetic_user_id, args.iam_user_id))
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for idx, (synthetic_user_id, iam_user_id) in enumerate(user_targets):
            seed = args.seed + idx
            futures.append(
                pool.submit(
                    run_one,
                    repo_root=repo_root,
                    python_exe=python_exe,
                    base_url=args.base_url,
                    api_key=args.api_key,
                    insecure=args.insecure,
                    synthetic_user_id=synthetic_user_id,
                    iam_user_id=iam_user_id,
                    repeats=args.repeats,
                    jitter=args.jitter,
                    seed=seed,
                    export_combined=export_combined,
                    campaign_dir=campaign_dir,
                )
            )
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            status = "ok" if r.returncode == 0 else f"rc={r.returncode}"
            print(
                f"synthetic_user={r.synthetic_user_id} iam_user={r.iam_user_id} "
                f"{status} dur={r.duration_s:.2f}s exp={r.experiment_run_id}"
            )
            if r.returncode != 0:
                print(r.stdout_tail)
                if r.stderr_tail:
                    print(r.stderr_tail)
                if not args.continue_on_error:
                    # let already-running futures finish, then fail
                    pass

    results.sort(key=lambda r: r.synthetic_user_id)
    aggregate_csv = campaign_dir / "aggregate_decisions.csv"
    rows_written = merge_csvs(results, aggregate_csv)
    merged_trace_path = campaign_dir / "merged_trace.json" if export_combined else None
    merged_counts = None
    if merged_trace_path:
        merged = merge_traces(results, merged_trace_path)
        merged_counts = merged["counts"]
    manifest = write_manifest(results, campaign_dir / "manifest.json", aggregate_csv, merged_trace_path)

    ok = sum(1 for r in results if r.returncode == 0)
    usable = sum(1 for r in results if is_usable_run(r))
    failed = len(results) - usable
    elapsed = time.perf_counter() - started
    print(
        json.dumps(
            {
                "campaign_id": campaign_id,
                "users_requested": len(user_targets),
                "successes": ok,
                "usable_runs": usable,
                "expectation_mismatches": sum(1 for r in results if r.returncode == 2),
                "failures": failed,
                "elapsed_s": round(elapsed, 2),
                "aggregate_decision_rows": rows_written,
                "merged_counts": merged_counts,
                "manifest": manifest.get("aggregate_csv"),
            },
            indent=2,
        )
    )
    if failed and not args.continue_on_error:
        sys.exit(2)


if __name__ == "__main__":
    main()
