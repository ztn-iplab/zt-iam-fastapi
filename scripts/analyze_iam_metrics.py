import csv
import statistics
from collections import defaultdict
from pathlib import Path


def write_summary(stats, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "mode", "ok_rate", "median_ms", "p95_ms", "total"])

        for (scenario, mode), items in stats.items():
            oks = [i["ok"] for i in items]
            lat = [i["latency_ms"] for i in items]
            ok_rate = (sum(oks) / len(oks)) if items else 0
            median = statistics.median(lat) if lat else 0
            p95 = statistics.quantiles(lat, n=20)[-1] if len(lat) >= 20 else (max(lat) if lat else 0)
            writer.writerow([scenario, mode, f"{ok_rate:.3f}", f"{median:.1f}", f"{p95:.1f}", len(items)])


def write_svg(stats, output_path):
    scenarios = [
        "legitimate_login",
        "seed_compromise",
        "relay_phishing",
        "offline_degraded",
        "offline_replay",
    ]
    modes = ["standard_totp", "zt_totp"]
    label_map = {
        "legitimate_login": "legitimate login",
        "seed_compromise": "seed compromise",
        "relay_phishing": "relay phishing",
        "offline_degraded": "offline degraded",
        "offline_replay": "offline replay",
        "standard_totp": "standard totp",
        "zt_totp": "zt totp",
    }
    data = []
    for scenario in scenarios:
        for mode in modes:
            items = stats.get((scenario, mode))
            if not items:
                continue
            oks = [i["ok"] for i in items]
            ok_rate = (sum(oks) / len(oks)) * 100 if items else 0
            data.append((scenario, mode, ok_rate))

    width = 900
    height = 480
    margin_left = 70
    margin_right = 30
    margin_top = 30
    margin_bottom = 90
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    groups = [s for s in scenarios if any(d[0] == s for d in data)]
    if not groups:
        return

    group_width = chart_width / max(len(groups), 1)
    bar_width = group_width * 0.35
    gap = group_width * 0.15

    def x_for(group_index, mode_index):
        base = margin_left + group_index * group_width
        return base + gap + mode_index * bar_width

    def y_for(value):
        return margin_top + chart_height - (value / 100) * chart_height

    lines = []
    lines.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>")
    lines.append("<rect width='100%' height='100%' fill='white' />")
    lines.append(
        f"<line x1='{margin_left}' y1='{margin_top}' x2='{margin_left}' y2='{margin_top + chart_height}' stroke='#222' />"
    )
    lines.append(
        f"<line x1='{margin_left}' y1='{margin_top + chart_height}' x2='{margin_left + chart_width}' y2='{margin_top + chart_height}' stroke='#222' />"
    )

    for tick in range(0, 101, 20):
        y = y_for(tick)
        lines.append(f"<line x1='{margin_left - 5}' y1='{y}' x2='{margin_left}' y2='{y}' stroke='#222' />")
        lines.append(
            f"<text x='{margin_left - 10}' y='{y + 4}' font-size='12' text-anchor='end' fill='#222'>{tick}</text>"
        )

    color_map = {"standard_totp": "#4C78A8", "zt_totp": "#F58518"}
    mode_index = {"standard_totp": 0, "zt_totp": 1}

    for gi, scenario in enumerate(groups):
        group_data = [d for d in data if d[0] == scenario]
        for _, mode, value in group_data:
            x = x_for(gi, mode_index[mode])
            y = y_for(value)
            h = margin_top + chart_height - y
            lines.append(f"<rect x='{x}' y='{y}' width='{bar_width}' height='{h}' fill='{color_map[mode]}' />")
            lines.append(
                f"<text x='{x + bar_width / 2}' y='{y - 6}' font-size='11' text-anchor='middle' fill='#222'>{value:.1f}%</text>"
            )

        label_x = margin_left + gi * group_width + group_width / 2
        label = label_map.get(scenario, scenario)
        lines.append(
            f"<text x='{label_x}' y='{margin_top + chart_height + 24}' font-size='12' text-anchor='middle' fill='#222'>{label}</text>"
        )

    legend_y = height - 30
    legend_x = margin_left
    for idx, mode in enumerate(modes):
        x = legend_x + idx * 160
        lines.append(f"<rect x='{x}' y='{legend_y - 10}' width='14' height='14' fill='{color_map[mode]}' />")
        label = label_map.get(mode, mode)
        lines.append(f"<text x='{x + 22}' y='{legend_y + 2}' font-size='12' fill='#222'>{label}</text>")

    lines.append("</svg>")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    path = "experiments/iam_metrics.csv"
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["ok"] = row["ok"].strip().lower() == "true"
            row["latency_ms"] = float(row["latency_ms"])
            rows.append(row)

    stats = defaultdict(list)
    for row in rows:
        stats[(row["scenario"], row["mode"])].append(row)

    print("Total rows:", len(rows))
    for (scenario, mode), items in stats.items():
        oks = [i["ok"] for i in items]
        lat = [i["latency_ms"] for i in items]
        ok_rate = sum(oks) / len(oks) if items else 0
        median = statistics.median(lat) if lat else 0
        p95 = statistics.quantiles(lat, n=20)[-1] if len(lat) >= 20 else (max(lat) if lat else 0)
        print(
            f"{scenario:16} {mode:13} ok_rate={ok_rate:.2f} "
            f"median_ms={median:.1f} p95_ms={p95:.1f}"
        )

    reason_counts = defaultdict(int)
    for row in rows:
        if not row["ok"]:
            reason_counts[(row["scenario"], row["mode"], row["reason"])] += 1

    print("\nFailure reasons:")
    for key, count in sorted(reason_counts.items()):
        print(key, count)

    write_summary(stats, "experiments/iam_summary.csv")
    write_svg(stats, "experiments/iam_plot.svg")
    print("\nWrote experiments/iam_summary.csv")
    print("Wrote experiments/iam_plot.svg")


if __name__ == "__main__":
    main()
