"""Component analysis module for analyzing ASCII components."""

from typing import Any

import networkx as nx
import numpy as np

from engine.modeling.component_model_representation import ComponentModel
from engine.pipeline.feature_extraction_processor import FeatureExtractionProcessor
from patterns.matching.hierarchical_clustering import HierarchicalClustering
from patterns.matching.parsing_algorithms import DistanceCalculator


class ComponentAnalyzer:
    """Analyzes ASCII components and their relationships."""

    def __init__(self, model: ComponentModel) -> None:
        """Initialize the ComponentAnalyzer class.

        Parameters
        ----------
        model : ComponentModel
            The component model to analyze
        """
        self.model = model
        self.feature_extractor = FeatureExtractionProcessor()
        self.clustering_algorithm = HierarchicalClustering()
        self.distance_calculator = DistanceCalculator()
        self.component_graph = nx.DiGraph()

    def get_component_dependencies(self, component_id: str) -> set[str]:
        """Get dependencies for a specific component."""
        if component_id in self.component_graph:
            return set(self.component_graph.predecessors(component_id))
        return set()

    def analyze(self, components: list, grid: np.ndarray | None = None) -> list:
        """Analyze multiple components and their relationships.

        Args:
            components: List of components to analyze
            grid: Optional original grid for contextual analysis

        Returns:
            List of analyzed components with additional properties
        """
        if not components:
            return []

        # Reset the component graph
        self.component_graph = nx.DiGraph()

        # Add nodes for each component
        for component in components:
            component_id = component.get("id", id(component))
            self.component_graph.add_node(component_id, data=component)

        # Analyze spatial relationships between components
        analyzed_components = self._analyze_spatial_relationships(components)

        # Build detailed component analyses
        result = []
        for component in analyzed_components:
            component_id = component.get("id", id(component))

            # Add component analysis data
            analysis_data = self._analyze_single_component(component, grid)

            # Update component with analysis results
            component_copy = (
                component.copy() if hasattr(component, "copy") else component
            )
            component_copy["analysis"] = analysis_data

            # Add relationship data
            if component_id in self.component_graph:
                relationships = {
                    "contains": list(self.component_graph.successors(component_id)),
                    "contained_by": list(
                        self.component_graph.predecessors(component_id)
                    ),
                }
                component_copy["relationships"] = relationships

            result.append(component_copy)

        return result

    def _analyze_spatial_relationships(self, components: list) -> list:
        """Analyze spatial relationships between components.

        Args:
            components: List of components to analyze

        Returns:
            Components with spatial relationship data
        """
        # Analyze containment relationships
        for i, container in enumerate(components):
            container_id = container.get("id", id(container))
            container_bounds = container.get("bounds", {})

            # Skip components without proper bounds
            if any(
                k not in container_bounds for k in ["min_x", "min_y", "max_x", "max_y"]
            ):
                continue

            # Check if other components are contained within this one
            for j, potential_child in enumerate(components):
                if i == j:  # Skip self
                    continue

                child_id = potential_child.get("id", id(potential_child))
                child_bounds = potential_child.get("bounds", {})

                # Skip components without proper bounds
                if any(
                    k not in child_bounds for k in ["min_x", "min_y", "max_x", "max_y"]
                ):
                    continue

                # Check containment
                if (
                    container_bounds["min_x"] <= child_bounds["min_x"]
                    and container_bounds["min_y"] <= child_bounds["min_y"]
                    and container_bounds["max_x"] >= child_bounds["max_x"]
                    and container_bounds["max_y"] >= child_bounds["max_y"]
                ):
                    # Add containment relationship to graph
                    self.component_graph.add_edge(
                        container_id, child_id, type="contains"
                    )

        return components

    def _analyze_single_component(
        self, component: dict, grid: np.ndarray | None = None
    ) -> dict:
        """Perform detailed analysis on a single component.

        Args:
            component: The component to analyze
            grid: Optional original grid

        Returns:
            Dictionary of analysis results
        """
        analysis = {"type_indicators": [], "complexity": 0, "characteristics": {}}

        # Basic geometric analysis
        bounds = component.get("bounds", {})
        if all(k in bounds for k in ["width", "height"]):
            self._analyze_bounds(bounds, analysis)
        # Content analysis
        content = component.get("content", {})
        if char_counts := content.get("char_counts", {}):
            analysis["complexity"] = len(char_counts)

            # Detect potential UI elements based on characters
            if any(c in "[](){}<>" for c in char_counts):
                analysis["type_indicators"].append("container")
            if any(c in "▢▣■□✓✗xX" for c in char_counts):
                analysis["type_indicators"].append("control")
            if (
                any(c == "_" for c in char_counts)
                and sum(count for char, count in char_counts.items() if char == "_") > 2
            ):
                analysis["type_indicators"].append("input")

        return analysis

    def _analyze_bounds(self, bounds: dict[str, Any], analysis: dict[str, Any]) -> None:
        """Analyze the bounds of a component and update the analysis dictionary."""
        width = bounds["width"]
        height = bounds["height"]
        area = width * height
        aspect_ratio = width / max(height, 1)

        analysis["characteristics"].update(
            {
                "width": width,
                "height": height,
                "area": area,
                "aspect_ratio": aspect_ratio,
            }
        )

        # Basic shape classification
        if aspect_ratio > 3:
            analysis["type_indicators"].append("horizontal_line")
        elif aspect_ratio < 0.33:
            analysis["type_indicators"].append("vertical_line")
        elif 0.9 < aspect_ratio < 1.1:
            analysis["type_indicators"].append("square")

    def component_analysis_from_model(
        self, components: list[dict[str, Any]], grid: np.ndarray
    ) -> list[list[int]]:
        """Analyze the components and return a list of feature vectors."""
        feature_vectors = []
        for comp in components:
            # Convert sets to numpy arrays for efficient computation
            interior = np.array(list(comp["interior"]))
            boundary = np.array(list(comp["boundary"]))

            width = comp["width"]
            height = comp["height"]

            # Calculate aspect ratio
            aspect_ratio = width / height if height > 0 else 0

            # Calculate border density
            border_density = (
                len(boundary) / (2 * (width + height))
                if width > 0 and height > 0
                else 0
            )

            # Calculate content density
            content_density = (
                len(interior) / (width * height) if width > 0 and height > 0 else 0
            )

            # Character distribution analysis
            chars = [grid[y, x] for x, y in interior]
            unique_chars, char_counts = np.unique(chars, return_counts=True)
            char_frequencies = char_counts / len(interior) if interior else np.array([])

            # Combine into feature vector
            feature_vectors.append(
                {
                    "id": comp.get("id"),
                    "aspect_ratio": aspect_ratio,
                    "border_density": border_density,
                    "content_density": content_density,
                    "char_frequencies": dict(
                        zip(unique_chars, char_frequencies, strict=False)
                    ),
                    "bounding_box": comp["bounding_box"],
                }
            )

        # Calculate pairwise distances
        n = len(feature_vectors)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                # Feature distance calculation
                f_i = feature_vectors[i]
                f_j = feature_vectors[j]

                # Weighted Euclidean distance between numeric features
                feature_distance = np.sqrt(
                    0.3 * (f_i["aspect_ratio"] - f_j["aspect_ratio"]) ** 2
                    + 0.4 * (f_i["border_density"] - f_j["border_density"]) ** 2
                    + 0.3 * (f_i["content_density"] - f_j["content_density"]) ** 2
                )

                # Spatial distance between components
                bb_i = [
                    int(x) for x in components[i]["bounding_box"]
                ]  # Convert to integers
                bb_j = [
                    int(x) for x in components[j]["bounding_box"]
                ]  # Convert to integers

                # Calculate minimum distance between bounding boxes using integers
                spatial_distance = max(
                    0,
                    int(max(bb_i[0], bb_j[0])) - int(min(bb_i[2], bb_j[2])),
                    int(max(bb_i[1], bb_j[1])) - int(min(bb_i[3], bb_j[3])),
                )

                # Combined distance
                combined_distance = 0.6 * feature_distance + 0.4 * spatial_distance
                distance_matrix[i, j] = distance_matrix[j, i] = float(combined_distance)

        # Group components based on distance thresholds (Moved outside inner loop)
        threshold = 0.5  # Adjust based on application
        grouped_components: list[list[int]] = []  # Initialize here
        processed: set[int] = set()

        for i in range(n):
            if i in processed:
                continue

            group = [i]
            processed.add(i)

            # Check neighbors for grouping
            for j in range(n):  # Check all other components
                if j != i and j not in processed and distance_matrix[i, j] < threshold:
                    group.append(j)
                    processed.add(j)

            if group:  # Ensure group is not empty before adding
                grouped_components.append(group)

        return grouped_components

    def connected_component_analysis(
        self, components: list[dict[str, Any]], grid: np.ndarray
    ) -> list[list[int]]:
        """Implements the mathematical CCA using NumPy operations.

        Parameters
        ----------
        components : List[Dict[str, Any]]
            List of components to analyze
        grid : np.ndarray
            Grid representation of the components

        Returns
        -------
        List[List[int]]
            List of grouped components
        """
        if not components:
            return []

        # Initialize empty list for grouped components and feature vectors
        grouped_components: list[list[int]] = []
        feature_vectors: list[list[float]] = []

        # Process each component
        for i, comp in enumerate(components):
            # Convert sets to numpy arrays for efficient computation
            interior = np.array(list(comp["interior"]))
            boundary = np.array(list(comp["boundary"]))

            # Calculate aspect ratio
            width = comp["width"]
            height = comp["height"]
            aspect_ratio = width / height if height > 0 else 0

            # Calculate border density
            border_density = (
                len(boundary) / (2 * (width + height))
                if width > 0 and height > 0
                else 0
            )

            # Calculate content density
            content_density = (
                len(interior) / (width * height) if width > 0 and height > 0 else 0
            )

            feature_vectors.append([aspect_ratio, border_density, content_density])
            grouped_components.append([i])  # Each component starts in its own group

        return grouped_components

    def analyze_component(self, component_id: str) -> dict[str, Any]:
        """Analyze a specific component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        features = self.feature_extractor.extract_features(component)
        # Convert features to list if it's a dictionary
        features_list = [features] if isinstance(features, dict) else features
        distance_matrix = self.distance_calculator.calculate_distance_matrix(
            features_list
        )
        clusters = self.clustering_algorithm.cluster(distance_matrix)

        return {
            "component_id": component_id,
            "features": features,
            "distance_matrix": distance_matrix,
            "clusters": clusters,
        }

    def analyze_all_components(self) -> list[list[int]]:
        """Analyze all components and return a list of feature vectors."""
        components = self.model.get_all_components()
        grid = self.model.get_grid()
        if grid is None:
            raise ValueError("Grid is not initialized in the component model")
        print(grid)
        print(components)
        print(self.connected_component_analysis(components, grid))
        print(self.component_analysis_from_model(components, grid))
        return self.connected_component_analysis(components, grid)

    def analyze_component_group(self, component_ids: list[str]) -> dict[str, Any]:
        """Analyze a group of components and return a list of feature vectors."""
        results = []
        results.extend(
            self.analyze_component(component_id)
            for component_id in component_ids
            if self.model.get_component(component_id)
        )
        return {"group_analysis": results}

    def analyze_component_hierarchy(self, component_id: str) -> list[dict[str, Any]]:
        """Analyze the hierarchy of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        hierarchy = self.model.get_component_hierarchy(component_id)
        return [self.analyze_component(child.id) for child in hierarchy]

    def analyze_component_relationships(self, component_id: str) -> dict[str, Any]:
        """Analyze relationships between components."""
        if self.model.get_component(component_id):
            return {"relationships": []}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_template(self, component_id: str) -> dict[str, Any]:
        """Analyze component template."""
        if self.model.get_component(component_id):
            return {"template": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_layout(self, component_id: str) -> dict[str, Any]:
        """Analyze component layout."""
        if self.model.get_component(component_id):
            return {"layout": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_style(self, component_id: str) -> dict[str, Any]:
        """Analyze component style."""
        if self.model.get_component(component_id):
            return {"style": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_behavior(self, component_id: str) -> dict[str, Any]:
        """Analyze component behavior."""
        if self.model.get_component(component_id):
            return {"behavior": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_performance(self, component_id: str) -> dict[str, Any]:
        """Analyze component performance."""
        if self.model.get_component(component_id):
            return {"performance": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_accessibility(self, component_id: str) -> dict[str, Any]:
        """Analyze component accessibility."""
        if self.model.get_component(component_id):
            return {"accessibility": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_usability(self, component_id: str) -> dict[str, Any]:
        """Analyze component usability."""
        if self.model.get_component(component_id):
            return {"usability": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_interaction(self, component_id: str) -> dict[str, Any]:
        """Analyze component interaction."""
        if self.model.get_component(component_id):
            return {"interaction": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_visualization(self, component_id: str) -> dict[str, Any]:
        """Analyze component visualization."""
        if self.model.get_component(component_id):
            return {"visualization": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_animation(self, component_id: str) -> dict[str, Any]:
        """Analyze component animation."""
        if self.model.get_component(component_id):
            return {"animation": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_state(self, component_id: str) -> dict[str, Any]:
        """Analyze component state."""
        if self.model.get_component(component_id):
            return {"state": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_events(self, component_id: str) -> dict[str, Any]:
        """Analyze component events."""
        if self.model.get_component(component_id):
            return {"events": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_memory(self, component_id: str) -> dict[str, Any]:
        """Analyze component memory usage."""
        if self.model.get_component(component_id):
            return {"memory": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_security(self, component_id: str) -> dict[str, Any]:
        """Analyze component security."""
        if self.model.get_component(component_id):
            return {"security": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_reliability(self, component_id: str) -> dict[str, Any]:
        """Analyze component reliability."""
        if self.model.get_component(component_id):
            return {"reliability": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")

    def analyze_component_maintainability(self, component_id: str) -> dict[str, Any]:
        """Analyze component maintainability."""
        if self.model.get_component(component_id):
            return {"maintainability": {}}
        else:
            raise ValueError(f"Component with id {component_id} not found")
