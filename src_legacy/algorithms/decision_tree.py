"""Decision tree implementation for ASCII pattern analysis."""

from dataclasses import dataclass
from typing import Any, Optional, cast

import numpy as np
from numpy.typing import NDArray


@dataclass
class Node:
    """Decision tree node."""

    feature_index: int | None = None
    threshold: float | None = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    value: Any | None = None
    is_leaf: bool = False


class DecisionTree:
    """Decision tree classifier for ASCII pattern analysis."""

    def __init__(self, max_depth: int = 5) -> None:
        self.max_depth = max_depth
        self.root: Node | None = None
        self.n_classes: int = 0

    def fit(self, X: NDArray[np.float_], y: NDArray[np.int_]) -> None:
        """Train the decision tree."""
        self.n_classes = len(np.unique(y))
        self.root = self._grow_tree(X, y, depth=0)

    def _grow_tree(
        self, X: NDArray[np.float_], y: NDArray[np.int_], depth: int
    ) -> Node:
        """Recursively grow the decision tree."""
        n_samples, n_features = X.shape

        # Check stopping criteria
        if depth >= self.max_depth or len(np.unique(y)) == 1:
            return Node(value=self._most_common_label(y), is_leaf=True)

        # Find best split
        best_feature, best_threshold = self._find_best_split(X, y)

        if best_feature is None:
            return Node(value=self._most_common_label(y), is_leaf=True)

        # Create child nodes
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask

        left_child = self._grow_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._grow_tree(X[right_mask], y[right_mask], depth + 1)

        return Node(
            feature_index=best_feature,
            threshold=cast(float, best_threshold),
            left=left_child,
            right=right_child,
        )

    def _find_best_split(
        self, X: NDArray[np.float_], y: NDArray[np.int_]
    ) -> tuple[int | None, float | None]:
        """Find the best split for a node."""
        best_gain = -1
        best_feature = None
        best_threshold = None

        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                gain = self._information_gain(y, X[:, feature], threshold)
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold

        return best_feature, best_threshold

    def _information_gain(
        self, y: NDArray[np.int_], feature: NDArray[np.float_], threshold: float
    ) -> float:
        """Calculate information gain for a split."""
        parent_entropy = self._entropy(y)

        left_mask = feature <= threshold
        right_mask = ~left_mask

        if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
            return 0.0

        n = len(y)
        n_l, n_r = np.sum(left_mask), np.sum(right_mask)
        e_l, e_r = self._entropy(y[left_mask]), self._entropy(y[right_mask])
        child_entropy = (n_l / n) * e_l + (n_r / n) * e_r

        return float(parent_entropy - child_entropy)

    @staticmethod
    def _entropy(y: NDArray[np.int_]) -> float:
        """Calculate entropy of a node."""
        proportions = np.bincount(y) / len(y)
        return float(-np.sum([p * np.log2(p) for p in proportions if p > 0]))

    @staticmethod
    def _most_common_label(y: NDArray[np.int_]) -> int:
        """Return the most common label in a node."""
        return int(np.bincount(y).argmax())

    def predict(self, X: NDArray[np.float_]) -> NDArray[np.int_]:
        """Predict class labels for samples in X."""
        if self.root is None:
            raise ValueError("Tree not fitted. Call fit() first.")
        return np.array([self._traverse_tree(x, self.root) for x in X])

    def _traverse_tree(self, x: NDArray[np.float_], node: Node) -> int:
        """Traverse the tree to make a prediction."""
        if node.is_leaf:
            return cast(int, node.value)

        if x[cast(int, node.feature_index)] <= cast(float, node.threshold):
            return self._traverse_tree(x, cast(Node, node.left))
        return self._traverse_tree(x, cast(Node, node.right))

    def classify(self, components: list, grid: np.ndarray = None) -> list:
        """Classify components based on their features.

        Args:
            components: List of components to classify
            grid: Optional grid data for additional feature extraction

        Returns:
            List of classified components with added classification information
        """
        if not components:
            return []

        # Check if tree is fitted
        if self.root is None:
            raise ValueError("Decision tree not fitted. Call fit() first.")

        # Extract features from components
        features = self._extract_features(components, grid)

        # Apply classification
        if isinstance(features, np.ndarray) and len(features.shape) == 2:
            predictions = self.predict(features)
        else:
            # Handle case where features aren't in expected format
            return components

        # Map predictions to component classification
        classified_components = []
        for i, component in enumerate(components):
            component_copy = (
                component.copy() if hasattr(component, "copy") else component
            )

            # Add classification information
            if i < len(predictions):
                prediction = int(predictions[i])
                component_copy["classification"] = {
                    "type_id": prediction,
                    "confidence": 1.0,  # Default confidence
                }

            classified_components.append(component_copy)

        return classified_components

    def _extract_features(
        self, components: list, grid: np.ndarray = None
    ) -> NDArray[np.float_]:
        """Extract features from components for classification.

        Args:
            components: List of components
            grid: Optional grid data

        Returns:
            Feature matrix for classification
        """
        # Simple feature extraction - expand as needed
        features = []

        for component in components:
            # Handle different component formats
            if isinstance(component, dict):
                component_features = []

                # Add bounding box features if available
                if "bounds" in component:
                    bounds = component["bounds"]
                    if all(k in bounds for k in ["width", "height"]):
                        component_features.extend(
                            [
                                float(bounds["width"]),
                                float(bounds["height"]),
                                float(bounds["width"])
                                / max(float(bounds["height"]), 1.0),
                            ]
                        )

                # Add character count features if available
                if "content" in component and "char_counts" in component["content"]:
                    char_counts = component["content"]["char_counts"]
                    component_features.append(float(len(char_counts)))

                features.append(component_features)

        # Ensure consistent feature dimensionality
        if features:
            max_features = max(len(f) for f in features)
            normalized_features = [
                f + [0.0] * (max_features - len(f)) for f in features
            ]
            return np.array(normalized_features, dtype=np.float_)

        # Return empty feature matrix if no features extracted
        return np.array([], dtype=np.float_)
