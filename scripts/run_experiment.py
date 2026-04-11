#!/usr/bin/env python3

"""
run_experiment.py

Runs one Mininet experiment in either:
- baseline mode: no ABM controller
- abm mode: ABM-inspired controller enabled

This script writes results into the results/ folder using mode-specific names.
"""

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import OVSBridge
import time
import os
import sys

# Import custom topology
sys.path.append("topo")
from abm_topo import ABMTopo


def start_server(receiver, server_log):
    """
    Start the short-flow server in the background on the receiver host.
    """
    receiver.cmd("pkill -f shortflow_server.py")
    receiver.cmd(f"python3 scripts/shortflow_server.py > {server_log} 2>&1 &")


def start_background_traffic(sender, receiver_ip, bandwidth, duration, log_path):
    """
    Start one background traffic flow using iperf3.
    """
    sender.cmd(
        f"./scripts/background_traffic.sh {receiver_ip} {bandwidth} {duration} "
        f"> {log_path} 2>&1 &"
    )


def start_queue_logger(switch_interface, queue_log):
    """
    Start queue logging on the root namespace.
    """
    os.system(
        f"python3 scripts/queue_logger.py {switch_interface} {queue_log} 0.01 "
        f"> /dev/null 2>&1 &"
    )


def start_abm_controller(switch_interface, controller_log):
    """
    Start the ABM-inspired controller.
    """
    os.system(
        f"python3 controller/abm_controller.py {switch_interface} 0.1 "
        f"> {controller_log} 2>&1 &"
    )


def run_incast(senders, receiver_ip, flow_size, fct_csv, mode):
    """
    Launch multiple short flows at nearly the same time.
    """
    flow_id = 0
    for host in senders:
        host.cmd(
            f"python3 scripts/shortflow_client.py {receiver_ip} 5001 {flow_size} "
            f"{host.name} {mode}_flow{flow_id} {fct_csv} "
            f"> results/{mode}_{host.name}_flow.log 2>&1 &"
        )
        flow_id += 1


def cleanup():
    """
    Kill background processes from earlier runs.
    """
    os.system("pkill -f shortflow_server.py")
    os.system("pkill -f queue_logger.py")
    os.system("pkill -f abm_controller.py")
    os.system("pkill -f shortflow_client.py")
    os.system("pkill -f iperf3")


def main():
    """
    Usage:
        sudo python3 scripts/run_experiment.py baseline 4M
        sudo python3 scripts/run_experiment.py abm 4M
    """
    if len(sys.argv) != 3:
        print("Usage: sudo python3 scripts/run_experiment.py <baseline|abm> <background_bandwidth>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    background_bw = sys.argv[2]

    if mode not in ["baseline", "abm"]:
        print("Mode must be either 'baseline' or 'abm'")
        sys.exit(1)

    cleanup()

    # Output files
    fct_csv = f"results/{mode}_fct_results.csv"
    queue_log = f"results/{mode}_queue_log.csv"
    controller_log = f"results/{mode}_abm_controller.log"
    server_log = f"results/{mode}_server.log"
    bg1_log = f"results/{mode}_background_h1.log"
    bg2_log = f"results/{mode}_background_h2.log"

    net = Mininet(
        topo=ABMTopo(),
        link=TCLink,
        switch=OVSBridge,
        controller=None
    )
    net.start()

    h1 = net.get("h1")
    h2 = net.get("h2")
    h3 = net.get("h3")
    h4 = net.get("h4")
    h5 = net.get("h5")

    receiver_ip = h5.IP()

    # Start server
    start_server(h5, server_log)
    time.sleep(1)

    # Start background traffic
    start_background_traffic(h1, receiver_ip, background_bw, 20, bg1_log)
    start_background_traffic(h2, receiver_ip, background_bw, 20, bg2_log)

    # Adjust this if your bottleneck interface name is different
    bottleneck_interface = "s1-eth3"

    # Start queue logger
    start_queue_logger(bottleneck_interface, queue_log)

    # Start controller only in ABM mode
    if mode == "abm":
        start_abm_controller(bottleneck_interface, controller_log)

    # Let background traffic stabilize
    time.sleep(3)

    # Launch incast short flows
    run_incast([h1, h2, h3, h4], receiver_ip, 1000000, fct_csv, mode)

    # Wait for flows to complete
    time.sleep(10)

    print(f"{mode.upper()} experiment completed.")
    print("Check the results/ folder for CSV and log files.")

    CLI(net)
    net.stop()
    cleanup()


if __name__ == "__main__":
    main()
