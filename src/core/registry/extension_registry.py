class ExtensionRegistry:
    def __init__(self):
        self.extensions = {}

    def register_extension(self, extension_point, plugin_id, extension):
        """Register an extension for a specific extension point."""
        if extension_point not in self.extensions:
            self.extensions[extension_point] = {}

        self.extensions[extension_point][plugin_id] = extension

    def get_extensions(self, extension_point):
        """Get all extensions for a specific extension point."""
        return self.extensions.get(extension_point, {})

    def get_extension(self, extension_point, plugin_id):
        """Get a specific extension."""
        extensions = self.get_extensions(extension_point)
        return extensions.get(plugin_id)
