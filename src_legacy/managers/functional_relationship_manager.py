"""Functional Relationship Manager Module."""


class FunctionalRelationshipPattern:
    def __init__(self, pattern_id, description, apply_function):
        """Initialize a new FunctionalRelationshipPattern.

        :param pattern_id: The unique identifier for the pattern.
        :type pattern_id: str
        :param description: A description of the pattern.
        :type description: str
        :param apply_function: The function to apply the pattern.
        :type apply_function: function
        """
        self.pattern_id = pattern_id
        self.description = description
        self.apply_function = apply_function

    def apply(self, component_model, context=None):
        """Apply the pattern to the component model."""
        if context is None:
            context = {}

        return self.apply_function(component_model, context)


class FunctionalRelationshipManager:
    def __init__(self):
        """Initialize a new FunctionalRelationshipManager.

        The manager has an empty list of registered relationship patterns.
        """
        self.relationship_patterns = []

    def register_relationship_pattern(self, pattern):
        """Register a relationship pattern."""
        self.relationship_patterns.append(pattern)

    def analyze(self, component_model, context=None):
        """Analyze functional relationships between components."""
        if context is None:
            context = {}

        # Apply all relationship patterns
        for pattern in self.relationship_patterns:
            pattern.apply(component_model, context)

        return component_model


class FunctionalRelationshipAnalyzer:
    def __init__(self):
        """Initialize a new FunctionalRelationshipAnalyzer.

        The analyzer has an empty list of registered relationship patterns.
        """
        self.relationship_patterns = []

    def register_relationship_pattern(self, pattern):
        """Register a relationship pattern."""
        self.relationship_patterns.append(pattern)

    def analyze(self, component_model, context=None):
        """Analyze functional relationships between components."""
        if context is None:
            context = {}

        # Apply all relationship patterns
        for pattern in self.relationship_patterns:
            pattern.apply(component_model, context)

        return component_model
