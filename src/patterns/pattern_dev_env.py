from typing import Any

from recognition.hunt_recognition_processor import HuntRecognitionProcessor
from src.dsl.hunt_grid import HuntGrid
from src.dsl.hunt_parser import HuntParser
from src.patterns.pattern_matcher import PatternMatcher
from src.patterns.pattern_registry import PatternRegistry
from visualization.hunt_visualizer import HuntVisualizer


class PatternDevelopmentEnvironment:
    def __init__(
        self, pattern_registry: PatternRegistry, interpreter: HuntParser
    ) -> None:
        self.pattern_registry = pattern_registry
        self.interpreter = interpreter
        self.visualizer = HuntVisualizer(pattern_registry)

    def interactive_session(self, grid_data: HuntGrid) -> None:
        """Start an interactive pattern development session."""
        # Display grid
        print("ASCII Grid:")
        print(grid_data.to_string())
        print()

        # Initialize components
        components = []

        while True:
            # Show menu
            print("Pattern Development Menu:")
            print("1. Create pattern")
            print("2. Apply patterns")
            print("3. Visualize matches")
            print("4. Edit pattern")
            print("5. Test pattern")
            print("6. Save patterns")
            print("7. Exit")

            choice = input("Enter choice (1-7): ")

            if choice == "1":
                # Create pattern
                pattern_code = self._create_pattern()

                if pattern_code:
                    self.interpreter.interpret(pattern_code)
                    print("Pattern created successfully.")

            elif choice == "2":
                # Apply patterns
                components = self._apply_patterns(grid_data)

                print(f"Applied patterns, found {len(components)} components.")

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
                print("Exiting pattern development session.")
                break

            else:
                print("Invalid choice. Please try again.")

    def _create_pattern(self) -> str | None:
        """Create a new pattern."""
        print("Enter HUNT DSL code for the pattern (end with a blank line):")

        lines = []
        while True:
            line = input()

            if not line:
                break

            lines.append(line)

        pattern_code = "\n".join(lines)

        return pattern_code

    def _apply_patterns(self, grid_data: HuntGrid) -> list[dict[str, Any]]:
        """Apply patterns to the grid."""
        # Process the grid using the pattern registry
        processor = HuntRecognitionProcessor(self.pattern_registry)

        # Perform initial component detection
        from FloodFillProcessor import FloodFillProcessor

        flood_fill_processor = FloodFillProcessor()
        components = flood_fill_processor.process(grid_data, {})

        # Process components using HUNT patterns
        context = {"components": components, "grid": grid_data}
        processed_components = processor.process(grid_data, context)

        return processed_components

    def _edit_pattern(self) -> None:
        """Edit an existing pattern."""
        # Show available patterns
        tracking_patterns = self.pattern_registry.get_all_tracking_patterns()

        if not tracking_patterns:
            print("No patterns available to edit.")
            return

        print("Available patterns:")

        for i, (name, _) in enumerate(tracking_patterns.items()):
            print(f"{i + 1}. {name}")

        choice = input("Enter pattern number to edit: ")

        try:
            index = int(choice) - 1
            name = list(tracking_patterns.keys())[index]

            # Show pattern code
            pattern = tracking_patterns[name]
            print(f"Pattern '{name}':")
            print(pattern)

            # Get new code
            print("Enter new HUNT DSL code (end with a blank line):")

            lines = []
            while True:
                line = input()

                if not line:
                    break

                lines.append(line)

            pattern_code = "\n".join(lines)

            # Update pattern
            self.interpreter.interpret(pattern_code)

            print("Pattern updated successfully.")

        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")

    def _test_pattern(self, grid_data: HuntGrid) -> None:
        """Test a pattern on the grid."""
        # Show available patterns
        tracking_patterns = self.pattern_registry.get_all_tracking_patterns()

        if not tracking_patterns:
            print("No patterns available to test.")
            return

        print("Available patterns:")

        for i, (name, _) in enumerate(tracking_patterns.items()):
            print(f"{i + 1}. {name}")

        choice = input("Enter pattern number to test: ")

        try:
            index = int(choice) - 1
            name = list(tracking_patterns.keys())[index]
            pattern = tracking_patterns[name]

            # Process the grid using this pattern
            processor = HuntRecognitionProcessor(self.pattern_registry)

            # Perform initial component detection
            from FloodFillProcessor import FloodFillProcessor

            flood_fill_processor = FloodFillProcessor()
            components = flood_fill_processor.process(grid_data, {})

            # Create a pattern matcher
            pattern_matcher = PatternMatcher(self.pattern_registry)

            # Convert grid_data to dictionary format
            grid_dict = {
                "grid": grid_data.grid,
                "width": grid_data.width,
                "height": grid_data.height,
                "components": grid_data.components,
            }

            # Test pattern on each component
            for component in components:
                matches = pattern_matcher.match_component(
                    grid_dict, component, {"test_pattern": name}
                )

                if matches:
                    print(f"Component {component.get('id')} matched pattern '{name}':")
                    for match in matches:
                        print(f"  Confidence: {match['confidence']:.2f}")
                        print(f"  Properties: {match['properties']}")
                        print(f"  Match: {match['match']}")
                        print(f"  Component: {component['ui_type']}")
                        print(f"  Bounding Box: {component.get('bounding_box')}")
                        print(f"  Content: {component.get('content')}")
                        print(f"  Metadata: {component.get('metadata')}")
                        print(f"  Relationships: {component.get('relationships')}")
                        print(f"  UI Type: {component.get('ui_type')}")
                        print(f"  ID: {component.get('id')}")
                        print(f"  Index: {component.get('index')}")
                        print(f"  Row: {component.get('row')}")
                        print(f"  Column: {component.get('column')}")
                        print(f"  Width: {component.get('width')}")
                        print(f"  Height: {component.get('height')}")
                        print(f"  X: {component.get('x')}")
                        print(f"  Y: {component.get('y')}")
                        print(f"  Z: {component.get('z')}")
                        print(f"  Rotation: {component.get('rotation')}")
                        print(f"  Scale: {component.get('scale')}")
                        print(f"  Visible: {component.get('visible')}")

        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")

    def _save_patterns(self) -> None:
        """Save patterns to a file."""
        filename = input("Enter filename to save patterns: ")

        # Get all patterns
        tracking_patterns = self.pattern_registry.get_all_tracking_patterns()
        extraction_patterns = self.pattern_registry.get_all_extraction_patterns()

        # Generate HUNT code for patterns
        hunt_code = []

        for name, pattern in tracking_patterns.items():
            # Generate HUNT code for tracking pattern
            # This is a simplified version; a real implementation would need to convert
            # the internal pattern representation back to HUNT DSL code
            hunt_code.append(f"< hunt Track:{name}")
            hunt_code.append("    [INIT GATHER =")

            for rule in pattern.get("rules", []):
                hunt_code.append(f"        {{param {rule['command']} =")
                hunt_code.append("            (val")

                for value in rule.get("values", []):
                    hunt_code.append(f"             {value},")

                hunt_code.append("            )")
                hunt_code.append("        }")

            hunt_code.append("    ]")
            hunt_code.append("><EXEC>")
            hunt_code.append("")

        # Write to file
        with open(filename, "w") as f:
            f.write("\n".join(hunt_code))

        print(f"Patterns saved to {filename}")
