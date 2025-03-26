from typing import Any, cast

from ..patterns.pattern_registry import PatternRegistry
from .hunt_parser import HuntParser


class HuntInterpreter:
    def __init__(self, pattern_registry: PatternRegistry | None = None) -> None:
        self.parser = HuntParser()
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.global_context: dict[str, Any] = {}

    def interpret(
        self, hunt_code: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Interpret HUNT DSL code and return the result."""
        if context is not None:
            self.global_context.update(context)

        # Parse the code
        ast = self.parser.parse(hunt_code)
        if ast is None:
            return {"error": "Failed to parse code"}

        # Evaluate the AST
        result = self._evaluate_node(ast, self.global_context)
        if result is None:
            return {"error": "Failed to evaluate AST"}

        return result

    def _evaluate_node(
        self, node: dict[str, Any] | None, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Evaluate an AST node."""
        if node is None:
            return None

        node_type = node.get("type")

        if node_type == "alpha_bracket":
            return self._evaluate_alpha_bracket(node, context)
        if node_type == "beta_bracket":
            return self._evaluate_beta_bracket(node, context)
        if node_type == "gamma_bracket":
            return self._evaluate_gamma_bracket(node, context)
        if node_type == "delta_bracket":
            return self._evaluate_delta_bracket(node, context)
        if node_type == "exec_param":
            return self._evaluate_exec_param(node, context)

        raise ValueError(f"Unknown node type: {node_type}")

    def _evaluate_alpha_bracket(
        self, node: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate an alpha bracket node."""
        command = node.get("command")

        # Create a new scope for this alpha bracket
        local_context = dict(context)

        # Handle hunt command
        if command == "hunt":
            # Check if there's a bridge target
            if node.get("has_bridge") and node.get("bridge_target"):
                bridge_target = cast(str, node.get("bridge_target"))
                local_context["current_module"] = bridge_target

                # Initialize module if not already present
                if bridge_target not in local_context:
                    local_context[bridge_target] = {}

            # Evaluate beta brackets
            beta_results: list[dict[str, Any]] = []

            for beta_node in node.get("beta_brackets", []):
                beta_result = self._evaluate_node(beta_node, local_context)
                if beta_result is not None:
                    beta_results.append(beta_result)

            # Execute the EXEC block if present
            exec_params = node.get("exec_params")

            if exec_params:
                exec_results: list[dict[str, Any]] = []

                for param in exec_params:
                    exec_result = self._evaluate_node(param, local_context)
                    if exec_result is not None:
                        exec_results.append(exec_result)

                # Return the results
                return {
                    "command": command,
                    "beta_results": beta_results,
                    "exec_results": exec_results,
                }

            # Return the results without EXEC
            return {"command": command, "beta_results": beta_results}

        if command == "Track":
            # Register a pattern for tracking
            # This could initiate component recognition based on the pattern

            # Evaluate beta brackets for tracking rules
            beta_results: list[dict[str, Any]] = []

            for beta_node in node.get("beta_brackets", []):
                beta_result = self._evaluate_node(beta_node, local_context)
                if beta_result is not None:
                    beta_results.append(beta_result)

            # Register the tracking pattern
            pattern_name = cast(str, node.get("bridge_target", "default_track"))
            self.pattern_registry.register_tracking_pattern(
                pattern_name, {"type": "track", "rules": beta_results}
            )

            return {
                "command": command,
                "pattern_name": pattern_name,
                "rules": beta_results,
            }

        # Add more commands as needed

        raise ValueError(f"Unknown alpha bracket command: {command}")

    def _evaluate_beta_bracket(
        self, node: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate a beta bracket node."""
        command = node.get("command")

        # Create a new scope for this beta bracket
        local_context = dict(context)

        # Handle INIT command
        if command == "INIT":
            # Check if there's an assignment
            if node.get("has_assign") and node.get("assign_value"):
                assign_value = node.get("assign_value")
                local_context["current_init"] = assign_value

            # Evaluate gamma brackets
            gamma_results: list[dict[str, Any]] = []

            for gamma_node in node.get("gamma_brackets", []):
                gamma_result = self._evaluate_node(gamma_node, local_context)
                if gamma_result is not None:
                    gamma_results.append(gamma_result)

            # Return the results
            return {
                "command": command,
                "init_target": node.get("assign_value"),
                "params": gamma_results,
            }

        if command == "GATHER" or command == "GET":
            # Extract data from the grid based on rules

            # Evaluate gamma brackets for extraction rules
            gamma_results: list[dict[str, Any]] = []

            for gamma_node in node.get("gamma_brackets", []):
                gamma_result = self._evaluate_node(gamma_node, local_context)
                if gamma_result is not None:
                    gamma_results.append(gamma_result)

            # Register the extraction pattern
            pattern_name = node.get("assign_value", "default_gather")
            self.pattern_registry.register_extraction_pattern(
                pattern_name, {"type": "gather", "rules": gamma_results}
            )

            return {
                "command": command,
                "pattern_name": pattern_name,
                "rules": gamma_results,
            }

        # Add more commands as needed

        raise ValueError(f"Unknown beta bracket command: {command}")

    def _evaluate_gamma_bracket(
        self, node: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate a gamma bracket node."""
        command = node.get("command")

        # Create a new scope for this gamma bracket
        local_context = dict(context)

        # Handle param command
        if command == "param":
            # Check if there's a bridge or assignment
            param_name = None

            if node.get("has_bridge") and node.get("bridge_target"):
                param_name = node.get("bridge_target")
            elif node.get("has_assign") and node.get("assign_value"):
                param_name = node.get("assign_value")

            # Evaluate delta brackets
            delta_results: list[dict[str, Any]] = []

            for delta_node in node.get("delta_brackets", []):
                delta_result = self._evaluate_node(delta_node, local_context)
                if delta_result is not None:
                    delta_results.append(delta_result)

            # Return the results
            return {
                "command": command,
                "param_name": param_name,
                "values": delta_results,
            }

        if command == "tag":
            # Define tags and labels for components

            # Evaluate delta brackets for tag rules
            delta_results: list[dict[str, Any]] = []

            for delta_node in node.get("delta_brackets", []):
                delta_result = self._evaluate_node(delta_node, local_context)
                if delta_result is not None:
                    delta_results.append(delta_result)

            # Return the results
            return {
                "command": command,
                "tag_name": node.get("bridge_target") or node.get("assign_value"),
                "rules": delta_results,
            }

        if command == "pluck":
            # Extract specific elements

            # Evaluate delta brackets for pluck rules
            delta_results: list[dict[str, Any]] = []

            for delta_node in node.get("delta_brackets", []):
                delta_result = self._evaluate_node(delta_node, local_context)
                if delta_result is not None:
                    delta_results.append(delta_result)

            # Return the results
            return {
                "command": command,
                "target": node.get("bridge_target") or node.get("assign_value"),
                "rules": delta_results,
            }

        # Add more commands as needed

        raise ValueError(f"Unknown gamma bracket command: {command}")

    def _evaluate_delta_bracket(
        self, node: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate a delta bracket node."""
        command = node.get("command")

        # Handle val command
        if command == "val":
            # Get the values
            values = node.get("values", [])

            # Return the results
            return {
                "command": command,
                "values": values,
            }

        raise ValueError(f"Unknown delta bracket command: {command}")

    def _evaluate_exec_param(
        self, node: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate an exec param node."""
        # Get the parameter name and value
        param_name = node.get("param_name")
        param_value = node.get("param_value")

        # Return the results
        return {
            "type": "exec_param",
            "param_name": param_name,
            "param_value": param_value,
        }
