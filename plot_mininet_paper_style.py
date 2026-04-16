import csv
import re
import matplotlib.pyplot as plt

# Map your Mininet load settings to slide-friendly percentages
loads = [20, 40, 80]

baseline_fct_files = [
    "results/load_sweep/baseline_4M_fct.csv",
    "results/load_sweep/baseline_8M_fct.csv",
    "results/load_sweep/baseline_10M_fct.csv",
]

abm_fct_files = [
    "results/load_sweep/abm_4M_fct.csv",
    "results/load_sweep/abm_8M_fct.csv",
    "results/load_sweep/abm_10M_fct.csv",
]

baseline_queue_files = [
    "results/load_sweep/baseline_4M_queue.csv",
    "results/load_sweep/baseline_8M_queue.csv",
    "results/load_sweep/baseline_10M_queue.csv",
]

abm_queue_files = [
    "results/load_sweep/abm_4M_queue.csv",
    "results/load_sweep/abm_8M_queue.csv",
    "results/load_sweep/abm_10M_queue.csv",
]


def read_fct_stats(csv_file):
    """
    Return tail FCT (max) and average FCT from one run.
    """
    values = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            values.append(float(row["fct_ms"]))

    tail = max(values)
    avg = sum(values) / len(values)
    return tail, avg


def read_max_backlog_pkts(csv_file):
    """
    Extract the maximum observed backlog in packets from the raw tc log.
    """
    max_pkts = 0

    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = row["raw_tc_output"]

            # Find all backlog packet matches like: backlog 160b 2p
            matches = re.findall(r"backlog\s+\S+\s+(\d+)p", raw)
            for m in matches:
                max_pkts = max(max_pkts, int(m))

    return max_pkts


# Build FCT series
baseline_tail = []
baseline_avg = []
abm_tail = []
abm_avg = []

for f in baseline_fct_files:
    tail, avg = read_fct_stats(f)
    baseline_tail.append(tail)
    baseline_avg.append(avg)

for f in abm_fct_files:
    tail, avg = read_fct_stats(f)
    abm_tail.append(tail)
    abm_avg.append(avg)

# Build queue series
baseline_q = [read_max_backlog_pkts(f) for f in baseline_queue_files]
abm_q = [read_max_backlog_pkts(f) for f in abm_queue_files]

# Create a 1x3 paper-style figure
fig, axs = plt.subplots(1, 3, figsize=(14, 4.5))

# (a) Tail FCT
axs[0].plot(loads, abm_tail, marker='s', label='ABM')
axs[0].plot(loads, baseline_tail, marker='x', label='DropTail')
axs[0].set_title('(a) Tail FCT')
axs[0].set_xlabel('Load (%)')
axs[0].set_ylabel('Tail FCT (ms)')
axs[0].legend()
axs[0].grid(True, linestyle='--', alpha=0.5)

# (b) Average FCT
axs[1].plot(loads, abm_avg, marker='s', label='ABM')
axs[1].plot(loads, baseline_avg, marker='x', label='DropTail')
axs[1].set_title('(b) Average FCT')
axs[1].set_xlabel('Load (%)')
axs[1].set_ylabel('Average FCT (ms)')
axs[1].legend()
axs[1].grid(True, linestyle='--', alpha=0.5)

# (c) Max queue backlog
axs[2].plot(loads, abm_q, marker='s', label='ABM')
axs[2].plot(loads, baseline_q, marker='x', label='DropTail')
axs[2].set_title('(c) Max Queue Backlog')
axs[2].set_xlabel('Load (%)')
axs[2].set_ylabel('Max backlog (pkts)')
axs[2].legend()
axs[2].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("results/load_sweep/mininet_paper_style_3panel.png", dpi=200)
plt.show()

