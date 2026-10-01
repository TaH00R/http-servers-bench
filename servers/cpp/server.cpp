#include "server.h"

#include <arpa/inet.h>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <netinet/tcp.h>
#include <unistd.h>

namespace {

constexpr int BACKLOG = 4096;

void exitWithError(const std::string& errorMessage) {
    std::cerr << "ERROR: " << errorMessage << std::endl;
    std::exit(EXIT_FAILURE);
}

}

namespace http {

TcpServer::TcpServer(const std::string& ip_address, int port)
    : m_ip_address(ip_address),
      m_port(port),
      m_socket(-1),
      m_new_socket(-1),
      m_socketAddress{},
      m_socketAddress_len(sizeof(m_socketAddress)),
      m_serverMessage(buildResponse())
{
    startServer();
}

TcpServer::~TcpServer() {
    closeServer();
}

int TcpServer::startServer() {

    // Creating the socket
    m_socket = socket(AF_INET, SOCK_STREAM, 0);

    /*
     * AF_INET -> IPv4 protocols
     * SOCK_STREAM -> TCP socket
     */
    if (m_socket < 0) {
        exitWithError("Cannot create socket");
    }

    // Allow the server to reuse the address after restarting
    int opt = 1;

    if (setsockopt(
        m_socket,
        SOL_SOCKET,
        SO_REUSEADDR,
        &opt,
        sizeof(opt)
    ) < 0) {
        exitWithError("Cannot set socket options");
    }

    // Creating a Binding Address for the socket
    m_socketAddress.sin_family = AF_INET;
    m_socketAddress.sin_port = htons(m_port);

    // Convert the IP address from text to binary form
    if (inet_pton(
        AF_INET,
        m_ip_address.c_str(),
        &m_socketAddress.sin_addr
    ) <= 0) {
        exitWithError("Invalid IP address");
    }

    // Bind the socket to the requested address
    if (bind(
        m_socket,
        reinterpret_cast<sockaddr*>(&m_socketAddress),
        m_socketAddress_len
    ) < 0) {
        exitWithError("Cannot bind socket");
    }

    // Start listening for incoming connections
    // Keep the same backlog as the other servers
    if (listen(m_socket, BACKLOG) < 0) {
        exitWithError("Cannot listen on socket");
    }

    std::cout
        << "C++ server listening on "
        << m_ip_address
        << ":"
        << m_port
        << std::endl;

    return 0;
}

void TcpServer::run() {

    while (true) {

        /*
         * Keep the client address separate from the server
         * address. accept() can modify the address structure.
         */
        sockaddr_in clientAddress{};
        socklen_t clientAddressLen = sizeof(clientAddress);

        // Accept an incoming connection
        m_new_socket = accept(
            m_socket,
            reinterpret_cast<sockaddr*>(&clientAddress),
            &clientAddressLen
        );

        if (m_new_socket < 0) {
            continue;
        }

        // Disable Nagle's algorithm for this client
        int tcp_nodelay = 1;

        setsockopt(
            m_new_socket,
            IPPROTO_TCP,
            TCP_NODELAY,
            &tcp_nodelay,
            sizeof(tcp_nodelay)
        );

        // Buffer for the HTTP request
        char buffer[4096];

        // Read the HTTP request
        ssize_t bytesReceived = recv(
            m_new_socket,
            buffer,
            sizeof(buffer) - 1,
            0
        );

        if (bytesReceived > 0) {

            buffer[bytesReceived] = '\0';

            // Send the fixed HTTP response
            ssize_t bytesSent = send(
                m_new_socket,
                m_serverMessage.c_str(),
                m_serverMessage.size(),
                0
            );

            // Client may have disconnected before the send completed
            (void)bytesSent;
        }

        // Close the connection after one request
        close(m_new_socket);

        m_new_socket = -1;
    }
}

std::string TcpServer::buildResponse() {

    const std::string body = "Hello World!\n";

    // HTTP response
    return
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: " + std::to_string(body.size()) + "\r\n"
        "Connection: close\r\n"
        "\r\n" +
        body;
}

void TcpServer::closeServer() {

    if (m_new_socket >= 0) {
        close(m_new_socket);
        m_new_socket = -1;
    }

    if (m_socket >= 0) {
        close(m_socket);
        m_socket = -1;
    }
}

}