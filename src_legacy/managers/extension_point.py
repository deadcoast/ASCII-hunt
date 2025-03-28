"""Extension Point Module.

This module provides an extension point mechanism for the application.
Extension points allow for modular and extensible design by providing
well-defined points for components to connect to the system.
"""

from collections.abc import Callable
from typing import Any


class ExtensionPoint:
    """A class that represents an extension point.

    Extension points allow plugins to register implementations of specific
    functionality that can be used by the core system. Each extension point
    has a name and a registry of extensions.
    """

    def __init__(self, name: str):
        """Initialize the ExtensionPoint class.

        Args:
            name: The name of the extension point.
        """
        self.name = name
        self.extensions: dict[str, Any] = {}
        self.callbacks: list[Callable[[str, Any], None]] = []

    def register_extension(self, name: str, extension: Any) -> None:
        """Register an extension.

        Args:
            name: The name of the extension.
            extension: The extension object.
        """
        self.extensions[name] = extension

        # Notify all registered callbacks
        for callback in self.callbacks:
            callback(name, extension)

    def unregister_extension(self, name: str) -> None:
        """Unregister an extension.

        Args:
            name: The name of the extension to unregister.
        """
        if name in self.extensions:
            del self.extensions[name]

    def get_extension(self, name: str) -> Any | None:
        """Get an extension by name.

        Args:
            name: The name of the extension to get.

        Returns:
            The extension object, or None if it does not exist.
        """
        return self.extensions.get(name)

    def get_extensions(self) -> dict[str, Any]:
        """Get all registered extensions.

        Returns:
            A dictionary mapping extension names to extension objects.
        """
        return self.extensions

    def register_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Register a callback to be called when an extension is registered.

        The callback will be called with the name of the extension and the
        extension object.

        Args:
            callback: The callback to register.
        """
        self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Unregister a callback.

        Args:
            callback: The callback to unregister.
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
