"""Component Validator Module."""

from components.component_model_representation import COMPONENT_PROPERTIES


class ComponentValidator:
    def __init__(self, property_definitions=COMPONENT_PROPERTIES):
        """Initialize the ComponentValidator.

        The ComponentValidator has the following property:
        - self.property_definitions: a dictionary of component type definitions,
          where each key is a component type and each value is a dictionary
          containing the component type's properties and their definitions.
        """
        self.property_definitions = property_definitions

    def validate_component(self, component):
        """Validate a component against its type definition."""
        if component.type not in self.property_definitions:
            return [f"Unknown component type: {component.type}"]

        errors = []
        type_def = self.property_definitions[component.type]

        # Check required properties
        for prop in type_def["required"]:
            if prop not in component.properties:
                errors.append(
                    f"Missing required property '{prop}' for {component.type}"
                )

        # Check property types (would implement type checking here)
        for prop, value in component.properties.items():
            if prop not in type_def["properties"]:
                errors.append(f"Unexpected property '{prop}' for {component.type}")
            elif not isinstance(value, type_def["properties"][prop]["type"]):
                errors.append(
                    f"Invalid type for property '{prop}' of {component.type}: expected {type_def['properties'][prop]['type']}, got {type(value)}"
                )
            elif type_def["properties"][prop]["type"] == "number":
                if not isinstance(value, (int, float)):
                    errors.append(
                        f"Invalid type for property '{prop}' of {component.type}: expected number, got {type(value)}"
                    )
            elif type_def["properties"][prop]["type"] == "boolean":
                if not isinstance(value, bool):
                    errors.append(
                        f"Invalid type for property '{prop}' of {component.type}: expected boolean, got {type(value)}"
                    )
            elif type_def["properties"][prop]["type"] == "string":
                if not isinstance(value, str):
                    errors.append(
                        f"Invalid type for property '{prop}' of {component.type}: expected string, got {type(value)}"
                    )
            elif type_def["properties"][prop]["type"] == "list":
                if not isinstance(value, list):
                    errors.append(
                        f"Invalid type for property '{prop}' of {component.type}: expected list, got {type(value)}"
                    )
            elif type_def["properties"][prop]["type"] == "object":
                if not isinstance(value, dict):
                    errors.append(
                        f"Invalid type for property '{prop}' of {component.type}: expected object, got {type(value)}"
                    )

        # Recursively validate children
        for child in component.children:
            child_errors = self.validate_component(child)
            errors.extend([f"In child {child.id}: {err}" for err in child_errors])

        return errors
