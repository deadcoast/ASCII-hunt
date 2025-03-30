"""Defines drawing modes for UI interactions."""

from enum import Enum, auto


class DrawingMode(Enum):
    """Enumeration for different drawing modes in the ASCII grid widget."""

    CHARACTER = auto()  # Standard character input/editing
    SELECTION = auto()  # Selecting a region
    LINE = auto()  # Drawing lines (placeholder)
    RECTANGLE = auto()  # Drawing rectangles (placeholder)
    # Add other modes as needed
