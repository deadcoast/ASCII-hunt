class PatternOptimizer:
    def __init__(self, pattern_registry, interpreter):
        self.pattern_registry = pattern_registry
        self.interpreter = interpreter

    def optimize_patterns(self, grid_data, components):
        """Optimize patterns for better matching performance and accuracy."""
        # Get all patterns
        tracking_patterns = self.pattern_registry.get_all_tracking_patterns()

        optimized_patterns = {}

        # Group components by type
        grouped_components = {}

        for component in components:
            component_type = component.get("ui_type")

            if component_type:
                if component_type not in grouped_components:
                    grouped_components[component_type] = []

                grouped_components[component_type].append(component)

        # Optimize each pattern
        for name, pattern in tracking_patterns.items():
            # Check if there are components for this pattern
            component_type = name

            if component_type in grouped_components:
                components_of_type = grouped_components[component_type]

                # Optimize pattern for these components
                optimized_pattern = self._optimize_pattern(
                    pattern, components_of_type, grid_data
                )
                optimized_patterns[name] = optimized_pattern

        # Generate HUNT code for optimized patterns
        hunt_code = self._generate_hunt_code(optimized_patterns)

        return hunt_code

    def _optimize_pattern(self, pattern, components, grid_data):
        """Optimize a pattern for better matching with specific components."""
        # Extract common features from components
        boundary_chars = set()
        content_patterns = []

        for component in components:
            # Extract boundary characters
            boundary_points = component.get("boundary_points", [])

            for x, y in boundary_points:
                if 0 <= y < grid_data.shape[0] and 0 <= x < grid_data.shape[1]:
                    char = grid_data[y, x]
                    boundary_chars.add(char)

            # Extract content patterns
            content = component.get("content", [])

            for line in content:
                # Look for patterns in content
                import re

                # Check for common patterns
                button_match = re.search(r"\[(.+?)\]", line)
                checkbox_match = re.search(r"(\[\s*\]|\[X\]|□|■|☐|☑)", line)
                radio_match = re.search(r"(\(\s*\)|\(•\)|○|●)", line)

                if button_match:
                    content_patterns.append(("button", button_match.group(0)))
                elif checkbox_match:
                    content_patterns.append(("checkbox", checkbox_match.group(0)))
                elif radio_match:
                    content_patterns.append(("radio", radio_match.group(0)))

        # Create optimized pattern
        optimized_pattern = dict(pattern)

        # Update pattern rules
        rules = optimized_pattern.get("rules", [])

        for rule in rules:
            rule_type = rule.get("command")

            if rule_type == "tag":
                # Update tag values
                values = rule.get("values", [])

                # Add boundary characters
                for char in boundary_chars:
                    if char not in values:
                        values.append(char)

                rule["values"] = values

            elif rule_type == "pluck":
                # Update pluck rules
                for pattern_type, pattern_value in content_patterns:
                    if pattern_type == rule.get("target"):
                        values = rule.get("values", [])

                        if pattern_value not in values:
                            values.append(pattern_value)

                        rule["values"] = values

        optimized_pattern["rules"] = rules

        return optimized_pattern

    def _generate_hunt_code(self, patterns):
        """Generate HUNT DSL code from patterns."""
        hunt_code = []

        for name, pattern in patterns.items():
            # Generate HUNT code for this pattern
            hunt_code.append(f"< hunt Track:{name}")
            hunt_code.append("    [INIT GATHER =")

            for rule in pattern.get("rules", []):
                rule_type = rule.get("command")

                if rule_type == "tag":
                    hunt_code.append(f"        {{param tag:{name} =")
                    hunt_code.append("            (val")

                    for value in rule.get("values", []):
                        hunt_code.append(f'             "{value}",')

                    hunt_code.append("            )")
                    hunt_code.append("        }")

                elif rule_type == "pluck":
                    target = rule.get("target")
                    hunt_code.append(f"        {{param pluck:{target} =")
                    hunt_code.append("            (val")

                    for value in rule.get("values", []):
                        hunt_code.append(f'             "{value}",')

                    hunt_code.append("            )")
                    hunt_code.append("        }")

            hunt_code.append("    ]")
            hunt_code.append("><EXEC>")
            hunt_code.append("")

        return "\n".join(hunt_code)
