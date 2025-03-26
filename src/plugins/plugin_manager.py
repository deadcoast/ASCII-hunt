import os
from importlib import util
from importlib.machinery import ModuleSpec


class PluginManager:
    def __init__(self):
        """Initialize the PluginManager.

        The PluginManager is responsible for managing plugins, component types, and code generators. It maintains a collection of registered plugins, a mapping of component types to plugins that support them, and a dictionary of code generators provided by the plugins.

        :ivar plugins: A dictionary mapping plugin IDs to plugin instances.
        :ivar component_types: A dictionary mapping component types to lists of plugin IDs that support them.
        :ivar generators: A dictionary mapping generator IDs to generator instances.
        """
        self.plugins = {}
        self.component_types = {}
        self.generators = {}

    def register_plugin(self, plugin_id, plugin_instance):
        """Register a plugin with the manager.

        :param plugin_id: A unique identifier for the plugin
        :type plugin_id: str
        :param plugin_instance: An instance of the plugin class
        :type plugin_instance: Plugin

        :raises ValueError: if the plugin is already registered
        """
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
        """Retrieve a code generator by its identifier.

        :param generator_id: The identifier of the generator to retrieve.
        :type generator_id: str

        :return: The code generator instance associated with the given ID.
        :rtype: object

        :raises ValueError: If the generator ID is not registered.
        """
        if generator_id not in self.generators:
            raise ValueError(f"Unknown generator: {generator_id}")
        return self.generators[generator_id]

    def get_plugins_for_component(self, component_type):
        """Retrieve the list of plugins that support the given component type.

        :param component_type: The component type to retrieve plugins for.
        :type component_type: str

        :return: A list of plugin IDs that support the given component type.
        :rtype: list[str]

        :raises ValueError: If the component type is not registered.
        """
        return self.component_types.get(component_type, [])

    def load_plugin_from_file(self, plugin_path: str) -> str:
        """Load a plugin from a Python file.

        The plugin module must contain a function called `create_plugin` that
        returns an instance of the plugin class.

        Args:
            plugin_path: The path to the Python file containing the plugin module.

        Returns:
            The plugin ID of the loaded plugin.

        Raises:
            ValueError: If the plugin module is invalid or cannot be loaded.
        """
        module_name = os.path.basename(plugin_path).replace(".py", "")
        spec: ModuleSpec | None = util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not load plugin module: {plugin_path}")

        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "create_plugin"):
            raise ValueError(f"Invalid plugin module: {plugin_path}")

        plugin_instance = module.create_plugin()
        plugin_id = plugin_instance.get_id()

        self.register_plugin(plugin_id, plugin_instance)
        return plugin_id
