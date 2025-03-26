class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.metrics = {}

    def start(self):
        """Start performance monitoring."""
        import os
        import time

        import psutil

        self.start_time = time.time()
        self.memory_usage = []

        # Record initial memory usage
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss)

    def end(self):
        """End performance monitoring."""
        import os
        import time

        import psutil

        self.end_time = time.time()

        # Record final memory usage
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss)

        # Calculate metrics
        if self.end_time is not None and self.start_time is not None:
            self.metrics["execution_time"] = self.end_time - self.start_time
        else:
            self.metrics["execution_time"] = (
                0.0  # Default value if timing is incomplete
            )

        self.metrics["memory_increase"] = self.memory_usage[-1] - self.memory_usage[0]

    def get_metrics(self):
        """Get performance metrics."""
        return self.metrics
