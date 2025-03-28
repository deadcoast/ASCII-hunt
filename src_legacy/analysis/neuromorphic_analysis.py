"""Neuromorphic analysis module for ASCII art processing."""

from collections.abc import Callable
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

T = TypeVar("T")


class NeuromorphicAnalyzer:
    """Analyzer for neuromorphic patterns in ASCII art."""

    def __init__(self, learning_rate: float = 0.01) -> None:
        """Initialize neuromorphic analyzer.

        Args:
            learning_rate: Learning rate for pattern adaptation
        """
        self.learning_rate = learning_rate
        self.patterns: dict[str, NDArray[np.float_]] = {}
        self.activation_fn: Callable[[NDArray[np.float_]], NDArray[np.float_]] = np.tanh

    def train(
        self, input_data: NDArray[np.str_], pattern_name: str, iterations: int = 100
    ) -> None:
        """Train the analyzer on input data.

        Args:
            input_data: ASCII grid to learn from
            pattern_name: Name to assign to learned pattern
            iterations: Number of training iterations
        """
        # Convert ASCII to numerical representation
        numerical_data = self._ascii_to_numerical(input_data)

        # Initialize pattern if not exists
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = np.random.randn(*numerical_data.shape)

        # Train pattern
        for _ in range(iterations):
            self._update_pattern(pattern_name, numerical_data)

    def _update_pattern(self, pattern_name: str, target: NDArray[np.float_]) -> None:
        """Update pattern weights using Hebbian learning.

        Args:
            pattern_name: Name of pattern to update
            target: Target numerical representation
        """
        pattern = self.patterns[pattern_name]
        activation = self.activation_fn(pattern)

        # Hebbian update rule
        delta = self.learning_rate * (target - activation)
        # Update pattern element-wise
        self.patterns[pattern_name] = pattern + delta

    def analyze(
        self, input_data: NDArray[np.str_]
    ) -> dict[str, list[tuple[tuple[int, int], float]]]:
        """Analyze input data for learned patterns.

        Args:
            input_data: ASCII grid to analyze

        Returns:
            Dictionary mapping pattern names to lists of (position, similarity) tuples
        """
        numerical_data = self._ascii_to_numerical(input_data)
        results: dict[str, list[tuple[tuple[int, int], float]]] = {}

        for name, pattern in self.patterns.items():
            matches = self._find_pattern_matches(numerical_data, pattern)
            results[name] = matches

        return results

    def _find_pattern_matches(
        self, data: NDArray[np.float_], pattern: NDArray[np.float_]
    ) -> list[tuple[tuple[int, int], float]]:
        """Find matches of pattern in data.

        Args:
            data: Numerical representation of ASCII grid
            pattern: Pattern to search for

        Returns:
            List of (position, similarity) tuples
        """
        pattern_h, pattern_w = pattern.shape
        data_h, data_w = data.shape
        matches: list[tuple[tuple[int, int], float]] = []

        for i in range(data_h - pattern_h + 1):
            for j in range(data_w - pattern_w + 1):
                window = data[i : i + pattern_h, j : j + pattern_w]
                similarity = self._calculate_similarity(window, pattern)
                matches.append(((i, j), similarity))

        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _calculate_similarity(
        self, window: NDArray[np.float_], pattern: NDArray[np.float_]
    ) -> float:
        """Calculate similarity between window and pattern.

        Args:
            window: Window from input data
            pattern: Pattern to compare against

        Returns:
            Similarity score between 0 and 1
        """
        activated_window = self.activation_fn(window)
        activated_pattern = self.activation_fn(pattern)

        # Cosine similarity
        dot_product = np.sum(activated_window * activated_pattern)
        window_norm = np.sqrt(np.sum(activated_window**2))
        pattern_norm = np.sqrt(np.sum(activated_pattern**2))

        if window_norm == 0 or pattern_norm == 0:
            return 0.0

        return float(dot_product / (window_norm * pattern_norm))

    def _ascii_to_numerical(self, ascii_grid: NDArray[np.str_]) -> NDArray[np.float_]:
        """Convert ASCII grid to numerical representation.

        Args:
            ascii_grid: Input ASCII grid

        Returns:
            Numerical representation of the grid
        """
        # Simple conversion: use ASCII values normalized to [0, 1]
        numerical = np.array([[ord(c) for c in row] for row in ascii_grid])
        return (numerical - numerical.min()) / (numerical.max() - numerical.min())
