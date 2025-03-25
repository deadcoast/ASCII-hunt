"""Python Tkinter Generator Module."""


class PythonTkinterGenerator:
    def __init__(self):
        """
        Initialize the PythonTkinterGenerator.

        The PythonTkinterGenerator has the following properties:
        - self.template_registry: a dictionary mapping component types to
          template functions for generating code
        - self.default_template: the template to use for components without a
          specific template
        """
        self.template_registry = {}
        self.default_template = None

    def register_template(self, component_type, template):
        """Register a template for a specific component type."""
        self.template_registry[component_type] = template

    def set_default_template(self, template):
        """Set the default template for components without a specific template."""
        self.default_template = template

    def generate(self, component_model, options=None):
        """Generate Tkinter code for the given component model."""
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

        # Get the component hierarchy
        hierarchy = component_model.get_hierarchy()

        # Generate code for each root component
        for root_id, node in hierarchy.items():
            component_code = self._generate_component_code(node, "        ", options)
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

    def _generate_component_code(self, node, indent, options):
        """Generate code for a component and its children."""
        component = node["component"]
        children = node["children"]

        # Get component type
        component_type = component.type

        # Get appropriate template
        template = self.template_registry.get(component_type, self.default_template)

        if not template:
            # Skip if no template
            return []

        # Generate code for this component
        try:
            component_code = template.render(component, indent, options)
        except Exception as e:
            # Log error and return empty list
            print(f"Error generating code for component {component.id}: {e!s}")
            return []

        code_parts = component_code.split("\n")

        # Generate code for children
        for child_node in children:
            child_code = self._generate_component_code(
                child_node, indent + "    ", options
            )
            code_parts.extend(child_code)

        return code_parts
