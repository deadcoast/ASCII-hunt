from typing import Any


class PatternRegistry:
    def __init__(self) -> None:
        self.tracking_patterns: dict[str, dict[str, Any]] = {}
        self.extraction_patterns: dict[str, dict[str, Any]] = {}
        self.component_patterns: dict[str, dict[str, Any]] = {}
        self.relationship_patterns: dict[str, dict[str, Any]] = {}

    def register_tracking_pattern(self, name: str, pattern: dict[str, Any]) -> None:
        """Register a pattern for tracking UI elements."""
        self.tracking_patterns[name] = pattern

    def register_extraction_pattern(self, name: str, pattern: dict[str, Any]) -> None:
        """Register a pattern for extracting data from UI elements."""
        self.extraction_patterns[name] = pattern

    def register_component_pattern(
        self, component_type: str, pattern: dict[str, Any]
    ) -> None:
        """Register a pattern for recognizing a specific component type."""
        self.component_patterns[component_type] = pattern

    def register_relationship_pattern(
        self, relationship_type: str, pattern: dict[str, Any]
    ) -> None:
        """Register a pattern for recognizing relationships between components."""
        self.relationship_patterns[relationship_type] = pattern

    def get_tracking_pattern(self, name: str) -> dict[str, Any] | None:
        """Get a tracking pattern by name."""
        return self.tracking_patterns.get(name)

    def get_extraction_pattern(self, name: str) -> dict[str, Any] | None:
        """Get an extraction pattern by name."""
        return self.extraction_patterns.get(name)

    def get_component_pattern(self, component_type: str) -> dict[str, Any] | None:
        """Get a component pattern by type."""
        return self.component_patterns.get(component_type)

    def get_relationship_pattern(self, relationship_type: str) -> dict[str, Any] | None:
        """Get a relationship pattern by type."""
        return self.relationship_patterns.get(relationship_type)

    def get_all_tracking_patterns(self) -> dict[str, dict[str, Any]]:
        """Get all registered tracking patterns."""
        return self.tracking_patterns

    def get_all_extraction_patterns(self) -> dict[str, dict[str, Any]]:
        """Get all registered extraction patterns."""
        return self.extraction_patterns

    def get_all_component_patterns(self) -> dict[str, dict[str, Any]]:
        """Get all registered component patterns."""
        return self.component_patterns

    def get_all_relationship_patterns(self) -> dict[str, dict[str, Any]]:
        """Get all registered relationship patterns."""
        return self.relationship_patterns
