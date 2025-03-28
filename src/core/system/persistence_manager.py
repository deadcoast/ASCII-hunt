"""Persistence manager for ASCII art projects."""

from pathlib import Path
from typing import Any

from src.core.storage import FileSystemStorageProvider, StorageProvider


class PersistenceManager:
    """Manages persistence of ASCII art projects."""

    def __init__(self, storage_provider: StorageProvider | None = None) -> None:
        """Initialize persistence manager.

        Args:
            storage_provider: Storage provider to use, defaults to FileSystemStorageProvider
        """
        self.storage = storage_provider or FileSystemStorageProvider()
        self.serializers: dict[str, Any] = {}

    def register_serializer(
        self, data_type: type[Any], serializer: Any, deserializer: Any
    ) -> None:
        """Register serializer for a data type.

        Args:
            data_type: Type of data to serialize
            serializer: Function to serialize data
            deserializer: Function to deserialize data
        """
        type_name = data_type.__name__
        self.serializers[type_name] = {
            "serialize": serializer,
            "deserialize": deserializer,
        }

    def save_project(self, project_data: dict[str, Any], path: str) -> None:
        """Save project data to storage.

        Args:
            project_data: Dictionary containing project data
            path: Path to save project to
        """
        serialized_data = self._serialize_data(project_data)
        self.storage.save(Path(path), serialized_data)

    def load_project(self, path: str) -> dict[str, Any]:
        """Load project data from storage.

        Args:
            path: Path to load project from

        Returns:
            Dictionary containing project data
        """
        raw_data = self.storage.load(Path(path))
        return self._deserialize_data(raw_data)

    def _serialize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Serialize data using registered serializers.

        Args:
            data: Data to serialize

        Returns:
            Serialized data
        """
        serialized: dict[str, Any] = {}

        for key, value in data.items():
            type_name = type(value).__name__
            if type_name in self.serializers:
                serialized[key] = {
                    "type": type_name,
                    "data": self.serializers[type_name]["serialize"](value),
                }
            else:
                serialized[key] = {"type": type_name, "data": value}

        return serialized

    def _deserialize_data(self, serialized: dict[str, Any]) -> dict[str, Any]:
        """Deserialize data using registered serializers.

        Args:
            serialized: Serialized data to deserialize

        Returns:
            Deserialized data
        """
        deserialized: dict[str, Any] = {}

        for key, value in serialized.items():
            type_name = value["type"]
            if type_name in self.serializers:
                deserialized[key] = self.serializers[type_name]["deserialize"](
                    value["data"]
                )
            else:
                deserialized[key] = value["data"]

        return deserialized
