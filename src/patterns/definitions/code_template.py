"""CodeTemplate class for rendering code templates with placeholders.

This class provides a mechanism to render code templates by replacing placeholders
with actual values. It supports component properties, options, and special
placeholders for variable names.
"""


class CodeTemplate:
    def __init__(self, template_text: str) -> None:
        """Initialize a CodeTemplate instance.

        Args:
            template_text (str): The template text containing placeholders
                                to be replaced during rendering.

        Attributes:
            template_text (str): Stores the provided template text.
            placeholders (list): A list of placeholders extracted from the
                                template text.
        """
        self.template_text = template_text
        self.placeholders = self._extract_placeholders(template_text)

    def render(self, component, indent="", options=None):
        """Render the template for a component.

        Args:
            component (Component): The component to render a template for.
            indent (str): The indentation to apply to the rendered template.
            options (dict): A dictionary of options to pass to the template.

        Returns:
            str: The rendered template.
        """
        if options is None:
            options = {}

        # Create context for rendering
        context = {"component": component, "options": options, "indent": indent}

        # Replace placeholders
        rendered_text = self.template_text

        for placeholder in self.placeholders:
            value = self._evaluate_placeholder(placeholder, context)
            rendered_text = rendered_text.replace(f"{{{placeholder}}}", str(value))

        return self._apply_indentation(rendered_text, indent)

    def _extract_placeholders(self, template_text):
        """Extracts placeholders from a given template text.

        Args:
            template_text (str): The template text to extract placeholders from.

        Returns:
            list: A list of placeholders extracted from the template text.

        Placeholders are any strings enclosed in curly braces (e.g. {prop_name}).
        The function iterates over the template text, finding the start and end
        positions of placeholders, and extracts the text within those positions.
        The extracted placeholders are stored in a list and returned.
        """
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
        """Evaluates a placeholder based on the given context.

        Placeholders can access component properties and options using the
        following syntax:
            - {component.<prop_name>} to access a component property
            - {options.<option_name>} to access an option value

        Additionally, the following special placeholders are available:
            - {component.id} to access the component ID
            - {component.type} to access the component type
            - {var_name} to generate a variable name based on the component
              type and ID

        If a placeholder is not recognized, an empty string is returned.
        """
        component = context["component"]
        options = context["options"]

        if placeholder.startswith("component."):
            # Component property
            prop_name = placeholder[len("component.") :]
            return component.properties.get(prop_name, "")

        if placeholder.startswith("options."):
            # Option value
            option_name = placeholder[len("options.") :]
            return options.get(option_name, "")

        if placeholder == "component.id":
            # Component ID
            return component.id

        if placeholder == "component.type":
            # Component type
            return component.type

        # Special placeholders
        if placeholder == "var_name":
            # Generate variable name
            return f"{component.type.lower()}_{component.id}"

        return ""

    def _apply_indentation(self, text, indent):
        """Apply the specified indentation to each line of the given text.

        Args:
            text (str): The text to which indentation should be applied.
            indent (str): The indentation string to prepend to each line.

        Returns:
            str: The text with indentation applied to each line.
        """
        lines = text.split("\n")
        indented_lines = [indent + line for line in lines]
        return "\n".join(indented_lines)
