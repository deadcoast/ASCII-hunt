"""Layout Analysis Module."""


class LayoutAnalyzer:
    def __init__(self):
        """
        Initialize a LayoutAnalyzer instance.

        This constructor creates a LayoutAnalyzer with an empty layout_graph
        dictionary to store layout relationships between components.
        """
        self.layout_graph = {}

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
        container_groups = {}

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
            groups_by_y = {}

            for comp, bb in components_with_bb:
                y_mid = (bb[1] + bb[3]) // 2

                if y_mid not in groups_by_y:
                    groups_by_y[y_mid] = []

                groups_by_y[y_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed = set()

            for y in sorted(groups_by_y.keys()):
                if y in processed:
                    continue

                # Find similar y-values
                aligned_group = groups_by_y[y]

                for y2 in range(y + 1, y + 3):
                    if y2 in groups_by_y:
                        aligned_group.extend(groups_by_y[y2])
                        processed.add(y2)

                if len(aligned_group) >= 2:
                    # Sort by x-coordinate
                    aligned_group.sort(key=lambda item: item[1][0])
                    aligned_groups.append(aligned_group)

        elif alignment_type == "vertical":
            # Group by x-coordinate
            groups_by_x = {}

            for comp, bb in components_with_bb:
                x_mid = (bb[0] + bb[2]) // 2

                if x_mid not in groups_by_x:
                    groups_by_x[x_mid] = []

                groups_by_x[x_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed = set()

            for x in sorted(groups_by_x.keys()):
                if x in processed:
                    continue

                # Find similar x-values
                aligned_group = groups_by_x[x]

                for x2 in range(x + 1, x + 3):
                    if x2 in groups_by_x:
                        aligned_group.extend(groups_by_x[x2])
                        processed.add(x2)

                if len(aligned_group) >= 2:
                    # Sort by y-coordinate
                    aligned_group.sort(key=lambda item: item[1][1])
                    aligned_groups.append(aligned_group)

        return aligned_groups

    def _get_bounding_box(self, component):
        """Get the bounding box of a component."""
        if "refined_bounding_box" in component.properties:
            return component.properties["refined_bounding_box"]
        elif "bounding_box" in component.properties:
            return component.properties["bounding_box"]
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
        row_positions = set()
        col_positions = set()

        for comp, bb in components_with_bb:
            y_mid = (bb[1] + bb[3]) // 2
            x_mid = (bb[0] + bb[2]) // 2

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

        if len(components_with_bb) < grid_size * 0.8:  # Allow some missing cells
            return None

        # Create a mapping of components to grid cells
        grid_map = {}

        for comp, bb in components_with_bb:
            y_mid = (bb[1] + bb[3]) // 2
            x_mid = (bb[0] + bb[2]) // 2

            row_idx = self._find_nearest_index(y_mid, rows)
            col_idx = self._find_nearest_index(x_mid, cols)

            grid_map[(row_idx, col_idx)] = comp.id

        return {"rows": len(rows), "columns": len(cols), "grid_map": grid_map}

    def _find_nearest_index(self, value, positions):
        """Find the index of the nearest position."""
        return min(range(len(positions)), key=lambda i: abs(positions[i] - value))

    def _analyze_flow_arrangement(self, component_model):
        """Analyze flow arrangements of components."""
        # Get all containers
        for container_id in list(component_model.components.keys()):
            # Get contained components
            contained = component_model.get_contained_components(container_id)

            if len(contained) < 2:  # Need at least 2 components for a flow
                continue

            # Get components with bounding boxes
            components_with_bb = [
                (c, self._get_bounding_box(c))
                for c in contained
                if self._get_bounding_box(c)
            ]

            if len(components_with_bb) < 2:
                continue

            # Check for horizontal flow
            h_flow = self._check_horizontal_flow(components_with_bb)

            if h_flow:
                # Add horizontal flow arrangement to container
                container = component_model.get_component(container_id)
                container.add_property("layout", "horizontal_flow")
                container.add_property("flow_info", h_flow)
                continue

            # Check for vertical flow
            v_flow = self._check_vertical_flow(components_with_bb)

            if v_flow:
                # Add vertical flow arrangement to container
                container = component_model.get_component(container_id)
                container.add_property("layout", "vertical_flow")
                container.add_property("flow_info", v_flow)

    def _check_horizontal_flow(self, components_with_bb):
        """Check if components form a horizontal flow arrangement."""
        # Sort by x-coordinate
        sorted_components = sorted(components_with_bb, key=lambda item: item[1][0])

        # Check if components are arranged horizontally
        avg_width = sum((bb[2] - bb[0]) for _, bb in sorted_components) / len(
            sorted_components
        )

        # Check that components have similar y-positions
        y_mids = [(bb[1] + bb[3]) // 2 for _, bb in sorted_components]
        y_variance = max(y_mids) - min(y_mids)

        if y_variance > avg_width * 0.5:  # Allow some vertical variation
            return None

        # Check for consistent spacing
        spacings = []
        for i in range(1, len(sorted_components)):
            prev_bb = sorted_components[i - 1][1]
            curr_bb = sorted_components[i][1]

            spacing = curr_bb[0] - prev_bb[2]
            spacings.append(spacing)

        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        spacing_variance = (
            max(abs(s - avg_spacing) for s in spacings) if spacings else 0
        )

        if spacing_variance > avg_width * 0.3:  # Allow some spacing variation
            return None

        # Create flow information
        flow_map = {}

        for i, (comp, _) in enumerate(sorted_components):
            flow_map[i] = comp.id

        return {
            "direction": "horizontal",
            "components": len(sorted_components),
            "flow_map": flow_map,
            "avg_spacing": avg_spacing,
        }

    def _check_vertical_flow(self, components_with_bb):
        """Check if components form a vertical flow arrangement."""
        # Sort by y-coordinate
        sorted_components = sorted(components_with_bb, key=lambda item: item[1][1])

        # Check if components are arranged vertically
        avg_height = sum((bb[3] - bb[1]) for _, bb in sorted_components) / len(
            sorted_components
        )

        # Check that components have similar x-positions
        x_mids = [(bb[0] + bb[2]) // 2 for _, bb in sorted_components]
        x_variance = max(x_mids) - min(x_mids)

        if x_variance > avg_height * 0.5:  # Allow some horizontal variation
            return None

        # Check for consistent spacing
        spacings = []
        for i in range(1, len(sorted_components)):
            prev_bb = sorted_components[i - 1][1]
            curr_bb = sorted_components[i][1]

            spacing = curr_bb[1] - prev_bb[3]
            spacings.append(spacing)

        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        spacing_variance = (
            max(abs(s - avg_spacing) for s in spacings) if spacings else 0
        )

        if spacing_variance > avg_height * 0.3:  # Allow some spacing variation
            return None

        # Create flow information
        flow_map = {}

        for i, (comp, _) in enumerate(sorted_components):
            flow_map[i] = comp.id

        return {
            "direction": "vertical",
            "components": len(sorted_components),
            "flow_map": flow_map,
            "avg_spacing": avg_spacing,
        }
