"""Component Validator Module."""

from typing import Any

from .component_properties import COMPONENT_PROPERTIES


class ComponentValidator:
    """A class that validates components against their type definitions."""

    def __init__(self, property_definitions: dict[str, Any] | None = None):
        """Initialize the ComponentValidator with property definitions."""
        self.property_definitions = property_definitions or COMPONENT_PROPERTIES

    def validate_component(self, component: dict[str, Any]) -> list[str]:
        """Validate a component against its type definition.

        Args:
            component: The component to validate.

        Returns:
            A list of error messages. Empty if validation passes.
        """
        errors = []

        # Check required properties
        if "type" not in component:
            errors.append("Component must have a type")
            return errors

        if "id" not in component:
            errors.append("Component must have an id")

        # Validate properties against their expected types
        for prop_name, prop_value in component.items():
            if prop_name in self.property_definitions:
                expected_type = self.property_definitions[prop_name]
                if not isinstance(prop_value, expected_type):
                    errors.append(
                        f"Property '{prop_name}' has incorrect type. "
                        f"Expected {expected_type.__name__}, got {type(prop_value).__name__}"
                    )

        return errors
