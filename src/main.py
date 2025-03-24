def register_hunt_processor(pipeline):
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
