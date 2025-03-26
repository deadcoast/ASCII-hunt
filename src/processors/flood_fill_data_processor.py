import re
from typing import Any

import numpy as np
from numpy.typing import NDArray

from src.data_structures.ascii_grid import ASCIIGrid


class FloodFillProcessor:
    def __init__(self):
        self.boundary_chars = set("┌┐└┘│─┬┴├┤┼╔╗╚╝║═╦╩╠╣╬┏┓┗┛┃━┳┻┣┫╋╭╮╰╯")
        self.grid: ASCIIGrid | None = None
        self.data: NDArray | None = None
        self.boundary_mask: NDArray | None = None
        self.visited: NDArray | None = None

    def process(
        self,
        grid_data: ASCIIGrid | str | NDArray,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Process a grid to identify enclosed regions using flood fill."""
        if context is None:
            context = {}

        # Convert input to ASCIIGrid if needed
        grid: ASCIIGrid
        if isinstance(grid_data, ASCIIGrid):
            grid = grid_data
        elif isinstance(grid_data, str):
            grid = ASCIIGrid(grid_data)
        elif isinstance(grid_data, np.ndarray):
            height, width = grid_data.shape
            grid = ASCIIGrid(width=width, height=height, data=grid_data)
        else:
            raise ValueError("Input must be ASCIIGrid, string, or NumPy array")

        # Get NumPy array for processing
        grid_array = grid.to_numpy()
        height, width = grid_array.shape

        # Initialize visited mask and result list
        visited = np.zeros((height, width), dtype=bool)
        boundary_mask = grid.get_boundary_mask()

        # Mark boundaries as visited
        visited[boundary_mask] = True

        # Store detected components
        components: list[dict[str, Any]] = []

        # Process all cells
        for y in range(height):
            for x in range(width):
                if not visited[y, x]:
                    # Perform flood fill from this seed point
                    component = self._flood_fill(grid_array, visited, x, y)

                    if component:
                        # Add component to results
                        components.append(component)

                        # Mark all points as visited
                        for px, py in component["interior_points"]:
                            visited[py, px] = True

        # Post-process components
        processed_components = self._process_components(components, grid_array)

        # Store in context for other stages
        context["flood_fill_results"] = processed_components

        return processed_components

    def _flood_fill(
        self, grid_array: NDArray, visited: NDArray, start_x: int, start_y: int
    ) -> dict[str, Any] | None:
        """Perform flood fill from a starting point."""
        height, width = grid_array.shape
        queue: list[tuple[int, int]] = [(start_x, start_y)]
        interior_points: set[tuple[int, int]] = {(start_x, start_y)}
        boundary_points: set[tuple[int, int]] = set()

        # Process all connected points
        while queue:
            x, y = queue.pop(0)

            # Check neighbors in all 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                # Check if in bounds
                if 0 <= nx < width and 0 <= ny < height:
                    if visited[ny, nx]:
                        # If it's a boundary character, add to boundary points
                        if grid_array[ny, nx] in self.boundary_chars:
                            boundary_points.add((nx, ny))
                    else:
                        # Mark as visited
                        visited[ny, nx] = True

                        # Add to queue and interior points
                        queue.append((nx, ny))
                        interior_points.add((nx, ny))

        # Only create a component if we have boundary points
        if boundary_points:
            # Calculate bounding box
            if interior_points:
                x_coords = [int(x) for x, y in interior_points]
                y_coords = [int(y) for x, y in interior_points]

                min_x = min(x_coords)
                max_x = max(x_coords)
                min_y = min(y_coords)
                max_y = max(y_coords)

                # Create component with explicit integer arithmetic
                width = int(max_x) - int(min_x) + 1
                height = int(max_y) - int(min_y) + 1

                component: dict[str, Any] = {
                    "interior_points": interior_points,
                    "boundary_points": boundary_points,
                    "bounding_box": (min_x, min_y, max_x, max_y),
                    "width": width,
                    "height": height,
                }

                return component

        return None

    def _process_components(
        self, components: list[dict[str, Any]], grid_array: NDArray
    ) -> list[dict[str, Any]]:
        """Post-process detected components to extract additional information."""
        processed_components: list[dict[str, Any]] = []

        for i, component in enumerate(components):
            # Assign ID
            component["id"] = f"component_{i}"

            # Extract content
            content = self._extract_component_content(component, grid_array)
            component["content"] = content

            # Determine component type based on boundary characters
            component_type = self._determine_component_type(component, grid_array)
            component["type"] = component_type

            # Extract special features
            special_features = self._extract_special_features(component, grid_array)
            component["special_features"] = special_features

            processed_components.append(component)

        return processed_components

    def _extract_component_content(
        self, component: dict[str, Any], grid_array: NDArray
    ) -> list[str]:
        """Extract the content (characters) from a component's interior."""
        # Get bounding box
        min_x, min_y, max_x, max_y = component["bounding_box"]

        # Extract content rows
        content_rows: list[str] = []
        for y in range(min_y, max_y + 1):
            row: list[str] = []
            for x in range(min_x, max_x + 1):
                if (x, y) in component["interior_points"]:
                    row.append(grid_array[y, x])
            if row:
                content_rows.append("".join(row))

        return content_rows

    def _determine_component_type(
        self, component: dict[str, Any], grid_array: NDArray
    ) -> str:
        """Determine the type of component based on boundary characters."""
        # Extract boundary characters and convert to strings
        boundary_chars = [
            str(grid_array[y, x]) for x, y in component["boundary_points"]
        ]
        char_set = set(boundary_chars)

        # Check for specific boundary patterns
        if all(c in "┌┐└┘│─" for c in char_set):
            return "single_line_box"
        if all(c in "╔╗╚╝║═" for c in char_set):
            return "double_line_box"
        if all(c in "┏┓┗┛┃━" for c in char_set):
            return "heavy_line_box"
        if all(c in "╭╮╰╯│─" for c in char_set):
            return "rounded_box"
        return "custom_box"

    def _extract_special_features(
        self, component: dict[str, Any], grid_array: NDArray
    ) -> dict[str, Any]:
        """Extract special features from a component."""
        # Look for special characters in content
        special_features: dict[str, Any] = {}

        # Check for button markers [text]
        content_text = " ".join(component["content"])
        if re.search(r"\[.*\]", content_text):
            special_features["button_text"] = re.findall(r"\[(.*?)\]", content_text)
            special_features["is_button"] = True

        # Check for other special indicators
        special_chars = {
            "●": "active_indicator",
            "○": "inactive_indicator",
            "▼": "dropdown_expanded",
            "▶": "dropdown_collapsed",
            "□": "checkbox_unchecked",
            "■": "checkbox_checked",
            "☐": "checkbox_unchecked",
            "☑": "checkbox_checked",
        }

        for char, feature in special_chars.items():
            if any(char in row for row in component["content"]):
                special_features[feature] = True

        return special_features

    def process_incremental(
        self, delta: dict[str, Any], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Process incremental updates to the grid."""
        # Check if we have the original grid in context
        if "grid" not in context:
            raise ValueError(
                "Cannot process incremental update without original grid in context"
            )

        # Get the original grid
        original_grid = context["grid"]

        # Apply the delta to create a new grid
        if delta["type"] == "character_change":
            # Single character change
            x, y, new_char = delta["data"]
            updated_grid = original_grid.copy()
            updated_grid.set_char(x, y, new_char)

        elif delta["type"] == "region_change":
            # Region change
            x1, y1, x2, y2, new_content = delta["data"]
            updated_grid = original_grid.copy()

            # Apply new content to region
            for y, row in enumerate(new_content):
                for x, char in enumerate(row):
                    if (
                        0 <= x1 + x < updated_grid.width
                        and 0 <= y1 + y < updated_grid.height
                    ):
                        updated_grid.set_char(x1 + x, y1 + y, char)

        elif delta["type"] == "full_update":
            # Full grid update
            updated_grid = ASCIIGrid(delta["data"])

        else:
            raise ValueError(f"Unknown delta type: {delta['type']}")

        # Process the updated grid
        return self.process(updated_grid, context)

    def process_data(self, data: str) -> None:
        """Process the input data.

        Args:
            data: Input data to process
        """
        # Create grid from input data
        self.grid = ASCIIGrid(data)

        # Convert to numpy array for processing
        self.data = self.grid.to_numpy()

        # Get boundary mask
        self.boundary_mask = self.grid.get_boundary_mask()

        # Initialize visited array
        self.visited = np.zeros_like(self.data, dtype=bool)
