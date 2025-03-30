"""Python Tkinter Generator Module."""

import logging
from collections.abc import Callable
from typing import Any

from src.core.generation.code_generator import CodeGenerator
from src.engine.modeling.component_model_representation import ComponentModel

# Setup logger
logger = logging.getLogger(__name__)


class PythonTkinterGenerator(CodeGenerator):
    """Generates Python Tkinter code from a component model representation."""

    def __init__(self) -> None:
        """Initialize the PythonTkinterGenerator."""
        super().__init__()  # Call base class init if needed
        self.template_registry: dict[str, Callable[..., str]] = {}
        self.default_template: Callable[..., str] | None = None

    def register_template(
        self, component_type: str, template: Callable[..., str]
    ) -> None:
        """Register a template for a specific component type."""
        self.template_registry[component_type] = template

    def set_default_template(self, template: Callable[..., str]) -> None:
        """Set the default template for components without a specific template."""
        self.default_template = template

    # Renamed to avoid signature conflict with base class CodeGenerator.generate
    def generate_tkinter_code(
        self, component_model: ComponentModel, options: dict | None = None
    ) -> str:
        """Generate Tkinter code for the given component model.

        Args:
            component_model: The component model object.
            options: Dictionary of generation options.

        Returns:
            The generated Tkinter code as a string.
        """
        if options is None:
            options = {}

        # Start with imports
        code_parts = [
            "import tkinter as tk",
            "from tkinter import ttk\n",
            "class Application(tk.Tk):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.title('ASCII UI Application')",
            "        self.geometry('800x600')",
            "        self.create_widgets()\n",
            "    def create_widgets(self):",
        ]

        # Get the component hierarchy - Use get_all_components instead
        all_components = (
            component_model.get_all_components()
            if hasattr(component_model, "get_all_components")
            else []
        )

        # Assume the list contains the nodes needed
        # Might need filtering or specific root finding depending on model structure
        for _node in all_components:
            component_code = self._generate_component_code(_node, "        ", options)
            code_parts.extend(component_code)

        # Add main function
        code_parts.extend(
            [
                "\n",
                "if __name__ == '__main__':",
                "    app = Application()",
                "    app.mainloop()",
            ]
        )

        # Join all code parts
        return "\n".join(code_parts)

    def _generate_component_code(
        self, node: dict[str, Any], indent: str, options: dict
    ) -> list[str]:
        """Generate code for a component and its children."""
        component = node.get("component", {})
        children = node.get("children", [])

        # Get component type
        component_type = getattr(component, "type", "unknown")  # Safer access

        # Get appropriate template
        template = self.template_registry.get(component_type, self.default_template)

        if not template:
            # Skip if no template
            return []

        # Generate code for this component
        try:
            # Assuming template callable accepts component, indent, options
            component_code_str = template(component, indent, options)
            component_code = component_code_str.split("\n")
        except AttributeError:
            logger.exception(  # Use logger.exception
                "AttributeError rendering template for component type '%s'",
                component_type,
            )
            return []
        except Exception:  # Catch other potential template errors more broadly
            logger.exception(
                "Unexpected error rendering template for component type '%s'",
                component_type,
            )
            return []

        # Generate code for children
        for child_node in children:
            child_code = self._generate_component_code(
                child_node, f"{indent}    ", options
            )
            component_code.extend(child_code)

        return component_code
