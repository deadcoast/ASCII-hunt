"""Component analysis module for analyzing ASCII components."""

from typing import Any

import networkx as nx


class ComponentAnalyzer:
    """Analyzes ASCII components and their relationships."""

    def __init__(self) -> None:
        self.component_graph = nx.DiGraph()

    def analyze_component(self, component_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze a single component and return analysis results."""
        # Implementation will be added based on specific requirements
        return {}

    def get_component_dependencies(self, component_id: str) -> set[str]:
        """Get dependencies for a specific component."""
        if component_id in self.component_graph:
            return set(self.component_graph.predecessors(component_id))
        return set()

    def analyze(self, components: list, grid: Any = None) -> list:
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
            component_id = component.get("id", str(id(component)))
            self.component_graph.add_node(component_id, data=component)

        # Analyze spatial relationships between components
        analyzed_components = self._analyze_spatial_relationships(components)

        # Build detailed component analyses
        result = []
        for component in analyzed_components:
            component_id = component.get("id", str(id(component)))

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
            container_id = container.get("id", str(id(container)))
            container_bounds = container.get("bounds", {})

            # Skip components without proper bounds
            if not all(
                k in container_bounds for k in ["min_x", "min_y", "max_x", "max_y"]
            ):
                continue

            # Check if other components are contained within this one
            for j, potential_child in enumerate(components):
                if i == j:  # Skip self
                    continue

                child_id = potential_child.get("id", str(id(potential_child)))
                child_bounds = potential_child.get("bounds", {})

                # Skip components without proper bounds
                if not all(
                    k in child_bounds for k in ["min_x", "min_y", "max_x", "max_y"]
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

    def _analyze_single_component(self, component: dict, grid: Any = None) -> dict:
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

        # Content analysis
        content = component.get("content", {})
        char_counts = content.get("char_counts", {})

        if char_counts:
            analysis["complexity"] = len(char_counts)

            # Detect potential UI elements based on characters
            if any(c in "[](){}<>" for c in char_counts):
                analysis["type_indicators"].append("container")
            if any(c in "▢▣■□✓✗×X" for c in char_counts):
                analysis["type_indicators"].append("control")
            if (
                any(c == "_" for c in char_counts)
                and sum(count for char, count in char_counts.items() if char == "_") > 2
            ):
                analysis["type_indicators"].append("input")

        return analysis


def analyze_component_structure(data: dict[str, Any]) -> dict[str, Any]:
    """Analyze the structure of a component."""
    analyzer = ComponentAnalyzer()
    return analyzer.analyze_component(data)


def get_component_hierarchy(components: list[dict[str, Any]]) -> nx.DiGraph:
    """Build and return a component hierarchy graph."""
    graph = nx.DiGraph()
    # Implementation will be added based on specific requirements
    return graph
