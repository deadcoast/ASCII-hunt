"""Backend manager for ASCII art processing."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from src.algorithms.decision_tree import DecisionTree
from src.algorithms.flood_fill_processor import FloodFillProcessor
from src.algorithms.hierarchical_clustering import HierarchicalClustering
from src.analysis.component_analysis import ComponentAnalyzer
from src.generators.code_generator import CodeGenerator


class BackendManager:
    """Manages backend processing components for ASCII art analysis."""

    def __init__(self) -> None:
        """Initialize backend manager with processing components."""
        self.flood_fill_processor = FloodFillProcessor()
        self.connected_component_analyzer = ComponentAnalyzer()
        self.decision_tree_classifier = DecisionTree()
        self.hierarchical_clustering = HierarchicalClustering()
        self.code_generator = CodeGenerator()

    def process_grid(self, grid: NDArray[np.str_]) -> dict[str, Any]:
        """Process ASCII grid through recognition pipeline.

        Args:
            grid: Input ASCII grid

        Returns:
            Dictionary containing analysis results
        """
        # Process connected components
        components = self.flood_fill_processor.process(grid)

        # Analyze component structure
        component_analysis = self.connected_component_analyzer.analyze_component(
            components
        )

        # Classify components
        classifications = self.decision_tree_classifier.classify(component_analysis)

        # Generate code representation
        code = self.code_generator.generate(classifications)

        return {
            "components": components,
            "analysis": component_analysis,
            "classifications": classifications,
            "code": code,
        }

    def _grid_to_array(self, grid: list[list[str]]) -> NDArray[np.str_]:
        """Convert grid to numpy array.

        Args:
            grid: Input grid as list of lists

        Returns:
            Grid as numpy array
        """
        return np.array(grid)
