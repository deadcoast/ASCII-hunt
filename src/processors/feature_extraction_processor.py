"""Feature Extraction Processor Module."""

import numpy as np


class FeatureExtractionProcessor:
    """A class that processes and extracts features from components."""

    def __init__(self):
        """Initialize the FeatureExtractionProcessor class."""
        pass

    def extract_features(self, component):
        """
        Extract features from a component.

        Parameters
        ----------
        component : dict
            The component to extract features from

        Returns
        -------
        dict
            A dictionary containing the extracted features
        """
        features = {}

        if not component:
            return features

        # Extract basic geometric features
        if "bounding_box" in component:
            x_min, y_min, x_max, y_max = component["bounding_box"]
            width = x_max - x_min + 1
            height = y_max - y_min + 1

            features["width"] = width
            features["height"] = height
            features["aspect_ratio"] = width / height if height > 0 else 0
            features["area"] = width * height

        # Extract content features
        if "interior" in component:
            interior = component["interior"]
            features["content_density"] = (
                len(interior) / features["area"] if features.get("area", 0) > 0 else 0
            )

        # Extract boundary features
        if "boundary" in component:
            boundary = component["boundary"]
            perimeter = len(boundary)
            features["perimeter"] = perimeter
            features["compactness"] = (
                (4 * np.pi * features.get("area", 0)) / (perimeter * perimeter)
                if perimeter > 0
                else 0
            )

        return features
