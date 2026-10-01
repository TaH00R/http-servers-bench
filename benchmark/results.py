import csv
import json

from config import (
    RESULTS_FILE,
    SUMMARY_FILE
)


FIELDS = [

    "language",

    "threads",

    "connections",

    "run",

    "status",

    "startup_ms",

    "requests_per_sec",

    "latency",

    "p50",

    "p75",

    "p90",

    "p95",

    "p99",

    "avg_cpu",

    "peak_cpu",

    "avg_memory_mb",

    "peak_memory_mb"
]


def save_results(results):

    with open(
        RESULTS_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )


        writer.writeheader()

        writer.writerows(
            results
        )


    print(
        f"\nResults saved to:"
    )

    print(
        RESULTS_FILE
    )


def load_results():

    with open(
        RESULTS_FILE,
        newline=""
    ) as file:

        return list(
            csv.DictReader(file)
        )


def generate_summary(results):

    summary = {}


    languages = sorted(
        set(
            row["language"]
            for row in results
        )
    )


    for language in languages:

        successful = [

            row

            for row in results

            if (
                row["language"]
                == language
            )

            and (
                row["status"]
                == "SUCCESS"
            )
        ]


        if not successful:
            continue


        throughput = [

            float(
                row["requests_per_sec"]
            )

            for row in successful
        ]


        cpu = [

            float(
                row["avg_cpu"]
            )

            for row in successful
        ]


        memory = [

            float(
                row["peak_memory_mb"]
            )

            for row in successful
        ]


        startup = [

            float(
                row["startup_ms"]
            )

            for row in successful
        ]


        summary[language] = {

            "tests_completed":
                len(successful),

            "average_requests_per_sec":
                sum(throughput)
                /
                len(throughput),

            "average_cpu_percent":
                sum(cpu)
                /
                len(cpu),

            "average_peak_memory_mb":
                sum(memory)
                /
                len(memory),

            "average_startup_ms":
                sum(startup)
                /
                len(startup)
        }


    with open(
        SUMMARY_FILE,
        "w"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4
        )