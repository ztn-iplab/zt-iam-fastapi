#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


WIDTH, HEIGHT = 980, 740
ML, MT = 90, 42
FG = "#222222"
SUBTLE = "#666666"
GREEN = "#117A65"
BROWN = "#A04000"
BLUE = "#2D74A8"
GRAY = "#6C757D"
ALLOW_FILL = "#E9F6F2"
CHALLENGE_FILL = "#FBEFE8"
NEUTRAL_FILL = "#EEF3F8"
ARROW = "#8A939B"


def box(x: float, y: float, w: float, h: float, fill: str, title: str, body: list[str]) -> list[str]:
    lines = [
        f"<rect x='{x:.1f}' y='{y:.1f}' rx='16' ry='16' width='{w:.1f}' height='{h:.1f}' fill='{fill}' stroke='none'/>",
        f"<text x='{x + w/2:.1f}' y='{y + 28:.1f}' font-size='22' font-weight='700' text-anchor='middle' fill='{FG}'>{title}</text>",
    ]
    for idx, line in enumerate(body):
        lines.append(
            f"<text x='{x + w/2:.1f}' y='{y + 58 + idx * 22:.1f}' font-size='17' text-anchor='middle' fill='{FG}'>{line}</text>"
        )
    return lines


def arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{ARROW}' stroke-width='3' marker-end='url(#arrow)'/>"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_svg = repo_root / "fig_aig_calibration_pipeline.svg"

    left_x = 120
    mid_x = 370
    right_x = 620
    top_y = 120
    mid_y = 290
    low_y = 448
    w = 240
    h = 104

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' style=\"font-family: 'Times New Roman', serif;\">",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<defs><marker id='arrow' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'><path d='M0,0 L0,6 L9,3 z' fill='{ARROW}'/></marker></defs>",
        f"<text x='{ML}' y='{MT}' font-size='28' font-weight='700' fill='{FG}'>AIg calibration pipeline</text>",
        f"<text x='{ML}' y='{MT + 28}' font-size='18' fill='{SUBTLE}'>Offline learning calibrates feature contribution; runtime authorization remains analytical.</text>",
    ]

    lines.extend(
        box(
            left_x,
            top_y,
            w,
            h,
            ALLOW_FILL,
            "Input traces",
            ["HMS sessions and", "simulated takeovers", "raw telemetry histories"],
        )
    )
    lines.extend(
        box(
            right_x,
            top_y,
            w,
            h,
            NEUTRAL_FILL,
            "Telemetry collection",
            ["browser instrumentation", "plus telecom-state", "event capture"],
        )
    )
    lines.extend(
        box(
            left_x,
            mid_y,
            w,
            h + 22,
            ALLOW_FILL,
            "Feature extraction",
            ["x(t) = [e_telecom, e_device,", "e_timing, e_ordering,", "delta t, C(t-delta t)]"],
        )
    )
    lines.extend(
        box(
            right_x,
            mid_y,
            w,
            h,
            CHALLENGE_FILL,
            "Calibration dataset",
            ["label each decision as", "AIg preserved or", "AIg violated"],
        )
    )
    lines.extend(
        box(
            mid_x,
            low_y,
            w,
            h,
            NEUTRAL_FILL,
            "Weight estimation",
            ["logistic regression", "fit on held-out", "session-level splits"],
        )
    )
    lines.extend(
        box(
            mid_x,
            low_y + 144,
            w,
            h,
            ALLOW_FILL,
            "Analytical AIg model",
            ["learned weights inform", "confidence updates and", "authorization policy"],
        )
    )

    lines.extend(
        [
            arrow(left_x + w, top_y + h / 2, right_x, top_y + h / 2),
            arrow(right_x + w / 2, top_y + h, right_x + w / 2, mid_y),
            arrow(right_x, mid_y + h / 2, left_x + w, mid_y + h / 2),
            arrow(left_x + w / 2, mid_y + h + 22, mid_x + w / 2, low_y),
            arrow(mid_x + w / 2, low_y + h, mid_x + w / 2, low_y + 144),
            f"<text x='{490:.1f}' y='{162:.1f}' font-size='17' text-anchor='middle' fill='{BLUE}'>collect decision-time evidence</text>",
            f"<text x='{820:.1f}' y='{270:.1f}' font-size='17' text-anchor='middle' fill='{BLUE}'>assemble observation rows</text>",
            f"<text x='{490:.1f}' y='{352:.1f}' font-size='17' text-anchor='middle' fill='{BLUE}'>derive normalized features</text>",
            f"<text x='{490:.1f}' y='{434:.1f}' font-size='17' text-anchor='middle' fill='{BLUE}'>fit interpretable coefficients</text>",
            f"<text x='{490:.1f}' y='{588:.1f}' font-size='17' text-anchor='middle' fill='{GREEN}'>runtime still evaluates C(t) against theta</text>",
        ]
    )

    lines.append("</svg>")
    out_svg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
