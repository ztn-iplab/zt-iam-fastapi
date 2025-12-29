import csv
import statistics
from collections import defaultdict


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
        p95 = (
            statistics.quantiles(lat, n=20)[-1]
            if len(lat) >= 20
            else max(lat)
            if lat
            else 0
        )
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


if __name__ == "__main__":
    main()
