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
        visited = set()

        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if (i, j) not in visited and grid[i, j] == target_value:
                    component = set()
                    self._flood_fill_component(
                        grid, Point(i, j), target_value, component, visited
                    )
                    if component:
                        components.append(component)

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
