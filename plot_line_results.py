import csv
import matplotlib.pyplot as plt

loads_baseline = []
avg_baseline = []
max_baseline = []
queue_baseline = []

loads_abm = []
avg_abm = []
max_abm = []
queue_abm = []

with open("results/line_runs/summary.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        load = int(row["load"])
        avg_fct = float(row["avg_fct"])
        max_fct = float(row["max_fct"])
        peak_q = float(row["peak_backlog_pkts"])

        if row["mode"] == "baseline":
            loads_baseline.append(load)
            avg_baseline.append(avg_fct)
            max_baseline.append(max_fct)
            queue_baseline.append(peak_q)
        elif row["mode"] == "abm":
            loads_abm.append(load)
            avg_abm.append(avg_fct)
            max_abm.append(max_fct)
            queue_abm.append(peak_q)

plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(loads_baseline, max_baseline, marker='x', label='Baseline')
plt.plot(loads_abm, max_abm, marker='s', label='ABM')
plt.xlabel("Background Load (M)")
plt.ylabel("Max FCT (ms)")
plt.title("Tail FCT vs Load")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.subplot(1, 2, 2)
plt.plot(loads_baseline, queue_baseline, marker='x', label='Baseline')
plt.plot(loads_abm, queue_abm, marker='s', label='ABM')
plt.xlabel("Background Load (M)")
plt.ylabel("Peak Backlog (packets)")
plt.title("Queue Backlog vs Load")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("results/line_runs/final_line_chart.png")
plt.show()
