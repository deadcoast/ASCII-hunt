"""Hunt Code Generator Module."""


class HuntCodeGenerator:
    def __init__(self, template_registry=None):
        """Initialize the HuntCodeGenerator with an optional template registry.

        Args:
        template_registry (dict, optional): A dictionary containing templates
            for different formats. Defaults to an empty dictionary.
        """
        self.template_registry = template_registry or {}

    def _render_ascii_preview(self, components, options):
        """Render components as ASCII art preview.

        Args:
            components (list): List of components to render
            options (dict): Rendering options

        Returns:
            str: ASCII art representation of components
        """
        # Create ASCII grid
        width = options.get("width", 80)
        height = options.get("height", 24)
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Render each component
        for component in components:
            x = component.get("x", 0)
            y = component.get("y", 0)
            char = component.get("char", "?")
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = char

        # Convert grid to string
        return "\n".join("".join(row) for row in grid)

    def _render_html_preview(self, components, options):
        """Render components as HTML preview.

        Args:
            components (list): List of components to render
            options (dict): Rendering options

        Returns:
            str: HTML representation of components
        """
        html = ["<!DOCTYPE html>", "<html>", "<body>"]

        # Add styles
        html.append("<style>")
        html.append(".component { position: absolute; }")
        html.append("</style>")

        # Render each component
        for component in components:
            x = component.get("x", 0)
            y = component.get("y", 0)
            text = component.get("text", "")
            html.append(
                f'<div class="component" style="left: {x}px; top: {y}px;">{text}</div>'
            )

        html.extend(["</body>", "</html>"])
        return "\n".join(html)

    def _minimize_output(self, output, options):
        """Minimize the output by removing unnecessary whitespace and comments.

        Args:
            output (str): Output to minimize
            options (dict): Minimization options

        Returns:
            str: Minimized output
        """
        lines = []
        for line in output.split("\n"):
            # Remove comments
            if "#" in line:
                line = line[: line.index("#")]
            # Remove empty lines and whitespace
            line = line.strip()
            if line:
                lines.append(line)
        return ";".join(lines)

    def _prettify_output(self, output, options):
        """Prettify the output by adding proper indentation and spacing.

        Args:
            output (str): Output to prettify
            options (dict): Prettification options

        Returns:
            str: Prettified output
        """
        indent = 0
        indent_str = "    "
        lines = []

        for line in output.split("\n"):
            line = line.strip()
            if line:
                # Adjust indentation based on braces
                if line.endswith(":"):
                    lines.append(indent_str * indent + line)
                    indent += 1
                elif line.startswith(("return", "break", "continue", "pass")):
                    lines.append(indent_str * indent + line)
                    if indent > 0:
                        indent -= 1
                else:
                    lines.append(indent_str * indent + line)

        return "\n".join(lines)

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
        if view_mode == "html":
            return self._render_html_preview(components, options)
        raise ValueError(f"Unknown view mode: {view_mode}")

    def boil(self, output, mode, options=None):
        """Reduce or simplify the output."""
        if options is None:
            options = {}

        if mode == "minimal":
            return self._minimize_output(output, options)
        if mode == "pretty":
            return self._prettify_output(output, options)
        raise ValueError(f"Unknown boil mode: {mode}")
