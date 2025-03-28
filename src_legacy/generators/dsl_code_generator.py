from collections.abc import Callable
from typing import Any

from src.dsl.dsl_standard_library import DSLStandardLibrary
from src.dsl.hunt_parser import HuntParser
from src.mapping.component_mapping import Mapping


class DSLCodeGenerator:
    def __init__(self, mapping_source: str) -> None:
        """Initialize a DSLCodeGenerator.

        The DSLCodeGenerator has the following properties:
        - self.parser: the DSL parser to use for parsing mapping expressions
        - self.mapping: the parsed mapping object to use for generating code

        Args:
            mapping_source: Source code for the mapping
        """
        self.parser = HuntParser()
        DSLStandardLibrary.register_standard_functions(self.parser)

        # Parse the mapping source
        self.mapping = self._parse_mapping(mapping_source)

    def _parse_mapping(self, mapping_source: str) -> Mapping:
        """Parse a mapping source into a Mapping object.

        Args:
            mapping_source: The mapping source code

        Returns:
            A Mapping object representing the parsed mapping
        """
        # Use the parser to create an AST
        ast = self.parser.parse(mapping_source)

        # Convert the AST to a Mapping object
        # This is a simplified implementation
        component_mappings = {}
        # Build component mappings based on AST
        # For demonstration, just create an empty mapping
        return Mapping(component_mappings)

    def generate(self, component: Any) -> str:
        """Generate code for a component using the DSL mappings.

        Args:
            component: The component to generate code for

        Returns:
            The generated code as a string
        """
        return self.mapping.apply(component)

    def register_custom_function(self, name: str, func: Callable) -> None:
        """Register a custom function for use in mapping expressions.

        Args:
            name: The name to register the function under
            func: The function to register
        """
        self.parser.register_function(name, func)
