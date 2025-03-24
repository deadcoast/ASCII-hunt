class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.component_types = {}
        self.generators = {}

    def register_plugin(self, plugin_id, plugin_instance):
        """Register a plugin with the system."""
        if plugin_id in self.plugins:
            raise ValueError(f"Plugin already registered: {plugin_id}")

        self.plugins[plugin_id] = plugin_instance

        # Register component types provided by this plugin
        for component_type in plugin_instance.get_component_types():
            if component_type in self.component_types:
                self.component_types[component_type].append(plugin_id)
            else:
                self.component_types[component_type] = [plugin_id]

        # Register generators provided by this plugin
        for generator_id, generator in plugin_instance.get_generators().items():
            self.generators[f"{plugin_id}.{generator_id}"] = generator

    def get_generator(self, generator_id):
        """Get a registered code generator."""
        if generator_id not in self.generators:
            raise ValueError(f"Unknown generator: {generator_id}")
        return self.generators[generator_id]

    def get_plugins_for_component(self, component_type):
        """Get plugins that support a specific component type."""
        return self.component_types.get(component_type, [])

    def load_plugin_from_file(self, plugin_path):
        """Dynamically load a plugin from a Python file."""
        module_name = os.path.basename(plugin_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "create_plugin"):
            raise ValueError(f"Invalid plugin module: {plugin_path}")

        plugin_instance = module.create_plugin()
        plugin_id = plugin_instance.get_id()

        self.register_plugin(plugin_id, plugin_instance)
        return plugin_id
