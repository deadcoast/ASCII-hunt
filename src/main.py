from typing import Any

from .dsl.hunt_error_handler import HuntErrorHandler
from .dsl.hunt_recognition_processor import HuntRecognitionProcessor
from .dsl.pattern_registry import PatternRegistry


def register_hunt_processor(pipeline: Any) -> HuntRecognitionProcessor:
    """Register the HUNT processor with the processing pipeline."""
    # Create pattern registry
    pattern_registry = PatternRegistry()

    # Create HUNT processor
    hunt_processor = HuntRecognitionProcessor(pattern_registry)

    # Register built-in patterns
    hunt_processor.register_built_in_patterns()

    # Register processor with pipeline
    pipeline.register_processor(hunt_processor, "hunt_recognition")

    # Register error handler
    pipeline.register_error_handler("hunt_recognition", HuntErrorHandler())

    return hunt_processor
