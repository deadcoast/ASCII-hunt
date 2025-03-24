"""Containment Analyzer Module."""


class ContainmentAnalyzer:
    def __init__(self):
        """
        Initialize a new ContainmentAnalyzer.

        This constructor creates a new ContainmentAnalyzer instance with an empty
        containment_graph attribute.
        """
        self.containment_graph = {}

    def analyze(self, component_model, context=None):
        """Analyze containment relationships between components."""
        if context is None:
            context = {}

        # Get all components
        components = list(component_model.components.values())

        # Create spatial index for efficient querying
        spatial_index = self._create_spatial_index(components)

        # Analyze containment relationships
        self._analyze_containment(components, component_model, spatial_index)

        return component_model

    def _create_spatial_index(self, components):
        """Create a spatial index for the components."""
        # Determine grid dimensions
        max_x = max_y = 0

        for component in components:
            if "bounding_box" in component.properties:
                bb = component.properties["bounding_box"]
                max_x = max(max_x, bb[2])
                max_y = max(max_y, bb[3])

        # Create spatial index
        index = SpatialIndex(max_x + 1, max_y + 1)

        # Add components to index
        for component in components:
            index.add_component(component)

        return index

    def _analyze_containment(self, components, component_model, spatial_index):
        """Analyze containment relationships between components."""
        # Sort components by area (largest first)
        components.sort(key=lambda c: self._get_component_area(c), reverse=True)

        # Build containment graph
        for outer_component in components:
            outer_bb = self._get_bounding_box(outer_component)

            if not outer_bb:
                continue

            x1, y1, x2, y2 = outer_bb

            # Query spatial index for potential contained components
            potential_contained_ids = spatial_index.query_region(x1, y1, x2, y2)

            for inner_id in potential_contained_ids:
                inner_component = component_model.get_component(inner_id)

                if inner_component and inner_component.id != outer_component.id:
                    inner_bb = self._get_bounding_box(inner_component)

                    if not inner_bb:
                        continue

                    # Check if inner component is fully contained
                    if self._is_contained(inner_bb, outer_bb):
                        # Add containment relationship
                        component_model.add_relationship(
                            outer_component.id, inner_component.id, "contains"
                        )

    def _get_bounding_box(self, component):
        """Get the bounding box of a component."""
        if "refined_bounding_box" in component.properties:
            return component.properties["refined_bounding_box"]
        elif "bounding_box" in component.properties:
            return component.properties["bounding_box"]
        return None

    def _get_component_area(self, component):
        """Get the area of a component."""
        bb = self._get_bounding_box(component)

        if bb:
            x1, y1, x2, y2 = bb
            return (x2 - x1 + 1) * (y2 - y1 + 1)
        return 0

    def _is_contained(self, inner_bb, outer_bb):
        """Check if inner bounding box is contained within outer bounding box."""
        ix1, iy1, ix2, iy2 = inner_bb
        ox1, oy1, ox2, oy2 = outer_bb

        # Inner must be fully contained with some margin
        margin = 1
        return (
            ox1 + margin <= ix1 <= ix2 <= ox2 - margin
            and oy1 + margin <= iy1 <= iy2 <= oy2 - margin
        )
