"""Matches components against registered HUNT patterns."""

from typing import Any, TypedDict

# Corrected import path
from src.patterns.rules.dsl_pattern_matchers import PatternRegistry

# Constants
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


class MatchResult(TypedDict):
    """Typed dictionary for pattern match results."""

    match: bool
    confidence: float
    properties: dict[str, Any]


class PatternMatcher:
    """Matches components against patterns in a PatternRegistry."""

    def __init__(self, pattern_registry: PatternRegistry) -> None:
        """Initialize the PatternMatcher.

        Args:
            pattern_registry: The registry containing patterns to match against.
        """
        self.pattern_registry = pattern_registry

    def match_component(
        self,
        grid: dict[str, Any],
        component: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Match a component against registered patterns."""
        if context is None:
            context = {}

        # Get all component patterns by filtering the main patterns dictionary
        component_patterns = {
            name: pattern
            for name, pattern in self.pattern_registry.patterns.items()
            # Assuming pattern dict has a 'type' key indicating its purpose
            if pattern.get("type") == "COMPONENT"  # Adjust key/value if needed
        }

        # Try to match the component with each pattern
        matches: list[dict[str, Any]] = []

        for component_type, pattern in component_patterns.items():
            match_result = self._match_component_pattern(
                grid, component, pattern, context
            )

            if match_result["match"]:
                matches.append(
                    {
                        "component_type": component_type,
                        "confidence": match_result["confidence"],
                        "properties": match_result["properties"],
                    }
                )

        # Sort matches by confidence
        matches.sort(key=lambda m: m["confidence"], reverse=True)

        return matches

    def _match_component_pattern(
        self,
        grid: dict[str, Any],
        component: dict[str, Any],
        pattern: dict[str, Any],
        context: dict[str, Any],
    ) -> MatchResult:
        """Match a component against a specific pattern."""
        result: MatchResult = {"match": False, "confidence": 0.0, "properties": {}}

        # Extract pattern rules
        rules = pattern.get("rules", [])

        if not rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each rule
        for rule in rules:
            rule_type = rule.get("command")

            if rule_type == "tag":
                # Match tag rules
                tag_match = self._match_tag_rule(grid, component, rule, context)

                if tag_match["match"]:
                    total_confidence += tag_match["confidence"]
                    matched_rules += 1
                    result["properties"].update(tag_match["properties"])

            elif rule_type == "pluck":
                # Match pluck rules
                pluck_match = self._match_pluck_rule(grid, component, rule, context)

                if pluck_match["match"]:
                    total_confidence += pluck_match["confidence"]
                    matched_rules += 1
                    result["properties"].update(pluck_match["properties"])

            # Add more rule types as needed

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            # Use constant for threshold
            result["match"] = result["confidence"] > DEFAULT_CONFIDENCE_THRESHOLD

        return result

    def _match_tag_rule(
        self,
        _grid: dict[str, Any],  # Prefixed unused arg
        component: dict[str, Any],
        rule: dict[str, Any],
        _context: dict[str, Any],  # Prefixed unused arg
    ) -> MatchResult:
        """Match a tag rule against a component."""
        result: MatchResult = {"match": False, "confidence": 0.0, "properties": {}}

        # Get tag name and rules
        tag_name = rule.get("tag_name")
        tag_rules = rule.get("rules", [])

        if not tag_name or not tag_rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each tag rule
        for tag_rule in tag_rules:
            # Process tag rule
            if isinstance(tag_rule, list) and len(tag_rule) > 0:
                char_to_find = tag_rule[0]
                content = component.get("content", [])
                found = any(char_to_find in line for line in content)
                if found:
                    total_confidence += 1.0
                    matched_rules += 1
                    result["properties"][f"has_{tag_name}"] = True

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            # Use constant for threshold
            result["match"] = result["confidence"] > DEFAULT_CONFIDENCE_THRESHOLD

        return result

    def _match_pluck_rule(
        self,
        _grid: dict[str, Any],  # Prefixed unused arg
        component: dict[str, Any],
        rule: dict[str, Any],
        _context: dict[str, Any],  # Prefixed unused arg
    ) -> MatchResult:
        """Match a pluck rule against a component."""
        result: MatchResult = {"match": False, "confidence": 0.0, "properties": {}}

        # Get target and rules
        target = rule.get("target")
        pluck_rules = rule.get("rules", [])

        if not target or not pluck_rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each pluck rule
        for pluck_rule in pluck_rules:
            # Process pluck rule
            if isinstance(pluck_rule, list) and len(pluck_rule) > 0:
                pattern_str = pluck_rule[0]
                # Ensure pattern is a string before trying regex
                if isinstance(pattern_str, str):
                    content = component.get("content", [])
                    extracted_text = None
                    for line in content:
                        import re

                        try:
                            if match := re.search(pattern_str, line):
                                extracted_text = match.group(0)
                                break
                        except re.error:
                            # Handle invalid regex patterns gracefully if needed
                            pass  # Or log a warning

                    if extracted_text:
                        total_confidence += 1.0
                        matched_rules += 1
                        result["properties"][target] = extracted_text

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            # Use constant for threshold
            result["match"] = result["confidence"] > DEFAULT_CONFIDENCE_THRESHOLD

        return result

    def match_relationships(
        self,
        grid: dict[str, Any],
        components: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Match relationships between components."""
        if context is None:
            context = {}

        # Get all relationship patterns by filtering the main patterns dictionary
        relationship_patterns = {
            name: pattern
            for name, pattern in self.pattern_registry.patterns.items()
            # Assuming pattern dict has a 'type' or 'pattern_class' key
            if pattern.get("type") == "RELATE"  # Adjust key/value if needed
        }

        # Try to match relationships
        relationships: list[dict[str, Any]] = []

        for pattern in relationship_patterns.values():
            relationship_matches = self._match_relationship_pattern(
                grid, components, pattern, context
            )
            relationships.extend(relationship_matches)

        return relationships

    def _match_relationship_pattern(
        self,
        grid: dict[str, Any],
        components: list[dict[str, Any]],
        pattern: dict[str, Any],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Match a relationship pattern between components."""
        # Extract pattern rules
        rules = pattern.get("rules", [])

        if not rules:
            return []

        # Initialize relationships
        relationships = []

        # Check each rule
        for rule in rules:
            rule_type = rule.get("command")

            if rule_type == "tag":
                # Match tag rules for relationships
                tag_relationships = self._match_relationship_tag_rule(
                    grid, components, rule, context
                )
                relationships.extend(tag_relationships)

            # Add more rule types as needed

        return relationships

    def _match_relationship_tag_rule(
        self,
        _grid: dict[str, Any],  # Prefixed unused arg
        _components: list[dict[str, Any]],  # Prefixed unused arg
        rule: dict[str, Any],
        _context: dict[str, Any],  # Prefixed unused arg
    ) -> list[dict[str, Any]]:
        """Match a relationship tag rule between components."""
        # Get tag name and rules
        _tag_name = rule.get("tag_name")
        _tag_rules = rule.get("rules", [])

        # Placeholder: Implement actual relationship tag matching logic
        return []  # Return empty list for now
