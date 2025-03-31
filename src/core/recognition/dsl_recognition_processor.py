"""Process grid data using HUNT patterns."""

import pathlib
from typing import Any

from src.core.dsl.dsl_interpreter import DslInterpreter
from src.core.recognition.dsl_pattern_registry import PatternRegistry
from src.patterns.definitions.pattern_matcher import PatternMatcher


class DslRecognitionProcessor:
    """Process grid data using HUNT patterns."""

    def __init__(self, pattern_registry: PatternRegistry | None = None) -> None:
        """Initialize the DslRecognitionProcessor.

        Args:
            pattern_registry: The pattern registry to use.
        """
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.interpreter = DslInterpreter(self.pattern_registry)
        self.pattern_matcher = PatternMatcher(self.pattern_registry)

    def process(
        self, grid_data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Process grid data using HUNT patterns."""
        if context is None:
            context = {}

        # Load HUNT patterns from context if available
        dsl_patterns: list[str] = context.get("dsl_patterns", [])

        for pattern in dsl_patterns:
            self.interpreter.interpret(pattern, context)

        # Process components using the pattern matcher
        components: list[dict[str, Any]] = context.get("components", [])
        processed_components: list[dict[str, Any]] = []

        for component in components:
            if matches := self.pattern_matcher.match_component(
                grid_data, component, context
            ):
                # Get the best match
                best_match = matches[0]

                # Update component
                component["ui_type"] = best_match["component_type"]
                component.update(best_match["properties"])

            processed_components.append(component)

        # Match relationships
        relationships = self.pattern_matcher.match_relationships(
            grid_data, processed_components, context
        )

        # Update context
        context["components"] = processed_components
        context["relationships"] = relationships

        return processed_components

    def load_dsl_pattern_file(self, file_path: str) -> dict[str, Any] | None:
        """Load HUNT patterns from a file."""
        dsl_code = pathlib.Path(file_path).read_text()
        return self.interpreter.interpret(dsl_code)

    def register_built_in_patterns(self) -> None:
        """Register built-in HUNT patterns."""
        # Register patterns for common UI components

        # Button pattern
        button_pattern = """
        < hunt Track:
            [INIT GATHER =
                {param tag:button =
                    (val "[", "]")
                }
            ]
        ><EXEC>
        """

        self.interpreter.interpret(button_pattern)

        # Checkbox pattern
        checkbox_pattern = """
        < hunt Track:
            [INIT GATHER =
                {param tag:checkbox =
                    (val "□", "■", "☐", "☑", "[ ]", "[X]")
                }
            ]
        ><EXEC>
        """

        self.interpreter.interpret(checkbox_pattern)

        # Text field pattern
        text_field_pattern = """
        < hunt Track:
            [INIT GATHER =
                {param tag:text_field =
                    (val "_____", "____", "......")
                }
                {param pluck:field_text =
                    (val "([A-Za-z0-9_]+)")
                }
            ]
        ><EXEC>
        """

        self.interpreter.interpret(text_field_pattern)

        # Add more built-in patterns as needed
