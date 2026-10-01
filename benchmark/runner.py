import re
import subprocess
from monitor import ProcessMonitor

from config import (
    HOST,
    PORT,
    WARMUP_DURATION,
    DURATION
)


def warmup():

    subprocess.run(
        [
            "wrk",
            "-t1",
            "-c1",
            f"-d{WARMUP_DURATION}",
            f"http://{HOST}:{PORT}/"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def run_benchmark(
    threads,
    connections
):

    command = [
        "wrk",
        "--latency",
        f"-t{threads}",
        f"-c{connections}",
        f"-d{DURATION}",
        f"http://{HOST}:{PORT}/"
    ]


    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        raise RuntimeError(
            f"wrk failed\n\n"
            f"STDOUT:\n"
            f"{result.stdout}\n\n"
            f"STDERR:\n"
            f"{result.stderr}"
        )


    output = result.stdout


    requests_match = re.search(
        r"Requests/sec:\s*([\d.]+)",
        output,
        re.IGNORECASE
    )


    if not requests_match:

        raise RuntimeError(
            "Could not parse Requests/sec\n\n"
            + output
        )


    requests_per_sec = float(
        requests_match.group(1)
    )


    latency_match = re.search(
        r"Latency\s+([\d.]+)([a-zA-Zµ]+)",
        output,
        re.IGNORECASE
    )


    if latency_match:

        latency = (
            f"{latency_match.group(1)}"
            f"{latency_match.group(2)}"
        )

    else:

        latency = ""


    percentiles = {

        "p50": None,
        "p75": None,
        "p90": None,
        "p95": None,
        "p99": None
    }


    patterns = {

        "p50":
            r"50\.000%\s+([\d.]+)([a-zA-Zµ]+)",

        "p75":
            r"75\.000%\s+([\d.]+)([a-zA-Zµ]+)",

        "p90":
            r"90\.000%\s+([\d.]+)([a-zA-Zµ]+)",

        "p95":
            r"95\.000%\s+([\d.]+)([a-zA-Zµ]+)",

        "p99":
            r"99\.000%\s+([\d.]+)([a-zA-Zµ]+)"
    }


    for name, pattern in patterns.items():

        match = re.search(
            pattern,
            output
        )


        if match:

            percentiles[name] = (
                float(match.group(1)),
                match.group(2)
            )


    return {

        "requests_per_sec":
            requests_per_sec,

        "latency":
            latency,

        "p50":
            percentiles["p50"],

        "p75":
            percentiles["p75"],

        "p90":
            percentiles["p90"],

        "p95":
            percentiles["p95"],

        "p99":
            percentiles["p99"]
    }


def format_latency(value):

    if value is None:
        return ""


    number, unit = value


    return (
        f"{number:.2f}"
        f"{unit}"
    )



def run_test(
    language,
    config,
    threads,
    connections
):

    from server_manager import (
        start_server,
        stop_server
    )

    print()
    print("=" * 60)

    print(
        f"{language} | "
        f"{threads} threads | "
        f"{connections} connections"
    )

    print("=" * 60)


    process, startup_time = (
        start_server(
            language,
            config
        )
    )


    if process is None:

        return []


    results = []


    try:

        print("Warmup...")

        warmup()


        from config import RUNS


        for run in range(
            1,
            RUNS + 1
        ):

            if process.poll() is not None:

                print(
                    "SERVER CRASHED"
                )

                results.append({
                    "language": language,
                    "threads": threads,
                    "connections": connections,
                    "run": run,
                    "status": "CRASHED",
                    "startup_ms":
                        startup_time * 1000
                })

                break


            print(
                f"Run {run}/{RUNS}...",
                end=" "
            )


            monitor = ProcessMonitor(
                process
            )

            monitor.start()


            try:

                metrics = run_benchmark(
                    threads,
                    connections
                )


            except Exception as error:

                monitor.stop()

                print(
                    f"FAILED: {error}"
                )

                results.append({
                    "language": language,
                    "threads": threads,
                    "connections": connections,
                    "run": run,
                    "status": "FAILED",
                    "startup_ms":
                        startup_time * 1000
                })

                continue


            monitor.stop()


            print(
                f"{metrics['requests_per_sec']:.2f} "
                f"req/s | "
                f"{metrics['latency']} | "
                f"CPU "
                f"{monitor.average_cpu():.2f}% | "
                f"RAM "
                f"{monitor.peak_memory():.2f} MB"
            )


            results.append({

                "language": language,

                "threads": threads,

                "connections": connections,

                "run": run,

                "status": "SUCCESS",

                "startup_ms":
                    startup_time * 1000,

                "requests_per_sec":
                    metrics[
                        "requests_per_sec"
                    ],

                "latency":
                    metrics[
                        "latency"
                    ],

                "p50":
                    format_latency(
                        metrics["p50"]
                    ),

                "p75":
                    format_latency(
                        metrics["p75"]
                    ),

                "p90":
                    format_latency(
                        metrics["p90"]
                    ),

                "p95":
                    format_latency(
                        metrics["p95"]
                    ),

                "p99":
                    format_latency(
                        metrics["p99"]
                    ),

                "avg_cpu":
                    monitor.average_cpu(),

                "peak_cpu":
                    monitor.peak_cpu(),

                "avg_memory_mb":
                    monitor.average_memory(),

                "peak_memory_mb":
                    monitor.peak_memory()
            })


    finally:

        stop_server(
            process
        )


    return results