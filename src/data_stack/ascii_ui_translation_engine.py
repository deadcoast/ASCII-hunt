"""ASCII UI Translation Engine Module."""

from managers.cache_manager import CacheManager
from managers.configuration_manager import ConfigurationManager
from managers.extension_point import ExtensionPoint
from managers.performance_monitor import PerformanceMonitor
from managers.plugin_manager import PluginManager
from managers.processing_pipeline import ProcessingPipeline
from processors.code_generation_processor import CodeGenerationProcessor
from processors.component_classification_processor import (
    ComponentClassificationProcessor,
)
from processors.contour_detection_processor import ContourDetectionProcessor
from processors.feature_extraction_processor import FeatureExtractionProcessor
from processors.flood_fill_processor import FloodFillProcessor
from processors.pattern_recognition_processor import PatternRecognitionProcessor
from processors.relationship_analysis_processor import RelationshipAnalysisProcessor

from .ascii_grid import ASCIIGrid


class ASCIIUITranslationEngine:
    def __init__(self):
        # Create core components
        """
        Initialize the ASCII UI Translation Engine with all necessary processing components.

        This constructor sets up the processing pipeline by instantiating
        the following components:
        - FloodFillProcessor for identifying enclosed regions in the ASCII grid.
        - ConnectedComponentAnalyzer for analyzing and grouping connected components.
        - HierarchicalClustering for building component hierarchies.
        - DecisionTreeClassifier for classifying UI components.
        - CodeGenerator for generating code based on recognized components.

        """
        self.plugin_manager = PluginManager()
        self.config_manager = ConfigurationManager()
        self.pipeline = ProcessingPipeline()
        self.cache_manager = CacheManager()

        # Initialize processors
        self.flood_fill_processor = FloodFillProcessor()
        self.contour_detection_processor = ContourDetectionProcessor()
        self.pattern_recognition_processor = PatternRecognitionProcessor()
        self.feature_extraction_processor = FeatureExtractionProcessor()
        self.component_classification_processor = ComponentClassificationProcessor()
        self.relationship_analysis_processor = RelationshipAnalysisProcessor()
        self.code_generation_processor = CodeGenerationProcessor()

        # Initialize performance monitoring
        self.performance_monitors = {
            "flood_fill": PerformanceMonitor(),
            "contour_detection": PerformanceMonitor(),
            "pattern_recognition": PerformanceMonitor(),
            "feature_extraction": PerformanceMonitor(),
            "component_classification": PerformanceMonitor(),
            "relationship_analysis": PerformanceMonitor(),
            "code_generation": PerformanceMonitor(),
        }

        # Register processors with pipeline
        self.pipeline.register_processor(self.flood_fill_processor, "flood_fill")
        self.pipeline.register_processor(
            self.contour_detection_processor, "contour_detection"
        )
        self.pipeline.register_processor(
            self.pattern_recognition_processor, "pattern_recognition"
        )
        self.pipeline.register_processor(
            self.feature_extraction_processor, "feature_extraction"
        )
        self.pipeline.register_processor(
            self.component_classification_processor, "component_classification"
        )
        self.pipeline.register_processor(
            self.relationship_analysis_processor, "relationship_analysis"
        )
        self.pipeline.register_processor(
            self.code_generation_processor, "code_generation"
        )

        # Register performance monitors
        for stage_name, monitor in self.performance_monitors.items():
            self.pipeline.register_performance_monitor(stage_name, monitor)

        # Initialize extension points
        self._init_extension_points()

    def _init_extension_points(self):
        """Initialize extension points."""
        # Create extension points
        ext_points = {
            "pattern_matchers": ExtensionPoint("pattern_matchers"),
            "feature_extractors": ExtensionPoint("feature_extractors"),
            "component_classifiers": ExtensionPoint("component_classifiers"),
            "relationship_analyzers": ExtensionPoint("relationship_analyzers"),
            "code_generators": ExtensionPoint("code_generators"),
        }

        # Register extension points
        for name, ext_point in ext_points.items():
            self.plugin_manager.register_extension_point(name, ext_point)

    def process_ascii_ui(self, ascii_text, options=None):
        """Process ASCII UI text and generate code."""
        if options is None:
            options = {}

        # Create processing context
        context = {
            "options": options,
            "target_framework": options.get("target_framework", "default"),
            "generator_options": options.get("generator_options", {}),
        }

        # Process the ASCII text
        try:
            # Create ASCIIGrid from text
            grid = ASCIIGrid(ascii_text)
            context["grid"] = grid

            # Process through pipeline
            result, stage_results = self.pipeline.process(grid, context)

            # Extract performance metrics
            performance_metrics = {}
            for stage_name, monitor in self.performance_monitors.items():
                performance_metrics[stage_name] = monitor.get_metrics()

            # Prepare response
            response = {
                "success": True,
                "generated_code": (
                    result if isinstance(result, str) else context.get("generated_code")
                ),
                "component_model": context.get("component_model"),
                "performance_metrics": performance_metrics,
            }

            return response

        except Exception as e:
            # Handle errors
            return {"success": False, "error": str(e)}

    def load_plugins(self, plugin_dir):
        """Load plugins from a directory."""
        import os

        # Scan directory for plugin files
        plugin_files = []

        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    plugin_files.append(os.path.join(root, file))

        # Load each plugin
        loaded_plugins = []

        for plugin_file in plugin_files:
            try:
                plugin_name = self.plugin_manager.load_plugin_from_file(plugin_file)
                loaded_plugins.append(plugin_name)
            except Exception as e:
                print(f"Error loading plugin {plugin_file}: {e!s}")

        return loaded_plugins

    def load_config(self, config_path):
        """Load configuration from a file."""
        self.config_manager.load_config(config_path)

    def save_config(self, config_path):
        """Save configuration to a file."""
        self.config_manager.save_config(config_path)

    def get_supported_frameworks(self):
        """Get a list of supported frameworks for code generation."""
        ext_point = self.plugin_manager.get_extension_point("code_generators")

        if ext_point:
            return list(ext_point.get_extensions().keys())
        return ["default"]

    def list_frameworks(self):
        """List all supported frameworks."""
        frameworks = self.get_supported_frameworks()
        print("Supported Frameworks:")
        for idx, framework in enumerate(frameworks, 1):
            print(f"{idx}. {framework}")

    def list_plugins(self):
        """List all available plugins."""
        plugins = self.plugin_manager.get_plugins()
        print("Available Plugins:")
        for idx, plugin in enumerate(plugins, 1):
            print(f"{idx}. {plugin}")

    def get_plugin_info(self, plugin_name):
        """Get information about a specific plugin."""
        return self.plugin_manager.get_plugin_info(plugin_name)
