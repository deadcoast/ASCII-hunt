from typing import Any

from src.core.grid.ascii_grid import ASCIIGrid
from src.interface.api.dsl_visualizer import DslVisualizer
from src.interface.ui.dsl_grid import DslGrid
from src.patterns.definitions.pattern_matcher import PatternMatcher
from src.patterns.matching.flood_fill_processor import FloodFillProcessor
from src.patterns.rules.dsl_parser import DslParser
from src.patterns.rules.dsl_pattern_matchers import PatternRegistry
from src.patterns.rules.dsl_recognition_processor import DslRecognitionProcessor


class PatternDevelopmentEnvironment:
    def __init__(
        self, pattern_registry: PatternRegistry, interpreter: DslParser
    ) -> None:
        """Initialize the Pattern Development Environment."""
        self.pattern_registry = pattern_registry
        self.interpreter = interpreter
        self.visualizer = DslVisualizer(pattern_registry)

    def interactive_session(self, grid_data: DslGrid) -> None:
        """Start an interactive pattern development session."""
        # Display grid

        # Initialize components
        components = []

        while True:
            # Show menu

            choice = input("Enter choice (1-7): ")

            if choice == "1":
                if pattern_code := self._create_pattern():
                    self.interpreter.interpret(pattern_code)

            elif choice == "2":
                # Apply patterns
                components = self._apply_patterns(grid_data)

            elif choice == "3":
                # Visualize matches
                self.visualizer.visualize_pattern_matches(
                    grid_data.to_numpy(), components
                )

            elif choice == "4":
                # Edit pattern
                self._edit_pattern()

            elif choice == "5":
                # Test pattern
                self._test_pattern(grid_data)

            elif choice == "6":
                # Save patterns
                self._save_patterns()

            elif choice == "7":
                # Exit
                break

            else:
                pass

    def _create_pattern(self) -> str | None:
        """Create a new pattern."""

        lines = []
        while True:
            if line := input():
                lines.append(line)

            else:
                break

        return "\n".join(lines)

    def _apply_patterns(self, grid_data: DslGrid) -> list[dict[str, Any]]:
        """Apply patterns to the grid."""
        # Process the grid using the pattern registry
        processor = DslRecognitionProcessor(self.pattern_registry)

        # Perform initial component detection using FloodFillProcessor
        flood_fill_processor = FloodFillProcessor()
        # Create an ASCIIGrid instance from DslGrid data for the processor
        ascii_grid_obj = ASCIIGrid(grid_data.grid)
        components = flood_fill_processor.process(ascii_grid_obj, {})

        # Process components using HUNT patterns
        context = {"components": components, "grid": ascii_grid_obj}

        # Convert grid data to dict for DslRecognitionProcessor
        grid_dict_for_processor = {
            "grid": ascii_grid_obj.grid,
            "width": ascii_grid_obj.width,
            "height": ascii_grid_obj.height,
        }

        # Rename unused variable (result of process is handled via context)
        _ = processor.process(grid_dict_for_processor, context)
        # Return components potentially modified by the processor via context
        processed_components = context.get("components")
        return processed_components if isinstance(processed_components, list) else []

    def _edit_pattern(self) -> None:
        """Edit an existing pattern."""
        # Show available patterns - Access the patterns dictionary directly
        available_patterns = self.pattern_registry.patterns

        if not available_patterns:
            return

        pattern_names = list(available_patterns.keys())
        for i, name in enumerate(pattern_names):
            pass

        choice = input("Enter pattern number to edit: ")

        try:
            index = int(choice) - 1
            name = pattern_names[index]

            # Show pattern code
            # Rename unused variable
            _pattern_data = available_patterns[name]

            # Get new code

            lines = []
            while True:
                if line := input():
                    lines.append(line)

                else:
                    break

            pattern_code = "\n".join(lines)

            # Update pattern
            self.interpreter.interpret(pattern_code)

        except (ValueError, IndexError):
            pass

    def _test_pattern(self, grid_data: DslGrid) -> None:
        """Test a pattern on the grid."""
        # Show available patterns
        available_patterns = self.pattern_registry.patterns

        if not available_patterns:
            return

        pattern_names = list(available_patterns.keys())
        for i, name in enumerate(pattern_names):
            pass

        choice = input("Enter pattern number to test: ")

        try:
            index = int(choice) - 1
            name = pattern_names[index]
            _pattern_data = available_patterns[name]  # Rename unused

            # Process the grid using this pattern
            # Rename unused variable
            _processor = DslRecognitionProcessor(self.pattern_registry)

            # Perform initial component detection
            flood_fill_processor = FloodFillProcessor()
            # Create an ASCIIGrid instance from DslGrid data
            ascii_grid_obj = ASCIIGrid(grid_data.grid)
            components = flood_fill_processor.process(ascii_grid_obj, {})

            # Create a pattern matcher
            pattern_matcher = PatternMatcher(self.pattern_registry)

            # Convert grid_data to dictionary format for matcher
            grid_dict_for_matcher = {
                "grid": ascii_grid_obj.grid,
                "width": ascii_grid_obj.width,
                "height": ascii_grid_obj.height,
                "components": components,
            }

            # Test pattern on each component
            for component in components:
                # Pass the dictionary representation of the grid
                if matches := pattern_matcher.match_component(
                    grid_dict_for_matcher, component, {"test_pattern": name}
                ):
                    for match in matches:
                        print(f"Match found for pattern {name}:")
                        print(match)

        except (ValueError, IndexError):
            pass

    def _save_patterns(self) -> None:
        """Save patterns to a file."""
        filename = input("Enter filename to save patterns: ")

        # Get all patterns from the registry's dictionary
        all_patterns = self.pattern_registry.patterns
        # Removed assumption about extraction patterns

        # Generate HUNT code for patterns
        dsl_code: list[str] = []  # Added annotation

        # Use all_patterns dict
        for name, pattern_data in all_patterns.items():
            dsl_code.extend((f"< hunt Track:{name}", "    [INIT GATHER ="))
            # Assuming pattern_data dictionary structure is correct
            for rule in pattern_data.get("rules", []):
                dsl_code.extend(
                    (f"        {{param {rule['command']} =", "            (val")
                )
                dsl_code.extend(
                    f"             {value}," for value in rule.get("values", [])
                )
                dsl_code.extend(("            )", "        }"))
            dsl_code.extend(("    ]", "><EXEC>", ""))
        # Write to file
        with open(filename, "w") as f:
            f.write("\n".join(dsl_code))
