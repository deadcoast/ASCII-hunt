"""Component Analysis Module."""

import numpy as np

from components.component_model_representation import ComponentModel
from components.feature_extractor import FeatureExtractor
from components.distance_calculator import DistanceCalculator
from components.clustering_algorithm import ClusteringAlgorithm
from components.connected_component_analysis import ConnectedComponentAnalyzer
from components.component_analysis import ComponentAnalyzer
from widgets.ascii_grid_widget import AsciiGridWidget

class ComponentAnalyzer:
    def __init__(self, model: ComponentModel):
        self.model = model
        self.feature_extractor = FeatureExtractor()
        self.clustering_algorithm = ClusteringAlgorithm()
        self.distance_calculator = DistanceCalculator()

    def analyze_component(self, component_id):
        """Analyze a specific component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        features = self.feature_extractor.extract_features(component)
        distance_matrix = self.distance_calculator.calculate_distance_matrix(features)
        clusters = self.clustering_algorithm.cluster(distance_matrix)

        return clusters

    def analyze_all_components(self):
        """Analyze all components and return a list of feature vectors."""
        components = self.model.get_all_components()
        return [self.analyze_component(component.id) for component in components]

    def analyze_component_group(self, component_ids):
        """Analyze a group of components and return a list of feature vectors."""
        components = [
            self.model.get_component(component_id) for component_id in component_ids
        ]
        return self.analyze_component(components)

    def analyze_component_hierarchy(self, component_id):
        """Analyze the hierarchy of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        hierarchy = self.model.get_component_hierarchy(component_id)
        return [self.analyze_component(child.id) for child in hierarchy]

    def analyze_component_relationships(self, component_id):
        """Analyze the relationships of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        relationships = self.model.get_component_relationships(component_id)
        return [
            self.analyze_component(relationship.target_id)
            for relationship in relationships
        ]

    def analyze_component_template(self, component_id):
        """Analyze the template of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        template = self.model.get_component_template(component_id)
        return self.analyze_component(template)

    def analyze_component_layout(self, component_id):
        """Analyze the layout of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        layout = self.model.get_component_layout(component_id)
        return self.analyze_component(layout)

    def analyze_component_style(self, component_id):
        """Analyze the style of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        style = self.model.get_component_style(component_id)
        return self.analyze_component(style)

    def analyze_component_behavior(self, component_id):
        """Analyze the behavior of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        behavior = self.model.get_component_behavior(component_id)
        return self.analyze_component(behavior)

    def analyze_component_performance(self, component_id):
        """Analyze the performance of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        performance = self.model.get_component_performance(component_id)
        return self.analyze_component(performance)

    def analyze_component_accessibility(self, component_id):
        """Analyze the accessibility of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        accessibility = self.model.get_component_accessibility(component_id)
        return self.analyze_component(accessibility)

    def analyze_component_usability(self, component_id):
        """Analyze the usability of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        usability = self.model.get_component_usability(component_id)
        return self.analyze_component(usability)

    def analyze_component_interaction(self, component_id):
        """Analyze the interaction of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        interaction = self.model.get_component_interaction(component_id)
        return self.analyze_component(interaction)

    def analyze_component_visualization(self, component_id):
        """Analyze the visualization of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        visualization = self.model.get_component_visualization(component_id)
        return self.analyze_component(visualization)

    def analyze_component_animation(self, component_id):
        """Analyze the animation of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        animation = self.model.get_component_animation(component_id)
        return self.analyze_component(animation)

    def analyze_component_state(self, component_id):
        """Analyze the state of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        state = self.model.get_component_state(component_id)
        return self.analyze_component(state)

    def analyze_component_events(self, component_id):
        """Analyze the events of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        events = self.model.get_component_events(component_id)
        return self.analyze_component(events)

    def analyze_component_memory(self, component_id):
        """Analyze the memory of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        memory = self.model.get_component_memory(component_id)
        return self.analyze_component(memory)

    def analyze_component_security(self, component_id):
        """Analyze the security of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        security = self.model.get_component_security(component_id)
        return self.analyze_component(security)

    def analyze_component_reliability(self, component_id):
        """Analyze the reliability of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        reliability = self.model.get_component_reliability(component_id)
        return self.analyze_component(reliability)

    def analyze_component_maintainability(self, component_id):
        """Analyze the maintainability of a component and return a list of feature vectors."""
        component = self.model.get_component(component_id)
        if not component:
            raise ValueError(f"Component with id {component_id} not found")

        maintainability = self.model.get_component_maintainability(component_id)
        return self.analyze_component(maintainability)


