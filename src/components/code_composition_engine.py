"""Code Composition Engine Module."""

from components.abstract_component import AbstractComponent


class CodeCompositionEngine:
    def __init__(self, generator):
        """
        Initialize a CodeCompositionEngine.

        The CodeCompositionEngine has the following properties:
        - self.generator: the code generator to use for generating code
        """
        self.generator = generator

    def compose_container_with_children(self, container, child_codes):
        """Compose container code with its children."""
        container_type = container.type

        if container_type == "Window":
            # For windows, we add child components into the window context
            container_code = self.generator.generate_window_code(container)
            child_codes = [
                self.generator.generate_component_code(child)
                for child in container.children
            ]
            adjusted_child_codes = [
                self._adjust_parent(code, container_code) for code in child_codes
            ]

            return f"{container_code}\n\n" + "\n".join(adjusted_child_codes)

        elif container_type == "Panel":
            # For panels, we need to add child components as panel children
            panel_var = self._get_variable_name(container)
            adjusted_child_codes = [
                self._adjust_parent(code, panel_var) for code in child_codes
            ]
            return f"{container_code}\n\n" + "\n".join(adjusted_child_codes)

        else:
            # Handle other container types...
            pass

    def _get_variable_name(self, component):
        """Get the variable name used for a component."""
        return f"{component.type.lower()}_{component.id}"

    def _adjust_parent(self, child_code, parent_var):
        """Adjust child code to use the correct parent variable."""
        # This would be framework-specific logic
        pass
