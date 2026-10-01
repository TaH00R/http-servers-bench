#include <arpa/inet.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <unistd.h>

#define BUFFER_SIZE 4096
#define PORT 8081
#define BACKLOG 4096

int main() {
    char buffer[BUFFER_SIZE];

    /*
     * Ignore SIGPIPE.
     *
     * This can happen when a client disconnects before
     * we finish sending the response.
     */
    signal(SIGPIPE, SIG_IGN);

    // HTTP response
    // Keep this exactly the same across all servers
    const char resp[] =
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 13\r\n"
        "Connection: close\r\n"
        "\r\n"
        "Hello World!\n";

    // Creating the socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);

    /*
     * AF_INET -> IPv4 protocols
     * SOCK_STREAM -> TCP socket
     */
    if (sockfd == -1) {
        perror("webserver (socket)");
        return 1;
    }

    // Allow the server to reuse the address after restarting
    int opt = 1;

    if (setsockopt(
        sockfd,
        SOL_SOCKET,
        SO_REUSEADDR,
        &opt,
        sizeof(opt)
    ) < 0) {
        perror("webserver (setsockopt)");
        close(sockfd);
        return 1;
    }

    // Creating a Binding Address for the socket
    struct sockaddr_in host_addr = {};
    struct sockaddr_in client_addr;

    socklen_t host_addrlen = sizeof(host_addr);
    socklen_t client_addrlen = sizeof(client_addr);

    host_addr.sin_family = AF_INET;
    host_addr.sin_port = htons(PORT);
    host_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    // Binding the socket to the address
    if (bind(
        sockfd,
        (struct sockaddr *)&host_addr,
        host_addrlen
    ) != 0) {
        perror("webserver (bind)");
        close(sockfd);
        return 1;
    }

    // Start listening for incoming connections
    // Use the same backlog in every language
    if (listen(sockfd, BACKLOG) != 0) {
        perror("webserver (listen)");
        close(sockfd);
        return 1;
    }

    printf("C server listening on port %d\n", PORT);

    for (;;) {

        // Reset the client address length before every accept
        client_addrlen = sizeof(client_addr);

        // Accept an incoming connection
        int newsockfd = accept(
            sockfd,
            (struct sockaddr *)&client_addr,
            &client_addrlen
        );

        if (newsockfd < 0) {
            continue;
        }

        // Disable Nagle's algorithm for the client connection
        int tcp_nodelay = 1;

        setsockopt(
            newsockfd,
            IPPROTO_TCP,
            TCP_NODELAY,
            &tcp_nodelay,
            sizeof(tcp_nodelay)
        );

        // Read the HTTP request
        ssize_t valread = read(
            newsockfd,
            buffer,
            BUFFER_SIZE - 1
        );

        if (valread > 0) {

            // Send the fixed HTTP response
            ssize_t valwrite = write(
                newsockfd,
                resp,
                strlen(resp)
            );

            // Ignore failed sends caused by a disconnected client
            (void)valwrite;
        }

        // Close the connection after one request
        close(newsockfd);
    }

    close(sockfd);

    return 0;
}