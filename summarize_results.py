import csv
import glob
import os
import re

def summarize_fct_file(path):
    fcts = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fcts.append(float(row["fct_ms"]))
    if not fcts:
        return None
    return {
        "avg_fct": sum(fcts) / len(fcts),
        "max_fct": max(fcts),
        "min_fct": min(fcts),
    }

def summarize_queue_file(path):
    peak_pkts = 0
    with open(path, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 3:
                continue
            raw = row[2]
            matches = re.findall(r"backlog\s+\S+\s+(\d+)p", raw)
            for m in matches:
                peak_pkts = max(peak_pkts, int(m))
    return {"peak_backlog_pkts": peak_pkts}

rows = []

for fct_file in sorted(glob.glob("results/line_runs/*_fct.csv")):
    name = os.path.basename(fct_file).replace("_fct.csv", "")
    queue_file = f"results/line_runs/{name}_queue.csv"

    mode, load = name.split("_", 1)

    fct_summary = summarize_fct_file(fct_file)
    queue_summary = summarize_queue_file(queue_file)

    if fct_summary:
        rows.append({
            "mode": mode,
            "load": load.replace("M", ""),
            "avg_fct": round(fct_summary["avg_fct"], 3),
            "max_fct": round(fct_summary["max_fct"], 3),
            "min_fct": round(fct_summary["min_fct"], 3),
            "peak_backlog_pkts": queue_summary["peak_backlog_pkts"],
        })

rows = sorted(rows, key=lambda r: (r["mode"], int(r["load"])))

with open("results/line_runs/summary.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["mode", "load", "avg_fct", "max_fct", "min_fct", "peak_backlog_pkts"]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Wrote results/line_runs/summary.csv")
