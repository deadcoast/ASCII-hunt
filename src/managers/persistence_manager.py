"""Persistence Manager Module."""

from .storage_providers import FileSystemStorageProvider


class PersistenceManager:
    def __init__(self, storage_provider=None):
        """
        Initialize a PersistenceManager.

        :param storage_provider: The storage provider to use for persistence.
        :type storage_provider: :class:`StorageProvider`
        """
        self.storage_provider = storage_provider or FileSystemStorageProvider()
        self.serializers = {}

    def register_serializer(self, data_type, serializer):
        """Register a serializer for a specific data type."""
        self.serializers[data_type] = serializer

    def save_project(self, project_data, project_path):
        """Save project data to the specified path."""
        # Validate project data
        if not isinstance(project_data, dict):
            raise ValueError("Project data must be a dictionary")

        # Prepare serialized data
        serialized_data = {}

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

    def load_project(self, project_path):
        """Load project data from the specified path."""
        # Load from storage
        serialized_data = self.storage_provider.load(project_path)

        if not isinstance(serialized_data, dict):
            raise ValueError("Invalid project data format")

        # Deserialize data
        project_data = {}

        for key, value_info in serialized_data.items():
            if (
                not isinstance(value_info, dict)
                or "type" not in value_info
                or "data" not in value_info
            ):
                raise ValueError(f"Invalid data format for key {key}")

            data_type = value_info["type"]
            serialized_value = value_info["data"]

            if data_type in self.serializers:
                project_data[key] = self.serializers[data_type].deserialize(
                    serialized_value
                )
            else:
                # Use default deserialization if no specific serializer
                project_data[key] = self._default_deserialize(
                    serialized_value, data_type
                )

        return project_data

    def _default_serialize(self, value):
        """Default serialization for types without specific serializers."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._default_serialize(item) for item in value]
        elif isinstance(value, dict):
            return {str(k): self._default_serialize(v) for k, v in value.items()}
        else:
            # For complex types, use their __dict__ if available
            if hasattr(value, "__dict__"):
                return {
                    "__class__": value.__class__.__name__,
                    "__module__": value.__class__.__module__,
                    "__dict__": self._default_serialize(value.__dict__),
                }
            else:
                # Last resort: string representation
                return str(value)

    def _default_deserialize(self, value, data_type):
        """Default deserialization for types without specific deserializers."""
        if data_type in ("str", "int", "float", "bool", "NoneType"):
            return value
        elif data_type in ("list", "tuple"):
            result = [
                self._default_deserialize(item, type(item).__name__) for item in value
            ]
            return tuple(result) if data_type == "tuple" else result
        elif data_type == "dict":
            return {
                k: self._default_deserialize(v, type(v).__name__)
                for k, v in value.items()
            }
        else:
            # Complex types - try to reconstruct if we have class info
            if (
                isinstance(value, dict)
                and "__class__" in value
                and "__module__" in value
                and "__dict__" in value
            ):
                try:
                    module = __import__(
                        value["__module__"], fromlist=[value["__class__"]]
                    )
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
