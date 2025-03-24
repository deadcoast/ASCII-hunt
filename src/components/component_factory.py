"""Component Factory Module."""

import uuid

from components.component_model_representation import AbstractComponent
from components.component_analysis import ConnectedComponentAnalyzer


class ComponentFactory:
    def __init__(self, id_generator=None):
        """
        Initialize a ComponentFactory.

        The ComponentFactory has the following properties:
        - self.id_generator: a function for generating unique identifiers for
          components
        - self.type_classifier: a function for classifying components by type
        """
        self.id_generator = id_generator or (lambda: str(uuid.uuid4()))
        self.type_classifier = None  # To be set with trained classifier

    def create_from_flood_fill(self, flood_fill_result, grid):
        """Create a component from flood fill results."""
        component_id = self.id_generator()

        # Extract features for classification
        connected_component_analyzer = ConnectedComponentAnalyzer()
        features = connected_component_analyzer.component_analysis_from_model(
            flood_fill_result, grid
        )
        features = features[0]
        feature_vectors = features[1]

        # Classify component type
        component_type = self.classify_component_type(features)

        # Create the component
        component = AbstractComponent(component_id, component_type)

        # Set basic properties
        bounding_box = flood_fill_result["bounding_box"]
        component.add_property("x", bounding_box[0])
        component.add_property("y", bounding_box[1])
        component.add_property("width", bounding_box[2] - bounding_box[0] + 1)
        component.add_property("height", bounding_box[3] - bounding_box[1] + 1)

        # Extract and set component-specific properties
        self.extract_component_properties(component, flood_fill_result, grid)

        return component

    def classify_component_type(self, features):
        """Classify component type based on features."""
        if self.type_classifier:
            return self.type_classifier.predict([features])[0]

        # Fallback classification logic
        if features["has_border"] and features["has_title"]:
            return "Window"
        elif features["is_rectangular"] and features["contains_text"]:
            if features["text_is_bracketed"]:
                return "Button"
            else:
                return "Label"
        # More classification rules...

        return "Unknown"

    def extract_component_properties(self, component, flood_fill_result, grid):
        """Extract component-specific properties based on content."""
        content = flood_fill_result.get("content", [])

        if component.type == "Window":
            # Extract window title from first line
            if content and len(content) > 0:
                component.add_property("title", content[0].strip())

        elif component.type == "Button":
            # Extract button text
            text = " ".join(content).strip()
            # Remove brackets if present
            if text.startswith("[") and text.endswith("]"):
                text = text[1:-1].strip()
            component.add_property("text", text)

        # More property extraction for other types...
