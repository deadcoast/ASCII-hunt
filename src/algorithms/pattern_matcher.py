"""Pattern matching algorithms for ASCII art analysis."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class PatternMatch:
    """Represents a pattern match result."""

    position: tuple[int, int]  # Top-left corner
    confidence: float  # Match confidence score
    pattern_size: tuple[int, int]  # Height, width of matched pattern


class PatternMatcher:
    """Implements pattern matching algorithms for ASCII art."""

    def __init__(self, similarity_threshold: float = 0.8) -> None:
        """Initialize pattern matcher.

        Args:
            similarity_threshold: Minimum similarity score to consider a match
        """
        self.similarity_threshold = similarity_threshold

    def find_pattern(
        self, grid: NDArray[np.str_], pattern: NDArray[np.str_]
    ) -> list[PatternMatch]:
        """Find all occurrences of pattern in grid.

        Args:
            grid: 2D numpy array of ASCII grid to search in
            pattern: 2D numpy array of pattern to find

        Returns:
            List of pattern matches with positions and confidence scores
        """
        matches: list[PatternMatch] = []
        pattern_height, pattern_width = pattern.shape

        # Scan grid for pattern matches
        for i in range(grid.shape[0] - pattern_height + 1):
            for j in range(grid.shape[1] - pattern_width + 1):
                window = grid[i : i + pattern_height, j : j + pattern_width]
                similarity = self._calculate_similarity(window, pattern)

                if similarity >= self.similarity_threshold:
                    match = PatternMatch(
                        position=(i, j),
                        confidence=similarity,
                        pattern_size=(pattern.shape[0], pattern.shape[1]),
                    )
                    matches.append(match)

        return sorted(matches, key=lambda m: m.confidence, reverse=True)

    def _calculate_similarity(
        self, window: NDArray[np.str_], pattern: NDArray[np.str_]
    ) -> float:
        """Calculate similarity score between window and pattern.

        Args:
            window: Grid section to compare
            pattern: Pattern to match against

        Returns:
            Similarity score between 0 and 1
        """
        if window.shape != pattern.shape:
            return 0.0

        matches = np.sum(window == pattern)
        total = pattern.size
        return float(matches) / total

    def find_repeating_patterns(
        self,
        grid: NDArray[np.str_],
        min_size: tuple[int, int] = (2, 2),
        max_size: tuple[int, int] | None = None,
    ) -> dict[str, list[PatternMatch]]:
        """Find repeating patterns in grid.

        Args:
            grid: ASCII grid to analyze
            min_size: Minimum pattern size to consider
            max_size: Maximum pattern size to consider

        Returns:
            Dictionary mapping pattern strings to their matches
        """
        if max_size is None:
            max_size = (grid.shape[0] // 2, grid.shape[1] // 2)

        patterns: dict[str, list[PatternMatch]] = {}

        # Try different pattern sizes
        for height in range(min_size[0], max_size[0] + 1):
            for width in range(min_size[1], max_size[1] + 1):
                self._find_patterns_of_size(grid, (height, width), patterns)

        return patterns

    def _find_patterns_of_size(
        self,
        grid: NDArray[np.str_],
        size: tuple[int, int],
        patterns: dict[str, list[PatternMatch]],
    ) -> None:
        """Find repeating patterns of specific size.

        Args:
            grid: ASCII grid to analyze
            size: (height, width) of patterns to find
            patterns: Dictionary to store found patterns
        """
        height, width = size

        # Extract and analyze all possible windows of given size
        for i in range(grid.shape[0] - height + 1):
            for j in range(grid.shape[1] - width + 1):
                window = grid[i : i + height, j : j + width]
                pattern_str = self._pattern_to_string(window)

                if pattern_str not in patterns:
                    # Search for this pattern in rest of grid
                    matches = self.find_pattern(grid, window)
                    if len(matches) > 1:  # Pattern repeats
                        patterns[pattern_str] = matches

    def _pattern_to_string(self, pattern: NDArray[np.str_]) -> str:
        """Convert pattern array to string representation."""
        return "\n".join("".join(row) for row in pattern)

    def highlight_matches(
        self,
        grid: NDArray[np.str_],
        matches: list[PatternMatch],
        highlight_char: str = "*",
    ) -> NDArray[np.str_]:
        """Create new grid with pattern matches highlighted.

        Args:
            grid: Original ASCII grid
            matches: List of pattern matches to highlight
            highlight_char: Character to use for highlighting

        Returns:
            New grid with highlights around matches
        """
        result = grid.copy()

        for match in matches:
            i, j = match.position
            h, w = match.pattern_size

            # Draw highlight border
            # Top and bottom edges
            for x in range(j, j + w):
                if i > 0:
                    result[i - 1, x] = highlight_char
                if i + h < grid.shape[0]:
                    result[i + h, x] = highlight_char

            # Left and right edges
            for y in range(i, i + h):
                if j > 0:
                    result[y, j - 1] = highlight_char
                if j + w < grid.shape[1]:
                    result[y, j + w] = highlight_char

        return result
