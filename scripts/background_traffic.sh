#!/bin/bash

# background_traffic.sh
#
# Starts a simple iperf3 background flow.
# This is used to create steady load before triggering short-flow incast traffic.
#
# Usage:
# ./background_traffic.sh <server_ip> <bandwidth> <duration>
#
# Example:
# ./background_traffic.sh 10.0.0.5 8M 30

SERVER_IP=$1
BANDWIDTH=$2
DURATION=$3

iperf3 -c "$SERVER_IP" -b "$BANDWIDTH" -t "$DURATION"
