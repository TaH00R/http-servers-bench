const net = require("net");

const HOST = "0.0.0.0";
const PORT = 8081;

const BACKLOG = 4096;

// HTTP response
// Keep this exactly the same as the other servers
const body = "Hello World!\n";

const response =
    "HTTP/1.1 200 OK\r\n" +
    "Content-Type: text/plain\r\n" +
    "Content-Length: 13\r\n" +
    "Connection: close\r\n" +
    "\r\n" +
    body;

// Creating the TCP server
const server = net.createServer((socket) => {

    // Disable Nagle's algorithm for this connection
    socket.setNoDelay(true);

    /*
     * The client may disconnect before we finish writing.
     * Ignore that error for the benchmark instead of crashing.
     */
    socket.on("error", () => {});

    // Read the first piece of the HTTP request
    socket.once("data", () => {

        // Send the response and close the connection
        socket.end(response);
    });
});

server.on("error", (error) => {
    console.error("Server error:", error);
    process.exit(1);
});

// Start listening for incoming connections
// Explicitly use the same backlog as the other servers
server.listen({
    host: HOST,
    port: PORT,
    backlog: BACKLOG
}, () => {
    console.log(`JavaScript server listening on port ${PORT}`);
});