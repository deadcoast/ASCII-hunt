"""Performance Monitor Module.

This module provides a performance monitoring mechanism for the application.
It allows tracking execution time, memory usage, and other metrics for
various operations in the system.
"""

import time
from typing import Any


class PerformanceMonitor:
    """A class for monitoring performance of operations.

    This class provides methods for measuring execution time, tracking
    memory usage, and collecting other performance-related metrics for
    various operations in the system.
    """

    def __init__(self) -> None:
        """Initialize the PerformanceMonitor class."""
        self.metrics: dict[str, Any] = {
            "execution_time": 0.0,
            "calls": 0,
            "avg_execution_time": 0.0,
            "min_execution_time": float("inf"),
            "max_execution_time": 0.0,
            "timestamps": [],
            "custom_metrics": {},
        }
        self.start_time: float | None = None
        self.is_running = False

    def start(self) -> None:
        """Start the performance monitor."""
        self.start_time = time.time()
        self.is_running = True

    def stop(self) -> float:
        """Stop the performance monitor and return the elapsed time.

        Returns:
            The elapsed time in seconds.
        """
        if not self.is_running or self.start_time is None:
            return 0.0

        elapsed_time = time.time() - self.start_time
        self.metrics["execution_time"] += elapsed_time
        self.metrics["calls"] += 1
        self.metrics["timestamps"].append(time.time())

        # Update min/max/avg
        self.metrics["min_execution_time"] = min(
            self.metrics["min_execution_time"], elapsed_time
        )
        self.metrics["max_execution_time"] = max(
            self.metrics["max_execution_time"], elapsed_time
        )

        self.metrics["avg_execution_time"] = (
            self.metrics["execution_time"] / self.metrics["calls"]
        )

        self.is_running = False
        self.start_time = None

        return elapsed_time

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            "execution_time": 0.0,
            "calls": 0,
            "avg_execution_time": 0.0,
            "min_execution_time": float("inf"),
            "max_execution_time": 0.0,
            "timestamps": [],
            "custom_metrics": {},
        }
        self.start_time = None
        self.is_running = False

    def add_custom_metric(self, name: str, value: Any) -> None:
        """Add a custom metric.

        Args:
            name: The name of the metric.
            value: The value of the metric.
        """
        if name not in self.metrics["custom_metrics"]:
            self.metrics["custom_metrics"][name] = []

        self.metrics["custom_metrics"][name].append(value)

    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics.

        Returns:
            A dictionary containing all metrics.
        """
        return self.metrics
