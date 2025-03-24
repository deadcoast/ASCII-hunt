"""Component Template Engine Module."""

import re


class TemplateEngine:
    def __init__(self):
        """Initialize the TemplateEngine.

        The TemplateEngine has the following property:
        - self.expression_pattern: a regular expression pattern for matching template
          expressions of the form {expression}, where expression is a simple
          Python expression that can be evaluated in the context of the
          component being rendered.
        """
        self.expression_pattern = re.compile(r"\{([^}]+)\}")

    def render(self, template, data):
        """Render a template with the provided data."""

        def replace_expr(match):
            expr = match.group(1).strip()

            # Handle special case for children
            if expr == "children":
                return "{children}"

            # Simple expression evaluation
            try:
                result = self._evaluate_expression(expr, data)
                return str(result)
            except Exception as e:
                return f"{{Error: {str(e)}}}"

        return self.expression_pattern.sub(replace_expr, template)

    def _evaluate_expression(self, expr, data):
        """Evaluate a simple expression within template."""
        # For simplicity, we're using a straightforward approach
        # A more robust implementation would use a proper expression parser

        if expr.startswith("component."):
            path = expr[10:].split(".")
            value = data["component"]

            for key in path:
                if hasattr(value, key):
                    value = getattr(value, key)
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return value

        elif expr.startswith("properties."):
            key = expr[11:]
            return data["properties"].get(key)

        # Support for simple conditionals
        elif " if " in expr and " else " in expr:
            condition, rest = expr.split(" if ", 1)
            then_part, else_part = rest.split(" else ", 1)

            condition_value = self._evaluate_expression(condition, data)

            if condition_value:
                return self._evaluate_expression(then_part, data)
            else:
                return self._evaluate_expression(else_part, data)

        # Handle literals
        elif expr == "true":
            return True
        elif expr == "false":
            return False
        elif expr == "null" or expr == "none":
            return None
        elif expr.isdigit():
            return int(expr)
        elif expr.replace(".", "", 1).isdigit() and expr.count(".") <= 1:
            return float(expr)
        elif expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        return f"{{Unknown: {expr}}}"