class ConnectedComponentAnalyzer:
    def __init__(self):
        """
        Initialize the ConnectedComponentAnalyzer class.
        """
        pass

    def component_analysis(self, components, grid):
        """
        Analyze the components and return a list of feature vectors.
        """
        return self.connected_component_analysis(components, grid)

    def component_analysis_from_model(self, components, grid):
        """
        Analyze the components and return a list of feature vectors.
        """
        return self.connected_component_analysis(components, grid)

    def connected_component_analysis(self, components, grid):
        """
        Implements the mathematical CCA using NumPy operations.
        """

    feature_vectors = []

    # Extract feature vectors for each component
    for comp in components:
        # Convert sets to numpy arrays for efficient computation
        interior = np.array(list(comp["interior"]))
        boundary = np.array(list(comp["boundary"]))

        width = comp["width"]
        height = comp["height"]

        # Calculate aspect ratio
        aspect_ratio = width / height if height > 0 else 0

        # Calculate border density
        border_density = (
            len(boundary) / (2 * (width + height)) if width > 0 and height > 0 else 0
        )

        # Calculate content density
        content_density = (
            len(interior) / (width * height) if width > 0 and height > 0 else 0
        )

    # Character distribution analysis
    if grid is not None:
        chars = [grid[y, x] for x, y in interior]
        unique_chars, char_counts = np.unique(chars, return_counts=True)
        char_frequencies = char_counts / len(interior) if interior else np.array([])
    else:
        char_frequencies = np.array([])
        unique_chars = np.array([])

    # Combine into feature vector
    features = {
        "id": comp.get("id"),
        "aspect_ratio": aspect_ratio,
        "border_density": border_density,
        "content_density": content_density,
        "char_frequencies": dict(zip(unique_chars, char_frequencies)),
        "bounding_box": comp["bounding_box"],
    }

    feature_vectors.append(features)

    # Calculate pairwise distances
    n = len(feature_vectors)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            # Feature distance calculation
            f_i = feature_vectors[i]
            f_j = feature_vectors[j]

        # Weighted Euclidean distance between numeric features
        feature_distance = np.sqrt(
            0.3 * (f_i["aspect_ratio"] - f_j["aspect_ratio"]) ** 2
            + 0.4 * (f_i["border_density"] - f_j["border_density"]) ** 2
            + 0.3 * (f_i["content_density"] - f_j["content_density"]) ** 2
        )

        # Spatial distance between components
        bb_i = components[i]["bounding_box"]
        bb_j = components[j]["bounding_box"]

        # Calculate minimum distance between bounding boxes
        spatial_distance = max(
            0,
            max(bb_i[0], bb_j[0]) - min(bb_i[2], bb_j[2]),
            max(bb_i[1], bb_j[1]) - min(bb_i[3], bb_j[3]),
        )

        # Combined distance
        distance_matrix[i, j] = distance_matrix[j, i] = (
            0.6 * feature_distance + 0.4 * spatial_distance
        )

        # Group components based on distance thresholds
        threshold = 0.5  # Adjust based on application

        grouped_components = []
        processed = set()

        for i in range(n):
            if i in processed:
                continue

            group = [i]
            processed.add(i)

            for j in range(n):
                if j not in processed and distance_matrix[i, j] < threshold:
                    group.append(j)
                    processed.add(j)

                    if group:
                        grouped_components.append(group)
