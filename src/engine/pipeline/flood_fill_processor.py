"""Flood fill processor for ASCII grid processing."""

from dataclasses import dataclass

import numpy as np


@dataclass
class Point:
    """2D point representation."""

    x: int
    y: int


class FloodFillProcessor:
    """Processes ASCII grids using flood fill algorithm."""

    def __init__(self, diagonal: bool = False) -> None:
        """Initialize flood fill processor.

        Args:
            diagonal: Whether to include diagonal neighbors in flood fill
        """
        self.diagonal = diagonal
        self._directions = self._get_directions()

    def _get_directions(self) -> list[tuple[int, int]]:
        """Get list of valid directions for flood fill."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # NESW
        if self.diagonal:
            directions.extend([(1, 1), (1, -1), (-1, -1), (-1, 1)])  # Diagonals
        return directions

    def process(self, grid: np.ndarray) -> list[dict]:
        """Process ASCII grid to identify and analyze components.

        Args:
            grid: 2D numpy array representing ASCII grid

        Returns:
            List of component dictionaries with position and metadata
        """
        if grid.size == 0:
            return []

        # Find all non-space characters (assuming spaces are background)
        background_char = " "
        components = []

        # Find all unique characters in the grid
        unique_chars = set(np.unique(grid))
        if background_char in unique_chars:
            unique_chars.remove(background_char)

        # Process each character type separately
        all_component_points = []
        for char in unique_chars:
            char_components = self.find_connected_components(grid, target_value=char)
            all_component_points.extend(char_components)

        for idx, component_points in enumerate(all_component_points):
            if not component_points:
                continue

            # Convert points to NumPy array for efficient boundary calculation
            points_array = np.array(list(component_points))

            # Extract component boundaries using NumPy and convert to Python int
            min_x = int(np.min(points_array[:, 0]).item())
            max_x = int(np.max(points_array[:, 0]).item())
            min_y = int(np.min(points_array[:, 1]).item())
            max_y = int(np.max(points_array[:, 1]).item())

            # Create a component representation
            component = {
                "id": f"component_{idx}",
                "points": list(component_points),
                "bounds": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y,
                    "width": max_x - min_x + 1,
                    "height": max_y - min_y + 1,
                },
                "content": self._extract_component_content(grid, component_points),
            }

            components.append(component)

        return components

    def _extract_component_content(
        self, grid: np.ndarray, points: set[tuple[int, int]]
    ) -> dict:
        """Extract content details from a component.

        Args:
            grid: ASCII grid containing the component
            points: Set of (x, y) points in the component

        Returns:
            Dictionary with component content details
        """
        # Count character occurrences
        char_counts: dict[str, int] = {}

        for x, y in points:
            char = grid[x, y]
            char_counts[char] = char_counts.get(char, 0) + 1

        # Get most common character
        most_common = max(char_counts.items(), key=lambda x: x[1], default=("", 0))

        return {
            "char_counts": char_counts,
            "most_common_char": most_common[0],
            "unique_chars": list(char_counts.keys()),
        }

    def flood_fill(
        self, grid: np.ndarray, start: Point, target_value: str, replacement_value: str
    ) -> np.ndarray:
        """Perform flood fill on ASCII grid.

        Args:
            grid: 2D numpy array representing ASCII grid
            start: Starting point for flood fill
            target_value: Value to replace
            replacement_value: Value to fill with

        Returns:
            Modified grid after flood fill
        """
        if not self._is_valid_point(grid, start):
            return grid

        if grid[start.x, start.y] != target_value:
            return grid

        result = grid.copy()
        self._flood_fill_recursive(
            result, start, target_value, replacement_value, set()
        )
        return result

    def _flood_fill_recursive(
        self,
        grid: np.ndarray,
        point: Point,
        target: str,
        replacement: str,
        visited: set[tuple[int, int]],
    ) -> None:
        """Recursive helper for flood fill."""
        if not self._is_valid_point(grid, point):
            return

        pos = (point.x, point.y)
        if pos in visited or grid[point.x, point.y] != target:
            return

        visited.add(pos)
        grid[point.x, point.y] = replacement

        # Process neighbors
        for dx, dy in self._directions:
            next_point = Point(point.x + dx, point.y + dy)
            self._flood_fill_recursive(grid, next_point, target, replacement, visited)

    def _is_valid_point(self, grid: np.ndarray, point: Point) -> bool:
        """Check if point is within grid bounds."""
        return 0 <= point.x < grid.shape[0] and 0 <= point.y < grid.shape[1]

    def find_connected_components(
        self, grid: np.ndarray, target_value: str
    ) -> list[set[tuple[int, int]]]:
        """Find all connected components with target value.

        Args:
            grid: 2D numpy array representing ASCII grid
            target_value: Value to find components for

        Returns:
            List of sets containing points in each component
        """
        components: list[set[tuple[int, int]]] = []
        visited: set[tuple[int, int]] = set()

        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if (i, j) not in visited and grid[i, j] == target_value:
                    component_points: set[tuple[int, int]] = set()
                    self._flood_fill_component(
                        grid, Point(i, j), target_value, component_points, visited
                    )
                    if component_points:
                        components.append(component_points)

        return components

    def _flood_fill_component(
        self,
        grid: np.ndarray,
        point: Point,
        target: str,
        component: set[tuple[int, int]],
        visited: set[tuple[int, int]],
    ) -> None:
        """Recursive helper for finding connected components."""
        if not self._is_valid_point(grid, point):
            return

        pos = (point.x, point.y)
        if pos in visited or grid[point.x, point.y] != target:
            return

        visited.add(pos)
        component.add(pos)

        # Process neighbors
        for dx, dy in self._directions:
            next_point = Point(point.x + dx, point.y + dy)
            self._flood_fill_component(grid, next_point, target, component, visited)
