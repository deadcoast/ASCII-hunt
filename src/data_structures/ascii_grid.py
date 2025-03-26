import numpy as np
from numpy.typing import NDArray


class ASCIIGrid:
    """A 2D grid for storing ASCII characters with numpy support."""

    def __init__(
        self,
        width: int | str,
        height: int | None = None,
        data: list[list[str]] | NDArray | None = None,
    ):
        """Initialize an ASCII grid.

        Args:
            width: Width of the grid in characters, or a string to parse
            height: Height of the grid in characters (optional if width is a string)
            data: Initial data for the grid (optional)
        """
        if isinstance(width, str):
            # Parse string input
            lines = width.strip().split("\n")
            self.height = len(lines)
            self.width = max(len(line) for line in lines)
            self.grid = np.array(
                [[" " for _ in range(self.width)] for _ in range(self.height)]
            )
            for y, line in enumerate(lines):
                for x, char in enumerate(line):
                    self.grid[y, x] = char
        else:
            self.width = width
            self.height = height or 24
            if data is not None:
                if isinstance(data, np.ndarray):
                    self.grid = data.astype(str)
                else:
                    self.grid = np.array(data)
            else:
                self.grid = np.array(
                    [[" " for _ in range(self.width)] for _ in range(self.height)]
                )

    def set_char(self, x: int, y: int, char: str) -> None:
        """Set a character at the specified position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = char[0] if char else " "

    def get_char(self, x: int, y: int) -> str:
        """Get the character at the specified position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x]
        return " "

    def clear(self) -> None:
        """Clear the grid by filling it with spaces."""
        self.grid.fill(" ")

    def resize(self, width: int, height: int) -> None:
        """Resize the grid, preserving existing content where possible."""
        new_grid = np.full((height, width), " ", dtype=str)
        h = min(height, self.height)
        w = min(width, self.width)
        new_grid[:h, :w] = self.grid[:h, :w]
        self.width = width
        self.height = height
        self.grid = new_grid

    def get_size(self) -> tuple[int, int]:
        """Get the current size of the grid."""
        return self.width, self.height

    def get_region(self, x: int, y: int, width: int, height: int) -> NDArray:
        """Get a rectangular region of the grid."""
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(self.width, x + width)
        y2 = min(self.height, y + height)
        return self.grid[y1:y2, x1:x2].copy()

    def set_region(self, x: int, y: int, region: list[list[str]] | NDArray) -> None:
        """Set a rectangular region of the grid."""
        if not isinstance(region, np.ndarray):
            region = np.array(region)
        if region.size == 0:
            return
        x1 = max(0, x)
        y1 = max(0, y)
        h, w = region.shape
        x2 = min(self.width, x + w)
        y2 = min(self.height, y + h)
        self.grid[y1:y2, x1:x2] = region[: (y2 - y1), : (x2 - x1)]

    def to_numpy(self) -> NDArray:
        """Convert the grid to a numpy array."""
        return self.grid

    def get_boundary_mask(self) -> NDArray:
        """Get a boolean mask indicating boundary cells."""
        mask = np.zeros((self.height, self.width), dtype=bool)
        mask[0, :] = True  # Top edge
        mask[-1, :] = True  # Bottom edge
        mask[:, 0] = True  # Left edge
        mask[:, -1] = True  # Right edge
        return mask

    def __str__(self) -> str:
        """Convert the grid to a string representation."""
        return "\n".join("".join(row) for row in self.grid)
