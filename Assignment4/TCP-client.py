"""File Overview
Description:
Sends a time request to the server. Upon receiving a response, it
calculates the time difference between the server's time and the
client's local time. The client should establish a connection to the
server on a specified IP address and port, which is received as user input.

How to Run:
Run the server application using the following command, where the
server public IP and local port number is provided as user input:
    python TCP-client.py <server-IP-address> <server-port-number>

AI Disclosure Statement: 
This code was written on 01 Oct with Claude Sonnet-5.5
https://claude.ai/share/a7532e98-b43a-4e00-8428-50edd4cb578f
"""

import socket
import sys
from datetime import datetime, timezone

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python TCP-client.py <server-IP-address> <server-port-number>")
        sys.exit(1)
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
        if not 0 < port < 65536:
            raise ValueError
    except ValueError:
        print("Error: port must be an integer between 1 and 65535.")
        sys.exit(1)

    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            t_send = datetime.now(timezone.utc)          # local time at request
            sock.sendall(b"TIME_REQUEST")
            data = sock.recv(1024)
            t_recv = datetime.now(timezone.utc)          # local time at response
    except (OSError, socket.timeout) as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    if not data:
        print("Error: server closed the connection without a response.")
        sys.exit(1)

    server_str = data.decode("utf-8").strip()
    try:
        server_time = datetime.strptime(server_str, TIME_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: could not parse server timestamp {server_str!r}")
        sys.exit(1)

    ms = lambda td: td.total_seconds() * 1000
    diff = ms(t_recv - server_time)            # local receive time minus server time
    rtt = ms(t_recv - t_send)                  # full round-trip time
    midpoint = t_send + (t_recv - t_send) / 2
    offset = ms(server_time - midpoint)        # NTP-style clock offset estimate

    print(f"Server timestamp : {server_str}")
    print(f"Local time       : {fmt(t_recv)}")
    print(f"Difference       : {diff:.3f} ms (local receive time - server time)")
    print(f"Round-trip time  : {rtt:.3f} ms")
    print(f"Clock offset     : {offset:+.3f} ms (server - local, RTT-compensated)")


if __name__ == "__main__":
    main()
