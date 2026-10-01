import threading

import psutil


class ProcessMonitor:

    def __init__(self, process):

        self.process = process

        self.cpu_samples = []

        self.memory_samples = []

        self.running = False

        self.thread = None


    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self._monitor,
            daemon=True
        )

        self.thread.start()


    def _monitor(self):

        try:

            process = psutil.Process(
                self.process.pid
            )


            process.cpu_percent(
                interval=None
            )


            while self.running:

                try:

                    cpu = process.cpu_percent(
                        interval=0.1
                    )


                    memory = (
                        process.memory_info().rss
                        /
                        (1024 * 1024)
                    )


                    self.cpu_samples.append(
                        cpu
                    )

                    self.memory_samples.append(
                        memory
                    )


                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied
                ):

                    break


        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied
        ):

            pass


    def stop(self):

        self.running = False

        if self.thread:

            self.thread.join(
                timeout=1
            )


    def average_cpu(self):

        if not self.cpu_samples:
            return 0.0

        return (
            sum(self.cpu_samples)
            /
            len(self.cpu_samples)
        )


    def peak_cpu(self):

        if not self.cpu_samples:
            return 0.0

        return max(
            self.cpu_samples
        )


    def average_memory(self):

        if not self.memory_samples:
            return 0.0

        return (
            sum(self.memory_samples)
            /
            len(self.memory_samples)
        )


    def peak_memory(self):

        if not self.memory_samples:
            return 0.0

        return max(
            self.memory_samples
        )