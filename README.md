# http server benchmark

this project contains small http servers written in different languages so they can be tested under the same kind of workload.

the goal is not to build a production-ready web server. the servers are intentionally simple so the benchmark is mostly about the cost of handling tcp connections and sending a tiny http response.

the current implementations are:

- C
- C++
- Python
- JavaScript / Node.js

more languages can be added later using the same structure.

## how the server works

even though the code looks different in each language, the basic flow is the same:

```text
create socket
    ↓
set socket options
    ↓
bind to ip + port
    ↓
listen for connections
    ↓
accept a client
    ↓
read the http request
    ↓
send the http response
    ↓
close the client connection
    ↓
accept the next client
```

the important part is that all of the implementations follow this same basic idea.

### 1. creating the socket

the first step is creating a tcp socket.

in c and c++ this is done with:

```c
socket(AF_INET, SOCK_STREAM, 0);
```

`AF_INET` means that the server is using ipv4 and `SOCK_STREAM` means tcp.

python and node.js expose the same idea through their own socket apis.

at this point the socket exists, but it is not attached to a port yet.

### 2. setting socket options

the servers use `SO_REUSEADDR` so the program can be restarted without unnecessarily getting stuck because the old socket was recently used.

the client sockets also use `TCP_NODELAY`.

this one is important for the benchmark, so it is explained in more detail below.

### 3. binding the socket

the server binds the socket to:

```text
0.0.0.0:8081
```

`0.0.0.0` means the server listens on the available ipv4 interfaces.

after the bind, the operating system knows that this process owns port `8081`.

### 4. listening

the socket is then changed into a listening socket.

the server uses a backlog of `4096`:

```text
listen(socket, 4096)
```

the backlog is basically the amount of pending connection pressure the operating system is allowed to queue for the listening socket.

using the same value across the implementations is important because otherwise one server could be given a much smaller queue than another one.

### 5. accepting a connection

the server waits in:

```text
accept()
```

when a client connects, `accept()` gives the server a new socket representing that particular client.

the original listening socket stays open so more clients can connect later.

this gives us two different sockets:

```text
listening socket
    └── accepts connections

client socket
    └── talks to one client
```

### 6. reading the request

the client sends something similar to:

```http
get / http/1.1
host: 127.0.0.1:8081
connection: close
```

the server reads the incoming bytes from the client socket.

the benchmark does not need a full http parser because every request is going to receive the same response. the server only needs to receive the request before responding.

this keeps the implementations small and avoids making one language do much more http parsing work than another.

### 7. sending the response

the response is:

```http
http/1.1 200 ok
content-type: text/plain
content-length: 13
connection: close

hello world!
```

the body contains:

```text
hello world!\n
```

which is 13 bytes.

keeping the response identical matters because otherwise we would not really be comparing the same workload.

### 8. closing the connection

after sending the response, the server closes the client socket.

that means the benchmark is currently testing a connection pattern like this:

```text
connect
request
response
close

connect
request
response
close

connect
request
response
close
```

so there can be a huge amount of tcp connection creation and teardown when the concurrency is high.

this is intentional for the current benchmark, but it also means high-connection tests measure more than just the language runtime. they also put a lot of pressure on the operating system's tcp connection handling.

## why the servers are single-threaded

the current servers use one main loop instead of creating a worker thread for every connection.

the basic loop is:

```text
accept
read
write
close
repeat
```

this makes the implementations easier to understand and gives us a simple baseline.

it also means that the benchmark is not measuring a highly optimized production architecture. it is measuring these small server implementations under the same basic architecture.

## nagle's algorithm

nagle's algorithm is a tcp mechanism designed to reduce the number of tiny packets sent over a network.

the problem it tries to solve is pretty simple.

imagine an application repeatedly writes tiny pieces of data:

```text
"a"
"b"
"c"
"d"
```

without any kind of coalescing, those writes can lead to lots of very small tcp segments.

each packet has protocol overhead, so sending a large number of tiny packets is inefficient.

nagle's algorithm tries to reduce this by holding small outgoing pieces of data and combining them when appropriate, especially when earlier data on the connection has not been acknowledged yet.

so conceptually:

```text
without nagle:

"a" → packet
"b" → packet
"c" → packet
"d" → packet
```

with nagle, tcp can instead wait and combine small pieces:

```text
"a" + "b" + "c" + "d"
          ↓
       one larger packet
```

the exact behavior is handled by tcp, not by the http server itself.

the original idea behind nagle's algorithm came from the small-packet congestion problem in tcp networks.

reference: https://www.rfc-editor.org/rfc/rfc896.html

## why we disable nagle here

for this benchmark, the responses are tiny:

```text
hello world!\n
```

we want every implementation to have the same tcp behavior, so the client sockets enable:

```text
tcp_nodelay = 1
```

which disables nagle's algorithm.

in linux, `TCP_NODELAY` tells tcp to disable the nagle algorithm and send outgoing segments without that particular delay mechanism.

reference: https://man7.org/linux/man-pages/man7/tcp.7.html

this does not mean that packets are magically guaranteed to appear on the wire instantly. it simply removes nagle's small-packet delay behavior from the comparison.

that is useful here because otherwise differences in how each language/runtime buffers tiny writes could make the benchmark harder to interpret.

## what this benchmark is actually measuring

the benchmark should be thought of as:

```text
accept connection
        +
receive request
        +
send tiny response
        +
close connection
```

rather than:

```text
"which language is the fastest web server?"
```

there are a lot of things that can affect the numbers:

- operating system scheduling
- tcp connection setup and teardown
- socket backlog
- runtime overhead
- memory usage
- cpu usage
- system load
- client-side benchmarking overhead
- implementation details

that is why keeping the actual server implementations as similar as possible is important.

## benchmark setup

the benchmark uses `wrk` and varies:

```text
threads:
1
2
4
8

connections:
1
10
100
500
1000

runs:
3
```

the benchmark collects:

```text
requests/sec
average latency
p50
p75
p90
p95
p99
cpu usage
memory usage
startup time
```

each server is started, warmed up, tested, and then stopped by the benchmark runner.

## project structure

```text
http-servers-bench/
│
├── servers/
│   ├── c/
│   │   └── main.c
│   │
│   ├── cpp/
│   │   ├── main.cpp
│   │   ├── server.cpp
│   │   └── server.h
│   │
│   ├── python/
│   │   └── server.py
│   │
│   └── javascript/
│       └── server.js
│
├── benchmark/
│   ├── benchmark.py
│   ├── config.py
│   ├── server_manager.py
│   ├── runner.py
│   ├── monitor.py
│   ├── results.py
│   └── graphs.py
│
└── results/
```

## running a server manually

for example, the python server can be started with:

```bash
python servers/python/server.py
```

then it can be tested with:

```bash
curl http://127.0.0.1:8081/
```

the expected response is:

```text
hello world!
```

## a note about the benchmark

high connection counts can create a lot of tcp connection churn because every request currently closes its connection.

that can produce things like `TIME_WAIT` sockets and long latency tails.

this is not necessarily a bug in the language being tested. it is a property of the workload and the server design.

a useful future extension would be to add a second benchmark using http keep-alive, where one tcp connection can carry multiple requests.

that would let us compare:

```text
connection close benchmark
```

against:

```text
persistent connection benchmark
```

which would give a much better picture of how the implementations behave under different kinds of workloads.
