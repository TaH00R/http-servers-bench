import os


ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SERVERS_ROOT = os.path.join(
    ROOT,
    "servers"
)


HOST = "127.0.0.1"
PORT = 8081


SERVERS = {

    "C": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "c"
        ),
        "build": [
            "gcc",
            "-O2",
            "main.c",
            "-o",
            "server"
        ],
        "run": [
            "./server"
        ],
    },


    "C++": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "cpp"
        ),
        "build": [
            "g++",
            "-O2",
            "-std=c++17",
            "main.cpp",
            "server.cpp",
            "-o",
            "server"
        ],
        "run": [
            "./server"
        ],
    },


    "Python": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "python"
        ),
        "build": None,
        "run": [
            "python",
            "server.py"
        ],
    },


    "JavaScript": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "javascript"
        ),
        "build": None,
        "run": [
            "node",
            "server.js"
        ],
    },


    "Java": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "java"
        ),
        "build": [
            "javac",
            "Server.java"
        ],
        "run": [
            "java",
            "Server"
        ],
    },
    
        "Go": {
        "directory": os.path.join(
            SERVERS_ROOT,
            "go"
        ),
        "build": [
            "go",
            "build",
            "-o",
            "server",
            "server.go"
        ],
        "run": [
            "./server"
        ],
    },
}


THREADS = [
    1,
    2,
    4,
    8
]


CONNECTIONS = [
    1,
    10,
    100,
    500,
    1000
]


# wrk requires connections >= threads
TESTS = [
    {
        "threads": threads,
        "connections": connections
    }
    for threads in THREADS
    for connections in CONNECTIONS
    if connections >= threads
]


DURATION = "10s"

WARMUP_DURATION = "2s"

RUNS = 3

SERVER_START_TIMEOUT = 5

GRACEFUL_SHUTDOWN_TIMEOUT = 2


RESULTS_DIR = os.path.join(
    ROOT,
    "results"
)

RESULTS_FILE = os.path.join(
    RESULTS_DIR,
    "results.csv"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "summary.json"
)