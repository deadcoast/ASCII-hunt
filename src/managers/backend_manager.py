"""Backend Manager Module."""

from algorithms.hierarchical_clustering import HierarchicalClustering
from algorithms.decision_tree_classifier import DecisionTreeClassifier
from generators.code_generator import CodeGenerator
from algorithms.flood_fill_processor import FloodFillProcessor
from components.component_analysis import ComponentAnalysis


class BackendManager:
    def __init__(self):
        """
        Initialize the BackendManager with all necessary processing components.

        This constructor sets up the processing pipeline by instantiating
        the following components:
        - FloodFillProcessor for identifying enclosed regions in the ASCII grid.
        - ConnectedComponentAnalyzer for analyzing and grouping connected components.
        - HierarchicalClustering for building component hierarchies.
        - DecisionTreeClassifier for classifying UI components.
        - CodeGenerator for generating code based on recognized components.
        """

        self.flood_fill_processor = FloodFillProcessor()
        self.connected_component_analyzer = ComponentAnalysis()
        self.hierarchical_clustering = HierarchicalClustering()
        self.decision_tree_classifier = DecisionTreeClassifier()
        self.code_generator = CodeGenerator()

    def process_ascii_grid(self, grid_data):
        """Process ASCII grid and return recognized components."""
        # Convert grid data to NumPy array
        grid_array = self.convert_to_numpy_array(grid_data)

        # Run recognition pipeline
        components = self.run_recognition_pipeline(grid_array)

        return components

    def run_recognition_pipeline(self, grid_array):
        """Run the full recognition pipeline on grid data."""
        # Step 1: Flood Fill
        flood_fill_results = self.flood_fill_processor.process(grid_array)

        # Step 2: Connected Component Analysis
        component_groups = self.connected_component_analyzer.analyze(
            flood_fill_results, grid_array
        )

        # Step 3: Hierarchical Clustering
        component_hierarchy = self.hierarchical_clustering.cluster(component_groups)

        # Step 4: Component Classification
        classified_components = self.decision_tree_classifier.classify(
            component_hierarchy, grid_array
        )

        return classified_components

    def generate_code(self, components, framework, options):
        """Generate code for the given components."""
        return self.code_generator.generate(components, framework, options)
