class HuntParser:
    def __init__(self):
        self.tokens = []
        self.ast = None
        self.current_token_idx = 0

    def parse(self, hunt_code):
        """Parse HUNT DSL code into an abstract syntax tree."""
        # Tokenization
        self.tokens = self._tokenize(hunt_code)
        self.current_token_idx = 0

        # Parse the top-level structure
        self.ast = self._parse_alpha_bracket()

        return self.ast

    def _tokenize(self, hunt_code):
        """Convert HUNT code into tokens."""
        tokens = []
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

    def _tokenize_line(self, line, line_num):
        """Tokenize a single line of HUNT code."""
        tokens = []
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

    def _parse_alpha_bracket(self):
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
            beta_brackets = []

            while self._match("BETA_OPEN"):
                beta_bracket = self._parse_beta_bracket()
                beta_brackets.append(beta_bracket)

            # Parse the closing alpha bracket and EXEC if present
            exec_params = None

            if self._match("ALPHA_CLOSE"):
                self._consume("ALPHA_CLOSE")

                if self._match("KEYWORD") and self._peek_value() == "EXEC":
                    self._consume("KEYWORD")  # Consume EXEC

                    # Check for EXEC parameters
                    if self._match("BRIDGE"):
                        self._consume("BRIDGE")
                        exec_params = self._parse_exec_params()

                    # Check for closing alpha bracket for EXEC
                    if self._match("ALPHA_CLOSE"):
                        self._consume("ALPHA_CLOSE")

            # Construct AST node
            return {
                "type": "alpha_bracket",
                "command": command,
                "has_bridge": has_bridge,
                "bridge_target": bridge_target,
                "beta_brackets": beta_brackets,
                "exec_params": exec_params,
            }

        raise SyntaxError("Expected alpha bracket opening '<'")

    def _parse_beta_bracket(self):
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

                if self._match("IDENTIFIER"):
                    assign_value = self._parse_identifier()

            # Parse nested gamma brackets
            gamma_brackets = []

            while self._match("GAMMA_OPEN"):
                gamma_bracket = self._parse_gamma_bracket()
                gamma_brackets.append(gamma_bracket)

            # Parse the closing beta bracket
            if self._match("BETA_CLOSE"):
                self._consume("BETA_CLOSE")

            # Construct AST node
            return {
                "type": "beta_bracket",
                "command": command,
                "has_assign": has_assign,
                "assign_value": assign_value,
                "gamma_brackets": gamma_brackets,
            }

        raise SyntaxError("Expected beta bracket opening '['")

    def _parse_gamma_bracket(self):
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

                if self._match("IDENTIFIER") or self._match("KEYWORD"):
                    bridge_target = self._parse_identifier()
            elif self._match("ASSIGN"):
                self._consume("ASSIGN")
                has_assign = True

                if self._match("IDENTIFIER") or self._match("KEYWORD"):
                    assign_value = self._parse_identifier()

            # Parse nested delta brackets
            delta_brackets = []

            while self._match("DELTA_OPEN"):
                delta_bracket = self._parse_delta_bracket()
                delta_brackets.append(delta_bracket)

            # Parse the closing gamma bracket
            if self._match("GAMMA_CLOSE"):
                self._consume("GAMMA_CLOSE")

            # Construct AST node
            return {
                "type": "gamma_bracket",
                "command": command,
                "has_bridge": has_bridge,
                "bridge_target": bridge_target,
                "has_assign": has_assign,
                "assign_value": assign_value,
                "delta_brackets": delta_brackets,
            }

        raise SyntaxError("Expected gamma bracket opening '{'")

    def _parse_delta_bracket(self):
        """Parse a delta bracket structure."""
        if self._match("DELTA_OPEN"):
            self._consume("DELTA_OPEN")

            # Parse values
            values = []

            # Parse first value if present
            if not self._match("DELTA_CLOSE"):
                values.append(self._parse_value())

                # Parse additional values separated by commas
                while self._match("COMMA"):
                    self._consume("COMMA")

                    if not self._match("DELTA_CLOSE"):
                        values.append(self._parse_value())

            # Parse the closing delta bracket
            if self._match("DELTA_CLOSE"):
                self._consume("DELTA_CLOSE")

            # Construct AST node
            return {"type": "delta_bracket", "values": values}

        raise SyntaxError("Expected delta bracket opening '('")

    def _parse_identifier(self):
        """Parse an identifier or keyword."""
        if self._match("IDENTIFIER"):
            identifier = self._current_token()
            self._consume("IDENTIFIER")
            return identifier
        elif self._match("KEYWORD"):
            keyword = self._current_token()
            self._consume("KEYWORD")
            return keyword

        raise SyntaxError("Expected identifier or keyword")

    def _parse_value(self):
        """Parse a value (identifier, string, etc.)."""
        if self._match("IDENTIFIER"):
            value = self._current_token()
            self._consume("IDENTIFIER")
            return value
        elif self._match("STRING"):
            value = self._current_token()
            self._consume("STRING")
            return value
        elif self._match("KEYWORD"):
            value = self._current_token()
            self._consume("KEYWORD")
            return value

        raise SyntaxError("Expected value")

    def _parse_exec_params(self):
        """Parse EXEC parameters."""
        params = []

        # Parse first parameter
        param = self._parse_exec_param()
        params.append(param)

        # Parse additional parameters separated by chains
        while self._match("CHAIN"):
            self._consume("CHAIN")
            param = self._parse_exec_param()
            params.append(param)

        return params

    def _parse_exec_param(self):
        """Parse a single EXEC parameter."""
        if self._match("IDENTIFIER") or self._match("KEYWORD"):
            param = self._parse_identifier()

            # Check for nested parameters
            if self._match("GAMMA_OPEN"):
                nested_param = self._parse_gamma_bracket()
                return {"type": "exec_param", "param": param, "nested": nested_param}

            return {"type": "exec_param", "param": param, "nested": None}

        elif self._match("GAMMA_OPEN"):
            nested_param = self._parse_gamma_bracket()
            return {"type": "exec_param", "param": None, "nested": nested_param}

        raise SyntaxError("Expected EXEC parameter")

    def _match(self, token_type):
        """Check if the current token matches the expected type."""
        if self.current_token_idx >= len(self.tokens):
            return False

        return self.tokens[self.current_token_idx][0] == token_type

    def _peek_value(self):
        """Peek at the value of the current token."""
        if self.current_token_idx >= len(self.tokens):
            return None

        return self.tokens[self.current_token_idx][1]

    def _current_token(self):
        """Get the current token."""
        if self.current_token_idx >= len(self.tokens):
            return None

        return self.tokens[self.current_token_idx][1]

    def _consume(self, token_type):
        """Consume a token of the expected type."""
        if not self._match(token_type):
            token = (
                self.tokens[self.current_token_idx]
                if self.current_token_idx < len(self.tokens)
                else ("EOF", None)
            )
            raise SyntaxError(
                f"Expected {token_type}, got {token[0]} at line {token[2]}"
            )

        token = self.tokens[self.current_token_idx]
        self.current_token_idx += 1
        return token[1]
