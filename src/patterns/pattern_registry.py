class PatternRegistry:
    def __init__(self):
        self.tracking_patterns = {}
        self.extraction_patterns = {}
        self.component_patterns = {}
        self.relationship_patterns = {}

    def register_tracking_pattern(self, name, pattern):
        """Register a pattern for tracking UI elements."""
        self.tracking_patterns[name] = pattern

    def register_extraction_pattern(self, name, pattern):
        """Register a pattern for extracting data from UI elements."""
        self.extraction_patterns[name] = pattern

    def register_component_pattern(self, component_type, pattern):
        """Register a pattern for recognizing a specific component type."""
        self.component_patterns[component_type] = pattern

    def register_relationship_pattern(self, relationship_type, pattern):
        """Register a pattern for recognizing relationships between components."""
        self.relationship_patterns[relationship_type] = pattern

    def get_tracking_pattern(self, name):
        """Get a tracking pattern by name."""
        return self.tracking_patterns.get(name)

    def get_extraction_pattern(self, name):
        """Get an extraction pattern by name."""
        return self.extraction_patterns.get(name)

    def get_component_pattern(self, component_type):
        """Get a component pattern by type."""
        return self.component_patterns.get(component_type)

    def get_relationship_pattern(self, relationship_type):
        """Get a relationship pattern by type."""
        return self.relationship_patterns.get(relationship_type)

    def get_all_tracking_patterns(self):
        """Get all registered tracking patterns."""
        return self.tracking_patterns

    def get_all_extraction_patterns(self):
        """Get all registered extraction patterns."""
        return self.extraction_patterns

    def get_all_component_patterns(self):
        """Get all registered component patterns."""
        return self.component_patterns

    def get_all_relationship_patterns(self):
        """Get all registered relationship patterns."""
        return self.relationship_patterns
