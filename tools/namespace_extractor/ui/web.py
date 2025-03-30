# File: namespace_extractor/ui/web.py
"""
Web interface for browsing namespace extraction results.

This module provides a Flask-based web interface for browsing, searching,
and visualizing the results of namespace extraction.
"""

import json
import os
from pathlib import Path
from typing import Any

import yaml
from flask import Flask, Response, jsonify, render_template, request

from ..config import ExtractorConfig


class WebInterface:
    """Web interface for browsing extraction results."""

    def __init__(
        self,
        data_file: str,
        config: ExtractorConfig | None = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> None:
        """
        Initialize the web interface.

        Args:
            data_file: Path to the extraction results file
            config: Configuration used for extraction (optional)
            host: Host address to bind the server to
            port: Port to run the server on
        """
        self.data_file = data_file
        self.config = config or ExtractorConfig()
        self.host = host
        self.port = port
        self.data: dict[str, Any] | None = None

        # Create Flask app
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / "templates"),
            static_folder=str(Path(__file__).parent / "static"),
        )

        # Set up routes
        self._configure_routes()

        # Load data
        self._load_data()

    def _load_data(self) -> None:
        """Load extraction data from file."""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        extension = os.path.splitext(self.data_file)[1].lower()

        try:
            if extension == ".json":
                with open(self.data_file, encoding="utf-8") as f:
                    self.data = json.load(f)
            elif extension in [".yaml", ".yml"]:
                with open(self.data_file, encoding="utf-8") as f:
                    self.data = yaml.safe_load(f)
            elif extension == ".md":
                # Parse markdown file (assuming it follows our format)
                self.data = self._parse_markdown_file()
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        except Exception as e:
            raise ValueError(f"Error loading data file: {e!s}") from e

    def _parse_markdown_file(self) -> dict[str, Any]:
        """
        Parse a markdown file into a structured dictionary.

        Returns:
            Dictionary with parsed data
        """
        # This is a simplified implementation that assumes a specific format
        result: dict[str, dict[str, list[dict[str, Any]]]] = {}
        current_directory = ""
        current_file = ""

        with open(self.data_file, encoding="utf-8") as f:
            content = f.read()

        # Extract content between guard rails
        if "##GUARD_!_RAIL##" in content:
            parts = content.split("##GUARD_!_RAIL##")
            if len(parts) >= 3:
                content = parts[1].strip()

        # Process lines
        lines = content.split("\n")
        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for directory docstring
            if line.startswith('"""') and '"""' in line[3:]:
                # Single line docstring
                current_directory = line[3:-3].strip()
                if current_directory not in result:
                    result[current_directory] = {}
            elif line.startswith('"""'):
                # Start of multi-line docstring
                current_directory = ""
            elif line.endswith('"""') and current_directory == "":
                # End of multi-line docstring
                current_directory = line[:-3].strip()
                if current_directory not in result:
                    result[current_directory] = {}

            # Check for file marker
            elif line.startswith("# ") and not line.startswith("# #"):
                current_file = line[2:].strip()
                if current_directory not in result:
                    result[current_directory] = {}
                if current_file not in result[current_directory]:
                    result[current_directory][current_file] = []

            # TODO: Add more detailed parsing for classes, methods, etc.
            # This would require a more sophisticated parser

        return result

    def _configure_routes(self) -> None:
        """Configure Flask routes."""
        app = self.app

        @app.route("/")
        def index() -> str:
            """Render the main page."""
            return render_template(
                "index.html", title="Namespace Extractor", config=self.config
            )

        @app.route("/api/data")
        def get_data() -> Response:
            """API endpoint to get extraction data."""
            return jsonify({"data": self.data})

        @app.route("/api/search")
        def search() -> Response:
            """API endpoint for searching the data."""
            query = request.args.get("q", "").lower()

            if not query or not self.data:
                return jsonify({"results": []})

            results = []

            # Search logic depends on data structure
            if isinstance(self.data, dict) and all(
                isinstance(v, dict) for v in self.data.values()
            ):
                # Dictionary format
                for directory, files in self.data.items():
                    for filename, namespaces in files.items():
                        for namespace in namespaces:
                            if self._namespace_matches_query(namespace, query):
                                results.append(
                                    {
                                        "directory": directory,
                                        "file": filename,
                                        "namespace": namespace,
                                    }
                                )

            return jsonify({"results": results})

        @app.route("/api/stats")
        def stats() -> Response:
            """API endpoint to get statistics about the data."""
            if not self.data:
                return jsonify({"stats": {}})

            # Calculate statistics
            stats = self._calculate_statistics()

            return jsonify({"stats": stats})

    def _namespace_matches_query(self, namespace: dict[str, Any], query: str) -> bool:
        """
        Check if a namespace matches a search query.

        Args:
            namespace: Namespace dictionary
            query: Search query string

        Returns:
            True if the namespace matches the query, False otherwise
        """
        # Check name
        if query in namespace.get("name", "").lower():
            return True

        # Check signature for functions
        if (
            namespace.get("type") == "function"
            and query in namespace.get("signature", "").lower()
        ):
            return True

        # Check docstring
        if (
            self.config.include_docstrings
            and query in namespace.get("docstring", "").lower()
        ):
            return True

        # Check nested elements
        if "methods" in namespace:
            for method in namespace["methods"]:
                if self._namespace_matches_query(method, query):
                    return True

        if "nested_classes" in namespace:
            for nested_class in namespace["nested_classes"]:
                if self._namespace_matches_query(nested_class, query):
                    return True

        return False

    def _calculate_statistics(self) -> dict[str, Any]:
        """
        Calculate statistics about the extraction data.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_classes": 0,
            "total_functions": 0,
            "total_methods": 0,
            "total_nested_classes": 0,
            "total_variables": 0,
        }

        if isinstance(self.data, dict):
            stats["total_directories"] = len(self.data)
            for files in self.data.values():
                stats["total_files"] += len(files)
                for namespaces in files.values():
                    for namespace in namespaces:
                        self._namespace_statistics_update(stats, namespace)

        return stats

    def _update_stats_from_namespace(
        self, stats: dict[str, int], namespace: dict[str, Any]
    ) -> None:
        """
        Update statistics based on a namespace.

        Args:
            stats: Statistics dictionary to update
            namespace: Namespace dictionary
        """
        namespace_type = namespace.get("type", "")

        if namespace_type == "class":
            self._namespace_statistics_update(stats, namespace)
        elif namespace_type == "function":
            if namespace.get("parent") is None:
                stats["total_functions"] += 1

        elif namespace_type == "variable":
            stats["total_variables"] += 1

    def _namespace_statistics_update(
        self, stats: dict[str, int], namespace: dict[str, Any]
    ) -> None:
        """
        Update statistics based on a namespace.

        Args:
            stats: Statistics dictionary to update
            namespace: Namespace dictionary
        """
        stats["total_classes"] += 1

        # Count methods
        methods = namespace.get("methods", [])
        stats["total_methods"] += len(methods)

        # Count nested classes
        nested_classes = namespace.get("nested_classes", [])
        if isinstance(nested_classes, list):
            stats["total_nested_classes"] += len(nested_classes)
            for nested_class in nested_classes:
                self._update_stats_from_namespace(stats, nested_class)
        elif isinstance(nested_classes, dict):
            stats["total_nested_classes"] += len(nested_classes)
            for nested_class in nested_classes.values():
                self._update_stats_from_namespace(stats, nested_class)

        # Process methods
        for method in methods:
            self._update_stats_from_namespace(stats, method)

    def run(self) -> None:
        """Run the web interface server."""
        print(f"Starting web interface at http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop the server")

        self.app.run(host=self.host, port=self.port, debug=False)
