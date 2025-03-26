"""Plugin class for managing plugins.

This class provides a base class for creating plugins that can be used to extend the
functionality of the application.

The Plugin class has the following properties:
- self.plugin_id: a string identifying the plugin
- self.name: a string representing the name of the plugin
- self.version: a string representing the version of the plugin
- self._component_types: a list of component types supported by the plugin
- self._generators: a dictionary mapping component types to their code generators

The Plugin class has the following methods:
- get_id(): a method that returns the plugin identifier
- get_info(): a method that returns plugin information
- get_component_types(): a method that returns a list of component types supported by the plugin
- get_generators(): a method that returns a dictionary mapping component types to their code generators
- register_component_type(): a method that registers a component type for the plugin
- register_generator(): a method that registers a code generator for a specific component type
"""


class Plugin:
    def __init__(self, plugin_id, name, version):
        """Initialize a Plugin.

        The Plugin has the following properties:
        - self.plugin_id: a string identifying the plugin
        - self.name: a string representing the name of the plugin
        - self.version: a string representing the version of the plugin
        - self._component_types: a list of component types supported by the plugin
        - self._generators: a dictionary mapping component types to their code generators
        """
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self._component_types = []
        self._generators = {}

    def get_id(self):
        """Get the plugin identifier.

        Returns:
            str: The unique identifier for the plugin.
        """
        return self.plugin_id

    def get_info(self):
        """Get plugin information.

        Returns:
            dict: A dictionary with the following properties:
                - id: The unique identifier for the plugin.
                - name: The name of the plugin.
                - version: The version of the plugin.
        """
        return {"id": self.plugin_id, "name": self.name, "version": self.version}

    def get_component_types(self):
        """Get a list of component types supported by the plugin.

        Returns:
            list[str]: A list of strings, each representing a component type.
        """
        return self._component_types

    def get_generators(self):
        """Get the code generators for the plugin.

        Returns:
            dict[str, BaseGenerator]: A dictionary mapping generator identifiers to their
            corresponding code generators.
        """
        return self._generators

    def register_component_type(self, component_type):
        """Register a component type for the plugin.

        :param component_type: A string representing the component type to be registered.
        """
        if component_type not in self._component_types:
            self._component_types.append(component_type)

    def register_generator(self, generator_id, generator):
        """Register a code generator for a specific component type.

        :param generator_id: A string identifying the generator.
        :type generator_id: str
        :param generator: A code generator instance.
        :type generator: BaseGenerator
        """
        self._generators[generator_id] = generator
