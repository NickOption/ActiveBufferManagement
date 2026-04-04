#!/usr/bin/env python3

"""
shortflow_server.py

Simple TCP server used to measure flow completion time (FCT).
It accepts connections from short-flow clients, reads a fixed number
of bytes, and then sends back a small acknowledgement.

This is intentionally lightweight so it is easy to explain in the report.
"""

import socket

# Server bind settings
HOST = "0.0.0.0"
PORT = 5001

# Number of bytes to read per client connection before replying
BUFFER_SIZE = 4096


def handle_client(conn):
    """
    Read all incoming bytes from the client until the client closes
    the sending side of the socket. Then return a small ACK.
    """
    total_bytes = 0

    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        total_bytes += len(data)

    # Send a simple ACK so the client knows the transfer completed
    conn.sendall(b"ACK")
    conn.close()

    print(f"Completed short flow of {total_bytes} bytes")


def main():
    """
    Start a TCP server and handle clients one at a time.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(128)

    print(f"Short-flow server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(conn)


if __name__ == "__main__":
    main()
