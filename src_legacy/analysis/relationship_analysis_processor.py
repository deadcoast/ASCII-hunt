"""Relationship Analysis Processor Module."""

import uuid

from src.components.abstract_component import AbstractComponent
from src.components.component_model_representation import ComponentModel


class RelationshipAnalysisProcessor:
    def __init__(self):
        """Initialize a new RelationshipAnalysisProcessor.

        This constructor creates a new RelationshipAnalysisProcessor instance
        with an empty list of relationship analyzers.
        """
        self.relationship_analyzers = []

    def register_relationship_analyzer(self, analyzer):
        """Register a relationship analyzer."""
        self.relationship_analyzers.append(analyzer)

    def process(self, components, context=None):
        """Analyze relationships between components."""
        if context is None:
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
