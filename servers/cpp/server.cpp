#include "server.h"

#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

namespace {

void log(const std::string& message) {
    std::cout << message << std::endl;
}

void exitWithError(const std::string& errorMessage) {
    log("ERROR: " + errorMessage);
    std::exit(EXIT_FAILURE);
}

}

namespace http {

TcpServer::TcpServer(const std::string& ip_address, int port)
    : m_ip_address(ip_address),
      m_port(port),
      m_socket(-1),
      m_new_socket(-1),
      m_incomingMessage(),
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
    m_socket = socket(AF_INET, SOCK_STREAM, 0);

    if (m_socket < 0) {
        exitWithError("Cannot create socket");
    }

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

    m_socketAddress.sin_family = AF_INET;
    m_socketAddress.sin_port = htons(m_port);

    if (inet_pton(
        AF_INET,
        m_ip_address.c_str(),
        &m_socketAddress.sin_addr
    ) <= 0) {
        exitWithError("Invalid IP address");
    }

    if (bind(
        m_socket,
        reinterpret_cast<sockaddr*>(&m_socketAddress),
        m_socketAddress_len
    ) < 0) {
        exitWithError("Cannot bind socket");
    }

    if (listen(m_socket, 10) < 0) {
        exitWithError("Cannot listen on socket");
    }

    log(
        "Server listening on " +
        m_ip_address +
        ":" +
        std::to_string(m_port)
    );

    return 0;
}

void TcpServer::run() {
    while (true) {
        m_new_socket = accept(
            m_socket,
            reinterpret_cast<sockaddr*>(&m_socketAddress),
            &m_socketAddress_len
        );

        if (m_new_socket < 0) {
            log("ERROR: Cannot accept connection");
            continue;
        }

        char buffer[4096];

        ssize_t bytesReceived = recv(
            m_new_socket,
            buffer,
            sizeof(buffer) - 1,
            0
        );

        if (bytesReceived > 0) {
            buffer[bytesReceived] = '\0';
            m_incomingMessage = buffer;

            log("Request received:");
            log(m_incomingMessage);

            send(
                m_new_socket,
                m_serverMessage.c_str(),
                m_serverMessage.size(),
                0
            );
        }

        close(m_new_socket);
        m_new_socket = -1;
    }
}

std::string TcpServer::buildResponse() {
    const std::string body = "Hello World!\n";

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