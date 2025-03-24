from .dsl_parser import DSLParser
from .dsl_standard_library import DSLStandardLibrary


class DSLCodeGenerator:
    def __init__(self, mapping_source):
        """
        Initialize a DSLCodeGenerator.

        The DSLCodeGenerator has the following properties:
        - self.parser: the DSL parser to use for parsing mapping expressions
        - self.mapping: the parsed mapping object to use for generating code
        """
        self.parser = DSLParser()
        DSLStandardLibrary.register_standard_functions(self.parser)

        # Parse the mapping source
        self.mapping = self.parser.parse(mapping_source)

    def generate(self, component):
        """Generate code for a component using the DSL mappings."""
        return self.mapping.apply(component)

    def register_custom_function(self, name, func):
        """Register a custom function for use in mapping expressions."""
        self.parser.register_function(name, func)
