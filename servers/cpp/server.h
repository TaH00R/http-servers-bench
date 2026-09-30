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

    void run();

private:
    std::string m_ip_address;
    int m_port;

    int m_socket;
    int m_new_socket;

    std::string m_incomingMessage;

    sockaddr_in m_socketAddress;
    socklen_t m_socketAddress_len;

    std::string m_serverMessage;

    int startServer();
    void closeServer();
    std::string buildResponse();
};

}

#endif