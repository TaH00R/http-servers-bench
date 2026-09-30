#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define BUFFER_SIZE 1024
#define PORT 8081


int main() {
    char buffer[BUFFER_SIZE];

    // HTTP response
    char resp[] = "HTTP/1.1 200 OK\r\n"
                  "Server: webserver-c\r\n"
                  "Content-Type: text/plain\r\n"
                  "Content-Length: 12\r\n"
                  "Connection: close\r\n"
                  "\r\n"
                  "Hello World!";

    // Creating the socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0); // * socket(domain, type, protocol)

    /*
     * AF_INET -> IPv4 protocols
     * SOCK_STREAM -> TCP socket
     */
    if (sockfd == -1) {
        perror("webserver (socket)");
        return 1;
    }

    printf("socket created successfully\n");

    // Setting socket options (basically allowing the socket to be reused)
    int opt = 1;

    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("webserver (setsockopt)");
        return 1;
    }

    // Creating a Binding Address for the socket
    struct sockaddr_in host_addr; // * Address structure for the host (IPv4)
    socklen_t host_addrlen = sizeof(host_addr); // * Size of the address structure (sockaddr_in)

    // Create client address
    struct sockaddr_in client_addr;
    socklen_t client_addrlen = sizeof(client_addr);

    host_addr.sin_family = AF_INET; // * IPv4 Family Address (always set to AF_INET)
    host_addr.sin_port = htons(PORT); // * Host Port Number (htons converts the port number to network byte order)
    host_addr.sin_addr.s_addr = htonl(INADDR_ANY); // * Host Interface Address

    // Binding the socket to the address (if not obvious)
    if (bind(sockfd, (struct sockaddr *)&host_addr, host_addrlen) != 0) {
        perror("webserver (bind)");
        return 1;
    }

    printf("socket successfully bound to address\n");

    // Listen to Incoming Connections
    if (listen(sockfd, SOMAXCONN) != 0) {

        //* listen(socket, backlog), SOMAXCONN -> Maximum number of connections
        perror("webserver (listen)");
        return 1;
    }

    printf("server listening for connections\n");

    for (;;) {

        // Accept incoming connections
        client_addrlen = sizeof(client_addr);

        int newsockfd = accept(
            sockfd,
            (struct sockaddr *)&client_addr,
            &client_addrlen
        );

        // * accept(socket, address, address_length) -> returns a new socket descriptor for the accepted connection
        if (newsockfd < 0) {
            perror("webserver (accept)");
            continue;
        }

        // Read from the socket
        ssize_t valread = read(newsockfd, buffer, BUFFER_SIZE - 1);

        if (valread < 0) {
            perror("webserver (read)");
            close(newsockfd);
            continue;
        }

        buffer[valread] = '\0';

        // Read the request
        char method[BUFFER_SIZE];
        char uri[BUFFER_SIZE];
        char version[BUFFER_SIZE];

        if (sscanf(buffer, "%1023s %1023s %1023s", method, uri, version) == 3) {

            // Request logging disabled during benchmarking
            // printf("[%s:%u] %s %s %s\n",
            //        inet_ntoa(client_addr.sin_addr),
            //        ntohs(client_addr.sin_port),
            //        method,
            //        version,
            //        uri);
        }

        // Write to the socket
        size_t response_length = strlen(resp);
        ssize_t valwrite = write(newsockfd, resp, response_length);

        if (valwrite < 0) {
            perror("webserver (write)");
            close(newsockfd);
            continue;
        }

        close(newsockfd);
    }

    close(sockfd);

    return 0;
}