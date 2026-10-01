import socket

HOST = "0.0.0.0"
PORT = 8081

BUFFER_SIZE = 4096
BACKLOG = 4096

# HTTP response
# Keep this exactly the same as the other servers
body = b"Hello World!\n"

response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 13\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    + body
)

# Creating the socket
server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Allow the server to reuse the address after restarting
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

# Binding the socket to the address
server.bind((HOST, PORT))

# Start listening for incoming connections
# Keep the same backlog as the other servers
server.listen(BACKLOG)

print(f"Python server listening on port {PORT}")

while True:

    # Accept an incoming connection
    client, address = server.accept()

    try:

        # Disable Nagle's algorithm for this connection
        client.setsockopt(
            socket.IPPROTO_TCP,
            socket.TCP_NODELAY,
            1
        )

        # Read the HTTP request
        request = client.recv(BUFFER_SIZE)

        if request:

            # Send the fixed HTTP response
            client.sendall(response)

    except (BrokenPipeError, ConnectionResetError):

        # The client may have disconnected before we replied
        pass

    finally:

        # Close the connection after one request
        client.close()