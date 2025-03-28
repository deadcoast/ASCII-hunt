class TransformationPipeline:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.transforms = []

    def add_transform(self, transform_id, plugin_id, params=None):
        """Add a transformation to the pipeline."""
        self.transforms.append(
            {
                "transform_id": transform_id,
                "plugin_id": plugin_id,
                "params": params or {},
            }
        )

    def process(self, component):
        """Process a component through the transformation pipeline."""
        result = component

        for transform_config in self.transforms:
            plugin_id = transform_config["plugin_id"]
            transform_id = transform_config["transform_id"]
            params = transform_config["params"]

            plugins = self.plugin_manager.plugins
            if plugin_id not in plugins:
                raise ValueError(f"Unknown plugin: {plugin_id}")

            plugin = plugins[plugin_id]
            extensions = plugin.get_extensions("transforms")

            if transform_id not in extensions:
                raise ValueError(f"Unknown transform: {transform_id}")

            transform = extensions[transform_id]
            result = transform.transform(result, **params)

        return result
