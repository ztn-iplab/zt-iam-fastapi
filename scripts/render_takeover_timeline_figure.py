#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


WIDTH, HEIGHT = 1180, 700
ML, MR, MT, MB = 90, 55, 88, 94
FG = "#222222"
SUBTLE = "#666666"
GRID = "#E9E9E9"
GREEN = "#117A65"
BROWN = "#A04000"
BLUE = "#2D74A8"
GRAY = "#6C757D"
ALLOW_FILL = "#E9F6F2"
CHALLENGE_FILL = "#FBEFE8"
NEUTRAL_FILL = "#EEF3F8"


def xp(frac: float) -> float:
    return ML + frac * (WIDTH - ML - MR)


def lane_y(idx: int) -> float:
    return MT + 150 + idx * 190


def event_box(x: float, y: float, w: float, h: float, fill: str, label: str, text_fill: str = FG) -> list[str]:
    return [
        f"<rect x='{x:.1f}' y='{y:.1f}' rx='12' ry='12' width='{w:.1f}' height='{h:.1f}' fill='{fill}' stroke='none'/>",
        f"<text x='{x + w/2:.1f}' y='{y + h/2 + 7:.1f}' font-size='21' font-weight='700' text-anchor='middle' fill='{text_fill}'>{label}</text>",
    ]


