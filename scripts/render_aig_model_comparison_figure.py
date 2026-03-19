#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


MODELS = [
    ("manual_policy", "Manual", "#A04000"),
    ("logistic_base", "Pointwise\nlogistic", "#8C6D46"),
    ("logistic_rich_no_step", "History-aware\nlogistic", "#117A65"),
]

METRICS = [
    ("False step-up\nrate", "False step-up rate (benign)"),
    ("Takeover blocking\nrate", "Takeover blocking rate"),
    ("Task continuity", "Task completion continuity"),
]


def load_manual(path: Path) -> dict[str, float]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
        return {
            "False step-up rate (benign)": float(row["False step-up rate (benign)"]),
            "Takeover blocking rate": float(row["Takeover blocking rate"]),
            "Task completion continuity": float(row["Task completion continuity"]),
        }


def load_models(path: Path) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            out[row["Model"]] = {
                "False step-up rate (benign)": float(row["False step-up rate (benign)"]),
                "Takeover blocking rate": float(row["Takeover blocking rate"]),
                "Task completion continuity": float(row["Task completion continuity"]),
            }
    return out


def build_svg(values: dict[str, dict[str, float]]) -> str:
    width, height = 1120, 560
    ml, mr, mt, mb = 92, 36, 110, 118
    cw, ch = width - ml - mr, height - mt - mb
    group_w = cw / len(METRICS)
    bar_w = 60
    label_gap = 6
    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' style=\"font-family: 'Times New Roman', serif;\">",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<text x='{ml}' y='44' font-size='31' font-weight='700' fill='#222'>AIg calibration comparison across manual and learned models</text>",
        f"<text x='{ml}' y='76' font-size='20' fill='#555'>Held-out session split; history-aware features materially improve the benign-interruption/blocking tradeoff.</text>",
        f"<line x1='{ml}' y1='{mt}' x2='{ml}' y2='{mt + ch}' stroke='#222'/>",
        f"<line x1='{ml}' y1='{mt + ch}' x2='{ml + cw}' y2='{mt + ch}' stroke='#222'/>",
    ]
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = mt + ch - (tick * ch)
        lines.append(f"<line x1='{ml}' y1='{y:.1f}' x2='{ml + cw}' y2='{y:.1f}' stroke='#ececec'/>")
        lines.append(f"<text x='{ml - 10}' y='{y + 6:.1f}' font-size='18' text-anchor='end' fill='#222'>{tick:.2f}</text>")

    for idx, (metric_label, metric_key) in enumerate(METRICS):
        gx = ml + idx * group_w + (group_w / 2)
        start_x = gx - ((len(MODELS) * bar_w + (len(MODELS) - 1) * label_gap) / 2)
        for m_idx, (model_key, _display, color) in enumerate(MODELS):
            value = values[model_key][metric_key]
            bh = value * ch
            x = start_x + m_idx * (bar_w + label_gap)
            y = mt + ch - bh
            value_y = max(96.0, y - 10.0)
            lines.append(
                f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w}' height='{bh:.1f}' fill='{color}' opacity='0.92'/>"
            )
            lines.append(
                f"<text x='{x + bar_w/2:.1f}' y='{value_y:.1f}' font-size='18' font-weight='700' text-anchor='middle' fill='#222'>{value:.3f}</text>"
            )
        label_y = mt + ch + 34
        for line_idx, part in enumerate(metric_label.split("\n")):
            lines.append(
                f"<text x='{gx:.1f}' y='{label_y + line_idx * 22:.1f}' font-size='20' text-anchor='middle' fill='#222'>{part}</text>"
            )

    lx = ml
    ly = height - 34
    for _model_key, display, color in MODELS:
        lines.append(f"<rect x='{lx}' y='{ly - 14}' width='24' height='14' fill='{color}'/>")
        label = display.replace("\n", " ")
        lines.append(f"<text x='{lx + 36}' y='{ly}' font-size='19' fill='#222'>{label}</text>")
        lx += 210

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.input_dir).resolve()
    manual = load_manual(root / "manual_baseline.csv")
    learned = load_models(root / "model_comparison.csv")
    values = {"manual_policy": manual}
    values.update(learned)

    svg_path = Path(args.output_svg).resolve() if args.output_svg else root / "fig6_model_comparison.svg"
    pdf_path = Path(args.output_pdf).resolve() if args.output_pdf else root / "fig6_model_comparison.pdf"
    svg_path.write_text(build_svg(values), encoding="utf-8")
    subprocess.run(
        [args.rsvg_convert, "-f", "pdf", "-o", str(pdf_path), str(svg_path)],
        check=True,
    )
    print(svg_path)
    print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the AIg model comparison figure from benchmark CSV outputs")
    parser.add_argument("--input-dir", required=True, help="Directory containing manual_baseline.csv and model_comparison.csv")
    parser.add_argument("--output-svg", help="Output SVG path; defaults to <input-dir>/fig6_model_comparison.svg")
    parser.add_argument("--output-pdf", help="Output PDF path; defaults to <input-dir>/fig6_model_comparison.pdf")
    parser.add_argument("--rsvg-convert", default="rsvg-convert", help="Path to rsvg-convert")
    return parser.parse_args()

