const net = require("net");

const HOST = "0.0.0.0";
const PORT = 8081;

const body = "Hello World!\n";

const response =
    "HTTP/1.1 200 OK\r\n" +
    "Content-Type: text/plain\r\n" +
    `Content-Length: ${Buffer.byteLength(body)}\r\n` +
    "Connection: close\r\n" +
    "\r\n" +
    body;

const server = net.createServer((socket) => {
    socket.setNoDelay(true);

    socket.on("error", () => {
        // Client may disconnect before we finish writing.
        // Ignore the socket error for this benchmark.
    });

    socket.once("data", () => {
        socket.end(response);
    });
});

server.on("error", (error) => {
    console.error("Server error:", error);
    process.exit(1);
});

server.listen(PORT, HOST, () => {
    console.log(`JavaScript server listening on ${HOST}:${PORT}`);
});