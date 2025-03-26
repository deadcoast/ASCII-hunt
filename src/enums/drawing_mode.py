from enum import Enum, auto


class DrawingMode(Enum):
    """Enum for different drawing modes in the ASCII editor."""

    CHARACTER = auto()  # Single character editing
    BOX = auto()  # Drawing rectangular components
    LINE = auto()  # Drawing connecting lines
    TEXT = auto()  # Inserting and editing text content
    ERASE = auto()  # Erasing characters
    SELECT = auto()  # Selecting regions
    FILL = auto()  # Filling regions

    @classmethod
    def get_default(cls) -> "DrawingMode":
        """Get the default drawing mode."""
        return cls.CHARACTER
