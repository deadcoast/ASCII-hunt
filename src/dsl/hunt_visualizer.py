class HuntVisualizer:
    def __init__(self, pattern_registry):
        self.pattern_registry = pattern_registry

    def visualize_pattern_matches(self, grid, components, output_file=None):
        """Visualize pattern matches on the grid."""
        # Create a copy of the grid for visualization
        visual_grid = grid.copy()

        # Create color mapping for different component types
        color_map = {
            "button": "blue",
            "checkbox": "green",
            "radio_button": "cyan",
            "dropdown": "magenta",
            "text_field": "yellow",
            "text_area": "red",
            "label": "white",
            "window": "blue",
            "panel": "green",
            "group_box": "cyan",
        }

        # Colorize components
        for component in components:
            ui_type = component.get("ui_type")

            if not ui_type:
                continue

            color = color_map.get(ui_type, "white")

            # Colorize component boundaries
            bounding_box = component.get("bounding_box")

            if bounding_box:
                x1, y1, x2, y2 = bounding_box

                # Draw colored border
                for x in range(x1, x2 + 1):
                    for y in range(y1, y2 + 1):
                        if x == x1 or x == x2 or y == y1 or y == y2:
                            visual_grid[y, x] = self._colorize(visual_grid[y, x], color)

        # Save or display the visualization
        if output_file:
            with open(output_file, "w") as f:
                for y in range(visual_grid.shape[0]):
                    line = "".join(visual_grid[y])
                    f.write(line + "\n")
        else:
            # Display in console
            for y in range(visual_grid.shape[0]):
                line = "".join(visual_grid[y])
                print(line)

    def _colorize(self, char, color):
        """Add ANSI color to a character."""
        color_codes = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
        }

        reset = "\033[0m"

        return color_codes.get(color, "") + char + reset
