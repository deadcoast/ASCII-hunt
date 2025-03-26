"""Utility functions for ASCII art processing."""

from pathlib import Path

import numpy as np


class ASCIIUtils:
    """Common utilities for ASCII art processing."""

    @staticmethod
    def load_grid(file_path: Path) -> np.ndarray:
        """Load ASCII grid from file.

        Args:
            file_path: Path to ASCII art file

        Returns:
            2D numpy array of characters
        """
        with open(file_path) as f:
            lines = f.readlines()

        # Remove trailing newlines and normalize line lengths
        lines = [line.rstrip("\n") for line in lines]
        max_width = max(len(line) for line in lines)
        lines = [line.ljust(max_width) for line in lines]

        # Convert to numpy array
        return np.array([list(line) for line in lines])

    @staticmethod
    def save_grid(grid: np.ndarray, file_path: Path) -> None:
        """Save ASCII grid to file.

        Args:
            grid: ASCII grid to save
            file_path: Output file path
        """
        with open(file_path, "w") as f:
            for row in grid:
                f.write("".join(row) + "\n")

    @staticmethod
    def grid_to_string(grid: np.ndarray) -> str:
        """Convert ASCII grid to string.

        Args:
            grid: ASCII grid to convert

        Returns:
            String representation of grid
        """
        return "\n".join("".join(row) for row in grid)

    @staticmethod
    def string_to_grid(text: str) -> np.ndarray:
        """Convert string to ASCII grid.

        Args:
            text: String to convert

        Returns:
            ASCII grid representation
        """
        lines = text.split("\n")
        max_width = max(len(line) for line in lines)
        lines = [line.ljust(max_width) for line in lines]
        return np.array([list(line) for line in lines])

    @staticmethod
    def get_dimensions(grid: np.ndarray) -> tuple[int, int]:
        """Get dimensions of ASCII grid.

        Args:
            grid: ASCII grid

        Returns:
            Tuple of (height, width)
        """
        return grid.shape

    @staticmethod
    def count_chars(grid: np.ndarray) -> dict[str, int]:
        """Count occurrences of each character in grid.

        Args:
            grid: ASCII grid to analyze

        Returns:
            Dictionary mapping characters to their counts
        """
        unique, counts = np.unique(grid, return_counts=True)
        return dict(zip(unique, counts, strict=False))

    @staticmethod
    def get_unique_chars(grid: np.ndarray) -> set[str]:
        """Get set of unique characters in grid.

        Args:
            grid: ASCII grid to analyze

        Returns:
            Set of unique characters
        """
        return set(np.unique(grid))

    @staticmethod
    def replace_char(grid: np.ndarray, old_char: str, new_char: str) -> np.ndarray:
        """Replace character in grid.

        Args:
            grid: ASCII grid to modify
            old_char: Character to replace
            new_char: Replacement character

        Returns:
            Modified grid
        """
        result = grid.copy()
        result[grid == old_char] = new_char
        return result

    @staticmethod
    def find_char_positions(grid: np.ndarray, char: str) -> list[tuple[int, int]]:
        """Find all positions of a character in grid.

        Args:
            grid: ASCII grid to search
            char: Character to find

        Returns:
            List of (row, col) positions
        """
        positions = np.where(grid == char)
        return list(zip(positions[0], positions[1], strict=False))

    @staticmethod
    def extract_region(
        grid: np.ndarray, top_left: tuple[int, int], bottom_right: tuple[int, int]
    ) -> np.ndarray:
        """Extract rectangular region from grid.

        Args:
            grid: Source ASCII grid
            top_left: (row, col) of top-left corner
            bottom_right: (row, col) of bottom-right corner

        Returns:
            Extracted region as new grid
        """
        row1, col1 = top_left
        row2, col2 = bottom_right
        return grid[row1 : row2 + 1, col1 : col2 + 1]

    @staticmethod
    def insert_grid(
        target: np.ndarray, source: np.ndarray, position: tuple[int, int]
    ) -> np.ndarray:
        """Insert one grid into another.

        Args:
            target: Target ASCII grid
            source: Grid to insert
            position: (row, col) position to insert at

        Returns:
            Modified target grid
        """
        result = target.copy()
        row, col = position
        h, w = source.shape
        result[row : row + h, col : col + w] = source
        return result

    @staticmethod
    def create_border(grid: np.ndarray, border_char: str = "#") -> np.ndarray:
        """Add border around ASCII grid.

        Args:
            grid: Grid to add border to
            border_char: Character to use for border

        Returns:
            Grid with border added
        """
        h, w = grid.shape
        result = np.full((h + 2, w + 2), border_char)
        result[1:-1, 1:-1] = grid
        return result

    @staticmethod
    def remove_border(grid: np.ndarray) -> np.ndarray:
        """Remove border from ASCII grid.

        Args:
            grid: Grid with border

        Returns:
            Grid with border removed
        """
        return grid[1:-1, 1:-1]

    @staticmethod
    def center_text(
        text: str, width: int, height: int | None = None, fill_char: str = " "
    ) -> np.ndarray:
        """Center text in fixed-width ASCII grid.

        Args:
            text: Text to center
            width: Width of output grid
            height: Optional height (auto-calculated if None)
            fill_char: Character to use for padding

        Returns:
            Grid with centered text
        """
        lines = text.split("\n")
        if height is None:
            height = len(lines)

        result = np.full((height, width), fill_char)

        for i, line in enumerate(lines[:height]):
            if not line:
                continue

            # Center line horizontally
            start = (width - len(line)) // 2
            end = start + len(line)
            result[i, start:end] = list(line)

        return result
