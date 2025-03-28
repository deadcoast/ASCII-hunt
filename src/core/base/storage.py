"""Storage module for the persistence system."""

import json
import os
from pathlib import Path
from typing import Any, Protocol


class StorageProvider(Protocol):
    """Protocol defining a storage provider interface."""

    def save(self, path: Path, data: dict[str, Any]) -> None:
        """Save data to a file.

        Args:
            path: Path to the file
            data: Data to save
        """
        ...

    def load(self, path: Path) -> dict[str, Any]:
        """Load data from a file.

        Args:
            path: Path to the file

        Returns:
            The loaded data
        """
        ...


class FileSystemStorageProvider:
    """Provides file system storage for persistence."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize FileSystemStorageProvider.

        Args:
            base_dir: Base directory for file storage, defaults to current directory.
        """
        self.base_dir = base_dir or os.getcwd()
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, path: Path, data: dict[str, Any]) -> None:
        """Save data to a file.

        Args:
            path: Path to the file, can be absolute or relative to base_dir
            data: Data to save
        """
        full_path = self._get_full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path) -> dict[str, Any]:
        """Load data from a file.

        Args:
            path: Path to the file, can be absolute or relative to base_dir

        Returns:
            The loaded data

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        full_path = self._get_full_path(path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")

        with open(full_path, encoding="utf-8") as f:
            return json.load(f)

    def _get_full_path(self, path: Path) -> str:
        """Get full path from a Path object.

        Args:
            path: Path object

        Returns:
            Full path as a string
        """
        if path.is_absolute():
            return str(path)
        return os.path.join(self.base_dir, str(path))
