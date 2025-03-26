"""Component Classification Processor Module.

This module provides a processor for classifying components based on their features.
"""

from typing import Any


class ComponentClassificationProcessor:
    """A processor for classifying components based on their features.

    This processor takes a list of components with their features and classifies
    them into UI component types using registered classifiers.
    """

    def __init__(self) -> None:
        """Initialize the ComponentClassificationProcessor class."""
        self.classifiers: list[Any] = []
        self.confidence_threshold = 0.7
        self.fallback_type = "unknown"

    def register_classifier(self, classifier: Any) -> None:
        """Register a component classifier.

        Args:
            classifier: The classifier to register.
        """
        self.classifiers.append(classifier)

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the confidence threshold for classification.

        Args:
            threshold: The confidence threshold value (0.0 to 1.0).
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))

    def set_fallback_type(self, fallback_type: str) -> None:
        """Set the fallback component type when classification fails.

        Args:
            fallback_type: The fallback component type.
        """
        self.fallback_type = fallback_type

    def process(
        self, components: list[dict[str, Any]], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Classify components based on their features.

        Args:
            components: The list of components with features to classify.
            context: The context dictionary containing processing information.

        Returns:
            The list of classified components.
        """
        if not components:
            return []

        # Extract features from context if available
        features = context.get("features", {})

        classified_components = []

        for component in components:
            component_features = features.get(component.get("id", ""), {})

            # Skip components that are already classified with high confidence
            if (
                "ui_type" in component
                and component.get("confidence", 0) >= self.confidence_threshold
            ):
                classified_components.append(component)
                continue

            # Try to classify with each registered classifier
            best_classification = None
            best_confidence = 0.0

            for classifier in self.classifiers:
                try:
                    classification, confidence = classifier.classify(
                        component, component_features
                    )

                    if confidence > best_confidence:
                        best_classification = classification
                        best_confidence = confidence

                except Exception as e:
                    # Log the error but continue with other classifiers
                    if "classification_errors" not in context:
                        context["classification_errors"] = []
                    context["classification_errors"].append(
                        {"component_id": component.get("id"), "error": str(e)}
                    )

            # Use the best classification or fallback
            if best_classification and best_confidence >= self.confidence_threshold:
                component["ui_type"] = best_classification
                component["confidence"] = best_confidence
            else:
                # Use fallback type
                component["ui_type"] = self.fallback_type
                component["confidence"] = 0.0

            classified_components.append(component)

        # Store classified components in context
        context["classified_components"] = classified_components

        return classified_components

    def analyze_classification_accuracy(
        self, components: list[dict[str, Any]], ground_truth: dict[str, str]
    ) -> dict[str, float]:
        """Analyze classification accuracy against ground truth.

        Args:
            components: The list of classified components.
            ground_truth: Dictionary mapping component IDs to their true types.

        Returns:
            Dictionary with accuracy metrics.
        """
        if not components or not ground_truth:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}

        correct = 0
        total = 0

        for component in components:
            component_id = component.get("id")
            if component_id is not None and component_id in ground_truth:
                total += 1
                if component.get("ui_type") == ground_truth[component_id]:
                    correct += 1

        accuracy = correct / total if total > 0 else 0.0

        return {
            "accuracy": accuracy,
            "total_components": total,
            "correctly_classified": correct,
        }
