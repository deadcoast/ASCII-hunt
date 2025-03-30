"""Main module."""

import sys

from PyQt5.QtWidgets import QApplication

from src.core.recognition.dsl_pattern_registry import PatternRegistry
from src.core.recognition.dsl_recognition_processor import DslRecognitionProcessor
from src.engine.pipeline.processing_pipeline import ProcessingPipeline
from src.interface.api.application_controller import ApplicationController
from src.interface.ui.main_window import MainWindow


def pipeline() -> ProcessingPipeline:
    """Create a processing pipeline."""
    # The pipeline is instantiated directly in the return statement.
    # If PluginManager or TransformationPipeline setup is needed,
    # it should likely happen elsewhere or be passed into the pipeline.
    return ProcessingPipeline()


def register_dsl_processor(pipeline: ProcessingPipeline) -> DslRecognitionProcessor:
    """Register the HUNT processor with the processing pipeline."""
    # Create pattern registry
    pattern_registry = PatternRegistry()

    # Create HUNT processor
    dsl_processor = DslRecognitionProcessor(pattern_registry)

    # Register built-in patterns
    dsl_processor.register_built_in_patterns()

    # Register processor with pipeline
    pipeline.register_processor(dsl_processor, "dsl_recognition")

    # Error handling appears integrated into pipeline.process()

    return dsl_processor


# GUI Application Entry Point
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the main window
    main_win = MainWindow()

    # Create the application controller and link it to the window
    controller = ApplicationController(main_win)

    # Show the main window
    main_win.show()

    # Start the Qt event loop
    sys.exit(app.exec_())
