import csv
import math
import statistics
from pathlib import Path


def load_latencies(path, scenario, mode):
    values = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["scenario"] != scenario or row["mode"] != mode:
                continue
            if row["ok"].strip().lower() != "true":
                continue
            values.append(float(row["latency_ms"]))
    return values


def percentile(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    k = int(round((p / 100) * (len(values) - 1)))
    return values[k]


def main():
    path = "experiments/iam_metrics.csv"
    recovery = load_latencies(path, "offline_degraded", "zt_totp")
    rebind = load_latencies(path, "rebind_time", "zt_totp")

    if not recovery and not rebind:
        print("No recovery/rebind data found.")
        return

    width = 800
    height = 420
    margin_left = 70
    margin_right = 30
    margin_top = 30
    margin_bottom = 70
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    max_val = max(recovery + rebind) if (recovery or rebind) else 1.0
    max_val = math.ceil(max_val / 200.0) * 200.0
    if max_val <= 0:
        max_val = 1.0

    def y_for(value):
        return margin_top + chart_height - (value / max_val) * chart_height

    lines = []
    lines.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>")
    lines.append("<rect width='100%' height='100%' fill='white' />")
    lines.append(
        f"<line x1='{margin_left}' y1='{margin_top}' x2='{margin_left}' y2='{margin_top + chart_height}' stroke='#222' />"
    )
    lines.append(
        f"<line x1='{margin_left}' y1='{margin_top + chart_height}' x2='{margin_left + chart_width}' y2='{margin_top + chart_height}' stroke='#222' />"
    )

    tick_step = 200
    tick = 0
    while tick <= max_val:
        y = y_for(tick)
        lines.append(f"<line x1='{margin_left - 5}' y1='{y}' x2='{margin_left}' y2='{y}' stroke='#222' />")
        lines.append(
            f"<text x='{margin_left - 10}' y='{y + 4}' font-size='12' text-anchor='end' fill='#222'>{int(tick)}</text>"
        )
        tick += tick_step

    groups = [
        ("offline recovery", recovery),
        ("device rebind", rebind),
    ]
    group_x = [
        margin_left + chart_width * 0.30,
        margin_left + chart_width * 0.70,
    ]
    bar_width = 60

    for (label, values), x in zip(groups, group_x):
        if values:
            median = statistics.median(values)
            p95 = percentile(values, 95)
        else:
            median = 0.0
            p95 = 0.0

        bar_top = y_for(median)
        bar_height = (margin_top + chart_height) - bar_top
        lines.append(
            f"<rect x='{x - bar_width / 2}' y='{bar_top}' width='{bar_width}' height='{bar_height}' fill='#4C78A8' />"
        )
        # P95 whisker above the median bar.
        lines.append(
            f"<line x1='{x}' y1='{y_for(median)}' x2='{x}' y2='{y_for(p95)}' stroke='#222' stroke-width='2' />"
        )
        lines.append(
            f"<line x1='{x - 12}' y1='{y_for(p95)}' x2='{x + 12}' y2='{y_for(p95)}' stroke='#222' stroke-width='2' />"
        )

        lines.append(
            f"<text x='{x}' y='{bar_top - 8}' font-size='12' text-anchor='middle' fill='#222'>{median:.1f} ms</text>"
        )
        lines.append(
            f"<text x='{x}' y='{y_for(p95) - 8}' font-size='11' text-anchor='middle' fill='#222'>p95 {p95:.1f} ms</text>"
        )

        lines.append(
            f"<text x='{x}' y='{margin_top + chart_height + 28}' font-size='12' text-anchor='middle' fill='#222'>{label}</text>"
        )

    lines.append(
        f"<text x='{margin_left - 50}' y='{margin_top - 8}' font-size='12' text-anchor='start' fill='#222'>ms</text>"
    )
    lines.append("</svg>")

    Path("experiments/iam_recovery_rebind.svg").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote experiments/iam_recovery_rebind.svg")


if __name__ == "__main__":
    main()
