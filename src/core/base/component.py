"""Component Module.

This module provides a class for representing UI components in the system.
"""

from typing import Any


class Component:
    """A class for representing UI components.

    The Component class stores information about a UI component, including its
    properties, relationships, and constraints.
    """

    def __init__(
        self,
        name: str = "",
        component_id: str | None = None,
        component_type: str | None = None,
        properties: dict[str, Any] | None = None,
        constraints: list[str] | None = None,
    ):
        """Initialize the Component class.

        Args:
            name: The name of the component.
            component_id: The ID of the component.
            component_type: The type of the component.
            properties: A dictionary of component properties.
            constraints: A list of constraints for the component.
        """
        self.name = name
        self.id = component_id
        self.type = component_type
        self.properties = properties or {}
        self.constraints = constraints or []
        self.children: list[Component] = []
        self.parent: Component | None = None
        self.relationships: dict[str, list[Component]] = {}
        self.metadata: dict[str, Any] = {}
        self.bounds: dict[str, int] | None = None
        self.tags: set[str] = set()

    def add_property(self, name: str, value: Any) -> None:
        """Add a property to the component.

        Args:
            name: The name of the property.
            value: The value of the property.
        """
        self.properties[name] = value

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property from the component.

        Args:
            name: The name of the property.
            default: The default value to return if the property doesn't exist.

        Returns:
            The value of the property, or the default value if it doesn't exist.
        """
        return self.properties.get(name, default)

    def add_child(self, child: "Component") -> None:
        """Add a child component.

        Args:
            child: The child component to add.
        """
        self.children.append(child)
        child.parent = self

    def remove_child(self, child: "Component") -> None:
        """Remove a child component.

        Args:
            child: The child component to remove.
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def add_relationship(self, relationship_type: str, component: "Component") -> None:
        """Add a relationship to another component.

        Args:
            relationship_type: The type of relationship.
            component: The related component.
        """
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []

        if component not in self.relationships[relationship_type]:
            self.relationships[relationship_type].append(component)

    def get_relationships(
        self, relationship_type: str | None = None
    ) -> dict[str, list["Component"]]:
        """Get relationships of the component.

        Args:
            relationship_type: The type of relationship to get, or None to get all.

        Returns:
            A dictionary of relationship types to lists of related components,
            or a dictionary with only the specified relationship type if provided.
        """
        if relationship_type is None:
            return self.relationships

        return {relationship_type: self.relationships.get(relationship_type, [])}

    def add_constraint(self, constraint: str) -> None:
        """Add a constraint to the component.

        Args:
            constraint: The constraint to add.
        """
        if constraint not in self.constraints:
            self.constraints.append(constraint)

    def get_constraints(self) -> list[str]:
        """Get all constraints of the component.

        Returns:
            A list of constraints.
        """
        return self.constraints

    def add_tag(self, tag: str) -> None:
        """Add a tag to the component.

        Args:
            tag: The tag to add.
        """
        self.tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the component.

        Args:
            tag: The tag to remove.
        """
        self.tags.discard(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if the component has a tag.

        Args:
            tag: The tag to check.

        Returns:
            True if the component has the tag, False otherwise.
        """
        return tag in self.tags

    def set_bounds(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Set the bounds of the component.

        Args:
            x1: The x-coordinate of the top-left corner.
            y1: The y-coordinate of the top-left corner.
            x2: The x-coordinate of the bottom-right corner.
            y2: The y-coordinate of the bottom-right corner.
        """
        self.bounds = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

    def get_bounds(self) -> dict[str, int] | None:
        """Get the bounds of the component.

        Returns:
            A dictionary with the bounds of the component, or None if not set.
        """
        return self.bounds

    def to_dict(self) -> dict[str, Any]:
        """Convert the component to a dictionary.

        Returns:
            A dictionary representation of the component.
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "properties": self.properties.copy(),
            "constraints": self.constraints.copy(),
            "children": [child.to_dict() for child in self.children],
            "relationships": {
                rel_type: [comp.id for comp in comps]
                for rel_type, comps in self.relationships.items()
            },
            "bounds": self.bounds,
            "tags": list(self.tags),
            "metadata": self.metadata.copy(),
        }
