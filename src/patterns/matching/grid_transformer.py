"""Grid transformation operations for ASCII art processing."""

from enum import Enum

import numpy as np


class RotationType(Enum):
    """Types of rotation operations."""

    CLOCKWISE_90 = 90
    COUNTERCLOCKWISE_90 = -90
    CLOCKWISE_180 = 180


class FlipType(Enum):
    """Types of flip operations."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class GridTransformer:
    """Handles ASCII grid transformations."""

    @staticmethod
    def rotate(grid: np.ndarray, rotation_type: RotationType) -> np.ndarray:
        """Rotate ASCII grid.

        Args:
            grid: ASCII grid to rotate
            rotation_type: Type of rotation to perform

        Returns:
            Rotated grid
        """
        if rotation_type == RotationType.CLOCKWISE_90:
            return np.rot90(grid, k=-1)
        elif rotation_type == RotationType.COUNTERCLOCKWISE_90:
            return np.rot90(grid, k=1)
        elif rotation_type == RotationType.CLOCKWISE_180:
            return np.rot90(grid, k=2)
        else:
            raise ValueError(f"Unsupported rotation type: {rotation_type}")

    @staticmethod
    def flip(grid: np.ndarray, flip_type: FlipType) -> np.ndarray:
        """Flip ASCII grid.

        Args:
            grid: ASCII grid to flip
            flip_type: Type of flip to perform

        Returns:
            Flipped grid
        """
        if flip_type == FlipType.HORIZONTAL:
            return np.fliplr(grid)
        elif flip_type == FlipType.VERTICAL:
            return np.flipud(grid)
        else:
            raise ValueError(f"Unsupported flip type: {flip_type}")

    @staticmethod
    def crop(
        grid: np.ndarray, top: int, left: int, height: int, width: int
    ) -> np.ndarray:
        """Crop ASCII grid to specified region.

        Args:
            grid: ASCII grid to crop
            top: Top edge of crop region
            left: Left edge of crop region
            height: Height of crop region
            width: Width of crop region

        Returns:
            Cropped grid
        """
        if (
            top < 0
            or left < 0
            or top + height > grid.shape[0]
            or left + width > grid.shape[1]
        ):
            raise ValueError("Crop region outside grid bounds")

        return grid[top : top + height, left : left + width]

    @staticmethod
    def pad(
        grid: np.ndarray, padding: int | tuple[int, int, int, int], fill_char: str = " "
    ) -> np.ndarray:
        """Pad ASCII grid.

        Args:
            grid: ASCII grid to pad
            padding: Either single value for all sides or
                    (top, right, bottom, left) padding values
            fill_char: Character to use for padding

        Returns:
            Padded grid
        """
        if isinstance(padding, int):
            padding = (padding, padding, padding, padding)

        top, right, bottom, left = padding
        height, width = grid.shape
        new_height = height + top + bottom
        new_width = width + left + right

        result = np.full((new_height, new_width), fill_char)
        result[top : top + height, left : left + width] = grid
        return result

    @staticmethod
    def resize(
        grid: np.ndarray, new_height: int, new_width: int, fill_char: str = " "
    ) -> np.ndarray:
        """Resize ASCII grid.

        Args:
            grid: ASCII grid to resize
            new_height: Target height
            new_width: Target width
            fill_char: Character to use for padding if needed

        Returns:
            Resized grid
        """
        if new_height < 1 or new_width < 1:
            raise ValueError("Invalid dimensions")

        result = np.full((new_height, new_width), fill_char)

        # Copy as much of original grid as will fit
        copy_height = min(grid.shape[0], new_height)
        copy_width = min(grid.shape[1], new_width)
        result[:copy_height, :copy_width] = grid[:copy_height, :copy_width]

        return result

    @staticmethod
    def overlay(
        background: np.ndarray,
        foreground: np.ndarray,
        position: tuple[int, int],
        transparent_char: str | None = None,
    ) -> np.ndarray:
        """Overlay one ASCII grid on another.

        Args:
            background: Base grid
            foreground: Grid to overlay
            position: (top, left) position to place foreground
            transparent_char: Character to treat as transparent

        Returns:
            Combined grid
        """
        if not (
            0 <= position[0] <= background.shape[0] - foreground.shape[0]
            and 0 <= position[1] <= background.shape[1] - foreground.shape[1]
        ):
            raise ValueError("Foreground position outside background bounds")

        result = background.copy()
        top, left = position
        height, width = foreground.shape

        if transparent_char is None:
            # Simple overlay
            result[top : top + height, left : left + width] = foreground
        else:
            # Overlay with transparency
            mask = foreground != transparent_char
            result[top : top + height, left : left + width][mask] = foreground[mask]

        return result

    @staticmethod
    def tile(grid: np.ndarray, repeat: tuple[int, int]) -> np.ndarray:
        """Create tiled pattern from ASCII grid.

        Args:
            grid: Grid to tile
            repeat: (vertical, horizontal) repeat counts

        Returns:
            Tiled grid
        """
        if repeat[0] < 1 or repeat[1] < 1:
            raise ValueError("Invalid repeat counts")

        return np.tile(grid, repeat)

    @staticmethod
    def mirror(grid: np.ndarray, axis: str | None = None) -> np.ndarray:
        """Create mirrored version of ASCII grid.

        Args:
            grid: Grid to mirror
            axis: 'horizontal', 'vertical', or None for both

        Returns:
            Mirrored grid
        """
        if axis == "horizontal":
            return np.hstack((grid, np.fliplr(grid)))
        elif axis == "vertical":
            return np.vstack((grid, np.flipud(grid)))
        elif axis is None:
            # Mirror both horizontally and vertically
            top_half = np.hstack((grid, np.fliplr(grid)))
            return np.vstack((top_half, np.flipud(top_half)))
        else:
            raise ValueError("Invalid mirror axis")
