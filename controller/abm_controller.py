#!/usr/bin/env python3

"""
abm_controller.py

This script approximates ABM in a Mininet/Linux environment by:
1. Reading queue statistics periodically
2. Estimating whether congestion is increasing
3. Adjusting the queue limit using a simple ABM-inspired policy

This is NOT a hardware-accurate implementation of the SIGCOMM paper.
Instead, it is a control-plane approximation designed for Mininet experiments.
"""

import subprocess
import sys
import time
import re


def get_backlog_packets(interface):
    """
    Extract the current queue backlog in packets from 'tc -s qdisc' output.

    Returns:
        backlog_pkts (int): estimated backlog in packets
    """
    cmd = ["tc", "-s", "qdisc", "show", "dev", interface]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    # Example tc output often includes text like:
    # backlog 0b 0p requeues 0
    # We try to extract the packet count after backlog
    match = re.search(r"backlog\s+\S+\s+(\d+)p", output)

    if match:
        return int(match.group(1))

    return 0


def set_queue_limit(interface, limit_packets):
    """
    Update the pfifo queue limit on the given interface.

    Note:
    Depending on the qdisc Mininet applies, this command may need adjustment.
    This is a simple starting point for a packet-based queue limit.
    """
    cmd = [
        "tc", "qdisc", "replace", "dev", interface,
        "root", "pfifo", "limit", str(limit_packets)
    ]
    subprocess.run(cmd, capture_output=True, text=True)


def compute_abm_limit(current_backlog, min_limit=20, max_limit=200):
    """
    Very simple ABM-inspired heuristic.

    Idea:
    - If backlog is high, reduce the queue limit to prevent excessive queueing delay.
    - If backlog is low, allow a somewhat larger limit so bursts can be absorbed.

    This is intentionally simple and explainable for the report.
    """
    if current_backlog > 100:
        return min_limit
    elif current_backlog > 50:
        return 50
    elif current_backlog > 20:
        return 100
    else:
        return max_limit


def main():
    """
    Periodically read queue state and update queue limit.
    """
    if len(sys.argv) != 3:
        print("Usage: python3 abm_controller.py <interface> <interval_seconds>")
        sys.exit(1)

    interface = sys.argv[1]
    interval = float(sys.argv[2])

    print(f"Starting ABM-inspired controller on {interface}")

    while True:
        backlog = get_backlog_packets(interface)
        new_limit = compute_abm_limit(backlog)

        set_queue_limit(interface, new_limit)

        print(f"[ABM] backlog={backlog} packets, applied_limit={new_limit}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
