"""Processing Pipeline Module.

This module provides a pipeline mechanism for processing data through a sequence
of processors. Each processor in the pipeline can transform the data and pass
it to the next processor.
"""

from collections.abc import Callable
from typing import Any

from src.managers.performance_monitor import PerformanceMonitor


class ProcessingPipeline:
    """A class for managing a pipeline of processors.

    This class provides methods for registering processors, processing data
    through the pipeline, and monitoring performance of each processor.
    """

    def __init__(self) -> None:
        """Initialize the ProcessingPipeline class."""
        self.processors: dict[str, Any] = {}
        self.pipeline_stages: list[str] = []
        self.performance_monitors: dict[str, PerformanceMonitor] = {}
        self.stage_status: dict[str, str] = {}
        self.pre_stage_hooks: dict[str, list[Callable[[Any, dict[str, Any]], None]]] = (
            {}
        )
        self.post_stage_hooks: dict[
            str, list[Callable[[Any, dict[str, Any]], None]]
        ] = {}

    def register_processor(self, processor: Any, stage_name: str) -> None:
        """Register a processor for a specific stage in the pipeline.

        Args:
            processor: The processor object.
            stage_name: The name of the stage.
        """
        self.processors[stage_name] = processor

        if stage_name not in self.pipeline_stages:
            self.pipeline_stages.append(stage_name)

        self.stage_status[stage_name] = "registered"

        # Create a performance monitor for this stage if it doesn't exist
        if stage_name not in self.performance_monitors:
            self.performance_monitors[stage_name] = PerformanceMonitor()

        # Initialize hooks for this stage
        if stage_name not in self.pre_stage_hooks:
            self.pre_stage_hooks[stage_name] = []
        if stage_name not in self.post_stage_hooks:
            self.post_stage_hooks[stage_name] = []

    def register_performance_monitor(
        self, stage_name: str, monitor: PerformanceMonitor
    ) -> None:
        """Register a performance monitor for a specific stage.

        Args:
            stage_name: The name of the stage.
            monitor: The performance monitor object.
        """
        self.performance_monitors[stage_name] = monitor

    def register_pre_stage_hook(
        self, stage_name: str, hook: Callable[[Any, dict[str, Any]], None]
    ) -> None:
        """Register a hook to be called before a stage is processed.

        Args:
            stage_name: The name of the stage.
            hook: The hook function.
        """
        if stage_name not in self.pre_stage_hooks:
            self.pre_stage_hooks[stage_name] = []

        self.pre_stage_hooks[stage_name].append(hook)

    def register_post_stage_hook(
        self, stage_name: str, hook: Callable[[Any, dict[str, Any]], None]
    ) -> None:
        """Register a hook to be called after a stage is processed.

        Args:
            stage_name: The name of the stage.
            hook: The hook function.
        """
        if stage_name not in self.post_stage_hooks:
            self.post_stage_hooks[stage_name] = []

        self.post_stage_hooks[stage_name].append(hook)

    def process(
        self, data: Any, context: dict[str, Any] | None = None
    ) -> tuple[Any, dict[str, Any]]:
        """Process data through the pipeline.

        Args:
            data: The data to process.
            context: The context dictionary to pass to processors.

        Returns:
            A tuple containing the processed data and a dictionary of stage results.
        """
        if context is None:
            context = {}

        stage_results: dict[str, Any] = {}
        result = data

        for stage_name in self.pipeline_stages:
            processor = self.processors.get(stage_name)

            if processor is None:
                continue

            self.stage_status[stage_name] = "running"

            # Call pre-stage hooks
            for hook in self.pre_stage_hooks.get(stage_name, []):
                hook(result, context)

            # Start performance monitoring
            monitor = self.performance_monitors.get(stage_name)
            if monitor:
                monitor.start()

            try:
                # Process data
                stage_result = processor.process(result, context)
                stage_results[stage_name] = stage_result
                result = stage_result
                self.stage_status[stage_name] = "completed"
            except Exception as e:
                self.stage_status[stage_name] = "failed"
                context["error"] = str(e)
                context["error_stage"] = stage_name
                raise
            finally:
                # Stop performance monitoring
                if monitor:
                    elapsed_time = monitor.stop()
                    context[f"{stage_name}_time"] = elapsed_time

            # Call post-stage hooks
            for hook in self.post_stage_hooks.get(stage_name, []):
                hook(result, context)

        return result, stage_results

    def get_stage_status(self, stage_name: str) -> str:
        """Get the status of a specific stage.

        Args:
            stage_name: The name of the stage.

        Returns:
            The status of the stage.
        """
        return self.stage_status.get(stage_name, "unknown")

    def reset(self) -> None:
        """Reset the pipeline."""
        for stage_name in self.stage_status:
            self.stage_status[stage_name] = "registered"

        # Reset all performance monitors
        for monitor in self.performance_monitors.values():
            monitor.reset()
