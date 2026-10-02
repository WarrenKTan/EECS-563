"""File Overview
Description:
Listens for TCP connections. For each request received, replies
with the formatted current UTC timestamp. The file should...
    • Retrieve the current timestamp
    • Construct a response packet containing the timestamp
    • Send the response back to the requesting client using TCP

How to Run:
Run the server application using the following command,
where the local port number is provided as user input:
    python TCP-server.py <server-port-number>

AI Disclosure Statement: 
This code was written on 01 Oct with Claude Sonnet-5.5
https://claude.ai/share/a7532e98-b43a-4e00-8428-50edd4cb578f
This code was reviewed by Warren Tan to ensure intended functionality.
"""

import socket
import sys
from datetime import datetime, timezone

# returns the current time in UTC with millisecond precision.
# format: {YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}.
def utc_timestamp() -> str:
    # returns the current time
    now = datetime.now(timezone.utc)

    # current time in string format
    currentTime = now.strftime("%Y-%m-%dT%H:%M:%S.")

    # milliseconds
    milliseconds = now.microsecond // 1000
    return currentTime + f"{milliseconds:03d}Z"

# receives user request, then sends the current timestamp of the server.
def handle_client(conn: socket.socket, addr) -> None:
    with conn:
        # receive data from the socket (1024 bytes buffer)
        request = conn.recv(1024)
        
        # client has disconnected. Exit handling
        if not request:
            return

        # Stamp as late as possible so it is close to the moment of sending.
        response = utc_timestamp()
        
        # send request through the socket (encoded  in utf-8)
        conn.sendall(response.encode("utf-8"))
        
        # print confirmation message to console
        print(f"[{response}] Served {addr[0]}:{addr[1]} "
              f"(request: {request.decode('utf-8', 'replace').strip()!r})")


def main() -> None:
    # confirm number of arguments
    if len(sys.argv) != 2:
        print("Usage: python TCP-server.py <server-port-number>")
        sys.exit(1)

    # validate port argument
    try:
        port = int(sys.argv[1])
        if not (0 < port and port < 65536):
            raise ValueError
    except ValueError:
        print("Error: port must be an integer between 1 and 65535.")
        sys.exit(1)

    # AF_INET - IPv4
    # SOCK_STREAM - two-way connection byte streams (TCP connection)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # socket settings
        # SOL_SOCKET - general socket level (not protocol-specific)
        # SO_REUSEADDR - reuse the same address when restarting the server
        # 1 - enables settings
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # bind socket to any valid IP address on the host machine
        server.bind(("", port))
        
        # start listening for incoming connections
        # backlog of 5 incoming connections before refusing more connections
        server.listen(5)
        print(f"Time server listening on port {port} (Ctrl+C to stop)")
        
        try:
            while True:
                # accept connection
                conn, addr = server.accept()

                # receive client and send server timestamp back
                try:
                    handle_client(conn, addr)
                except OSError as e:
                    print(f"Error with client {addr}: {e}")

        # shut down server
        except KeyboardInterrupt:
            print("\nServer shutting down.")


if __name__ == "__main__":
    main()
