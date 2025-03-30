"""ASCII Grid Module.

This module provides a class for representing and manipulating ASCII art grids.
"""

import itertools
from typing import Any


class ASCIIGrid:
    """A class for representing and manipulating ASCII art grids.

    The ASCIIGrid class stores the grid as a 2D array of characters and provides
    methods for accessing and manipulating the grid.
    """

    def __init__(self, grid_data: list[list[str]] | None = None) -> None:
        """Initialize the ASCIIGrid class.

        Args:
            grid_data: A 2D array of characters representing the grid.
                If None, an empty grid is created.
        """
        self.grid: list[list[str]] = grid_data if grid_data is not None else []
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0
        self.metadata: dict[str, Any] = {}

    @classmethod
    def from_string(cls, text: str) -> "ASCIIGrid":
        """Create an ASCIIGrid from a string.

        Args:
            text: A string representing the grid.

        Returns:
            An ASCIIGrid instance.
        """
        lines = text.splitlines()
        grid_data = [list(line) for line in lines]
        return cls(grid_data)

    def get_cell(self, x: int, y: int) -> str:
        """Get the character at the specified position.

        Args:
            x: The x-coordinate.
            y: The y-coordinate.

        Returns:
            The character at the specified position, or an empty string if the
            position is out of bounds.
        """
        return self.grid[y][x] if 0 <= y < self.height and 0 <= x < self.width else ""

    def set_cell(self, x: int, y: int, value: str) -> None:
        """Set the character at the specified position.

        Args:
            x: The x-coordinate.
            y: The y-coordinate.
            value: The character to set.
        """
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y][x] = value[0] if value else " "

    def get_region(self, x1: int, y1: int, x2: int, y2: int) -> list[list[str]]:
        """Get a rectangular region of the grid.

        Args:
            x1: The x-coordinate of the top-left corner.
            y1: The y-coordinate of the top-left corner.
            x2: The x-coordinate of the bottom-right corner.
            y2: The y-coordinate of the bottom-right corner.

        Returns:
            A 2D array of characters representing the region.
        """
        # Ensure coordinates are in bounds
        x1 = max(0, min(x1, self.width - 1))
        y1 = max(0, min(y1, self.height - 1))
        x2 = max(0, min(x2, self.width - 1))
        y2 = max(0, min(y2, self.height - 1))

        # Ensure x1 <= x2 and y1 <= y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        region = []
        for y in range(y1, y2 + 1):
            row = [self.grid[y][x] for x in range(x1, x2 + 1)]
            region.append(row)
        return region

    def set_region(self, x1: int, y1: int, region: list[list[str]]) -> None:
        """Set a rectangular region of the grid.

        Args:
            x1: The x-coordinate of the top-left corner.
            y1: The y-coordinate of the top-left corner.
            region: A 2D array of characters representing the region.
        """
        region_height = len(region)
        region_width = len(region[0]) if region_height > 0 else 0

        for y_offset, x_offset in itertools.product(
            range(region_height), range(region_width)
        ):
            x = x1 + x_offset
            y = y1 + y_offset
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = region[y_offset][x_offset]

    def to_string(self) -> str:
        """Convert the grid to a string.

        Returns:
            A string representing the grid.
        """
        return "\n".join(["".join(row) for row in self.grid])

    def get_size(self) -> tuple[int, int]:
        """Get the size of the grid.

        Returns:
            A tuple containing the width and height of the grid.
        """
        return (self.width, self.height)

    def resize(self, width: int, height: int, fill_char: str = " ") -> None:
        """Resize the grid.

        Args:
            width: The new width.
            height: The new height.
            fill_char: The character to use for filling new cells.
        """
        # Create a new grid with the specified size
        new_grid = [[fill_char for _ in range(width)] for _ in range(height)]

        # Copy existing data to new grid
        for y, x in itertools.product(
            range(min(self.height, height)), range(min(self.width, width))
        ):
            new_grid[y][x] = self.grid[y][x]

        # Update grid data
        self.grid = new_grid
        self.width = width
        self.height = height

    def clear(self, fill_char: str = " ") -> None:
        """Clear the grid.

        Args:
            fill_char: The character to use for filling cells.
        """
        for y, x in itertools.product(range(self.height), range(self.width)):
            self.grid[y][x] = fill_char
