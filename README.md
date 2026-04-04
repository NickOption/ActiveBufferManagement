ABM Replication – Active Buffer Management in Datacenters

Introduction

Modern datacenter networks rely on shared buffer architectures within switches to absorb bursts and prevent packet loss. Traditional approaches separate Buffer Management (BM), which controls how buffer space is allocated across queues, and Active Queue Management (AQM), which controls when packets are admitted or dropped. While effective in isolation, this separation leads to poor coordination, increased queueing delay, lack of isolation between traffic, and unpredictable behavior under bursty workloads.

The paper “ABM: Active Buffer Management in Datacenters” proposes a unified approach that combines both perspectives. ABM dynamically adjusts queue thresholds using both total buffer occupancy and per-queue drain time, allowing it to better handle incast traffic and reduce tail latency without sacrificing throughput.

This work is important because modern datacenter traffic is increasingly bursty, and traditional buffering strategies struggle to maintain performance as link speeds increase and buffers become relatively smaller.

Target Result / Claim

The result we chose to replicate is:

ABM significantly improves the 99th percentile Flow Completion Time (FCT) for bursty/incast traffic under moderate to high network load, without reducing throughput.

We selected this claim because:
- It is the central result of the paper
- It clearly demonstrates the benefit of ABM over existing approaches like Dynamic Thresholds (DT)
- It is measurable in a Mininet environment using traffic generation and timing

Our goal is not to exactly reproduce the numerical values from the paper, but to replicate the trend:
- Baseline buffering leads to rapidly increasing FCT under load
- ABM leads to more stable FCT under the same conditions

Methodology from the Paper

The original paper evaluates ABM using large-scale simulation (NS-3) with a datacenter-style leaf-spine topology.

Key characteristics:
- Shared-memory switch buffers
- 10 Gbps links with controlled delay
- Multiple queues per port
- Workloads include background web-search traffic and incast traffic
- Metrics include 99th percentile FCT, buffer occupancy, and throughput

ABM dynamically computes queue thresholds based on remaining buffer space, number of congested queues, and queue drain rate.

Our Methodology (Mininet Implementation)

We implemented an approximation of ABM using Mininet due to hardware limitations.

Environment:
- Mininet with Linux-based software switches (OVS)
- Simplified leaf-spine-inspired topology
- Configurable bandwidth, delay, and queue sizes

Traffic Model:
- Background TCP traffic (iperf3) to simulate load levels from 20% to 80%
- Incast traffic using multiple short flows starting simultaneously

Compared Approaches:
1. Baseline (Drop-Tail / DT-like)
   - Static queue limits
   - No dynamic behavior

2. ABM Approximation
   - Periodically samples queue statistics
   - Estimates congestion and drain rate
   - Dynamically adjusts queue thresholds using an ABM-inspired approach

Metrics Collected:
- Flow Completion Time (FCT)
- 99th percentile FCT
- Throughput
- Queue occupancy

Results and Comparison

Original Paper Trend:
- Baseline shows rapid FCT increase under load
- ABM maintains stable FCT and reduces tail latency significantly

Our Results:
- Baseline shows increasing FCT and queue buildup
- ABM approximation reduces tail FCT and stabilizes performance
- Throughput remains similar across both approaches

Discussion

Our results differ from the paper numerically due to:
- Software-based buffering vs hardware shared-memory switches
- Approximate measurement of queue occupancy and drain rate
- Control-plane updates instead of real-time data-plane implementation

Despite this, the observed trends match the paper’s conclusions.

Lessons Learned

- Buffer management plays a key role in tail latency performance
- Combining buffer occupancy and drain rate improves congestion handling
- Many networking algorithms assume hardware features not available in software environments
- Control-plane approximations can still capture important system behavior

Conclusion

We successfully replicated the core idea of ABM using a Mininet-based approximation. While exact behavior differs from the original paper, the trends align with the main claim:

ABM reduces tail latency under bursty traffic without degrading throughput.

Repository Contents

- Mininet topology scripts
- Traffic generation scripts
- ABM approximation controller
- Experiment automation scripts
- Result data and plots
- README documentation

References

Addanki et al., “ABM: Active Buffer Management in Datacenters,” SIGCOMM 2022.







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
