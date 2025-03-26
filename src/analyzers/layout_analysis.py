"""Layout Analysis Module."""

from typing import Any, TypeVar, cast

import numpy as np

Component = TypeVar("Component")


class LayoutAnalyzer:
    def __init__(self):
        """Initialize a LayoutAnalyzer instance.

        This constructor creates a LayoutAnalyzer with an empty layout_graph
        dictionary to store layout relationships between components.
        """
        self.layout_graph: dict = {}

    def analyze(self, component_model, context=None):
        """Analyze layout relationships between components."""
        if context is None:
            context = {}

        # Analyze alignment relationships
        self._analyze_alignment(component_model)

        # Analyze grid arrangements
        self._analyze_grid_arrangement(component_model)

        # Analyze flow arrangements
        self._analyze_flow_arrangement(component_model)

        return component_model

    def _analyze_alignment(self, component_model):
        """Analyze alignment relationships between components."""
        # Get all components
        components = list(component_model.components.values())

        # Group components by containers
        container_groups: dict[str, list] = {}

        for component in components:
            container = component_model.get_container(component.id)

            if container:
                container_id = container.id
                if container_id not in container_groups:
                    container_groups[container_id] = []
                container_groups[container_id].append(component)

        # Analyze alignment within each container
        for container_id, container_components in container_groups.items():
            self._analyze_group_alignment(container_components, component_model)

    def _analyze_group_alignment(self, components, component_model):
        """Analyze alignment within a group of components."""
        # Skip if too few components
        if len(components) < 2:
            return

        # Sort components by position
        components_with_bb = [
            (c, self._get_bounding_box(c))
            for c in components
            if self._get_bounding_box(c)
        ]

        if not components_with_bb:
            return

        # Analyze horizontal alignment
        h_aligned_groups = self._find_aligned_groups(components_with_bb, "horizontal")

        for group in h_aligned_groups:
            if len(group) >= 2:
                # Add 'alignsHorizontally' relationship between components
                first_component = group[0][0]

                for i in range(1, len(group)):
                    component_model.add_relationship(
                        first_component.id, group[i][0].id, "alignsHorizontally"
                    )

        # Analyze vertical alignment
        v_aligned_groups = self._find_aligned_groups(components_with_bb, "vertical")

        for group in v_aligned_groups:
            if len(group) >= 2:
                # Add 'alignsVertically' relationship between components
                first_component = group[0][0]

                for i in range(1, len(group)):
                    component_model.add_relationship(
                        first_component.id, group[i][0].id, "alignsVertically"
                    )

    def _find_aligned_groups(self, components_with_bb, alignment_type):
        """Find groups of aligned components."""
        aligned_groups = []

        if alignment_type == "horizontal":
            # Group by y-coordinate
            groups_by_y: dict[int, list] = {}

            for comp, bb in components_with_bb:
                y_mid = int((bb[1] + bb[3]) / 2)  # Convert to int for indexing

                if y_mid not in groups_by_y:
                    groups_by_y[y_mid] = []

                groups_by_y[y_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed: set[int] = set()

            for y in sorted(groups_by_y.keys()):
                if y in processed:
                    continue

                # Find similar y-values
                aligned_group = groups_by_y[y]

                # Convert to int to avoid type issues
                y_range = range(int(y) + 1, int(y) + 3)
                for y2 in y_range:
                    if y2 in groups_by_y:
                        aligned_group.extend(groups_by_y[y2])
                        processed.add(y2)

                if len(aligned_group) >= 2:
                    # Sort by x-coordinate
                    aligned_group.sort(key=lambda item: int(item[1][0]))
                    aligned_groups.append(aligned_group)

        elif alignment_type == "vertical":
            # Group by x-coordinate
            groups_by_x: dict[int, list] = {}

            for comp, bb in components_with_bb:
                x_mid = int((bb[0] + bb[2]) / 2)  # Convert to int for indexing

                if x_mid not in groups_by_x:
                    groups_by_x[x_mid] = []

                groups_by_x[x_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed: set[int] = set()

            for x in sorted(groups_by_x.keys()):
                if x in processed:
                    continue

                # Find similar x-values
                aligned_group = groups_by_x[x]

                # Convert to int to avoid type issues
                x_range = range(int(x) + 1, int(x) + 3)
                for x2 in x_range:
                    if x2 in groups_by_x:
                        aligned_group.extend(groups_by_x[x2])
                        processed.add(x2)

                if len(aligned_group) >= 2:
                    # Sort by y-coordinate
                    aligned_group.sort(key=lambda item: int(item[1][1]))
                    aligned_groups.append(aligned_group)

        return aligned_groups

    def _get_bounding_box(self, component) -> list[int] | None:
        """Get the bounding box of a component."""
        if "refined_bounding_box" in component.properties:
            bb = component.properties["refined_bounding_box"]
            return [int(x) for x in bb] if bb else None
        if "bounding_box" in component.properties:
            bb = component.properties["bounding_box"]
            return [int(x) for x in bb] if bb else None
        return None

    def _analyze_grid_arrangement(self, component_model):
        """Analyze grid arrangements of components."""
        # Get all containers
        for container_id in list(component_model.components.keys()):
            # Get contained components
            contained = component_model.get_contained_components(container_id)

            if len(contained) < 4:  # Need at least 4 components for a grid
                continue

            # Check if components form a grid
            grid_info = self._check_grid_arrangement(contained)

            if grid_info:
                # Add grid arrangement to container
                container = component_model.get_component(container_id)
                container.add_property("layout", "grid")
                container.add_property("grid_info", grid_info)

    def _check_grid_arrangement(self, components):
        """Check if components form a grid arrangement."""
        # Get components with bounding boxes
        components_with_bb = [
            (c, self._get_bounding_box(c))
            for c in components
            if self._get_bounding_box(c)
        ]

        if len(components_with_bb) < 4:
            return None

        # Extract row and column positions
        row_positions: set[int] = set()
        col_positions: set[int] = set()

        for comp, bb in components_with_bb:
            if bb:  # Check if bounding box exists
                y_mid = int((bb[1] + bb[3]) / 2)
                x_mid = int((bb[0] + bb[2]) / 2)

                row_positions.add(y_mid)
                col_positions.add(x_mid)

        # Check if we have at least 2 rows and 2 columns
        if len(row_positions) < 2 or len(col_positions) < 2:
            return None

        # Sort positions
        rows = sorted(row_positions)
        cols = sorted(col_positions)

        # Check if number of components matches grid size
        grid_size = len(rows) * len(cols)
        min_components = int(grid_size * 0.8)  # Allow some missing cells

        if len(components_with_bb) < min_components:
            return None

        # Create a mapping of components to grid cells
        grid_map: dict[tuple[int, int], str] = {}

        for comp, bb in components_with_bb:
            if bb:  # Check if bounding box exists
                y_mid = int((bb[1] + bb[3]) / 2)
                x_mid = int((bb[0] + bb[2]) / 2)

                row_idx = self._find_nearest_index(y_mid, rows)
                col_idx = self._find_nearest_index(x_mid, cols)

                grid_map[(row_idx, col_idx)] = comp.id

        return {"rows": len(rows), "columns": len(cols), "grid_map": grid_map}

    def _find_nearest_index(self, value: float, positions: list[int]) -> int:
        """Find the index of the nearest position."""
        value = int(value)  # Convert to int for comparison
        return min(range(len(positions)), key=lambda i: abs(positions[i] - value))

    def _analyze_flow_arrangement(self, component_model):
        """Analyze flow arrangements of components."""
        # Get all containers
        for container_id in list(component_model.components.keys()):
            # Get contained components
            contained = component_model.get_contained_components(container_id)

            if len(contained) < 2:  # Need at least 2 components for flow
                continue

            # Get components with bounding boxes and filter out None values
            components_with_bb = [
                (c, bb)
                for c in contained
                if (bb := self._get_bounding_box(c)) is not None
            ]

            if len(components_with_bb) < 2:
                continue

            # Check for horizontal flow
            h_flow = self._check_horizontal_flow(components_with_bb)
            if h_flow:
                container = component_model.get_component(container_id)
                container.add_property("layout", "horizontal-flow")
                container.add_property("flow_info", h_flow)
                continue

            # Check for vertical flow
            v_flow = self._check_vertical_flow(components_with_bb)
            if v_flow:
                container = component_model.get_component(container_id)
                container.add_property("layout", "vertical-flow")
                container.add_property("flow_info", v_flow)

    def _check_horizontal_flow(
        self, components_with_bb: list[tuple[Component, list[int]]]
    ) -> dict[str, Any] | None:
        """Check if components form a horizontal flow arrangement."""
        # Convert bounding boxes to numpy arrays for easier computation
        bboxes = np.array([bb for _, bb in components_with_bb], dtype=np.float64)

        # Calculate centers
        centers_x = np.mean(bboxes[:, [0, 2]], axis=1)
        centers_y = np.mean(bboxes[:, [1, 3]], axis=1)

        # Sort components by x-coordinate
        sorted_indices = np.argsort(centers_x)
        sorted_components = [components_with_bb[i][0] for i in sorted_indices]
        sorted_centers_x = centers_x[sorted_indices]
        sorted_centers_y = centers_y[sorted_indices]

        # Check if components are roughly aligned horizontally
        y_variation = float(np.std(sorted_centers_y))
        if y_variation > 10.0:  # Threshold for vertical alignment
            return None

        # Check if spacing between components is consistent
        x_gaps = np.diff(sorted_centers_x)
        gap_variation = float(np.std(x_gaps))
        mean_gap = float(np.mean(x_gaps))

        if gap_variation > mean_gap * 0.5:  # Allow 50% variation in spacing
            return None

        return {
            "direction": "horizontal",
            "components": [cast("Any", comp).id for comp in sorted_components],
            "mean_gap": mean_gap,
            "gap_variation": gap_variation,
        }

    def _check_vertical_flow(
        self, components_with_bb: list[tuple[Component, list[int]]]
    ) -> dict[str, Any] | None:
        """Check if components form a vertical flow arrangement."""
        # Convert bounding boxes to numpy arrays for easier computation
        bboxes = np.array([bb for _, bb in components_with_bb], dtype=np.float64)

        # Calculate centers
        centers_x = np.mean(bboxes[:, [0, 2]], axis=1)
        centers_y = np.mean(bboxes[:, [1, 3]], axis=1)

        # Sort components by y-coordinate
        sorted_indices = np.argsort(centers_y)
        sorted_components = [components_with_bb[i][0] for i in sorted_indices]
        sorted_centers_x = centers_x[sorted_indices]
        sorted_centers_y = centers_y[sorted_indices]

        # Check if components are roughly aligned vertically
        x_variation = float(np.std(sorted_centers_x))
        if x_variation > 10.0:  # Threshold for horizontal alignment
            return None

        # Check if spacing between components is consistent
        y_gaps = np.diff(sorted_centers_y)
        gap_variation = float(np.std(y_gaps))
        mean_gap = float(np.mean(y_gaps))

        if gap_variation > mean_gap * 0.5:  # Allow 50% variation in spacing
            return None

        return {
            "direction": "vertical",
            "components": [cast("Any", comp).id for comp in sorted_components],
            "mean_gap": mean_gap,
            "gap_variation": gap_variation,
        }
