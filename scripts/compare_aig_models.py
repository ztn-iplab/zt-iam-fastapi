#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, roc_auc_score


BASE_FEATURE_COLUMNS = [
    "e_telecom",
    "e_device",
    "e_timing",
    "e_ordering",
    "delta_t_minutes",
    "prev_confidence",
]

RICH_FEATURE_COLUMNS = [
    *BASE_FEATURE_COLUMNS[:-2],
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

RICH_NO_STEP_COLUMNS = [name for name in RICH_FEATURE_COLUMNS if name != "session_step_index"]
RICH_NO_STEP_NO_PREV_COLUMNS = [name for name in RICH_NO_STEP_COLUMNS if name != "prev_confidence"]


@dataclass
class DataRow:
    session_id: str
    scenario: str
    raw: dict[str, float]
    label: int
    manual_allow: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark multiple AIg ML models on the publication dataset")
    parser.add_argument("--dataset-csv", required=True, help="Publication dataset CSV")
    parser.add_argument("--output-dir", required=True, help="Directory for benchmark outputs")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--train-ratio", type=float, default=0.60)
    parser.add_argument("--dev-ratio", type=float, default=0.20)
    return parser.parse_args()


def feature_vector(row: DataRow, feature_names: list[str]) -> list[float]:
    return [row.raw[name] for name in feature_names]


def load_rows(path: Path) -> list[DataRow]:
    rows: list[DataRow] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                DataRow(
                    session_id=row["session_id"],
                    scenario=row["scenario"],
                    raw={name: float(row[name]) for name in RICH_FEATURE_COLUMNS},
                    label=int(row["aig_label"]),
                    manual_allow=int(row["manual_allow"]),
                )
            )
    return rows


def stratified_session_split(
    rows: list[DataRow],
    *,
    seed: int,
    train_ratio: float,
    dev_ratio: float,
) -> tuple[set[str], set[str], set[str]]:
    rng = random.Random(seed)
    by_scenario: dict[str, list[str]] = {}
    for row in rows:
        sessions = by_scenario.setdefault(row.scenario, [])
        if row.session_id not in sessions:
            sessions.append(row.session_id)

    train_sessions: set[str] = set()
    dev_sessions: set[str] = set()
    test_sessions: set[str] = set()
    for sessions in by_scenario.values():
        local = list(sessions)
        rng.shuffle(local)
        n = len(local)
        train_count = max(1, round(n * train_ratio))
        dev_count = max(1, round(n * dev_ratio))
        if train_count + dev_count >= n:
            dev_count = 1
            train_count = max(1, n - 2)
        train_sessions.update(local[:train_count])
        dev_sessions.update(local[train_count : train_count + dev_count])
        test_sessions.update(local[train_count + dev_count :])
    return train_sessions, dev_sessions, test_sessions


