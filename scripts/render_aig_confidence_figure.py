#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path


WIDTH, HEIGHT = 980, 520
ML, MR, MT, MB = 90, 36, 92, 86
CW, CH = WIDTH - ML - MR, HEIGHT - MT - MB

FG = "#222222"
SUBTLE = "#666666"
GRID = "#E9E9E9"
GREEN = "#117A65"
BROWN = "#A04000"
THRESH = "#6C757D"
ALLOW_FILL = "#E9F6F2"
CHALLENGE_FILL = "#FBEFE8"


def x_pos(t: float) -> float:
    return ML + (t / 10.0) * CW


def y_pos(c: float) -> float:
    return MT + CH - (c * CH)


def confidence(t: float) -> float:
    if t <= 1.6:
        return 0.34 + 0.33 * (t / 1.6)
    if t <= 3.2:
        return 0.67 + 0.21 * ((t - 1.6) / 1.6)
    if t <= 6.6:
        decay = math.exp(-0.52 * (t - 3.2))
        return 0.33 + (0.88 - 0.33) * decay
    if t <= 8.0:
        return 0.44 + 0.26 * ((t - 6.6) / 1.4)
    return max(0.36, 0.70 - 0.08 * ((t - 8.0) / 2.0))


def build_svg() -> str:
    threshold = 0.58
    title_y = 34
    subtitle_y = 62
    points = [(t / 50.0, confidence(t / 50.0)) for t in range(0, 501)]
    path_d = "M " + " L ".join(f"{x_pos(t):.1f} {y_pos(c):.1f}" for t, c in points)
    threshold_y = y_pos(threshold)

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' style=\"font-family: 'Times New Roman', serif;\">",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<text x='{ML}' y='{title_y}' font-size='28' font-weight='700' fill='{FG}'>Evolution of AIg confidence over time</text>",
        f"<text x='{ML}' y='{subtitle_y}' font-size='18' fill='{SUBTLE}'>Reinforcing observations increase confidence; in the absence of evidence, confidence decays toward the challenge region.</text>",
        f"<rect x='{ML}' y='{MT}' width='{CW}' height='{threshold_y - MT:.1f}' fill='{ALLOW_FILL}'/>",
        f"<rect x='{ML}' y='{threshold_y:.1f}' width='{CW}' height='{MT + CH - threshold_y:.1f}' fill='{CHALLENGE_FILL}'/>",
        f"<line x1='{ML}' y1='{MT}' x2='{ML}' y2='{MT+CH}' stroke='{FG}'/>",
        f"<line x1='{ML}' y1='{MT+CH}' x2='{ML+CW}' y2='{MT+CH}' stroke='{FG}'/>",
    ]

    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = y_pos(tick)
        lines.append(f"<line x1='{ML}' y1='{y:.1f}' x2='{ML+CW}' y2='{y:.1f}' stroke='{GRID}'/>")
        lines.append(f"<text x='{ML-10}' y='{y+6:.1f}' font-size='19' text-anchor='end' fill='{FG}'>{tick:.2f}</text>")

    for tick in range(0, 11, 2):
        x = x_pos(float(tick))
        lines.append(f"<line x1='{x:.1f}' y1='{MT}' x2='{x:.1f}' y2='{MT+CH}' stroke='{GRID}'/>")
        lines.append(f"<text x='{x:.1f}' y='{MT+CH+32}' font-size='19' text-anchor='middle' fill='{FG}'>{tick}</text>")

    lines.extend(
        [
            f"<line x1='{ML}' y1='{threshold_y:.1f}' x2='{ML+CW}' y2='{threshold_y:.1f}' stroke='{THRESH}' stroke-width='2.5' stroke-dasharray='10 8'/>",
            f"<text x='{ML+CW-4}' y='{threshold_y-10:.1f}' font-size='21' text-anchor='end' fill='{THRESH}'>Threshold θ</text>",
            f"<text x='{ML+CW-4}' y='{MT+30}' font-size='21' text-anchor='end' fill='{GREEN}'>AIg action permitted</text>",
            f"<text x='{ML+CW-4}' y='{MT+CH-12:.1f}' font-size='21' text-anchor='end' fill='{BROWN}'>Challenge / deny region</text>",
            f"<path d='{path_d}' fill='none' stroke='{GREEN}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/>",
        ]
    )

    markers = [
        (0.6, confidence(0.6), "Authentication at t0", GREEN, -16),
        (2.3, confidence(2.3), "Reinforcing observations", GREEN, -18),
        (5.8, confidence(5.8), "No new evidence; decay", BROWN, 28),
        (7.4, confidence(7.4), "Fresh evidence raises C(t)", GREEN, -18),
    ]
    for t, c, label, color, dy in markers:
        x = x_pos(t)
        y = y_pos(c)
        lines.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6.5' fill='{color}' stroke='white' stroke-width='2'/>")
        label_y = y + dy
        anchor = "start"
        label_x = x + 10
        if t > 7.0:
            anchor = "end"
            label_x = x - 10
        lines.append(f"<text x='{label_x:.1f}' y='{label_y:.1f}' font-size='20' text-anchor='{anchor}' fill='{color}'>{label}</text>")

    lines.extend(
        [
            f"<text x='{ML + CW/2:.1f}' y='{HEIGHT-18}' font-size='21' text-anchor='middle' fill='{FG}'>Time</text>",
            f"<text x='26' y='{MT + CH/2:.1f}' font-size='21' text-anchor='middle' fill='{FG}' transform='rotate(-90 26 {MT + CH/2:.1f})'>AIg confidence C(t)</text>",
            "</svg>",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_svg = repo_root / "Figure2_AIg_Confidence.svg"
    out_svg.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
