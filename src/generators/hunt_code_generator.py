"""Hunt Code Generator Module."""

import jinja2


class HuntCodeGenerator:
    def __init__(self, template_registry=None):
        """
        Initialize the HuntCodeGenerator with an optional template registry.

        Args:
        template_registry (dict, optional): A dictionary containing templates
            for different formats. Defaults to an empty dictionary.
        """
        self.template_registry = template_registry or {}

    def cook(self, components, format_name, options=None):
        """Generate code for components in the specified format."""
        if options is None:
            options = {}

        if format_name not in self.template_registry:
            raise ValueError(f"Unknown format: {format_name}")

        template = self.template_registry[format_name]
        return template.render(components, options)

    def rack(self, components, view_mode, options=None):
        """Create a visual preview of components."""
        if options is None:
            options = {}

        if view_mode == "ascii":
            return self._render_ascii_preview(components, options)
        elif view_mode == "html":
            return self._render_html_preview(components, options)
        else:
            raise ValueError(f"Unknown view mode: {view_mode}")

    def boil(self, output, mode, options=None):
        """Reduce or simplify the output."""
        if options is None:
            options = {}

        if mode == "minimal":
            return self._minimize_output(output, options)
        elif mode == "pretty":
            return self._prettify_output(output, options)
        else:
            raise ValueError(f"Unknown boil mode: {mode}")
