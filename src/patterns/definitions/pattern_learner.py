"""Learns HUNT patterns from examples."""

import re
from typing import Any

# Trying the dsl_pattern_matchers path again
from src.patterns.rules.dsl_pattern_matchers import PatternRegistry

# Constants (consider moving to a constants file)
CONFIDENCE_THRESHOLD = 0.8
MIN_EXAMPLES = 5  # Using the last defined value
MAX_EXAMPLES = 100
MAX_PATTERNS = 10
MIN_CONFIDENCE = 0.7


class PatternLearner:
    """Learns HUNT patterns from annotated examples."""

    def __init__(self, pattern_registry: PatternRegistry) -> None:
        """Initialize the PatternLearner.

        Args:
            pattern_registry: The registry to store learned patterns.
        """
        self.pattern_registry = pattern_registry
        # Consider initializing a logger instance here if needed

    def learn_from_examples(self, examples: list[dict[str, Any]]) -> str:
        """Learn patterns from annotated examples and generate DSL code.

        Args:
            examples: A list of dictionaries, each representing an annotated example.

        Returns:
            A string containing the generated HUNT DSL code.
        """
        # Extract common patterns from examples
        extracted_patterns = self._extract_patterns(examples)
        # Renamed variable to avoid shadowing

        return self._generate_dsl_code(extracted_patterns)

    def _extract_patterns(
        self, examples: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """Extract common patterns from examples."""
        # Implement pattern extraction logic
        # For example, finding common character sequences in components of the same type

        patterns: dict[str, dict[str, Any]] = {}

        # Group examples by component type
        grouped_examples: dict[str, list[dict[str, Any]]] = {}

        for example in examples:
            if component_type := example.get("ui_type"):
                if component_type not in grouped_examples:
                    grouped_examples[component_type] = []

                grouped_examples[component_type].append(example)

        # Extract patterns for each component type
        for component_type, components in grouped_examples.items():
            type_patterns = self._extract_type_patterns(component_type, components)
            patterns[component_type] = type_patterns

        return patterns

    def _extract_type_patterns(
        self,
        _component_type: str,
        components: list[dict[str, Any]],  # Prefixed unused arg
    ) -> dict[str, Any]:
        """Extract patterns for a specific component type."""
        # Implement type-specific pattern extraction

        # For example, finding common boundary characters
        boundary_chars: set[str] = set()

        for component in components:
            boundary_points = component.get("boundary_points", [])

            for x, y in boundary_points:
                # Safely access grid coordinates
                grid_data = component.get("grid", {})
                char = grid_data.get((x, y))
                if char:
                    boundary_chars.add(str(char))  # Ensure it's a string

        # Find common content patterns
        content_patterns: list[tuple[str, str]] = []

        for component in components:
            content = component.get("content", [])

            for line in content:
                # Look for common patterns like brackets, labels, etc.
                # Removed commented-out import re

                if button_match := re.search(r"\[(.+?)\]", line):
                    content_patterns.append(("button", button_match[0]))

                if checkbox_match := re.search(r"(\[\s*\]|\[X\]|□|■|☐|☑)", line):
                    content_patterns.append(("checkbox", checkbox_match[0]))

                if radio_match := re.search(r"(\(\s*\)|\(•\)|○|●)", line):
                    content_patterns.append(("radio", radio_match[0]))

        return {
            "boundary_chars": list(boundary_chars),
            "content_patterns": content_patterns,
        }

    def _generate_dsl_code(self, patterns_data: dict[str, dict[str, Any]]) -> str:
        # Renamed arg to avoid shadowing
        """Generate HUNT DSL code from extracted patterns."""
        dsl_code = []

        for component_type, type_patterns in patterns_data.items():
            # Generate HUNT code for this component type
            component_code = [f"< hunt {component_type}:", "    [INIT GATHER ="]

            if boundary_chars := type_patterns.get("boundary_chars", []):
                component_code.extend(
                    (f"        {{param tag:{component_type} =", "            (val")
                )
                component_code.extend(
                    f'             boundary_char:("{char}"),' for char in boundary_chars
                )
                component_code.extend(("            )", "        }"))
            # Add pluck parameters for content patterns
            content_patterns = type_patterns.get("content_patterns", [])
            pattern_types: dict[str, list[str]] = {}  # Corrected annotation value type

            for pattern_type, pattern_value in content_patterns:  # Renamed loop var
                if pattern_type not in pattern_types:
                    pattern_types[pattern_type] = []
                # Ensure pattern_value is treated as a string if needed for escape
                pattern_types[pattern_type].append(str(pattern_value))

            # Renamed loop variable here to avoid shadowing outer scope `patterns`
            for pattern_key, pattern_values in pattern_types.items():
                component_code.extend(
                    (f"        {{param pluck:{pattern_key} =", "            (val")
                )
                component_code.extend(
                    # Escape the regex pattern value before embedding in the string
                    f'             pattern:("{re.escape(value)}"),'
                    for value in pattern_values
                )
                component_code.extend(("            )", "        }"))
            component_code.extend(("    ]", "><EXEC>", ""))
            dsl_code.extend(component_code)

        return "\n".join(dsl_code)
