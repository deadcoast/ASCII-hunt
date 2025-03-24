class DSLParser:
    def __init__(self):
        self.functions = {}

    def register_function(self, name, func):
        """Register a function for use in expressions."""
        self.functions[name] = func

    def parse(self, source):
        """Parse DSL source and return a mapping object."""
        # Lexical analysis and parsing implementation
        # This would convert the DSL source to an abstract syntax tree
        ast = self._parse_source(source)

        # Build a mapping object from the AST
        return self._build_mapping(ast)

    def _parse_source(self, source):
        """Parse DSL source into an abstract syntax tree."""
        # Implement parsing logic
        # This could use a library like PLY, lark, or a recursive descent parser
        pass

    def _build_mapping(self, ast):
        """Build a mapping object from an AST."""
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
        """Build an executable expression from an AST."""
        if expr_ast["kind"] == "literal":
            return lambda ctx: expr_ast["value"]

        elif expr_ast["kind"] == "reference":
            path = expr_ast["path"]

            if path[0] == "parent":
                return lambda ctx: ctx.get("parent", {}).get(path[1], None)
            elif path[0] == "index":
                return lambda ctx: ctx.get("index", 0)
            elif path[0] == "type":
                return lambda ctx: ctx.get("component", {}).get("type", None)
            else:
                return (
                    lambda ctx: ctx.get("component", {})
                    .get("properties", {})
                    .get(path[0], None)
                )

        elif expr_ast["kind"] == "function_call":
            func_name = expr_ast["name"]
            arg_exprs = [self._build_expression(arg) for arg in expr_ast["arguments"]]

            if func_name not in self.functions:
                raise ValueError(f"Unknown function: {func_name}")

            func = self.functions[func_name]

            return lambda ctx: func(*[arg_expr(ctx) for arg_expr in arg_exprs])

        elif expr_ast["kind"] == "conditional":
            condition = self._build_expression(expr_ast["condition"])
            then_expr = self._build_expression(expr_ast["then"])
            else_expr = self._build_expression(expr_ast["else"])

            return lambda ctx: then_expr(ctx) if condition(ctx) else else_expr(ctx)

        raise ValueError(f"Unknown expression type: {expr_ast['kind']}")
