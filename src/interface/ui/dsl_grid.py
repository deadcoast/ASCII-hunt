"""Grid management for the HUNT DSL."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from src.core.dsl.dsl_error import DSLFatalError


class DslGrid:
    """A grid for tracking and manipulating ASCII art components."""

    def __init__(self) -> None:
        """Initialize an empty grid."""
        self.grid: list[list[str]] = []
        self.width: int = 0
        self.height: int = 0
        self.components: list[dict[str, Any]] = []

    def to_string(self) -> str:
        """Convert grid to string representation.

        Returns:
            str: String representation of the grid
        """
        return "\n".join("".join(row) for row in self.grid)

    def to_numpy(self) -> NDArray[np.str_]:
        """Convert grid to numpy array.

        Returns:
            np.ndarray: Numpy array representation of the grid
        """
        return np.array(self.grid)

    def load_grid(self, data: str | list[str]) -> None:
        """Load grid data from string or list of strings.

        Args:
            data: Grid data as a string (newline separated) or list of strings
        """
        lines = data.split("\n") if isinstance(data, str) else data
        self.grid = [list(line) for line in lines]
        self.height = len(self.grid)
        self.width = max((len(line) for line in self.grid), default=0)

    def scan(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Scan the grid for components based on parameters.

        Args:
            params: Scan parameters including patterns to match

        Returns:
            List[Dict[str, Any]]: List of found components
        """
        # TODO: Implement grid scanning
        return []

    def extract(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract data from a region of the grid.

        Args:
            params: Extraction parameters including region coordinates

        Returns:
            Dict[str, Any]: Extracted data
        """
        # TODO: Implement data extraction
        return {}

    def get_region(self, x: int, y: int, width: int, height: int) -> list[list[str]]:
        """Get a rectangular region from the grid.

        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            width: Width of region
            height: Height of region

        Returns:
            List[List[str]]: Region data

        Raises:
            DSLFatalError: If region is out of bounds
        """
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            msg = "Region out of bounds"
            raise DSLFatalError(msg)

        return [self.grid[y + dy][x : x + width] for dy in range(height)]

    def find_pattern(
        self, pattern: str, start_x: int | None = None, start_y: int | None = None
    ) -> list[tuple[int, int]]:
        """Find all occurrences of a pattern in the grid.

        Args:
            pattern: Pattern to search for
            start_x: Optional starting x coordinate
            start_y: Optional starting y coordinate

        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates where pattern was found
        """
        # TODO: Implement pattern finding
        return []

    def flood_fill(self, x: int, y: int, target: str, replacement: str) -> None:
        """Flood fill from a point.

        Args:
            x: Starting x coordinate
            y: Starting y coordinate
            target: Character to replace
            replacement: Character to fill with

        Raises:
            DSLFatalError: If coordinates are out of bounds
        """
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            msg = "Coordinates out of bounds"
            raise DSLFatalError(msg)

        if self.grid[y][x] != target:
            return

        self.grid[y][x] = replacement

        # Recursively fill adjacent cells
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if (
                0 <= new_x < self.width
                and 0 <= new_y < self.height
                and self.grid[new_y][new_x] == target
            ):
                self.flood_fill(new_x, new_y, target, replacement)

    def get_component_at(self, x: int, y: int) -> dict[str, Any] | None:
        """Get component at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Optional[Dict[str, Any]]: Component if found at coordinates
        """
        for component in self.components:
            x1 = component.get("x", 0)
            y1 = component.get("y", 0)
            width = component.get("width", 0)
            height = component.get("height", 0)

            if x1 <= x < x1 + width and y1 <= y < y1 + height:
                return component

        return None
