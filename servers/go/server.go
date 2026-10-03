package main

import (
	"fmt"
	"net"
)

const (
	HOST        = "0.0.0.0"
	PORT        = 8081
	BUFFER_SIZE = 4096
)

// HTTP response
// Keep this the same as the other servers
var response = []byte(
	"HTTP/1.1 200 OK\r\n" +
		"Content-Type: text/plain\r\n" +
		"Content-Length: 13\r\n" +
		"Connection: close\r\n" +
		"\r\n" +
		"Hello World!\n",
)

func main() {

	// Creating the TCP listening socket
	listener, err := net.Listen(
		"tcp",
		fmt.Sprintf("%s:%d", HOST, PORT),
	)

	if err != nil {
		panic(err)
	}

	defer listener.Close()

	fmt.Printf("Go server listening on port %d\n", PORT)

	for {

		// Accept an incoming connection
		conn, err := listener.Accept()

		if err != nil {
			// Ignore failed accepts and keep the server running
			continue
		}

		handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {

	// Make sure the client connection is closed after one request
	defer conn.Close()

	/*
	 * TCP_NODELAY disables Nagle's algorithm.
	 *
	 * The response is tiny, so we don't want the TCP layer
	 * waiting to combine small packets.
	 */
	if tcpConn, ok := conn.(*net.TCPConn); ok {
		tcpConn.SetNoDelay(true)
	}

	// Buffer for the HTTP request
	buffer := make([]byte, BUFFER_SIZE)

	// Read the HTTP request
	_, err := conn.Read(buffer)

	if err != nil {
		return
	}

	// Send the fixed HTTP response
	_, err = conn.Write(response)

	if err != nil {
		// Client may have disconnected before the response was sent
		return
	}

	// Connection is closed by the defer above
}
