# README (Individual Submission)

## Environment Setup

This project was built and tested inside the P4 Tutorials Virtual Machine.

### Requirements

* P4 Tutorials VM (Ubuntu-based)
* Mininet
* Python 3
* Open vSwitch (OVS)
* Linux `tc` (traffic control)

The experiments rely on this environment. Running outside of it may require additional setup and could produce different results.

---

## Project Structure

* topo/ – Mininet topology definition
* controller/ – ABM control logic
* scripts/ – traffic generation and experiment runner
* results/load_sweep/ – collected experiment data and final plots
* plot_mininet_paper_style.py – script used to generate graphs

---

## Introduction

Datacenter networks use shared buffers inside switches to handle bursts of traffic and prevent packet loss. Traditional approaches separate Buffer Management (BM) and Active Queue Management (AQM), which can lead to poor coordination during congestion.

The paper:

**“ABM: Active Buffer Management in Datacenters” (SIGCOMM 2022)**

proposes combining these into a unified approach. Instead of treating buffer allocation and queue management separately, ABM dynamically adjusts queue thresholds based on:

* total buffer occupancy
* per-queue drain rate

This improves how switches handle incast traffic and reduces tail latency.

---

## Target Result / Claim

The main claim I focused on is:

> ABM reduces tail Flow Completion Time (FCT) under bursty/incast traffic without reducing throughput.

I chose this result because tail FCT is one of the most important performance metrics in datacenter networks, especially under incast scenarios where many flows compete for limited buffer space.

The goal of this project was to reproduce the **trend**, not the exact numerical results from the paper.

---

## Methodology from the Paper

The original paper uses:

* ns-3 simulation
* a hardware-like shared-memory buffer model
* a datacenter leaf-spine topology
* realistic traffic workloads

In their model, all queues share a common buffer pool and dynamically compete for space.

They evaluate performance using:

* 99th percentile (tail) FCT
* queue occupancy
* throughput

---

## My Methodology (Mininet Approximation)

I implemented a simplified version of the system using:

* Mininet inside the P4 VM
* Linux-based software switches (OVS)
* `tc qdisc` for queue behavior

### Topology

* Leaf-spine-inspired topology
* Bottleneck link:

  * 3 Mbps bandwidth
  * queue size = 10 packets

### Traffic

* TCP background traffic using `iperf3`
* Short incast flows using custom Python scripts

### ABM Approximation

* Periodically samples queue backlog
* Adjusts queue limits dynamically
* Implemented in the control plane rather than hardware

---

## Key Differences from the Paper

* No shared-memory buffer (uses Linux `tc`)
* No direct visibility into hardware queue state
* Control-plane approximation instead of data-plane implementation
* Lower timing precision compared to ns-3

Because of these differences, this implementation should be viewed as an approximation rather than a full reproduction.

---

## Results

### Baseline (DropTail)

* Large variation in Flow Completion Time
* Tail latency up to ~5600 ms
* Indicates congestion and uneven flow performance

### ABM

* Slight reduction in tail latency
* Some stabilization of flow behavior
* Improvements are present but limited

To better match the evaluation style of the paper, I ran experiments at multiple load levels (4M, 8M, 10M) and plotted tail FCT versus load.

Final results are shown in:

* `results/load_sweep/mininet_paper_style_3panel.png`

---

## Queue Behavior

Observed behavior:

* Queue is mostly empty
* Occasional short spikes (e.g., ~160 bytes / 2 packets)

This indicates that congestion is short-lived rather than sustained, which limits how effective ABM can be in this environment.

---

## Comparison to the Paper

| Aspect               | Paper (ns-3)  | This Work (Mininet) |
| -------------------- | ------------- | ------------------- |
| Queue buildup        | Sustained     | Minimal / bursty    |
| Tail FCT improvement | Significant   | Modest              |
| Environment          | Hardware-like | Software-based      |
| Accuracy             | High          | Approximate         |

---

## Discussion

The results only partially match the paper.

ABM does not show strong improvements in this environment, mainly because:

* queues do not stay full long enough
* congestion is not sustained
* Mininet does not replicate shared-memory buffering

These limitations make it harder for ABM to have a noticeable effect.

However, the overall behavior still supports the idea that buffer-aware management can influence flow performance.

---

## Lessons Learned

* Buffer management plays a major role in tail latency
* TCP traffic is necessary to create realistic congestion
* Mininet behaves very differently from real hardware
* Measurement resolution can hide short bursts of congestion
* Replication requires understanding both the algorithm and the system

This project showed that implementing the idea is only part of the challenge — the environment has a huge impact on the results.

---

## Conclusion

This project successfully replicated the core idea of ABM:

* ABM can improve flow completion time under congestion
* In this Mininet-based setup, improvements are limited
* Results depend heavily on the experimental environment

Overall, this reinforces the importance of realistic system modeling when evaluating networking algorithms.

---

## How to Run

```bash
sudo python3 scripts/run_experiment.py baseline 10M
sudo python3 scripts/run_experiment.py abm 10M
```

---

## Repository Contents

* topo/ – topology
* controller/ – ABM logic
* scripts/ – experiment tools
* results/ – collected data and plots
