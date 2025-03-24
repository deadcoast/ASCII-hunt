class HuntCommandDispatcher:
    def __init__(self):
        self.command_registry = {}

    def register_command(self, name, handler):
        """Register a command handler function."""
        self.command_registry[name] = handler

    def execute_command(self, command, params, context=None):
        """Execute a command with the given parameters."""
        if context is None:
            context = {}

        if command not in self.command_registry:
            raise ValueError(f"Unknown command: {command}")

        handler = self.command_registry[command]
        return handler(params, context)
