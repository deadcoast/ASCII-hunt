from components.ascii_grid_widget import AsciiGridWidget
from components.connected_component_analysis import ConnectedComponentAnalyzer
from dsl.parser import DSLParser
from dsl.standard_library import DSLStandardLibrary
from src.components.component_analysis import ComponentAnalyzer
from src.components.component_model_representation import ComponentModel


class MappingRegistry:
    def __init__(self):
        """Initialize a MappingRegistry.

        The MappingRegistry manages a collection of mappings, allowing for
        registration, retrieval, and code generation using these mappings.

        Attributes:
        mappings (dict): A dictionary to store mappings identified by their names.
        """
        self.mappings = {
            "ascii_grid": AsciiGridWidget,
            "component_analysis": ComponentAnalyzer,
            "connected_component_analysis": ConnectedComponentAnalyzer,
            "component_model": ComponentModel,
            "ascii_grid_widget": AsciiGridWidget,
            "component_model_representation": ComponentModel,
        }

    def register_mapping(self, name, mapping_source):
        """Register a mapping with the registry."""
        parser = DSLParser()
        DSLStandardLibrary.register_standard_functions(parser)

        mapping = parser.parse(mapping_source)
        self.mappings[name] = mapping

    def get_mapping(self, name):
        """Get a registered mapping."""
        if name not in self.mappings:
            raise ValueError(f"Unknown mapping: {name}")
        return self.mappings[name]

    def generate_code(self, component, mapping_name):
        """Generate code for a component using a specific mapping."""
        mapping = self.get_mapping(mapping_name)
        return mapping.apply(component)
