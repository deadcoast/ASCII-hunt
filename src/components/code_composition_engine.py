"""Code Composition Engine Module."""

from typing import Any


class CodeCompositionEngine:
    def __init__(self, generator: Any):
        """
        Initialize a CodeCompositionEngine.

        The CodeCompositionEngine has the following properties:
        - self.generator: the code generator to use for generating code
        """
        self.generator = generator

    def compose_container_with_children(
        self, container: Any, child_codes: list[str]
    ) -> str:
        """Compose container code with its children."""
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

        elif container_type == "Panel":
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

        else:
            # Handle other container types...
            return container_code

    def _get_variable_name(self, component: Any) -> str:
        """Get the variable name used for a component."""
        return f"{component.type.lower()}_{component.id}"

    def _adjust_parent(self, child_code: str | None, parent_var: str) -> str | None:
        """Adjust child code to use the correct parent variable."""
        if child_code is None:
            return None
        # This would be framework-specific logic
        return child_code  # Return the child_code for now
