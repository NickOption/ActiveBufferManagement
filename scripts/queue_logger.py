#!/usr/bin/env python3

"""
queue_logger.py

Periodically logs queue statistics from a Linux interface using 'tc -s qdisc'.
This is a lightweight way to observe queue backlog and drops during experiments.

Usage example:
python3 queue_logger.py s1-eth3 results/queue_log.csv 0.1
"""

import subprocess
import time
import csv
import sys
import os


def get_tc_stats(interface):
    """
    Run 'tc -s qdisc show dev <interface>' and return raw text output.
    """
    cmd = ["tc", "-s", "qdisc", "show", "dev", interface]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def main():
    """
    Periodically log raw queue statistics so they can be inspected later.
    """
    if len(sys.argv) != 4:
        print("Usage: python3 queue_logger.py <interface> <csv_path> <interval_seconds>")
        sys.exit(1)

    interface = sys.argv[1]
    csv_path = sys.argv[2]
    interval = float(sys.argv[3])

    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "interface", "raw_tc_output"])

        while True:
            timestamp = time.time()
            raw_output = get_tc_stats(interface)
            writer.writerow([timestamp, interface, raw_output.replace("\n", " | ")])
            f.flush()
            time.sleep(interval)


if __name__ == "__main__":
    main()
