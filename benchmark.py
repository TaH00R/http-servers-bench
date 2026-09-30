import matplotlib.pyplot as plt
import csv
import os
import re
import signal
import socket
import subprocess
import time

# Automation Service to Run Tests for all Servers
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVERS = {
    "C": {
        "directory": os.path.join(ROOT, "http-servers-bench", "servers", "c"),
        "build": ["gcc", "-O2", "main.c", "-o", "server"],
        "run": ["./server"],
    },
    "C++": {
        "directory": os.path.join(ROOT, "http-servers-bench", "servers", "cpp"),
        "build": [
            "g++",
            "-O2",
            "-std=c++17",
            "main.cpp",
            "server.cpp",
            "-o",
            "server",
        ],
        "run": ["./server"],
    },
}

HOST = "127.0.0.1"
PORT = 8081

TESTS = [
    {"threads": 1, "connections": 1},
    {"threads": 2, "connections": 10},
    {"threads": 4, "connections": 100},
]

DURATION = "10s"
RUNS = 3

RESULTS_DIR = os.path.join(ROOT, "http-servers-bench", "benchmark", "results")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.csv")


def build_server(name, config):
    print(f"\n[{name}] Building...")

    result = subprocess.run(
        config["build"],
        cwd=config["directory"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(f"Failed to build {name}")

    print(f"[{name}] Build successful")


def start_server(name, config):
    print(f"[{name}] Starting...")

    process = subprocess.Popen(
        config["run"],
        cwd=config["directory"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    wait_for_server()

    print(f"[{name}] Server ready")

    return process


def wait_for_server(timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        try:
            with socket.create_connection((HOST, PORT), timeout=0.2):
                return
        except (ConnectionRefusedError, TimeoutError, OSError):
            time.sleep(0.05)

    raise RuntimeError("Server did not start")


def stop_server(process):
    if process.poll() is None:
        process.terminate()

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def warmup():
    subprocess.run(
        [
            "wrk",
            "-t1",
            "-c1",
            "-d2s",
            f"http://{HOST}:{PORT}/",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def run_benchmark(threads, connections):
    command = [
        "wrk",
        f"-t{threads}",
        f"-c{connections}",
        f"-d{DURATION}",
        f"http://{HOST}:{PORT}/",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    output = result.stdout

    requests_match = re.search(
        r"Requests/sec:\s*([\d.]+)",
        output,
        re.IGNORECASE,
    )

    latency_match = re.search(
        r"Latency\s+([\d.]+)([a-zA-Zµ]+)",
        output,
        re.IGNORECASE,
    )

    if not requests_match:
        raise RuntimeError(
            f"Could not parse wrk output:\n{output}"
        )

    requests_per_sec = float(requests_match.group(1))

    if latency_match:
        latency = (
            f"{latency_match.group(1)}"
            f"{latency_match.group(2)}"
        )
    else:
        latency = ""

    return requests_per_sec, latency


def generate_graph():
    with open(RESULTS_FILE, newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    configurations = []

    for row in rows:
        config = (
            int(row["threads"]),
            int(row["connections"])
        )

        if config not in configurations:
            configurations.append(config)

    languages = sorted(
        set(row["language"] for row in rows)
    )

    averages = {}

    for language in languages:
        averages[language] = []

        for threads, connections in configurations:
            values = [
                float(row["requests_per_sec"])
                for row in rows
                if row["language"] == language
                and int(row["threads"]) == threads
                and int(row["connections"]) == connections
            ]

            averages[language].append(
                sum(values) / len(values)
            )

    x = range(len(configurations))
    width = 0.35

    plt.figure(figsize=(10, 6))

    for i, language in enumerate(languages):
        positions = [
            value + (i - (len(languages) - 1) / 2) * width
            for value in x
        ]

        plt.bar(
            positions,
            averages[language],
            width,
            label=language
        )

    labels = [
        f"{threads}T / {connections}C"
        for threads, connections in configurations
    ]

    plt.xticks(list(x), labels)

    plt.xlabel("Benchmark Configuration")
    plt.ylabel("Requests / Second")
    plt.title("HTTP Server Performance")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    graph_path = os.path.join(
        RESULTS_DIR,
        "requests_per_second.png"
    )

    plt.tight_layout()
    plt.savefig(graph_path, dpi=150)
    plt.close()

    print(f"Graph saved to:")
    print(graph_path)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    results = []

    for name, config in SERVERS.items():
        build_server(name, config)

        for test in TESTS:
            threads = test["threads"]
            connections = test["connections"]

            print(
                f"\n{name}: "
                f"{threads} threads / "
                f"{connections} connections"
            )

            process = start_server(name, config)

            try:
                warmup()

                for run in range(1, RUNS + 1):
                    print(f"  Run {run}/{RUNS}...", end=" ")

                    requests, latency = run_benchmark(
                        threads,
                        connections,
                    )

                    print(f"{requests:.2f} req/s")

                    results.append({
                        "language": name,
                        "threads": threads,
                        "connections": connections,
                        "run": run,
                        "requests_per_sec": requests,
                        "latency": latency,
                    })

            finally:
                stop_server(process)

    with open(
        RESULTS_FILE,
        "w",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "language",
                "threads",
                "connections",
                "run",
                "requests_per_sec",
                "latency",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to:")
    print(RESULTS_FILE)

    generate_graph()



if __name__ == "__main__":
    main()