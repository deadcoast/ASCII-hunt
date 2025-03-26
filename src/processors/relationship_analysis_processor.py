"""Relationship Analysis Processor Module.

This module provides a processor for analyzing relationships between components.
"""

import uuid
from typing import Any

from src.components.abstract_component import AbstractComponent
from src.components.component_model_representation import ComponentModel


class RelationshipAnalysisProcessor:
    """A processor for analyzing relationships between components.

    This processor analyzes the spatial and logical relationships between
    components and builds a component model with relationship information.
    """

    def __init__(self) -> None:
        """Initialize the RelationshipAnalysisProcessor class."""
        self.relationship_analyzers: list[Any] = []

    def register_relationship_analyzer(self, analyzer: Any) -> None:
        """Register a relationship analyzer.

        Args:
            analyzer: The relationship analyzer to register.
        """
        self.relationship_analyzers.append(analyzer)

    def process(
        self, components: list[dict[str, Any]], context: dict[str, Any]
    ) -> ComponentModel:
        """Analyze relationships between components.

        Args:
            components: The list of components to analyze.
            context: The context dictionary containing processing information.

        Returns:
            A ComponentModel containing the components and their relationships.
        """
        if not context:
            context = {}

        # Create component model
        component_model = ComponentModel()

        # Add components to model
        for component in components:
            # Create AbstractComponent
            abstract_component = AbstractComponent(
                component.get("id", str(uuid.uuid4())),
                component.get("ui_type", "unknown"),
            )

            # Add properties
            for key, value in component.items():
                if key not in ("id", "type", "ui_type"):
                    abstract_component.add_property(key, value)

            # Add to model directly via the components dictionary
            component_model.components[abstract_component.id] = abstract_component

        # Apply all relationship analyzers
        for analyzer in self.relationship_analyzers:
            analyzer.analyze(component_model, context)

        # Store in context for other stages
        context["component_model"] = component_model
        context["relationship_analysis_results"] = component_model

        return component_model

    def build_default_relationships(self, component_model: ComponentModel) -> None:
        """Build default relationships based on spatial analysis.

        This method adds default relationships between components based on their
        spatial arrangement when no custom relationship analyzers are registered.

        Args:
            component_model: The component model to analyze.
        """
        components = component_model.get_all_components()

        # Skip if no components
        if not components:
            return

        # Build containment relationships
        self._analyze_containment(component_model)

        # Build horizontal relationships (left-to-right)
        self._analyze_horizontal_relationships(component_model)

        # Build vertical relationships (top-to-bottom)
        self._analyze_vertical_relationships(component_model)

    def _analyze_containment(self, component_model: ComponentModel) -> None:
        """Analyze containment relationships between components.

        Args:
            component_model: The component model to analyze.
        """
        components = component_model.get_all_components()

        # Check each potential container against all other components
        for container in components:
            container_bounds = container.get_property("bounds", {})
            if not container_bounds:
                continue

            for contained in components:
                # Skip self
                if container.id == contained.id:
                    continue

                contained_bounds = contained.get_property("bounds", {})
                if not contained_bounds:
                    continue

                # Check if contained is fully inside container
                if (
                    contained_bounds.get("x1", 0) >= container_bounds.get("x1", 0)
                    and contained_bounds.get("y1", 0) >= container_bounds.get("y1", 0)
                    and contained_bounds.get("x2", 0) <= container_bounds.get("x2", 0)
                    and contained_bounds.get("y2", 0) <= container_bounds.get("y2", 0)
                ):
                    # Add "contains" relationship
                    container.add_relationship("contains", contained)

                    # Add "contained_by" relationship in the other direction
                    contained.add_relationship("contained_by", container)

    def _analyze_horizontal_relationships(
        self, component_model: ComponentModel
    ) -> None:
        """Analyze horizontal relationships between components.

        Args:
            component_model: The component model to analyze.
        """
        components = component_model.get_all_components()

        # Sort components by x-coordinate
        components.sort(key=lambda c: c.get_property("bounds", {}).get("x1", 0))

        # Establish left-to-right relationships for adjacent components
        for i in range(len(components) - 1):
            current = components[i]
            next_comp = components[i + 1]

            current_bounds = current.get_property("bounds", {})
            next_bounds = next_comp.get_property("bounds", {})

            if not current_bounds or not next_bounds:
                continue

            # Check if components are horizontally adjacent
            if (
                current_bounds.get("x2", 0) < next_bounds.get("x1", 0)
                and
                # Check for vertical overlap
                current_bounds.get("y1", 0) <= next_bounds.get("y2", 0)
                and current_bounds.get("y2", 0) >= next_bounds.get("y1", 0)
            ):
                # Add "left_of" relationship
                current.add_relationship("left_of", next_comp)

                # Add "right_of" relationship in the other direction
                next_comp.add_relationship("right_of", current)

    def _analyze_vertical_relationships(self, component_model: ComponentModel) -> None:
        """Analyze vertical relationships between components.

        Args:
            component_model: The component model to analyze.
        """
        components = component_model.get_all_components()

        # Sort components by y-coordinate
        components.sort(key=lambda c: c.get_property("bounds", {}).get("y1", 0))

        # Establish top-to-bottom relationships for adjacent components
        for i in range(len(components) - 1):
            current = components[i]
            next_comp = components[i + 1]

            current_bounds = current.get_property("bounds", {})
            next_bounds = next_comp.get_property("bounds", {})

            if not current_bounds or not next_bounds:
                continue

            # Check if components are vertically adjacent
            if (
                current_bounds.get("y2", 0) < next_bounds.get("y1", 0)
                and
                # Check for horizontal overlap
                current_bounds.get("x1", 0) <= next_bounds.get("x2", 0)
                and current_bounds.get("x2", 0) >= next_bounds.get("x1", 0)
            ):
                # Add "above" relationship
                current.add_relationship("above", next_comp)

                # Add "below" relationship in the other direction
                next_comp.add_relationship("below", current)

    def group_related_components(
        self, component_model: ComponentModel
    ) -> dict[str, list[str]]:
        """Group components based on their relationships.

        Args:
            component_model: The component model to analyze.

        Returns:
            A dictionary mapping group names to lists of component IDs.
        """
        groups: dict[str, list[str]] = {}
        components = component_model.get_all_components()

        # Group by containment hierarchy
        container_groups: dict[str, list[str]] = {}
        for component in components:
            # If component contains others, create a group
            if "contains" in component.get_relationships():
                container_id = component.id
                contained_components = [
                    c.id for c in component.get_relationships().get("contains", [])
                ]

                if contained_components:
                    container_groups[f"container_{container_id}"] = [
                        container_id
                    ] + contained_components

        # Group by horizontal alignment (components with similar y-coordinates)
        y_groups: dict[int, list[str]] = {}
        for component in components:
            bounds = component.get_property("bounds", {})
            if bounds:
                y_center = bounds.get("y1", 0) + (bounds.get("height", 0) // 2)
                y_key = y_center // 10  # Group by 10-pixel bands

                if y_key not in y_groups:
                    y_groups[y_key] = []

                y_groups[y_key].append(component.id)

        # Group by vertical alignment (components with similar x-coordinates)
        x_groups: dict[int, list[str]] = {}
        for component in components:
            bounds = component.get_property("bounds", {})
            if bounds:
                x_center = bounds.get("x1", 0) + (bounds.get("width", 0) // 2)
                x_key = x_center // 10  # Group by 10-pixel bands

                if x_key not in x_groups:
                    x_groups[x_key] = []

                x_groups[x_key].append(component.id)

        # Add all groups to result
        for group_id, group_components in container_groups.items():
            groups[group_id] = group_components

        for y_key, group_components in y_groups.items():
            if (
                len(group_components) > 1
            ):  # Only include groups with multiple components
                groups[f"row_{y_key}"] = group_components

        for x_key, group_components in x_groups.items():
            if (
                len(group_components) > 1
            ):  # Only include groups with multiple components
                groups[f"column_{x_key}"] = group_components

        return groups
