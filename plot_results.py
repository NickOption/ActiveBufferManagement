import matplotlib.pyplot as plt
import csv

def read_fct(file):
    flows = []
    fcts = []
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flows.append(row['sender'])
            fcts.append(float(row['fct_ms']))
    return flows, fcts

baseline_flows, baseline_fct = read_fct("results/baseline_FINAL_fct.csv")
abm_flows, abm_fct = read_fct("results/abm_FINAL_fct.csv")

# Force consistent order
flow_order = ["h1", "h2", "h3", "h4"]

baseline_map = dict(zip(baseline_flows, baseline_fct))
abm_map = dict(zip(abm_flows, abm_fct))

baseline_vals = [baseline_map[f] for f in flow_order]
abm_vals = [abm_map[f] for f in flow_order]

x = range(len(flow_order))

plt.figure(figsize=(8, 5))
plt.plot(x, baseline_vals, marker='x', label='Baseline')
plt.plot(x, abm_vals, marker='s', label='ABM')

plt.xticks(x, flow_order)
plt.xlabel("Flow (Sender)")
plt.ylabel("Flow Completion Time (ms)")
plt.title("Baseline vs ABM Flow Completion Time")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.savefig("results/fct_line_comparison.png")
plt.show()
