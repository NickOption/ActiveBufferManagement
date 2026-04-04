#!/usr/bin/env python3

"""
shortflow_client.py

This client sends a fixed number of bytes to the server and measures
flow completion time (FCT) as the elapsed time from connect/start-send
until the acknowledgement is received.

Usage example:
python3 shortflow_client.py 10.0.0.5 5001 1048576 h1 flow1 results/fct_results.csv
"""

import socket
import sys
import time
import csv
import os

# Chunk size for sending data
CHUNK_SIZE = 4096


def send_short_flow(server_ip, server_port, flow_size_bytes):
    """
    Send flow_size_bytes to the server and measure completion time.
    Returns the elapsed time in milliseconds.
    """
    payload = b"x" * CHUNK_SIZE
    bytes_remaining = flow_size_bytes

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    start_time = time.time()
    sock.connect((server_ip, server_port))

    while bytes_remaining > 0:
        to_send = min(CHUNK_SIZE, bytes_remaining)
        sock.sendall(payload[:to_send])
        bytes_remaining -= to_send

    # Signal that the client is done sending data
    sock.shutdown(socket.SHUT_WR)

    # Wait for ACK from the server
    _ = sock.recv(16)

    end_time = time.time()
    sock.close()

    # Return FCT in milliseconds
    return (end_time - start_time) * 1000.0


def append_result(csv_path, sender_name, flow_id, flow_size_bytes, fct_ms):
    """
    Append one FCT result row to a CSV file.
    Creates the file and header if it does not already exist.
    """
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["sender", "flow_id", "flow_size_bytes", "fct_ms"])

        writer.writerow([sender_name, flow_id, flow_size_bytes, round(fct_ms, 3)])


def main():
    """
    Read command-line arguments, send a short flow, and log the result.
    """
    if len(sys.argv) != 7:
        print("Usage: python3 shortflow_client.py <server_ip> <server_port> <flow_size_bytes> <sender_name> <flow_id> <csv_path>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    flow_size_bytes = int(sys.argv[3])
    sender_name = sys.argv[4]
    flow_id = sys.argv[5]
    csv_path = sys.argv[6]

    fct_ms = send_short_flow(server_ip, server_port, flow_size_bytes)
    append_result(csv_path, sender_name, flow_id, flow_size_bytes, fct_ms)

    print(f"Flow {flow_id} from {sender_name}: {fct_ms:.3f} ms")


if __name__ == "__main__":
    main()
