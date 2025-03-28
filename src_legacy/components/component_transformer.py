class ComponentTransformer:
    def __init__(self):
        self.transformations = {}

    def register_transformation(self, source_type, target_type, transform_func):
        """Register a transformation function between component types."""
        if source_type not in self.transformations:
            self.transformations[source_type] = {}
        self.transformations[source_type][target_type] = transform_func

    def transform(self, component, target_type):
        """Transform a component to a different type."""
        if component.type == target_type:
            return component

        if (
            component.type in self.transformations
            and target_type in self.transformations[component.type]
        ):
            return self.transformations[component.type][target_type](component)

        raise ValueError(
            f"No transformation defined from {component.type} to {target_type}"
        )
