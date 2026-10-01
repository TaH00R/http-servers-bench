#include "server.h"

#include <csignal>

int main() {

    /*
     * Ignore SIGPIPE.
     *
     * wrk can close a connection while the server is
     * trying to send the response.
     */
    std::signal(SIGPIPE, SIG_IGN);

    http::TcpServer server("0.0.0.0", 8081);

    server.run();

    return 0;
}