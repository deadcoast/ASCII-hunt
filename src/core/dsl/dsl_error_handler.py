"""DSL Error Handler Module."""

from src.core.dsl.dsl_error import DSLFatalError


class DslErrorHandler:
    """Dsl Error Handler."""

    def __init__(self) -> None:
        """Initializes an empty list of warnings."""
        self.warnings: list[str] = []

    def handle_scent(self, message: str) -> None:
        """Handle a non-critical failure.

        Appends the given message to the 'warnings' list.
        """
        self.warnings.append(message)

    def handle_snare(self, message: str) -> None:
        """Handle a critical failure.

        Raises a DSLFatalError with the given message.
        """
        raise DSLFatalError(message)

    def handle_trap(self, *, condition: bool, message: str) -> None:
        """Handle a trap condition.

        If the condition is False, raises a DSLFatalError with the given message.

        Args:
            condition (bool): The condition to check.
            message (str): The error message if the condition is False.
        """
        if not condition:
            self.handle_snare(message)

    def handle_alert(self, message: str) -> None:
        """Handle an alert.

        Raises a DSLFatalError with the given message.
        """
        raise DSLFatalError(message)

    def handle_warning(self, message: str) -> None:
        """Handle a warning.

        Appends the given message to the 'warnings' list.
        """
        self.warnings.append(message)
