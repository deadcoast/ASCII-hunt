"""Code Composition Engine Module."""

from typing import Any


class CodeCompositionEngine:
    def __init__(self, generator: Any):
        """Initialize a CodeCompositionEngine.

        The CodeCompositionEngine has the following properties:
        - self.generator: the code generator to use for generating code
        """
        self.generator = generator

    def compose_container_with_children(
        self, container: Any, child_codes: list[str]
    ) -> str:
        """Compose container code with its children.

        For windows, we add child components into the window context.
        For panels, we need to add child components as panel children.
        For other container types, we handle it differently.

        Args:
            container (Any): the container component
            child_codes (list[str]): the code of the child components

        Returns:
            str: the composed code
        """
        container_type = container.type
        container_code = ""  # Initialize container_code

        if container_type == "Window":
            # For windows, we add child components into the window context
            container_code = self.generator.generate_window_code(container)
            child_codes = [
                str(self.generator.generate_component_code(child))
                for child in container.children
            ]
            adjusted_child_codes = [
                self._adjust_parent(code, container_code)
                for code in child_codes
                if code is not None
            ]

            return f"{container_code}\n\n" + "\n".join(
                code for code in adjusted_child_codes if code is not None
            )

        if container_type == "Panel":
            # For panels, we need to add child components as panel children
            panel_var = self._get_variable_name(container)
            container_code = self.generator.generate_panel_code(
                container
            )  # Add this line
            adjusted_child_codes = [
                self._adjust_parent(code, panel_var)
                for code in child_codes
                if code is not None
            ]
            return f"{container_code}\n\n" + "\n".join(
                code for code in adjusted_child_codes if code is not None
            )

        # Handle other container types...
        return container_code

    def _get_variable_name(self, component: Any) -> str:
        """Get a variable name for a component, based on its type and ID.

        Args:
            component (Any): the component to get a variable name for

        Returns:
            str: the variable name
        """
        return f"{component.type.lower()}_{component.id}"

    def _adjust_parent(self, child_code: str | None, parent_var: str) -> str | None:
        """Adjust child code to use the correct parent variable.

        Args:
            child_code (str | None): the code of the child component
            parent_var (str): the variable name of the parent component

        Returns:
            str | None: the adjusted code
        """
        return None if child_code is None else child_code
