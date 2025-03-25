class ExtensionPoint:
    def __init__(self, name):
        self.name = name
        self.extensions = {}

    def register_extension(self, plugin_name, extension):
        """Register an extension."""
        self.extensions[plugin_name] = extension

    def get_extensions(self):
        """Get all registered extensions."""
        return self.extensions

    def get_extension(self, plugin_name):
        """Get an extension by plugin name."""
        return self.extensions.get(plugin_name)

    def invoke(self, method_name, *args, **kwargs):
        """Invoke a method on all extensions."""
        results = {}

        for plugin_name, extension in self.extensions.items():
            if hasattr(extension, method_name):
                method = getattr(extension, method_name)
                try:
                    results[plugin_name] = method(*args, **kwargs)
                except Exception as e:
                    # Log error and continue
                    print(
                        f"Error invoking {method_name} on extension {plugin_name}: {e!s}"
                    )

        return results
