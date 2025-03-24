class HuntErrorHandler:
    def __init__(self):
        self.warnings = []

    def handle_scent(self, message, context):
        """Handle a soft warning."""
        self.warnings.append(message)

    def handle_snare(self, message, context):
        """Handle a critical failure."""
        raise HuntCriticalError(message)

    def handle_trap(self, condition, message, context):
        """Handle a constraint check."""
        if not condition:
            self.handle_snare(message, context)
