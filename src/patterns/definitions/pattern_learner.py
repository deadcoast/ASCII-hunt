import re
from typing import Any

from .pattern_registry import PatternRegistry


class PatternLearner:
    def __init__(self, pattern_registry: PatternRegistry) -> None:
        self.pattern_registry = pattern_registry

    def learn_from_examples(self, examples: list[dict[str, Any]]) -> str:
        """Learn patterns from annotated examples."""
        # Extract common patterns from examples
        patterns = self._extract_patterns(examples)

        # Generate HUNT DSL code for patterns
        hunt_code = self._generate_hunt_code(patterns)

        return hunt_code

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
            component_type = example.get("ui_type")

            if component_type:
                if component_type not in grouped_examples:
                    grouped_examples[component_type] = []

                grouped_examples[component_type].append(example)

        # Extract patterns for each component type
        for component_type, components in grouped_examples.items():
            type_patterns = self._extract_type_patterns(component_type, components)
            patterns[component_type] = type_patterns

        return patterns

    def _extract_type_patterns(
        self, component_type: str, components: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Extract patterns for a specific component type."""
        # Implement type-specific pattern extraction

        # For example, finding common boundary characters
        boundary_chars: set[str] = set()

        for component in components:
            boundary_points = component.get("boundary_points", [])

            for x, y in boundary_points:
                char = component.get("grid", {}).get((x, y))

                if char:
                    boundary_chars.add(char)

        # Find common content patterns
        content_patterns: list[tuple[str, str]] = []

        for component in components:
            content = component.get("content", [])

            for line in content:
                # Look for common patterns like brackets, labels, etc.
                import re

                # Check for button pattern
                button_match = re.search(r"\[(.+?)\]", line)

                if button_match:
                    content_patterns.append(("button", button_match.group(0)))

                # Check for checkbox pattern
                checkbox_match = re.search(r"(\[\s*\]|\[X\]|□|■|☐|☑)", line)

                if checkbox_match:
                    content_patterns.append(("checkbox", checkbox_match.group(0)))

                # Check for radio button pattern
                radio_match = re.search(r"(\(\s*\)|\(•\)|○|●)", line)

                if radio_match:
                    content_patterns.append(("radio", radio_match.group(0)))

        return {
            "boundary_chars": list(boundary_chars),
            "content_patterns": content_patterns,
        }

    def _generate_hunt_code(self, patterns: dict[str, dict[str, Any]]) -> str:
        """Generate HUNT DSL code from extracted patterns."""
        hunt_code = []

        for component_type, type_patterns in patterns.items():
            # Generate HUNT code for this component type
            component_code = [f"< hunt {component_type}:", "    [INIT GATHER ="]

            # Add tag parameters
            boundary_chars = type_patterns.get("boundary_chars", [])

            if boundary_chars:
                component_code.append(f"        {{param tag:{component_type} =")
                component_code.append("            (val")

                for char in boundary_chars:
                    component_code.append(f'             boundary_char:("{char}"),')

                component_code.append("            )")
                component_code.append("        }")

            # Add pluck parameters for content patterns
            content_patterns = type_patterns.get("content_patterns", [])
            pattern_types = {}

            for pattern_type, pattern in content_patterns:
                if pattern_type not in pattern_types:
                    pattern_types[pattern_type] = []

                pattern_types[pattern_type].append(pattern)

            for pattern_type, patterns in pattern_types.items():
                component_code.append(f"        {{param pluck:{pattern_type} =")
                component_code.append("            (val")

                for pattern in patterns:
                    component_code.append(
                        f'             pattern:("{re.escape(pattern)}"),'
                    )

                component_code.append("            )")
                component_code.append("        }")

            # Close the HUNT code
            component_code.append("    ]")
            component_code.append("><EXEC>")
            component_code.append("")

            hunt_code.extend(component_code)

        return "\n".join(hunt_code)
