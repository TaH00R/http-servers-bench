import os
import re

import matplotlib.pyplot as plt

from config import (
    THREADS,
    CONNECTIONS,
    RESULTS_DIR
)


def generate_throughput_graphs(
    rows,
    languages
):

    for thread_count in THREADS:

        plt.figure(
            figsize=(12, 7)
        )


        x = list(
            range(
                len(CONNECTIONS)
            )
        )


        width = (
            0.8
            /
            len(languages)
        )


        for i, language in enumerate(
            languages
        ):

            values = []


            for connection_count in CONNECTIONS:

                runs = [

                    float(
                        row[
                            "requests_per_sec"
                        ]
                    )

                    for row in rows

                    if (
                        row["language"]
                        == language
                    )

                    and (
                        int(
                            row["threads"]
                        )
                        == thread_count
                    )

                    and (
                        int(
                            row["connections"]
                        )
                        == connection_count
                    )
                ]


                values.append(

                    sum(runs)
                    /
                    len(runs)

                    if runs

                    else 0
                )


            positions = [

                value
                - 0.4
                + width / 2
                + i * width

                for value in x
            ]


            plt.bar(
                positions,
                values,
                width,
                label=language
            )


        plt.xticks(
            x,
            [
                str(value)
                for value in CONNECTIONS
            ]
        )


        plt.xlabel(
            "Concurrent Connections"
        )

        plt.ylabel(
            "Requests / Second"
        )


        plt.title(
            f"HTTP Throughput - "
            f"{thread_count} Threads"
        )


        plt.legend()

        plt.grid(
            axis="y",
            alpha=0.3
        )


        path = os.path.join(

            RESULTS_DIR,

            f"throughput_"
            f"{thread_count}"
            f"_threads.png"
        )


        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()


def generate_cpu_graphs(
    rows,
    languages
):

    for thread_count in THREADS:

        plt.figure(
            figsize=(12, 7)
        )


        for language in languages:

            x_values = []

            y_values = []


            for connection_count in CONNECTIONS:

                values = [

                    float(
                        row["avg_cpu"]
                    )

                    for row in rows

                    if (
                        row["language"]
                        == language
                    )

                    and (
                        int(
                            row["threads"]
                        )
                        == thread_count
                    )

                    and (
                        int(
                            row["connections"]
                        )
                        == connection_count
                    )
                ]


                if values:

                    x_values.append(
                        connection_count
                    )

                    y_values.append(

                        sum(values)
                        /
                        len(values)
                    )


            if x_values:

                plt.plot(

                    x_values,

                    y_values,

                    marker="o",

                    label=language
                )


        plt.xlabel(
            "Concurrent Connections"
        )

        plt.ylabel(
            "Average CPU Usage (%)"
        )


        plt.title(
            f"CPU Usage - "
            f"{thread_count} Threads"
        )


        plt.legend()

        plt.grid(
            alpha=0.3
        )


        path = os.path.join(

            RESULTS_DIR,

            f"cpu_"
            f"{thread_count}"
            f"_threads.png"
        )


        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()


def generate_memory_graphs(
    rows,
    languages
):

    for thread_count in THREADS:

        plt.figure(
            figsize=(12, 7)
        )


        for language in languages:

            x_values = []

            y_values = []


            for connection_count in CONNECTIONS:

                values = [

                    float(
                        row[
                            "peak_memory_mb"
                        ]
                    )

                    for row in rows

                    if (
                        row["language"]
                        == language
                    )

                    and (
                        int(
                            row["threads"]
                        )
                        == thread_count
                    )

                    and (
                        int(
                            row["connections"]
                        )
                        == connection_count
                    )
                ]


                if values:

                    x_values.append(
                        connection_count
                    )

                    y_values.append(

                        sum(values)
                        /
                        len(values)
                    )


            if x_values:

                plt.plot(

                    x_values,

                    y_values,

                    marker="o",

                    label=language
                )


        plt.xlabel(
            "Concurrent Connections"
        )

        plt.ylabel(
            "Peak Memory (MB)"
        )


        plt.title(
            f"Memory Usage - "
            f"{thread_count} Threads"
        )


        plt.legend()

        plt.grid(
            alpha=0.3
        )


        path = os.path.join(

            RESULTS_DIR,

            f"memory_"
            f"{thread_count}"
            f"_threads.png"
        )


        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()


def generate_latency_graphs(
    rows,
    languages
):

    def to_microseconds(value):

        if not value:
            return None


        match = re.match(
            r"([\d.]+)"
            r"([a-zA-Zµ]+)",
            value
        )


        if not match:
            return None


        number = float(
            match.group(1)
        )

        unit = match.group(2)


        if unit == "ns":
            return number / 1000

        if unit in ("us", "µs"):
            return number

        if unit == "ms":
            return number * 1000

        if unit == "s":
            return number * 1_000_000


        return None


    for thread_count in THREADS:

        plt.figure(
            figsize=(12, 7)
        )


        for language in languages:

            x_values = []

            y_values = []


            for connection_count in CONNECTIONS:

                values = []


                for row in rows:

                    if (
                        row["language"]
                        != language
                    ):
                        continue


                    if (
                        int(row["threads"])
                        != thread_count
                    ):
                        continue


                    if (
                        int(row["connections"])
                        != connection_count
                    ):
                        continue


                    latency = (
                        to_microseconds(
                            row["latency"]
                        )
                    )


                    if latency is not None:

                        values.append(
                            latency
                        )


                if values:

                    x_values.append(
                        connection_count
                    )

                    y_values.append(

                        sum(values)
                        /
                        len(values)
                    )


            if x_values:

                plt.plot(

                    x_values,

                    y_values,

                    marker="o",

                    label=language
                )


        plt.xlabel(
            "Concurrent Connections"
        )

        plt.ylabel(
            "Average Latency (µs)"
        )


        plt.title(
            f"Latency - "
            f"{thread_count} Threads"
        )


        plt.legend()

        plt.grid(
            alpha=0.3
        )


        path = os.path.join(

            RESULTS_DIR,

            f"latency_"
            f"{thread_count}"
            f"_threads.png"
        )


        plt.tight_layout()

        plt.savefig(
            path,
            dpi=150
        )

        plt.close()