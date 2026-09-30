#include "server.h"

int main() {
    http::TcpServer server("0.0.0.0", 8081);

    server.run();

    return 0;
}