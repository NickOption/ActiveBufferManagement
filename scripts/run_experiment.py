#!/usr/bin/env python3

"""
run_experiment.py

Automates a simple ABM replication experiment in Mininet.

Experiment flow:
1. Start short-flow server on receiver
2. Start background traffic
3. Optionally start ABM-inspired controller
4. Launch multiple short-flow clients at nearly the same time (incast)
5. Log FCT results to CSV

This script is designed to be run from inside Mininet using host.cmd().
"""

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import OVSBridge
import time
import os
import sys

# Import topology from your custom topology file
sys.path.append("topo")
from abm_topo import ABMTopo


def start_server(receiver):
    """
    Start the short-flow server in the background on the receiver host.
    """
    receiver.cmd("pkill -f shortflow_server.py")
    receiver.cmd("python3 scripts/shortflow_server.py > results/server.log 2>&1 &")


def start_background_traffic(sender, receiver_ip, bandwidth="8M", duration=30):
    """
    Start one background traffic flow using iperf3.
    """
    sender.cmd(f"./scripts/background_traffic.sh {receiver_ip} {bandwidth} {duration} > results/background_{sender.name}.log 2>&1 &")


def start_queue_logger(switch_interface):
    """
    Start queue logging on the Mininet root namespace.
    """
    os.system(f"python3 scripts/queue_logger.py {switch_interface} results/queue_log.csv 0.1 > /dev/null 2>&1 &")


def start_abm_controller(switch_interface):
    """
    Start the ABM-inspired controller on the specified interface.
    """
    os.system(f"python3 controller/abm_controller.py {switch_interface} 0.1 > results/abm_controller.log 2>&1 &")


def run_incast(senders, receiver_ip, flow_size=500000):
    """
    Trigger multiple short flows at nearly the same time to create an incast-style burst.
    """
    flow_id = 0
    for host in senders:
        host.cmd(
            f"python3 scripts/shortflow_client.py {receiver_ip} 5001 {flow_size} "
            f"{host.name} flow{flow_id} results/fct_results.csv > results/{host.name}_flow.log 2>&1 &"
        )
        flow_id += 1


def cleanup():
    """
    Kill background Python processes from earlier runs.
    """
    os.system("pkill -f shortflow_server.py")
    os.system("pkill -f queue_logger.py")
    os.system("pkill -f abm_controller.py")
    os.system("pkill -f shortflow_client.py")
    os.system("pkill -f iperf3")


def main():
    """
    Build the Mininet topology, run one experiment, then drop to CLI if needed.
    """
    cleanup()

    # Use OVSBridge and no controller because this experiment does not
    # require an OpenFlow controller.
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

    # Receiver IP
    receiver_ip = h5.IP()

    # Start short-flow server on the receiver
    start_server(h5)
    time.sleep(1)

    # Start one or more background traffic sources
    start_background_traffic(h1, receiver_ip, bandwidth="4M", duration=20)
    start_background_traffic(h2, receiver_ip, bandwidth="4M", duration=20)

    # Start queue logger on a likely bottleneck interface
    # You may need to adjust this interface after checking Mininet link names.
    start_queue_logger("s1-eth3")

    # Optional: enable ABM controller
    # Comment this out for baseline runs.
    start_abm_controller("s1-eth3")

    # Let background traffic stabilize
    time.sleep(3)

    # Trigger incast-style short flows
    run_incast([h1, h2, h3, h4], receiver_ip, flow_size=500000)

    # Wait for flows to finish
    time.sleep(10)

    print("Experiment completed. Check results/ directory for logs and CSV files.")

    CLI(net)
    net.stop()
    cleanup()


if __name__ == "__main__":
    main()
