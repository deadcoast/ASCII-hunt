class ComponentModel:
    def __init__(self):
        self.components = {}
        self.root_components = set()
        self.component_types = {}
        self.relationships = {}

    def add_component(self, component):
        """Add a component to the model."""
        component_id = component.id
        self.components[component_id] = component

        # Register component by type
        component_type = component.type
        if component_type not in self.component_types:
            self.component_types[component_type] = set()
        self.component_types[component_type].add(component_id)

        # Initially, consider it a root component
        self.root_components.add(component_id)

    def add_relationship(self, source_id, target_id, relationship_type):
        """Add a relationship between components."""
        if source_id not in self.components or target_id not in self.components:
            raise ValueError("Both components must exist in the model")

        # Add to relationships dictionary
        if source_id not in self.relationships:
            self.relationships[source_id] = {}
        if relationship_type not in self.relationships[source_id]:
            self.relationships[source_id][relationship_type] = set()

        self.relationships[source_id][relationship_type].add(target_id)

        # If this is a containment relationship, update root status
        if relationship_type == "contains":
            if target_id in self.root_components:
                self.root_components.remove(target_id)

    def get_component(self, component_id):
        """Get a component by ID."""
        return self.components.get(component_id)

    def get_components_by_type(self, component_type):
        """Get all components of a specific type."""
        component_ids = self.component_types.get(component_type, set())
        return [self.components[cid] for cid in component_ids]

    def get_relationships(self, component_id, relationship_type=None):
        """Get components related to the specified component."""
        if component_id not in self.relationships:
            return []

        if relationship_type is not None:
            related_ids = self.relationships[component_id].get(relationship_type, set())
            return [self.components[rid] for rid in related_ids]
        else:
            # Get all relationships
            related_ids = set()
            for rel_type, ids in self.relationships[component_id].items():
                related_ids.update(ids)
            return [self.components[rid] for rid in related_ids]

    def get_contained_components(self, container_id):
        """Get components contained within a container component."""
        return self.get_relationships(container_id, "contains")

    def get_container(self, component_id):
        """Get the container of a component, if any."""
        for potential_container, relationships in self.relationships.items():
            if (
                "contains" in relationships
                and component_id in relationships["contains"]
            ):
                return self.components[potential_container]
        return None

    def get_hierarchy(self):
        """Get a hierarchical representation of the component model."""
        hierarchy = {}

        def build_hierarchy_node(component_id):
            component = self.components[component_id]
            node = {"component": component, "children": []}

            # Add contained components as children
            contained = self.get_contained_components(component_id)
            for child in contained:
                child_node = build_hierarchy_node(child.id)
                node["children"].append(child_node)

            return node

        # Start with root components
        for root_id in self.root_components:
            hierarchy[root_id] = build_hierarchy_node(root_id)

        return hierarchy

    def validate(self):
        """Validate the component model for consistency."""
        errors = []

        # Check that all components have required properties
        for component_id, component in self.components.items():
            if not component.validate():
                errors.append(f"Component {component_id} ({component.type}) is invalid")

        # Check for circular containment
        def check_circular_containment(component_id, visited=None):
            if visited is None:
                visited = set()

            if component_id in visited:
                return True  # Circular reference found

            visited.add(component_id)

            # Check all contained components
            contained = self.get_contained_components(component_id)
            for child in contained:
                if check_circular_containment(child.id, visited.copy()):
                    return True

            return False

        for root_id in self.root_components:
            if check_circular_containment(root_id):
                errors.append(f"Circular containment detected from component {root_id}")

        return len(errors) == 0, errors
