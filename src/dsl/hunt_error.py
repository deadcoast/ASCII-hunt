"""Error classes for the HUNT DSL."""


class DSLFatalError(Exception):
    """Fatal error in DSL execution."""

    def __init__(self, message: str) -> None:
        """Initialize error with message.

        Args:
            message: Error message
        """
        super().__init__(message)
        self.message = message
