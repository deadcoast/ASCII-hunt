from typing import Any

from ..patterns.pattern_matcher import PatternMatcher
from ..patterns.pattern_registry import PatternRegistry
from .hunt_interpreter import HuntInterpreter


class HuntRecognitionProcessor:
    def __init__(self, pattern_registry: PatternRegistry | None = None) -> None:
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.interpreter = HuntInterpreter(self.pattern_registry)
        self.pattern_matcher = PatternMatcher(self.pattern_registry)

    def process(
        self, grid_data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Process grid data using HUNT patterns."""
        if context is None:
            context = {}

        # Load HUNT patterns from context if available
        hunt_patterns: list[str] = context.get("hunt_patterns", [])

        for pattern in hunt_patterns:
            self.interpreter.interpret(pattern, context)

        # Process components using the pattern matcher
        components: list[dict[str, Any]] = context.get("components", [])
        processed_components: list[dict[str, Any]] = []

        for component in components:
            # Match component against patterns
            matches = self.pattern_matcher.match_component(
                grid_data, component, context
            )

            if matches:
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

    def load_hunt_pattern_file(self, file_path: str) -> Any:
        """Load HUNT patterns from a file."""
        with open(file_path) as f:
            hunt_code = f.read()

        return self.interpreter.interpret(hunt_code)

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
