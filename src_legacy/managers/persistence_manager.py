"""Persistence Manager Module."""

from collections.abc import Callable
from typing import Any, TypeVar

from .storage_providers import FileSystemStorageProvider

T = TypeVar("T")


class PersistenceManager:
    def __init__(
        self, storage_provider: FileSystemStorageProvider | None = None
    ) -> None:
        """Initialize a PersistenceManager.

        Args:
            storage_provider: The storage provider to use for persistence.
        """
        self.storage_provider = storage_provider or FileSystemStorageProvider()
        self.serializers: dict[str, Callable[[Any], dict[str, Any]]] = {}

    def register_serializer(
        self, data_type: str, serializer: Callable[[Any], dict[str, Any]]
    ) -> None:
        """Register a serializer for a specific data type."""
        self.serializers[data_type] = serializer

    def save_project(self, project_data: dict[str, Any], project_path: str) -> None:
        """Save project data to the specified path."""
        # Validate project data
        if not isinstance(project_data, dict):
            raise ValueError("Project data must be a dictionary")

        # Prepare serialized data
        serialized_data: dict[str, Any] = {}

        for key, value in project_data.items():
            data_type = type(value).__name__

            if data_type in self.serializers:
                serialized_data[key] = {
                    "type": data_type,
                    "data": self.serializers[data_type].serialize(value),
                }
            else:
                # Use default serialization if no specific serializer
                serialized_data[key] = {
                    "type": data_type,
                    "data": self._default_serialize(value),
                }

        # Save to storage
        self.storage_provider.save(project_path, serialized_data)

    def load_project(self, project_path: str) -> dict[str, Any]:
        """Load project data from the specified path."""
        # Load raw data from storage
        raw_data = self.storage_provider.load(project_path)

        # Deserialize data
        project_data: dict[str, Any] = {}

        for key, value_info in raw_data.items():
            data_type = value_info["type"]
            value = value_info["data"]

            if data_type in self.serializers:
                project_data[key] = self.serializers[data_type].deserialize(value)
            else:
                # Use default deserialization if no specific deserializer
                project_data[key] = self._default_deserialize(value, data_type)

        return project_data

    def _default_serialize(self, value: Any) -> Any:
        """Default serialization for types without specific serializers."""
        if isinstance(value, (str | int | float | bool | type(None))):
            return value
        if isinstance(value, (list | tuple)):
            return [self._default_serialize(item) for item in value]
        if isinstance(value, dict):
            return {k: self._default_serialize(v) for k, v in value.items()}
        # Complex types - store class info
        return {
            "__class__": value.__class__.__name__,
            "__module__": value.__class__.__module__,
            "__dict__": self._default_serialize(value.__dict__),
        }

    def _default_deserialize(self, value: Any, data_type: str) -> Any:
        """Default deserialization for types without specific deserializers."""
        if data_type in ("str", "int", "float", "bool", "NoneType"):
            return value
        if data_type in ("list", "tuple"):
            result = [
                self._default_deserialize(item, type(item).__name__) for item in value
            ]
            return tuple(result) if data_type == "tuple" else result
        if data_type == "dict":
            return {
                k: self._default_deserialize(v, type(v).__name__)
                for k, v in value.items()
            }
        # Complex types - try to reconstruct if we have class info
        if (
            isinstance(value, dict)
            and "__class__" in value
            and "__module__" in value
            and "__dict__" in value
        ):
            try:
                module = __import__(value["__module__"], fromlist=[value["__class__"]])
                cls = getattr(module, value["__class__"])
                instance = cls.__new__(cls)

                # Reconstruct __dict__
                instance_dict = self._default_deserialize(value["__dict__"], "dict")
                instance.__dict__.update(instance_dict)

                return instance
            except (ImportError, AttributeError):
                # Fallback: return as dict
                return value
        else:
            # No class info, return as is
            return value
