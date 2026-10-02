#!/usr/bin/env python3
"""UDP time client.

Usage: python UDP-client.py <server-IP-address> <server-port-number>

Sends a time request datagram to the server, then prints the server's
timestamp, the local time, and the difference in milliseconds.
"""
import socket
import sys
from datetime import datetime, timezone

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
TIMEOUT_SECONDS = 5


def fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python UDP-client.py <server-IP-address> <server-port-number>")
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
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # UDP is unreliable: without a timeout, a lost datagram would hang forever.
            sock.settimeout(TIMEOUT_SECONDS)
            t_send = datetime.now(timezone.utc)          # local time at request
            sock.sendto(b"TIME_REQUEST", (host, port))
            data, _ = sock.recvfrom(1024)
            t_recv = datetime.now(timezone.utc)          # local time at response
    except socket.timeout:
        print(f"Error: no response from {host}:{port} within {TIMEOUT_SECONDS}s "
              "(the datagram may have been lost, or the server is not running).")
        sys.exit(1)
    except OSError as e:
        print(f"Socket error: {e}")
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
