class CodeTemplate:
    def __init__(self, template_text):
        self.template_text = template_text
        self.placeholders = self._extract_placeholders(template_text)

    def render(self, component, indent="", options=None):
        """Render the template for a component."""
        if options is None:
            options = {}

        # Create context for rendering
        context = {"component": component, "options": options, "indent": indent}

        # Replace placeholders
        rendered_text = self.template_text

        for placeholder in self.placeholders:
            value = self._evaluate_placeholder(placeholder, context)
            rendered_text = rendered_text.replace(f"{{{placeholder}}}", str(value))

        # Apply indentation
        indented_text = self._apply_indentation(rendered_text, indent)

        return indented_text

    def _extract_placeholders(self, template_text):
        """Extract placeholders from template text."""
        placeholders = []
        current_pos = 0

        while True:
            start_pos = template_text.find("{", current_pos)

            if start_pos == -1:
                break

            end_pos = template_text.find("}", start_pos)

            if end_pos == -1:
                break

            placeholder = template_text[start_pos + 1 : end_pos]
            placeholders.append(placeholder)

            current_pos = end_pos + 1

        return placeholders

    def _evaluate_placeholder(self, placeholder, context):
        """Evaluate a placeholder in the given context."""
        component = context["component"]
        options = context["options"]

        if placeholder.startswith("component."):
            # Component property
            prop_name = placeholder[len("component.") :]
            return component.properties.get(prop_name, "")

        elif placeholder.startswith("options."):
            # Option value
            option_name = placeholder[len("options.") :]
            return options.get(option_name, "")

        elif placeholder == "component.id":
            # Component ID
            return component.id

        elif placeholder == "component.type":
            # Component type
            return component.type

        # Special placeholders
        if placeholder == "var_name":
            # Generate variable name
            return f"{component.type.lower()}_{component.id}"

        return ""

    def _apply_indentation(self, text, indent):
        """Apply indentation to text."""
        lines = text.split("\n")
        indented_lines = [indent + line for line in lines]
        return "\n".join(indented_lines)
