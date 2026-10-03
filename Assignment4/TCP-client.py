"""File Overview
Description:
Sends a TCP time request to the server. Upon receiving a response, it
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
This code was reviewed by Warren Tan to ensure intended functionality.
"""

import socket
import sys
from datetime import datetime, timezone

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# returns the given time argument in UTC with millisecond precision.
# format: {YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}.
def formatTime(dt: datetime) -> str:
    # current time in string format
    currentTime = dt.strftime("%Y-%m-%dT%H:%M:%S.")

    # milliseconds
    milliseconds = dt.microsecond // 1000
    return currentTime + f"{milliseconds:03d}Z"

def main() -> None:
    # confirm number of arguments
    if len(sys.argv) != 3:
        print("Usage: python TCP-client.py <server-IP-address> <server-port-number>")
        sys.exit(1)
    
    # server IP address
    host = sys.argv[1]
    
    # validate port argument
    try:
        port = int(sys.argv[2])
        if not 0 < port < 65536:
            raise ValueError
    except ValueError:
        print("Error: port must be an integer between 1 and 65535.")
        sys.exit(1)

    # send request to server
    try:
        # create connectionwith server at IP=host and port=port
        # spend 5 seconds before returning a socket timeout error
        with socket.create_connection((host, port), timeout=5) as sock:
            # time request was sent
            t_send = datetime.now(timezone.utc)          # local time at request
            
            # HTTP request
            sock.sendall(b"TIME_REQUEST")
            
            # received data
            data = sock.recv(1024)
            
            # time data was received
            t_recv = datetime.now(timezone.utc)          # local time at response
    
    # catch socket timeouts
    except (OSError, socket.timeout) as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    if not data:
        print("Error: server closed the connection without a response.")
        sys.exit(1)

    # decode utf-8 encoded data
    server_str = data.decode("utf-8").strip()
    
    # output server time
    try:
        server_time = datetime.strptime(server_str, TIME_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: could not parse server timestamp {server_str!r}")
        sys.exit(1)
    
    # converts seconds to milliseconds
    ms = lambda td: td.total_seconds() * 1000
    
    # server-to-client delay
    server_client = ms(t_recv - server_time)
    
    # time between request and receive
    rtt = ms(t_recv - t_send)

    # client-to-server delay
    client_server = ms(server_time - t_send)

    # print information
    print(f"Server timestamp : {server_str}")
    print(f"Local time       : {formatTime(t_recv)}")
    print(f"Round-trip time  : {rtt:.3f} ms")
    print(f"Server-Client    : {server_client:.3f} ms (local receive time - server time)")
    print(f"Client-Server    : {client_server:+.3f} ms (server time - local send time)")


if __name__ == "__main__":
    main()