def rows_to_xy(rows: list[DataRow], feature_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x = np.array([feature_vector(row, feature_names) for row in rows], dtype=float)
    y = np.array([row.label for row in rows], dtype=int)
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


def evaluate_predictions(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    benign_total = int((y_true == 1).sum())
    attack_total = int((y_true == 0).sum())
    benign_block = int(((y_true == 1) & (y_pred == 0)).sum())
    benign_allow = int(((y_true == 1) & (y_pred == 1)).sum())
    attack_block = int(((y_true == 0) & (y_pred == 0)).sum())
    return {
        "AUROC": float(roc_auc_score(y_true, y_prob)),
        "AUPRC": float(average_precision_score(y_true, y_prob)),
        "F1-score": float(f1_score(y_true, y_pred, zero_division=0)),
        "Brier score": float(brier_score_loss(y_true, y_prob)),
        "False step-up rate (benign)": benign_block / benign_total if benign_total else 0.0,
        "Takeover blocking rate": attack_block / attack_total if attack_total else 0.0,
        "Task completion continuity": benign_allow / benign_total if benign_total else 0.0,
        "Decision threshold": float(threshold),
    }


def evaluate_manual(rows: list[DataRow]) -> dict[str, float]:
    y_true = np.array([row.label for row in rows], dtype=int)
    y_pred = np.array([row.manual_allow for row in rows], dtype=int)
    benign_total = int((y_true == 1).sum())
    attack_total = int((y_true == 0).sum())
    benign_block = int(((y_true == 1) & (y_pred == 0)).sum())
    benign_allow = int(((y_true == 1) & (y_pred == 1)).sum())
    attack_block = int(((y_true == 0) & (y_pred == 0)).sum())
    return {
        "False step-up rate (benign)": benign_block / benign_total if benign_total else 0.0,
        "Takeover blocking rate": attack_block / attack_total if attack_total else 0.0,
        "Task completion continuity": benign_allow / benign_total if benign_total else 0.0,
    }


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(dataset_path)
    train_sessions, dev_sessions, test_sessions = stratified_session_split(
        rows,
        seed=args.seed,
        train_ratio=args.train_ratio,
        dev_ratio=args.dev_ratio,
    )
    train_rows = [row for row in rows if row.session_id in train_sessions]
    dev_rows = [row for row in rows if row.session_id in dev_sessions]
    test_rows = [row for row in rows if row.session_id in test_sessions]

    y_train = np.array([row.label for row in train_rows], dtype=int)
    y_dev = np.array([row.label for row in dev_rows], dtype=int)
    y_test = np.array([row.label for row in test_rows], dtype=int)

    model_specs = [
        ("logistic_base", BASE_FEATURE_COLUMNS, LogisticRegression(max_iter=4000, solver="lbfgs", random_state=args.seed)),
        ("logistic_rich", RICH_FEATURE_COLUMNS, LogisticRegression(max_iter=4000, solver="lbfgs", random_state=args.seed)),
        (
            "logistic_rich_no_step",
            RICH_NO_STEP_COLUMNS,
            LogisticRegression(max_iter=4000, solver="lbfgs", random_state=args.seed),
        ),
        (
            "logistic_rich_no_step_no_prev",
            RICH_NO_STEP_NO_PREV_COLUMNS,
            LogisticRegression(max_iter=4000, solver="lbfgs", random_state=args.seed),
        ),
        (
            "random_forest_rich",
            RICH_FEATURE_COLUMNS,
            RandomForestClassifier(
                n_estimators=400,
                max_depth=None,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=args.seed,
            ),
        ),
        (
            "random_forest_rich_no_step_no_prev",
            RICH_NO_STEP_NO_PREV_COLUMNS,
            RandomForestClassifier(
                n_estimators=400,
                max_depth=None,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=args.seed,
            ),
        ),
        (
            "extra_trees_rich",
            RICH_FEATURE_COLUMNS,
            ExtraTreesClassifier(
                n_estimators=400,
                max_depth=None,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=args.seed,
            ),
        ),
        (
            "extra_trees_rich_no_step_no_prev",
            RICH_NO_STEP_NO_PREV_COLUMNS,
            ExtraTreesClassifier(
                n_estimators=400,
                max_depth=None,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=args.seed,
            ),
        ),
        (
            "hist_gradient_boosting_rich",
            RICH_FEATURE_COLUMNS,
            HistGradientBoostingClassifier(
                max_depth=8,
                learning_rate=0.08,
                max_iter=300,
                min_samples_leaf=20,
                random_state=args.seed,
            ),
        ),
        (
            "hist_gradient_boosting_rich_no_step_no_prev",
            RICH_NO_STEP_NO_PREV_COLUMNS,
            HistGradientBoostingClassifier(
                max_depth=8,
                learning_rate=0.08,
                max_iter=300,
                min_samples_leaf=20,
                random_state=args.seed,
            ),
        ),
    ]

    comparison_rows: list[list[object]] = []
    importance_rows: list[list[object]] = []
    for model_name, feature_names, model in model_specs:
        x_train, _ = rows_to_xy(train_rows, feature_names)
        x_dev, _ = rows_to_xy(dev_rows, feature_names)
        x_test, _ = rows_to_xy(test_rows, feature_names)
        model.fit(x_train, y_train)
        dev_prob = model.predict_proba(x_dev)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(x_dev)
        if dev_prob.ndim != 1:
            dev_prob = dev_prob[:, 1]
        threshold = choose_threshold(y_dev, dev_prob)

        test_prob = model.predict_proba(x_test)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(x_test)
        if test_prob.ndim != 1:
            test_prob = test_prob[:, 1]
        metrics = evaluate_predictions(y_test, test_prob, threshold)
        comparison_rows.append(
            [
                model_name,
                *[f"{metrics[name]:.4f}" for name in [
                    "AUROC",
                    "AUPRC",
                    "F1-score",
                    "Brier score",
                    "False step-up rate (benign)",
                    "Takeover blocking rate",
                    "Task completion continuity",
                    "Decision threshold",
                ]],
            ]
        )
        if hasattr(model, "feature_importances_"):
            ranked = sorted(zip(feature_names, model.feature_importances_, strict=True), key=lambda item: item[1], reverse=True)[:5]
            for feature_name, score in ranked:
                importance_rows.append([model_name, feature_name, f"{score:.6f}"])
        elif hasattr(model, "coef_"):
            ranked = sorted(zip(feature_names, np.abs(model.coef_[0]), strict=True), key=lambda item: item[1], reverse=True)[:5]
            for feature_name, score in ranked:
                importance_rows.append([model_name, feature_name, f"{score:.6f}"])

    manual = evaluate_manual(test_rows)
    baseline_rows = [
        ["manual_policy", f"{manual['False step-up rate (benign)']:.4f}", f"{manual['Takeover blocking rate']:.4f}", f"{manual['Task completion continuity']:.4f}"]
    ]
    split_rows = [
        ["train_rows", len(train_rows)],
        ["dev_rows", len(dev_rows)],
        ["test_rows", len(test_rows)],
        ["train_sessions", len(train_sessions)],
        ["dev_sessions", len(dev_sessions)],
        ["test_sessions", len(test_sessions)],
    ]

    write_csv(
        output_dir / "model_comparison.csv",
        [
            "Model",
            "AUROC",
            "AUPRC",
            "F1-score",
            "Brier score",
            "False step-up rate (benign)",
            "Takeover blocking rate",
            "Task completion continuity",
            "Decision threshold",
        ],
        comparison_rows,
    )
    write_csv(
        output_dir / "manual_baseline.csv",
        ["Model", "False step-up rate (benign)", "Takeover blocking rate", "Task completion continuity"],
        baseline_rows,
    )
    write_csv(output_dir / "split_summary.csv", ["Metric", "Value"], split_rows)
    write_csv(output_dir / "feature_importance_top5.csv", ["Model", "Feature", "Importance"], importance_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
