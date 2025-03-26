"""Examples demonstrating ASCII art processing capabilities."""

import numpy as np

from ..algorithms.grid_transformer import RotationType
from ..ascii_processor import ASCIIProcessor


def create_example_art() -> np.ndarray:
    """Create example ASCII art for demonstrations."""
    art = """
    +-----+
    |     |
    | >_< |
    |     |
    +-----+
    """
    processor = ASCIIProcessor()
    return processor.utils.string_to_grid(art.strip("\n"))


def pattern_matching_example() -> None:
    """Demonstrate pattern matching capabilities."""
    processor = ASCIIProcessor()

    # Create a grid with repeating patterns
    art = """
    *-* *-* *-*
    | | | | | |
    *-* *-* *-*
    """
    grid = processor.utils.string_to_grid(art.strip("\n"))

    # Define pattern to search for
    pattern = """
    *-*
    | |
    *-*
    """
    pattern_grid = processor.utils.string_to_grid(pattern.strip("\n"))

    # Find all occurrences of the pattern
    matches = processor.find_patterns(grid, pattern_grid)
    print(f"Found {len(matches)} pattern matches")

    # Highlight matches
    highlighted = processor.pattern_matcher.highlight_matches(grid, matches)
    print("\nHighlighted matches:")
    print(processor.utils.grid_to_string(highlighted))


def flood_fill_example() -> None:
    """Demonstrate flood fill capabilities."""
    processor = ASCIIProcessor()

    # Create a grid with regions to fill
    art = """
    +-----+
    |     |
    |  X  |
    |     |
    +-----+
    """
    grid = processor.utils.string_to_grid(art.strip("\n"))

    # Fill empty space with dots
    filled = processor.flood_fill_region(grid, (1, 1), " ", ".")
    print("\nFlood fill result:")
    print(processor.utils.grid_to_string(filled))

    # Find all connected regions
    regions = processor.find_connected_regions(grid, " ")
    print(f"\nFound {len(regions)} connected empty regions")


def transformation_example() -> None:
    """Demonstrate grid transformation capabilities."""
    processor = ASCIIProcessor()

    # Create simple arrow
    art = """
    -->
    """
    grid = processor.utils.string_to_grid(art.strip("\n"))

    # Rotate arrow
    rotated = processor.rotate(grid, RotationType.CLOCKWISE_90)
    print("\nRotated arrow:")
    print(processor.utils.grid_to_string(rotated))

    # Create border
    bordered = processor.add_border(grid, "*")
    print("\nArrow with border:")
    print(processor.utils.grid_to_string(bordered))

    # Mirror horizontally
    mirrored = processor.mirror(grid, "horizontal")
    print("\nMirrored arrow:")
    print(processor.utils.grid_to_string(mirrored))


def text_layout_example() -> None:
    """Demonstrate text layout capabilities."""
    processor = ASCIIProcessor()

    # Center single line
    text = "Hello!"
    centered = processor.center_text(text, width=20, height=3)
    print("\nCentered text:")
    print(processor.utils.grid_to_string(centered))

    # Create text box
    text = "ASCII\nArt"
    box = processor.center_text(text, width=10, height=5)
    bordered = processor.add_border(box)
    print("\nText box:")
    print(processor.utils.grid_to_string(bordered))


def overlay_example() -> None:
    """Demonstrate overlay capabilities."""
    processor = ASCIIProcessor()

    # Create background
    background = processor.utils.string_to_grid(
        """
    ..........
    ..........
    ..........
    ..........
    """.strip("\n")
    )

    # Create foreground with transparency
    foreground = processor.utils.string_to_grid(
        """
    *-*
    | |
    *-*
    """.strip("\n")
    )

    # Overlay with transparency
    result = processor.overlay(
        background, foreground, position=(0, 3), transparent_char=" "
    )
    print("\nOverlay result:")
    print(processor.utils.grid_to_string(result))


def main() -> None:
    """Run all examples."""
    print("ASCII Art Processing Examples")
    print("===========================")

    print("\nPattern Matching Example:")
    pattern_matching_example()

    print("\nFlood Fill Example:")
    flood_fill_example()

    print("\nTransformation Example:")
    transformation_example()

    print("\nText Layout Example:")
    text_layout_example()

    print("\nOverlay Example:")
    overlay_example()


if __name__ == "__main__":
    main()
