import socket

HOST = "0.0.0.0"
PORT = 8081

body = b"Hello World!\n"

response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: " + str(len(body)).encode() + b"\r\n"
    b"Connection: close\r\n"
    b"\r\n" +
    body
)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen(128)

print(f"Python server listening on port {PORT}")

while True:
    client, address = server.accept()

    try:
        client.recv(4096)
        client.sendall(response)
    finally:
        client.close()