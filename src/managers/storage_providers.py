"""Storage Providers Module for the Persistence System."""

import json
import os
from typing import Any


class FileSystemStorageProvider:
    """Provides file system storage for persistence."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize FileSystemStorageProvider.

        Args:
            base_dir: Base directory for file storage, defaults to current directory.
        """
        self.base_dir = base_dir or os.getcwd()
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, file_path: str, data: dict[str, Any]) -> None:
        """Save data to a file.

        Args:
            file_path: Path to the file, relative to base_dir
            data: Data to save
        """
        path = self._get_full_path(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, file_path: str) -> dict[str, Any]:
        """Load data from a file.

        Args:
            file_path: Path to the file, relative to base_dir

        Returns:
            The loaded data

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = self._get_full_path(file_path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _get_full_path(self, file_path: str) -> str:
        """Get full path from a relative path.

        Args:
            file_path: Relative path

        Returns:
            Full path including base_dir
        """
        return os.path.join(self.base_dir, file_path)
