import os
import socket
import subprocess
import time

from config import (
    HOST,
    PORT,
    SERVER_START_TIMEOUT,
    GRACEFUL_SHUTDOWN_TIMEOUT
)


def build_server(name, config):

    if config["build"] is None:

        print(
            f"[{name}] No build step"
        )

        return True


    print(
        f"[{name}] Building..."
    )


    result = subprocess.run(
        config["build"],
        cwd=config["directory"],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        print(result.stdout)
        print(result.stderr)

        print(
            f"[{name}] BUILD FAILED"
        )

        return False


    print(
        f"[{name}] Build successful"
    )

    return True


def wait_for_server(
    timeout=SERVER_START_TIMEOUT
):

    start = time.perf_counter()


    while (
        time.perf_counter() - start
        < timeout
    ):

        try:

            with socket.create_connection(
                (HOST, PORT),
                timeout=0.2
            ):

                return (
                    True,
                    time.perf_counter() - start
                )


        except (
            ConnectionRefusedError,
            TimeoutError,
            OSError
        ):

            time.sleep(0.05)


    return (
        False,
        time.perf_counter() - start
    )


def start_server(name, config):

    print(
        f"[{name}] Starting..."
    )


    start_time = time.perf_counter()


    process = subprocess.Popen(
        config["run"],
        cwd=config["directory"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    ready, wait_time = wait_for_server()


    startup_time = (
        time.perf_counter()
        - start_time
    )


    if not ready:

        print(
            f"[{name}] Failed to start"
        )

        stop_server(process)

        return None, startup_time


    print(
        f"[{name}] Server ready "
        f"({startup_time * 1000:.2f} ms)"
    )


    return process, startup_time


def stop_server(process):

    if process is None:
        return


    if process.poll() is None:

        process.terminate()


        try:

            process.wait(
                timeout=GRACEFUL_SHUTDOWN_TIMEOUT
            )


        except subprocess.TimeoutExpired:

            process.kill()

            process.wait()