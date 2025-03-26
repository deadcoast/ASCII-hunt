"""DSL Parser Module

This module provides a DSLParser class for parsing Domain-Specific Languages (DSLs).
The DSLParser class can be used to parse DSL source code into a mapping object
that represents the parsed DSL structure.

The DSLParser class supports the following features:
- Lexical analysis and parsing of DSL source code
- Conversion of DSL source code into an abstract syntax tree (AST)
- Building a mapping object from the AST
- Execution of expressions defined in the DSL

The DSLParser class can be extended to support custom DSLs by overriding the
_parse_source and _build_mapping methods.

The DSLParser class also supports the following functions:
- register_function: Register a function for use in expressions
- parse: Parse DSL source code and return a mapping object

The DSLParser class can be used to parse DSL source code into a mapping object
that represents the parsed DSL structure.

The DSLParser class can be extended to support custom DSLs by overriding the
_parse_source and _build_mapping methods.
"""

from collections.abc import Callable
from typing import Any

from src.mapping.component_mapping import ComponentMapping, Mapping


class HuntParser:
    def __init__(self) -> None:
        self.tokens: list[tuple[str, str | None, int]] = []
        self.ast: dict[str, Any] | None = None
        self.current_token_idx: int = 0
        self.functions: dict[str, Callable[..., Any]] = {}

    def register_function(self, name: str, func: Callable[..., Any]) -> None:
        """Register a function that can be used in expressions.

        Args:
            name: Name of the function
            func: Function to register
        """

    def parse(self, hunt_code: str) -> dict[str, Any] | None:
        """Parse HUNT DSL code into an abstract syntax tree."""
        # Tokenization
        self.tokens = self._tokenize(hunt_code)
        self.current_token_idx = 0

        # Parse the top-level structure
        self.ast = self._parse_alpha_bracket()

        return self.ast

    def interpret(self, hunt_code: str) -> Any:
        """Interpret HUNT DSL code.

        Args:
            hunt_code: HUNT DSL code to interpret

        Returns:
            Any: Result of interpreting the code
        """
        ast = self.parse(hunt_code)
        if ast is None:
            return None
        return self._evaluate_ast(ast)

    def _evaluate_ast(self, ast: dict[str, Any]) -> Any:
        """Evaluate an AST node.

        Args:
            ast: AST node to evaluate

        Returns:
            Any: Result of evaluating the node
        """
        # TODO: Implement AST evaluation
        return None

    def _tokenize(self, hunt_code: str) -> list[tuple[str, str | None, int]]:
        """Convert HUNT code into tokens."""
        tokens: list[tuple[str, str | None, int]] = []
        lines = hunt_code.split("\n")

        # Track indentation levels
        current_indent = 0

        for line_num, line in enumerate(lines):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Calculate indentation
            indent = len(line) - len(line.lstrip())

            # Handle indentation changes
            if indent > current_indent:
                # Add INDENT tokens
                for _ in range(
                    (indent - current_indent) // 4
                ):  # Assuming 4 spaces per indent
                    tokens.append(("INDENT", None, line_num))
            elif indent < current_indent:
                # Add DEDENT tokens
                for _ in range((current_indent - indent) // 4):
                    tokens.append(("DEDENT", None, line_num))

            current_indent = indent

            # Tokenize the line content
            line_content = line.strip()
            tokens.extend(self._tokenize_line(line_content, line_num))

        # Add final DEDENT tokens if needed
        for _ in range(current_indent // 4):
            tokens.append(("DEDENT", None, len(lines)))

        # Add EOF token
        tokens.append(("EOF", None, len(lines)))

        return tokens

    def _tokenize_line(
        self, line: str, line_num: int
    ) -> list[tuple[str, str | None, int]]:
        """Tokenize a single line of HUNT code."""
        tokens: list[tuple[str, str | None, int]] = []
        i = 0

        while i < len(line):
            char = line[i]

            # Handle HUNT-specific tokens
            if char == "<":
                tokens.append(("ALPHA_OPEN", "<", line_num))
                i += 1
            elif char == ">":
                tokens.append(("ALPHA_CLOSE", ">", line_num))
                i += 1
            elif char == "[":
                tokens.append(("BETA_OPEN", "[", line_num))
                i += 1
            elif char == "]":
                tokens.append(("BETA_CLOSE", "]", line_num))
                i += 1
            elif char == "{":
                tokens.append(("GAMMA_OPEN", "{", line_num))
                i += 1
            elif char == "}":
                tokens.append(("GAMMA_CLOSE", "}", line_num))
                i += 1
            elif char == "(":
                tokens.append(("DELTA_OPEN", "(", line_num))
                i += 1
            elif char == ")":
                tokens.append(("DELTA_CLOSE", ")", line_num))
                i += 1
            elif char == "=":
                tokens.append(("ASSIGN", "=", line_num))
                i += 1
            elif char == ":":
                tokens.append(("BRIDGE", ":", line_num))
                i += 1
            elif char == ",":
                tokens.append(("COMMA", ",", line_num))
                i += 1
            elif char == "@" and i + 1 < len(line) and line[i + 1] == "@":
                tokens.append(("CHAIN", "@@", line_num))
                i += 2
            elif char.isalpha() or char == "_":
                # Handle identifiers
                identifier = ""
                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    identifier += line[i]
                    i += 1

                # Check for keywords
                if identifier in [
                    "hunt",
                    "INIT",
                    "param",
                    "val",
                    "EXEC",
                    "Track",
                    "GATHER",
                    "GET",
                    "HARVEST",
                    "HARV",
                    "RACK",
                    "COOK",
                    "tag",
                    "pluck",
                    "trap",
                    "skin",
                    "log",
                    "boil",
                    "scent",
                    "snare",
                    "true",
                    "false",
                    "req",
                    "prohib",
                ]:
                    tokens.append(("KEYWORD", identifier, line_num))
                else:
                    tokens.append(("IDENTIFIER", identifier, line_num))
            elif char.isspace():
                # Skip whitespace
                i += 1
            elif char == '"' or char == "'":
                # Handle string literals
                start_char = char
                string_value = ""
                i += 1  # Skip the opening quote

                while i < len(line) and line[i] != start_char:
                    string_value += line[i]
                    i += 1

                if i < len(line):  # Skip the closing quote
                    i += 1

                tokens.append(("STRING", string_value, line_num))
            else:
                # Handle other characters
                tokens.append(("CHAR", char, line_num))
                i += 1

        return tokens

    def _parse_alpha_bracket(self) -> dict[str, Any] | None:
        """Parse a top-level alpha bracket structure."""
        if self._match("ALPHA_OPEN"):
            self._consume("ALPHA_OPEN")

            # Parse the command or identifier
            command = self._parse_identifier()

            # Check for bridge
            has_bridge = False
            bridge_target = None

            if self._match("BRIDGE"):
                self._consume("BRIDGE")
                has_bridge = True

                if self._match("IDENTIFIER"):
                    bridge_target = self._parse_identifier()

            # Parse nested beta brackets
            beta_brackets: list[dict[str, Any]] = []

            while self._match("BETA_OPEN"):
                beta_bracket = self._parse_beta_bracket()
                if beta_bracket is not None:
                    beta_brackets.append(beta_bracket)

            # Parse the closing alpha bracket and EXEC if present
            exec_params = None

            if self._match("ALPHA_CLOSE"):
                self._consume("ALPHA_CLOSE")

                if self._match("KEYWORD") and self._peek_value() == "EXEC":
                    self._consume("KEYWORD")  # Consume EXEC
                    exec_params = self._parse_exec_params()

            return {
                "type": "alpha_bracket",
                "command": command,
                "has_bridge": has_bridge,
                "bridge_target": bridge_target,
                "beta_brackets": beta_brackets,
                "exec_params": exec_params,
            }

        return None

    def _parse_beta_bracket(self) -> dict[str, Any] | None:
        """Parse a beta bracket structure."""
        if self._match("BETA_OPEN"):
            self._consume("BETA_OPEN")

            # Parse the command or identifier
            command = self._parse_identifier()

            # Check for assignment
            has_assign = False
            assign_value = None

            if self._match("ASSIGN"):
                self._consume("ASSIGN")
                has_assign = True
                assign_value = self._parse_value()

            # Parse nested gamma brackets
            gamma_brackets: list[dict[str, Any]] = []

            while self._match("GAMMA_OPEN"):
                gamma_bracket = self._parse_gamma_bracket()
                if gamma_bracket is not None:
                    gamma_brackets.append(gamma_bracket)

            # Parse the closing beta bracket
            if self._match("BETA_CLOSE"):
                self._consume("BETA_CLOSE")

                return {
                    "type": "beta_bracket",
                    "command": command,
                    "has_assign": has_assign,
                    "assign_value": assign_value,
                    "gamma_brackets": gamma_brackets,
                }

        return None

    def _parse_gamma_bracket(self) -> dict[str, Any] | None:
        """Parse a gamma bracket structure."""
        if self._match("GAMMA_OPEN"):
            self._consume("GAMMA_OPEN")

            # Parse the command or identifier
            command = self._parse_identifier()

            # Check for bridge or assignment
            has_bridge = False
            bridge_target = None
            has_assign = False
            assign_value = None

            if self._match("BRIDGE"):
                self._consume("BRIDGE")
                has_bridge = True
                bridge_target = self._parse_identifier()
            elif self._match("ASSIGN"):
                self._consume("ASSIGN")
                has_assign = True
                assign_value = self._parse_value()

            # Parse nested delta brackets
            delta_brackets: list[dict[str, Any]] = []

            while self._match("DELTA_OPEN"):
                delta_bracket = self._parse_delta_bracket()
                if delta_bracket is not None:
                    delta_brackets.append(delta_bracket)

            # Parse the closing gamma bracket
            if self._match("GAMMA_CLOSE"):
                self._consume("GAMMA_CLOSE")

                return {
                    "type": "gamma_bracket",
                    "command": command,
                    "has_bridge": has_bridge,
                    "bridge_target": bridge_target,
                    "has_assign": has_assign,
                    "assign_value": assign_value,
                    "delta_brackets": delta_brackets,
                }

        return None

    def _parse_delta_bracket(self) -> dict[str, Any] | None:
        """Parse a delta bracket structure."""
        if self._match("DELTA_OPEN"):
            self._consume("DELTA_OPEN")

            # Parse the command or identifier
            command = self._parse_identifier()

            # Parse values
            values: list[Any] = []

            while not self._match("DELTA_CLOSE"):
                if self._match("COMMA"):
                    self._consume("COMMA")
                    continue

                value = self._parse_value()
                if value is not None:
                    values.append(value)

            # Parse the closing delta bracket
            if self._match("DELTA_CLOSE"):
                self._consume("DELTA_CLOSE")

                return {
                    "type": "delta_bracket",
                    "command": command,
                    "values": values,
                }

        return None

    def _parse_identifier(self) -> str | None:
        """Parse an identifier."""
        if self._match("IDENTIFIER") or self._match("KEYWORD"):
            token = self._current_token()
            self._consume(token[0])
            return token[1]

        return None

    def _parse_value(self) -> Any | None:
        """Parse a value."""
        if self._match("STRING"):
            token = self._current_token()
            self._consume("STRING")
            return token[1]
        elif self._match("IDENTIFIER"):
            token = self._current_token()
            self._consume("IDENTIFIER")
            return token[1]
        elif self._match("KEYWORD"):
            token = self._current_token()
            self._consume("KEYWORD")
            return token[1]

        return None

    def _parse_exec_params(self) -> list[dict[str, Any]]:
        """Parse EXEC parameters."""
        params: list[dict[str, Any]] = []

        while not self._match("EOF"):
            param = self._parse_exec_param()
            if param is not None:
                params.append(param)

        return params

    def _parse_exec_param(self) -> dict[str, Any] | None:
        """Parse an EXEC parameter."""
        if self._match("IDENTIFIER"):
            param_name = self._parse_identifier()
            param_value = None

            if self._match("ASSIGN"):
                self._consume("ASSIGN")
                param_value = self._parse_value()

            return {
                "type": "exec_param",
                "param_name": param_name,
                "param_value": param_value,
            }

        return None

    def _match(self, token_type: str) -> bool:
        """Check if current token matches the expected type."""
        if self.current_token_idx >= len(self.tokens):
            return False
        return self.tokens[self.current_token_idx][0] == token_type

    def _peek_value(self) -> str | None:
        """Get the value of the current token without consuming it."""
        if self.current_token_idx >= len(self.tokens):
            return None
        return self.tokens[self.current_token_idx][1]

    def _current_token(self) -> tuple[str, str | None, int]:
        """Get the current token."""
        if self.current_token_idx >= len(self.tokens):
            return ("EOF", None, -1)
        return self.tokens[self.current_token_idx]

    def _consume(self, token_type: str) -> None:
        """Consume a token of the expected type."""
        if not self._match(token_type):
            raise ValueError(
                f"Expected token type {token_type}, "
                f"got {self.tokens[self.current_token_idx][0]}"
            )
        self.current_token_idx += 1


class DSLParseCleaner:
    def __init__(self):
        """Initialize a DSLParser.

        The DSLParser has the following properties:
        - self.functions: a dictionary mapping function names to functions
          for use in expressions
        """
        self.functions = {}

    def register_function(self, name, func):
        """Register a function for use in expressions.

        :param name: the name of the function
        :param func: the function to register
        """
        self.functions[name] = func

    def parse(self, source):
        """Parse DSL source and return a mapping object.

        This method performs lexical analysis and parsing on the given DSL source
        to convert it into an abstract syntax tree (AST). The AST is then used to
        build and return a mapping object that represents the parsed DSL structure.

        :param source: The DSL source code to be parsed.
        :return: A mapping object built from the parsed abstract syntax tree.
        """
        # Lexical analysis and parsing implementation

        # This would convert the DSL source to an abstract syntax tree

        ast = self._parse_source(source)

        # Build a mapping object from the AST
        return self._build_mapping(ast)

    def _parse_source(self, source):
        # Implement parsing logic
        # This could use a library like PLY, lark, or a recursive descent parser
        """Perform lexical analysis and parsing on the given DSL source to
        convert it into an abstract syntax tree (AST).

        This method should be implemented using a library like PLY, lark, or
        a recursive descent parser.

        :param source: The DSL source code to be parsed.
        :return: An abstract syntax tree (AST) built from the parsed DSL source.
        """

    def _build_mapping(self, ast):
        """Build a mapping object from an AST.

        This method takes an abstract syntax tree (AST) produced by the
        parser and converts it into a mapping object. The mapping object
        represents the parsed DSL structure.

        :param ast: The abstract syntax tree to be converted into a mapping object.
        :return: A mapping object built from the given abstract syntax tree.
        """
        mappings = {}

        for component_mapping in ast:
            component_type = component_mapping["type"]
            property_mappings = {}
            template = None
            children_mappings = {}

            for item in component_mapping["mappings"]:
                if item["kind"] == "property":
                    property_mappings[item["name"]] = self._build_expression(
                        item["expression"]
                    )
                elif item["kind"] == "template":
                    template = item["code"]
                elif item["kind"] == "children":
                    for child_mapping in item["mappings"]:
                        children_mappings[child_mapping["type"]] = (
                            self._build_expression(child_mapping["expression"])
                        )

            mappings[component_type] = ComponentMapping(
                component_type, property_mappings, template, children_mappings
            )

        return Mapping(mappings)

    def _build_expression(self, expr_ast):
        """Build a function from an expression AST.

        This method takes an expression AST produced by the parser and
        converts it into a function. The function takes a context object
        as an argument and evaluates the expression based on the context.

        :param expr_ast: The expression AST to be converted into a function.
        :return: A function that takes a context object as an argument and
                 evaluates the expression based on the context.
        """
        if expr_ast["kind"] == "literal":
            return lambda ctx: expr_ast["value"]

        if expr_ast["kind"] == "reference":
            path = expr_ast["path"]

            if path[0] == "parent":
                return lambda ctx: ctx.get("parent", {}).get(path[1], None)
            if path[0] == "index":
                return lambda ctx: ctx.get("index", 0)
            if path[0] == "type":
                return lambda ctx: ctx.get("component", {}).get("type", None)
            return (
                lambda ctx: ctx.get("component", {})
                .get("properties", {})
                .get(path[0], None)
            )

        if expr_ast["kind"] == "function_call":
            func_name = expr_ast["name"]
            arg_exprs = [self._build_expression(arg) for arg in expr_ast["arguments"]]

            if func_name not in self.functions:
                raise ValueError(f"Unknown function: {func_name}")

            func = self.functions[func_name]

            return lambda ctx: func(*[arg_expr(ctx) for arg_expr in arg_exprs])

        if expr_ast["kind"] == "conditional":
            condition = self._build_expression(expr_ast["condition"])
            then_expr = self._build_expression(expr_ast["then"])
            else_expr = self._build_expression(expr_ast["else"])

            return lambda ctx: then_expr(ctx) if condition(ctx) else else_expr(ctx)

        raise ValueError(f"Unknown expression type: {expr_ast['kind']}")