def main() -> int:
    t0 = xp(0.18)
    t1 = xp(0.50)
    t2 = xp(0.78)
    lane1 = lane_y(0)
    lane2 = lane_y(1)
    box_w, box_h = 180, 46

    lines = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' style=\"font-family: 'Times New Roman', serif;\">",
        "<rect width='100%' height='100%' fill='white'/>",
        f"<text x='{ML}' y='34' font-size='28' font-weight='700' fill='{FG}'>Takeover timeline under identical authentication history</text>",
        f"<text x='{ML}' y='62' font-size='18' fill='{SUBTLE}'>The session stays active in both lanes; only the authorization basis changes after control transfer.</text>",
    ]

    for x, label in [(t0, "t0"), (t1, "t1"), (t2, "t2")]:
        lines.append(f"<line x1='{x:.1f}' y1='{MT}' x2='{x:.1f}' y2='{HEIGHT-MB}' stroke='{GRID}' stroke-dasharray='8 8'/>")
        lines.append(f"<text x='{x:.1f}' y='{HEIGHT-MB+36}' font-size='21' text-anchor='middle' fill='{FG}'>{label}</text>")

    for y, label in [(lane1, "Session"), (lane2, "AIg")]:
        lines.append(f"<line x1='{ML}' y1='{y:.1f}' x2='{WIDTH-MR}' y2='{y:.1f}' stroke='{GRAY}' stroke-width='3'/>")
        lines.append(f"<text x='{ML-4}' y='{y-38:.1f}' font-size='21' font-weight='700' fill='{FG}'>{label}</text>")

    lines.extend(event_box(t0 - box_w/2, lane1 - 74, box_w, box_h, ALLOW_FILL, "Authentication"))
    lines.extend(event_box(t1 - box_w/2, lane1 - 74, box_w, box_h, CHALLENGE_FILL, "Control transfer"))
    lines.extend(event_box(t2 - box_w/2, lane1 - 74, box_w, box_h, ALLOW_FILL, "Action allowed"))

    lines.extend(event_box(t0 - box_w/2, lane2 - 74, box_w, box_h, ALLOW_FILL, "Authentication"))
    lines.extend(event_box(t1 - box_w/2, lane2 - 74, box_w, box_h, CHALLENGE_FILL, "Control transfer"))
    lines.extend(event_box(t2 - box_w/2, lane2 - 74, box_w, box_h, CHALLENGE_FILL, "Not authorized"))

    lines.extend(
        [
            f"<circle cx='{t0:.1f}' cy='{lane1:.1f}' r='8' fill='{GREEN}' stroke='white' stroke-width='2'/>",
            f"<circle cx='{t1:.1f}' cy='{lane1:.1f}' r='8' fill='{BROWN}' stroke='white' stroke-width='2'/>",
            f"<circle cx='{t2:.1f}' cy='{lane1:.1f}' r='8' fill='{GREEN}' stroke='white' stroke-width='2'/>",
            f"<circle cx='{t0:.1f}' cy='{lane2:.1f}' r='8' fill='{GREEN}' stroke='white' stroke-width='2'/>",
            f"<circle cx='{t1:.1f}' cy='{lane2:.1f}' r='8' fill='{BROWN}' stroke='white' stroke-width='2'/>",
            f"<circle cx='{t2:.1f}' cy='{lane2:.1f}' r='8' fill='{BROWN}' stroke='white' stroke-width='2'/>",
        ]
    )

    arrow = "marker-end='url(#arrow)'"
    lines.extend(
        [
            "<defs><marker id='arrow' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'><path d='M0,0 L0,6 L9,3 z' fill='#222222'/></marker></defs>",
            f"<text x='{t0-26:.1f}' y='{lane1+44:.1f}' font-size='19' text-anchor='end' fill='{FG}'>Principal established</text>",
            f"<text x='{t1-18:.1f}' y='{lane1+66:.1f}' font-size='19' text-anchor='end' fill='{FG}'>Session still valid</text>",
            f"<text x='{t2-20:.1f}' y='{lane1+44:.1f}' font-size='19' text-anchor='end' fill='{GREEN}'>Allow on active session</text>",
            f"<line x1='{t1+8:.1f}' y1='{lane2-12:.1f}' x2='{t2-34:.1f}' y2='{lane2-12:.1f}' stroke='{BROWN}' stroke-width='3' {arrow}/>",
            f"<text x='{(t1+t2)/2:.1f}' y='{lane2-26:.1f}' font-size='19' text-anchor='middle' fill='{BROWN}'>C(t) falls below θ before the request</text>",
        ]
    )

    note_x = xp(0.66)
    note_y = lane2 + 78
    note_w = 255
    note_h = 62
    lines.extend(
        [
            f"<rect x='{note_x:.1f}' y='{note_y:.1f}' rx='10' ry='10' width='{note_w}' height='{note_h}' fill='{NEUTRAL_FILL}' stroke='none'/>",
            f"<text x='{note_x + note_w/2:.1f}' y='{note_y + 24:.1f}' font-size='18' text-anchor='middle' fill='{FG}'>Possible recovery:</text>",
            f"<text x='{note_x + note_w/2:.1f}' y='{note_y + 46:.1f}' font-size='18' text-anchor='middle' fill='{FG}'>continuity challenge / step-up</text>",
            f"<text x='{t2-10:.1f}' y='{lane2+46:.1f}' font-size='19' text-anchor='end' fill='{BROWN}'>Action not authorized</text>",
            f"<text x='{t2-10:.1f}' y='{lane2+70:.1f}' font-size='19' text-anchor='end' fill='{BROWN}'>under current continuity state</text>",
        ]
    )

    lines.extend(
        [
            f"<rect x='{ML}' y='{HEIGHT-56}' width='22' height='14' fill='{GREEN}'/>",
            f"<text x='{ML+34}' y='{HEIGHT-43}' font-size='18' fill='{FG}'>allowed / continuity preserved</text>",
            f"<rect x='{ML}' y='{HEIGHT-30}' width='22' height='14' fill='{BROWN}'/>",
            f"<text x='{ML+34}' y='{HEIGHT-17}' font-size='18' fill='{FG}'>takeover / not authorized under AIg</text>",
            f"<rect x='{ML+510}' y='{HEIGHT-43}' width='22' height='14' fill='{GRAY}'/>",
            f"<text x='{ML+544}' y='{HEIGHT-30}' font-size='18' fill='{FG}'>session remains active in both lanes</text>",
            "</svg>",
        ]
    )

    repo_root = Path(__file__).resolve().parents[1]
    out_svg = repo_root / "fig4_takeover_timeline.svg"
    out_svg.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
