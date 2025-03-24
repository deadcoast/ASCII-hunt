class Plugin:
    def __init__(self, plugin_id, name, version):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self._component_types = []
        self._generators = {}

    def get_id(self):
        """Get the plugin identifier."""
        return self.plugin_id

    def get_info(self):
        """Get plugin information."""
        return {"id": self.plugin_id, "name": self.name, "version": self.version}

    def get_component_types(self):
        """Get component types supported by this plugin."""
        return self._component_types

    def get_generators(self):
        """Get code generators provided by this plugin."""
        return self._generators

    def register_component_type(self, component_type):
        """Register a supported component type."""
        if component_type not in self._component_types:
            self._component_types.append(component_type)

    def register_generator(self, generator_id, generator):
        """Register a code generator."""
        self._generators[generator_id] = generator
