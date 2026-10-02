#!/usr/bin/env python3
"""UDP time server.

Usage: python UDP-server.py <server-port-number>

Waits for UDP datagrams. For each request received, replies to the sender
with the current UTC timestamp, e.g. "2024-09-28T12:34:56.789Z".
"""
import socket
import sys
from datetime import datetime, timezone


def utc_timestamp() -> str:
    """Current UTC time as an ISO-8601 string with millisecond precision."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python UDP-server.py <server-port-number>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        if not 0 < port < 65536:
            raise ValueError
    except ValueError:
        print("Error: port must be an integer between 1 and 65535.")
        sys.exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(("", port))  # all interfaces
        print(f"UDP time server listening on port {port} (Ctrl+C to stop)")
        try:
            while True:
                request, addr = server.recvfrom(1024)
                # Stamp as late as possible so it is close to the moment of sending.
                response = utc_timestamp()
                server.sendto(response.encode("utf-8"), addr)
                print(f"[{response}] Served {addr[0]}:{addr[1]} "
                      f"(request: {request.decode('utf-8', 'replace').strip()!r})")
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        except OSError as e:
            print(f"Socket error: {e}")


if __name__ == "__main__":
    main()
