#ifndef INCLUDED_HTTP_TCPSERVER
#define INCLUDED_HTTP_TCPSERVER

#include <string>
#include <sys/socket.h>
#include <netinet/in.h>

namespace http {

class TcpServer {
public:

    TcpServer(const std::string& ip_address, int port);
    ~TcpServer();

    // Start accepting connections
    void run();

private:

    std::string m_ip_address;
    int m_port;

    // Main listening socket
    int m_socket;

    // Socket for the current client
    int m_new_socket;

    // Address information for the server
    sockaddr_in m_socketAddress;
    socklen_t m_socketAddress_len;

    // HTTP response sent to every client
    std::string m_serverMessage;

    // Start the server socket
    int startServer();

    // Close open sockets
    void closeServer();

    // Build the fixed HTTP response
    std::string buildResponse();
};

}

#endif