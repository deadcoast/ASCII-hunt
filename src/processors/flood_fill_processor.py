"""Flood Fill Processor Module.

This module provides a processor for identifying enclosed regions in ASCII art.
"""

from typing import Any

from src.core.ascii_grid import ASCIIGrid


class FloodFillProcessor:
    """A processor for identifying enclosed regions in ASCII art.

    This processor uses flood fill algorithms to identify enclosed regions in
    ASCII art and groups them into potential UI components.
    """

    def __init__(self) -> None:
        """Initialize the FloodFillProcessor class."""
        self.boundary_chars = set(["+", "-", "|", "/", "\\", "*", "#", "="])
        self.ignore_chars = set([" ", "\t", "\n"])
        self.fill_char = "."
        self.min_component_size = 4  # Minimum size to consider as a component

    def set_boundary_chars(self, chars: set[str]) -> None:
        """Set characters that are considered as boundaries.

        Args:
            chars: Set of characters that act as boundaries.
        """
        self.boundary_chars = set(chars)

    def set_ignore_chars(self, chars: set[str]) -> None:
        """Set characters that should be ignored during flood fill.

        Args:
            chars: Set of characters to ignore.
        """
        self.ignore_chars = set(chars)

    def set_fill_char(self, char: str) -> None:
        """Set character used for filling regions.

        Args:
            char: Character to use for filling regions.
        """
        self.fill_char = char

    def process(self, grid: ASCIIGrid, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Process an ASCIIGrid to identify enclosed regions.

        Args:
            grid: The ASCIIGrid to process.
            context: The context dictionary containing processing information.

        Returns:
            A list of identified components.
        """
        # Get grid dimensions
        width, height = grid.get_size()

        # Create a working copy of the grid
        grid_copy = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(grid.get_cell(x, y))
            grid_copy.append(row)

        # Store original grid in context
        context["original_grid"] = grid_copy

        # Track visited cells
        visited: set[tuple[int, int]] = set()

        # List of identified components
        components = []

        # Perform flood fill for each cell
        for y in range(height):
            for x in range(width):
                if (
                    (x, y) in visited
                    or grid_copy[y][x] in self.boundary_chars
                    or grid_copy[y][x] in self.ignore_chars
                ):
                    continue

                # Found an unvisited, non-boundary cell - perform flood fill
                component = self._flood_fill(grid_copy, x, y, width, height, visited)

                # Only include components of sufficient size
                if len(component) >= self.min_component_size:
                    # Calculate component bounds
                    min_x = min(cell[0] for cell in component)
                    min_y = min(cell[1] for cell in component)
                    max_x = max(cell[0] for cell in component)
                    max_y = max(cell[1] for cell in component)

                    # Create component object
                    comp_obj = {
                        "id": f"component_{len(components)}",
                        "cells": list(component),
                        "bounds": {
                            "x1": min_x,
                            "y1": min_y,
                            "x2": max_x,
                            "y2": max_y,
                            "width": max_x - min_x + 1,
                            "height": max_y - min_y + 1,
                        },
                        "size": len(component),
                        "type": "region",
                    }

                    components.append(comp_obj)

        # Store components in context
        context["flood_fill_components"] = components

        return components

    def _flood_fill(
        self,
        grid: list[list[str]],
        start_x: int,
        start_y: int,
        width: int,
        height: int,
        visited: set[tuple[int, int]],
    ) -> set[tuple[int, int]]:
        """Perform flood fill algorithm starting from a specific cell.

        Args:
            grid: The grid to fill.
            start_x: Starting x-coordinate.
            start_y: Starting y-coordinate.
            width: Width of the grid.
            height: Height of the grid.
            visited: Set of already visited cells.

        Returns:
            Set of cells that form the filled component.
        """
        # Check if starting point is valid
        if (
            start_x < 0
            or start_x >= width
            or start_y < 0
            or start_y >= height
            or grid[start_y][start_x] in self.boundary_chars
            or grid[start_y][start_x] in self.ignore_chars
            or (start_x, start_y) in visited
        ):
            return set()

        # Use queue-based approach for flood fill (breadth-first)
        queue = [(start_x, start_y)]
        component: set[tuple[int, int]] = set()

        while queue:
            x, y = queue.pop(0)

            # Check if cell was already processed
            if (x, y) in visited:
                continue

            # Mark cell as visited
            visited.add((x, y))

            # Add to component if not boundary or ignored
            if (
                grid[y][x] not in self.boundary_chars
                and grid[y][x] not in self.ignore_chars
            ):
                component.add((x, y))

                # Mark filled in the grid
                grid[y][x] = self.fill_char

                # Add neighbors to queue
                neighbors = [
                    (x + 1, y),  # right
                    (x - 1, y),  # left
                    (x, y + 1),  # down
                    (x, y - 1),  # up
                ]

                for nx, ny in neighbors:
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) not in visited
                        and grid[ny][nx] not in self.boundary_chars
                        and grid[ny][nx] not in self.ignore_chars
                    ):
                        queue.append((nx, ny))

        return component

    def merge_adjacent_components(
        self, components: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge adjacent components that are likely part of the same UI element.

        Args:
            components: List of components identified by flood fill.

        Returns:
            List of merged components.
        """
        if not components:
            return []

        # Create a copy of components to avoid modifying the original
        components = components.copy()

        # Track which components have been merged
        merged = [False] * len(components)

        # Resulting merged components
        merged_components = []

        for i in range(len(components)):
            if merged[i]:
                continue

            current = components[i].copy()
            merged[i] = True

            # Find adjacent components
            for j in range(i + 1, len(components)):
                if merged[j]:
                    continue

                # Check if components are adjacent
                if self._are_components_adjacent(current, components[j]):
                    # Merge components
                    current = self._merge_components(current, components[j])
                    merged[j] = True

            merged_components.append(current)

        return merged_components

    def _are_components_adjacent(
        self, comp1: dict[str, Any], comp2: dict[str, Any]
    ) -> bool:
        """Check if two components are adjacent.

        Args:
            comp1: First component.
            comp2: Second component.

        Returns:
            True if components are adjacent, False otherwise.
        """
        # Get component bounds
        bounds1 = comp1["bounds"]
        bounds2 = comp2["bounds"]

        # Check if bounds overlap or are adjacent
        return (
            # Horizontally adjacent (left/right)
            (
                bounds1["x2"] + 1 >= bounds2["x1"]
                and bounds1["x1"] - 1 <= bounds2["x2"]
                and bounds1["y2"] >= bounds2["y1"]
                and bounds1["y1"] <= bounds2["y2"]
            )
            or
            # Vertically adjacent (top/bottom)
            (
                bounds1["y2"] + 1 >= bounds2["y1"]
                and bounds1["y1"] - 1 <= bounds2["y2"]
                and bounds1["x2"] >= bounds2["x1"]
                and bounds1["x1"] <= bounds2["x2"]
            )
        )

    def _merge_components(
        self, comp1: dict[str, Any], comp2: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge two components into one.

        Args:
            comp1: First component.
            comp2: Second component.

        Returns:
            The merged component.
        """
        # Merge cells
        merged_cells = list(
            set(tuple(cell) for cell in comp1["cells"] + comp2["cells"])
        )

        # Calculate new bounds
        min_x = min(comp1["bounds"]["x1"], comp2["bounds"]["x1"])
        min_y = min(comp1["bounds"]["y1"], comp2["bounds"]["y1"])
        max_x = max(comp1["bounds"]["x2"], comp2["bounds"]["x2"])
        max_y = max(comp1["bounds"]["y2"], comp2["bounds"]["y2"])

        # Create merged component
        merged = {
            "id": f"{comp1['id']}_{comp2['id']}",
            "cells": merged_cells,
            "bounds": {
                "x1": min_x,
                "y1": min_y,
                "x2": max_x,
                "y2": max_y,
                "width": max_x - min_x + 1,
                "height": max_y - min_y + 1,
            },
            "size": len(merged_cells),
            "type": "merged_region",
        }

        return merged
