from typing import Any

from .hunt_error import DSLFatalError


class HuntErrorHandler:
    def __init__(self) -> None:
        """Initializes an empty list of warnings."""
        self.warnings: list[str] = []

    def handle_scent(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Handle a non-critical failure.

        Appends the given message to the 'warnings' list.
        """
        self.warnings.append(message)

    def handle_snare(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Handle a critical failure.

        Raises a DSLFatalError with the given message.
        """
        raise DSLFatalError(message)

    def handle_trap(
        self, condition: bool, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Handle a trap condition.

        If the condition is False, raises a DSLFatalError with the given message.
        """
        if not condition:
            self.handle_snare(message, context)
