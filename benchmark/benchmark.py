import os

from config import (
    SERVERS,
    TESTS,
    RESULTS_DIR
)

from server_manager import (
    build_server
)

from runner import (
    run_test
)

from results import (
    save_results,
    generate_summary
)

from graphs import (
    generate_throughput_graphs,
    generate_latency_graphs,
    generate_cpu_graphs,
    generate_memory_graphs
)


def main():

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )


    print()
    print("=" * 60)
    print("        HTTP SERVER BENCHMARK")
    print("=" * 60)
    print()


    print(
        f"Languages: {len(SERVERS)}"
    )

    print(
        f"Tests: {len(TESTS)}"
    )


    # Build
    build_status = {}


    for name, config in SERVERS.items():

        build_status[name] = (
            build_server(
                name,
                config
            )
        )


    # Run benchmarks
    results = []


    for name, config in SERVERS.items():
        if not build_status[name]:
            print( f"Skipping {name}")
            continue


        for test in TESTS:
            test_results = run_test(
                name,
                config,
                test["threads"],
                test["connections"]
            )


            results.extend(test_results)



    # Save
    save_results(results)


    # Generate graphs
    successful = [
        row for row in results
        if row.get("status") == "SUCCESS"
    ]


    languages = sorted(
        set(row["language"] for row in successful
        )
    )


    print()
    print("Generating graphs...")


    generate_throughput_graphs(
        successful,
        languages
    )


    generate_latency_graphs(
        successful,
        languages
    )


    generate_cpu_graphs(
        successful,
        languages
    )


    generate_memory_graphs(
        successful,
        languages
    )


    # Summary
    generate_summary(results)


    print()
    print("=" * 60)
    print("             BENCHMARK DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()