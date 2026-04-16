# README (Individual Submission)

## Environment Setup

This project is designed to run inside the P4 Tutorials Virtual Machine.

### Requirements

* P4 Tutorials VM (Ubuntu-based)
* Mininet
* Python 3
* Open vSwitch (OVS)
* Linux `tc` (traffic control)

Note: This project was tested in the P4 VM environment. Running it outside may require additional setup.

---

## Project Structure

* topo/ – Mininet topology
* controller/ – ABM control logic
* scripts/ – traffic generation + experiment runner
* results/load_sweep/ – collected data + final graphs
* plot_mininet_paper_style.py – plotting script

---

## Introduction

Datacenter networks use shared buffers to handle bursts of traffic. Traditional designs separate Buffer Management (BM) and Active Queue Management (AQM), which can lead to poor performance under congestion.

The paper:

**“ABM: Active Buffer Management in Datacenters” (SIGCOMM 2022)**

proposes combining these into a single system. The main idea is to dynamically adjust queue thresholds based on:

* total buffer usage
* queue drain rate

This improves performance during incast traffic and reduces tail latency.

---

## Target Result / Claim

The result replicated in this project is:

> ABM reduces tail Flow Completion Time (FCT) under incast traffic without reducing throughput.

This result was chosen because tail FCT is a key metric in datacenter performance, especially when multiple flows compete for limited buffer space.

---

## Methodology from the Paper

The original paper uses:

* ns-3 simulation
* shared-memory buffer model
* leaf-spine topology
* realistic workloads

All queues share a common buffer pool and dynamically compete for space.

Metrics:

* tail (99th percentile) FCT
* queue occupancy
* throughput

---

## My Methodology (Mininet)

This project implements a simplified version using:

* Mininet inside the P4 VM
* OVS software switches
* Linux `tc` for queue behavior

### Topology

* Leaf-spine-inspired
* Bottleneck link:

  * 3 Mbps bandwidth
  * queue size = 10 packets

### Traffic

* TCP background traffic (iperf3)
* Short incast flows (Python scripts)

### ABM Approximation

* Periodically reads queue backlog
* Adjusts queue limits
* Implemented in control plane

---

## Key Differences from the Paper

* No shared-memory buffer (uses Linux `tc`)
* No hardware-level queue visibility
* Control-plane approximation instead of hardware implementation
* Lower timing accuracy

This means the implementation is an approximation of the original system.

---

## How to Run

### Clean environment

```bash
sudo mn -c
```

### Run baseline (DropTail)

```bash
sudo python3 scripts/run_experiment.py baseline 10M
```

### Run ABM

```bash
sudo python3 scripts/run_experiment.py abm 10M
```

---

## Results

### Baseline

* Large variation in FCT
* Tail latency up to ~5600 ms

### ABM

* Slight reduction in tail latency
* More stable flow behavior

Load tests were performed at:

* 4M
* 8M
* 10M

Final graph:

* results/load_sweep/mininet_paper_style_3panel.png

---

## Queue Behavior

Observed:

* Queue mostly empty
* Small spikes (e.g., ~160 bytes / 2 packets)

This indicates short-lived congestion rather than sustained queue buildup.

---

## Comparison to Paper

| Aspect               | Paper         | This Work   |
| -------------------- | ------------- | ----------- |
| Queue buildup        | Sustained     | Minimal     |
| Tail FCT improvement | Large         | Small       |
| Environment          | Hardware-like | Software    |
| Accuracy             | High          | Approximate |

---

## Discussion

Results differ from the paper because:

* queues do not stay full long enough
* congestion is not sustained
* Mininet does not replicate shared buffers

Because of this, ABM does not show strong improvements.

However, the general idea of buffer-aware control is still visible.

---

## Lessons Learned

* Buffer management affects tail latency
* TCP is required for realistic congestion
* Mininet behaves differently from hardware
* Measurement resolution matters
* Environment strongly impacts results

---

## Conclusion

This project replicates the main idea of ABM:

* ABM can improve flow completion time
* In Mininet, improvements are limited
* Results depend heavily on the environment

---

## Repository Contents

* topo/ – topology
* controller/ – ABM logic
* scripts/ – experiment tools
* results/ – data + graphs
