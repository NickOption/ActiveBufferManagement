Environment Setup!

This project is designed to run inside the P4 Tutorials Virtual Machine environment.

Required Environment
P4 Tutorials VM (Ubuntu-based)
Mininet (pre-installed)
Python3
Open vSwitch (OVS)
Linux tc (traffic control)

This project is built and tested in the P4 VM environment and may not work correctly outside of it without additional setup.

Introduction

Modern datacenter networks rely on shared buffer architectures within switches to absorb bursts and prevent packet loss. Traditional approaches separate Buffer Management (BM) and Active Queue Management (AQM), which can lead to poor coordination and increased latency under bursty workloads.

The paper:

“ABM: Active Buffer Management in Datacenters” (SIGCOMM 2022)

proposes a unified approach that dynamically adjusts queue thresholds based on:

total buffer occupancy
per-queue drain rate

This allows better handling of incast traffic and reduces tail latency.

Target Result / Claim

We replicate the core claim:

ABM reduces tail Flow Completion Time (FCT) under bursty/incast traffic without reducing throughput.

Our goal is to reproduce the trend, not exact numerical values.

Methodology from the Paper

The original paper uses:

ns-3 simulation (C++)
hardware-like shared buffer model
datacenter leaf-spine topology
realistic workloads

Metrics:

99th percentile FCT
queue occupancy
throughput
Our Methodology (Mininet – P4 VM)

We implemented an approximation using:

Mininet (inside P4 VM)
Linux-based software switches (OVS)
tc qdisc for queue management
Topology
Leaf-spine-inspired
Bottleneck link:
3 Mbps bandwidth
queue size = 10 packets
Traffic
TCP background traffic (iperf3)
Incast short flows using custom Python scripts
ABM Approximation
Periodically samples queue backlog
Adjusts queue limits dynamically
Uses control-plane logic instead of hardware data-plane
Results
Baseline
High variation in Flow Completion Time
Tail latency up to ~5600 ms
Indicates congestion and unfairness
ABM
Slight reduction in tail latency
Some stabilization of flow performance
Improvements are modest
Queue Behavior

Observed:

Queue mostly empty
Occasional small spikes (e.g., 160 bytes / 2 packets)

Indicates short-lived congestion rather than sustained queue buildup

Comparison to Paper
Aspect	Paper (ns-3)	Mininet (This Work)
Queue buildup	Sustained	Minimal / short bursts
Tail FCT improvement	Significant	Modest
Environment	Hardware-like	Software-based
Accuracy	High	Approximate
Discussion

Our results differ from the paper due to:

Software-based buffering vs hardware shared-memory switches
Limited queue visibility using tc
Coarse timing and sampling resolution
Control-plane approximation instead of real-time hardware control

Despite these differences:

The conceptual behavior of ABM is still partially observed

Lessons Learned
Buffer management strongly impacts tail latency
TCP vs UDP traffic significantly changes queue behavior
Software environments (Mininet) differ from hardware simulations
Measurement resolution affects observed results
Replication requires understanding both theory and system limitations
Conclusion

We successfully replicated the core concept of ABM:

ABM can improve flow completion time under congestion
However, in Mininet, improvements are limited
This highlights the importance of environment when evaluating networking algorithms
Repository Contents
Mininet topology (topo/)
ABM controller (controller/)
Traffic scripts (scripts/)
Experiment runner
Results (final CSV outputs)



Flow Completion Time (Slowdown)
        ^
      8 |                                       / <-- Baseline (Drop-Tail / DT)
        |                                     /
      7 |                                   /
        |                                 /
      6 |                               /
        |                             /
      5 |                           /
        |                         /
      4 |                       /
        |                     /
      3 |                   /                   _ -- <-- ABM (Expected)
        |                 /            _ -- - 
      2 |               /     _ -- - 
        |      _ -- - - - - 
      1 | - - 
        |
        +---|-------|-------|-------|-------|-------|---> Network Load 
           0.2     0.4     0.6     0.8     0.9     1.0   (Congestion)
