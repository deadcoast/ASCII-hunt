"""Main entry point for ASCII art processing."""

from pathlib import Path

import numpy as np

from .algorithms.ascii_utils import ASCIIUtils
from .algorithms.flood_fill_processor import FloodFillProcessor
from .algorithms.grid_transformer import (FlipType, GridTransformer,
                                          RotationType)
from .algorithms.pattern_matcher import PatternMatch, PatternMatcher


class ASCIIProcessor:
    """Main class for processing ASCII art."""

    def __init__(self) -> None:
        """Initialize ASCII processor with its components."""
        self.flood_fill = FloodFillProcessor()
        self.pattern_matcher = PatternMatcher()
        self.transformer = GridTransformer()
        self.utils = ASCIIUtils()

    def load_art(self, file_path: str | Path) -> np.ndarray:
        """Load ASCII art from file.

        Args:
            file_path: Path to ASCII art file

        Returns:
            ASCII grid as numpy array
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        return self.utils.load_grid(file_path)

    def save_art(self, grid: np.ndarray, file_path: str | Path) -> None:
        """Save ASCII art to file.

        Args:
            grid: ASCII grid to save
            file_path: Output file path
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        self.utils.save_grid(grid, file_path)

    def find_patterns(
        self, grid: np.ndarray, pattern: np.ndarray, min_confidence: float = 0.8
    ) -> list[PatternMatch]:
        """Find pattern occurrences in grid.

        Args:
            grid: ASCII grid to search in
            pattern: Pattern to find
            min_confidence: Minimum confidence threshold

        Returns:
            List of pattern matches
        """
        self.pattern_matcher.similarity_threshold = min_confidence
        return self.pattern_matcher.find_pattern(grid, pattern)

    def find_repeating_patterns(
        self,
        grid: np.ndarray,
        min_size: tuple[int, int] = (2, 2),
        max_size: tuple[int, int] | None = None,
    ) -> dict[str, list[PatternMatch]]:
        """Find repeating patterns in grid.

        Args:
            grid: ASCII grid to analyze
            min_size: Minimum pattern size
            max_size: Maximum pattern size

        Returns:
            Dictionary of patterns and their matches
        """
        return self.pattern_matcher.find_repeating_patterns(grid, min_size, max_size)

    def flood_fill_region(
        self, grid: np.ndarray, start: tuple[int, int], target: str, replacement: str
    ) -> np.ndarray:
        """Perform flood fill on grid region.

        Args:
            grid: ASCII grid to modify
            start: Starting position
            target: Character to replace
            replacement: New character

        Returns:
            Modified grid
        """
        from .algorithms.flood_fill_processor import Point

        start_point = Point(start[0], start[1])
        return self.flood_fill.flood_fill(grid, start_point, target, replacement)

    def find_connected_regions(
        self, grid: np.ndarray, target: str
    ) -> list[list[tuple[int, int]]]:
        """Find connected regions of target character.

        Args:
            grid: ASCII grid to analyze
            target: Character to find regions of

        Returns:
            List of regions (lists of positions)
        """
        components = self.flood_fill.find_connected_components(grid, target)
        return [list(component) for component in components]

    def rotate(self, grid: np.ndarray, rotation_type: RotationType) -> np.ndarray:
        """Rotate ASCII grid.

        Args:
            grid: Grid to rotate
            rotation_type: Type of rotation

        Returns:
            Rotated grid
        """
        return self.transformer.rotate(grid, rotation_type)

    def flip(self, grid: np.ndarray, flip_type: FlipType) -> np.ndarray:
        """Flip ASCII grid.

        Args:
            grid: Grid to flip
            flip_type: Type of flip

        Returns:
            Flipped grid
        """
        return self.transformer.flip(grid, flip_type)

    def crop(
        self, grid: np.ndarray, top: int, left: int, height: int, width: int
    ) -> np.ndarray:
        """Crop ASCII grid.

        Args:
            grid: Grid to crop
            top: Top edge
            left: Left edge
            height: Height
            width: Width

        Returns:
            Cropped grid
        """
        return self.transformer.crop(grid, top, left, height, width)

    def pad(
        self,
        grid: np.ndarray,
        padding: int | tuple[int, int, int, int],
        fill_char: str = " ",
    ) -> np.ndarray:
        """Pad ASCII grid.

        Args:
            grid: Grid to pad
            padding: Padding values
            fill_char: Character for padding

        Returns:
            Padded grid
        """
        return self.transformer.pad(grid, padding, fill_char)

    def resize(
        self, grid: np.ndarray, height: int, width: int, fill_char: str = " "
    ) -> np.ndarray:
        """Resize ASCII grid.

        Args:
            grid: Grid to resize
            height: New height
            width: New width
            fill_char: Fill character

        Returns:
            Resized grid
        """
        return self.transformer.resize(grid, height, width, fill_char)

    def overlay(
        self,
        background: np.ndarray,
        foreground: np.ndarray,
        position: tuple[int, int],
        transparent_char: str | None = None,
    ) -> np.ndarray:
        """Overlay one grid on another.

        Args:
            background: Base grid
            foreground: Grid to overlay
            position: Position to place overlay
            transparent_char: Transparent character

        Returns:
            Combined grid
        """
        return self.transformer.overlay(
            background, foreground, position, transparent_char
        )

    def tile(self, grid: np.ndarray, repeat: tuple[int, int]) -> np.ndarray:
        """Create tiled pattern.

        Args:
            grid: Grid to tile
            repeat: Repeat counts

        Returns:
            Tiled grid
        """
        return self.transformer.tile(grid, repeat)

    def mirror(self, grid: np.ndarray, axis: str | None = None) -> np.ndarray:
        """Mirror ASCII grid.

        Args:
            grid: Grid to mirror
            axis: Mirror axis

        Returns:
            Mirrored grid
        """
        return self.transformer.mirror(grid, axis)

    def analyze_grid(
        self, grid: np.ndarray
    ) -> dict[str, tuple[int, int] | dict[str, int] | list[str]]:
        """Analyze ASCII grid properties.

        Args:
            grid: Grid to analyze

        Returns:
            Dictionary with analysis results
        """
        return {
            "dimensions": self.utils.get_dimensions(grid),
            "char_counts": self.utils.count_chars(grid),
            "unique_chars": list(self.utils.get_unique_chars(grid)),
        }

    def replace_char(
        self, grid: np.ndarray, old_char: str, new_char: str
    ) -> np.ndarray:
        """Replace character in grid.

        Args:
            grid: Grid to modify
            old_char: Character to replace
            new_char: New character

        Returns:
            Modified grid
        """
        return self.utils.replace_char(grid, old_char, new_char)

    def find_char(self, grid: np.ndarray, char: str) -> list[tuple[int, int]]:
        """Find all positions of character.

        Args:
            grid: Grid to search
            char: Character to find

        Returns:
            List of positions
        """
        return self.utils.find_char_positions(grid, char)

    def add_border(self, grid: np.ndarray, border_char: str = "#") -> np.ndarray:
        """Add border to grid.

        Args:
            grid: Grid to modify
            border_char: Border character

        Returns:
            Grid with border
        """
        return self.utils.create_border(grid, border_char)

    def remove_border(self, grid: np.ndarray) -> np.ndarray:
        """Remove border from grid.

        Args:
            grid: Grid with border

        Returns:
            Grid without border
        """
        return self.utils.remove_border(grid)

    def center_text(
        self, text: str, width: int, height: int | None = None, fill_char: str = " "
    ) -> np.ndarray:
        """Center text in grid.

        Args:
            text: Text to center
            width: Grid width
            height: Grid height
            fill_char: Fill character

        Returns:
            Grid with centered text
        """
        return self.utils.center_text(text, width, height, fill_char)
