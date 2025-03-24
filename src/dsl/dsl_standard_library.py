class DSLStandardLibrary:
    @staticmethod
    def register_standard_functions(parser):
        """Register standard functions with a DSL parser."""
        # String functions
        parser.register_function(
            "concat", lambda *args: "".join(str(arg) for arg in args)
        )
        parser.register_function("format", lambda fmt, *args: fmt.format(*args))
        parser.register_function("uppercase", lambda s: str(s).upper())
        parser.register_function("lowercase", lambda s: str(s).lower())
        parser.register_function("capitalize", lambda s: str(s).capitalize())

        # Math functions
        parser.register_function("add", lambda a, b: a + b)
        parser.register_function("subtract", lambda a, b: a - b)
        parser.register_function("multiply", lambda a, b: a * b)
        parser.register_function("divide", lambda a, b: a / b if b != 0 else 0)
        parser.register_function("max", max)
        parser.register_function("min", min)
        parser.register_function("round", round)

        # Collection functions
        parser.register_function("length", len)
        parser.register_function("join", lambda sep, items: sep.join(items))
        parser.register_function(
            "map", lambda func, items: [func(item) for item in items]
        )
        parser.register_function(
            "filter", lambda func, items: [item for item in items if func(item)]
        )

        # Type conversion
        parser.register_function("str", str)
        parser.register_function(
            "int", lambda v: int(float(v)) if isinstance(v, (int, float, str)) else 0
        )
        parser.register_function(
            "float", lambda v: float(v) if isinstance(v, (int, float, str)) else 0.0
        )
        parser.register_function("bool", lambda v: bool(v))

        # UI-specific functions
        parser.register_function(
            "compute_width", lambda text, char_width=8: len(str(text)) * char_width
        )
        parser.register_function(
            "compute_height", lambda lines=1, line_height=20: lines * line_height
        )
        parser.register_function(
            "css_class", lambda enabled, cls: cls if enabled else ""
        )
