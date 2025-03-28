"""ASCII UI Translation Engine Module."""

from src.managers.cache_manager import CacheManager
from src.managers.configuration_manager import ConfigurationManager
from src.managers.extension_point import ExtensionPoint
from src.managers.performance_monitor import PerformanceMonitor
from src.managers.plugin_manager import PluginManager
from src.managers.processing_pipeline import ProcessingPipeline
from src.processors.code_generation_processor import CodeGenerationProcessor
from src.processors.component_classification_processor import (
    ComponentClassificationProcessor,
)
from src.processors.contour_detection_processor import ContourDetectionProcessor
from src.processors.feature_extraction_processor import FeatureExtractionProcessor
from src.processors.flood_fill_processor import FloodFillProcessor
from src.processors.pattern_recognition_processor import PatternRecognitionProcessor
from src.processors.relationship_analysis_processor import RelationshipAnalysisProcessor

from .ascii_grid import ASCIIGrid


class ASCIIUITranslationEngine:
    def __init__(self):
        # Create core components
        """Initialize the ASCII UI Translation Engine with all necessary processing components.

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
        # Create extension points
        """Initialize extension points.

        This function creates extension points for the following components:
        - PatternRecognizers for recognizing patterns in the ASCII grid.
        - FeatureExtractors for extracting features from recognized patterns.
        - ComponentClassifiers for classifying UI components.
        - RelationshipAnalyzers for analyzing relationships between components.
        - CodeGenerators for generating code based on recognized components.

        The extension points are registered with the PluginManager so that plugins can
        register their own implementations of the above components.

        """
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
        """Process the given ASCII text and generate code based on the specified options.

        The function processes the given ASCII text by running it through a pipeline
        of processors. The pipeline consists of the following stages:
        - FloodFill: Fills areas in the grid with a color.
        - ContourDetection: Detects contours in the filled grid.
        - PatternRecognition: Recognizes patterns in the contours.
        - FeatureExtraction: Extracts features from the recognized patterns.
        - ComponentClassification: Classifies the extracted features into UI components.
        - RelationshipAnalysis: Analyzes the relationships between the components.
        - CodeGeneration: Generates code based on the recognized components.

        The function returns a dictionary with the following keys:
        - success: A boolean indicating whether the processing was successful.
        - generated_code: A string containing the generated code.
        - component_model: A dictionary containing the component model.
        - performance_metrics: A dictionary containing performance metrics for each stage.

        If an error occurs during processing, the function returns a dictionary with
        a single key "error" containing the error message.
        """
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
        """Load plugins from a directory.

        :param plugin_dir: The directory to search for plugins
        :type plugin_dir: str

        :return: A list of loaded plugins
        :rtype: list

        Plugins are loaded from the given directory and any subdirectories.
        Plugins are Python files that do not start with '__'.
        For each plugin, the ``load_plugin_from_file`` method of the
        ``PluginManager`` is called to load the plugin.
        If an error occurs while loading a plugin, an error message is printed.
        """
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
        """Load the configuration from a file.

        :param config_path: The path to the configuration file to load.
        :type config_path: str
        """
        self.config_manager.load_config(config_path)

    def save_config(self, config_path):
        """Save the current configuration to a file.

        :param config_path: The path to save the configuration file to.
        :type config_path: str
        """
        self.config_manager.save_config(config_path)

    def get_supported_frameworks(self):
        """Get all supported frameworks for code generation.

        :return: List of supported frameworks (e.g. ["python_tkinter", "hunt", "dsl"])
        :rtype: List[str]
        """
        ext_point = self.plugin_manager.get_extension_point("code_generators")

        if ext_point:
            return list(ext_point.get_extensions().keys())
        return ["default"]

    def list_frameworks(self):
        """List all supported frameworks for code generation.

        This will print a list of supported frameworks to the console.
        """
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

    def get_plugin_info(self, plugin_name: str) -> dict:
        """Get information about a specific plugin.

        Args:
            plugin_name (str): The name of the plugin to get information about.

        Returns:
            dict: A dictionary containing plugin information including:
                - name: The plugin name
                - extensions: List of extension points implemented by the plugin
                - extension_points: List of extension points provided by the plugin
        """
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return {"error": f"Plugin {plugin_name} not found"}

        return {
            "name": plugin_name,
            "extensions": self.plugin_manager.get_extensions_for_plugin(plugin_name),
            "extension_points": self.plugin_manager.get_extension_points_for_plugin(
                plugin_name
            ),
        }
