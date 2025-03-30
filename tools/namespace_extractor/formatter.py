# File: namespace_extractor/formatter.py
"""
Formatter module for organizing and structuring extracted namespace data.

This module provides flexible formatting capabilities for Python namespace data,
with support for hierarchical organization, filtering, sorting, and various
output format preparations.
"""

import os
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

from tqdm import tqdm

from .config import ExtractorConfig


class NamespaceType(Enum):
    """Enumeration of namespace types for filtering and organization."""

    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    NESTED_CLASS = "nested_class"
    VARIABLE = "variable"
    MODULE = "module"
    PACKAGE = "package"


@dataclass
class FormattingOptions:
    """Configuration options for namespace formatting."""

    # Structural options
    group_by_type: bool = False
    group_by_module: bool = True
    group_by_package: bool = True

    # Sorting options
    sort_namespaces: bool = True
    sort_files: bool = True
    sort_directories: bool = True

    # Filtering options
    include_types: set[NamespaceType] = field(
        default_factory=lambda: {
            NamespaceType.CLASS,
            NamespaceType.FUNCTION,
            NamespaceType.METHOD,
            NamespaceType.NESTED_CLASS,
            NamespaceType.VARIABLE,
        }
    )
    name_patterns: list[str] = field(default_factory=list)
    exclude_name_patterns: list[str] = field(default_factory=list)

    # Display options
    show_inheritance: bool = True
    show_decorators: bool = True
    show_docstrings: bool = True
    include_line_numbers: bool = False
    max_docstring_length: int = 80
    indentation_size: int = 4


class FormatStatistics:
    """Collects statistics about the formatted data."""

    def __init__(self) -> None:
        """Initialize empty statistics counters."""
        self.total_files: int = 0
        self.total_classes: int = 0
        self.total_functions: int = 0
        self.total_methods: int = 0
        self.total_nested_classes: int = 0
        self.total_variables: int = 0
        self.total_directories: int = 0
        self.nested_depth_max: int = 0
        self.function_complexity: dict[str, int] = {}

    def update_from_namespace(
        self, namespace: dict[str, Any], directory: str, filename: str
    ) -> None:
        """
        Update statistics based on a namespace entry.

        Args:
            namespace: The namespace dictionary
            directory: The directory containing the file
            filename: The filename
        """
        namespace_type = namespace.get("type", "")

        if namespace_type == "class":
            self._extracted_from_update_from_namespace_15(
                namespace, directory, filename
            )
        elif namespace_type == "function":
            if namespace.get("parent") is None:
                self.total_functions += 1

            # Calculate function complexity (e.g., by parameter count)
            name = namespace.get("name", "unknown")
            param_count = len(namespace.get("parameters", []))
            key = f"{directory}/{filename}:{name}"
            self.function_complexity[key] = param_count

    # TODO Rename this here and in `update_from_namespace`
    def _extracted_from_update_from_namespace_15(
        self, namespace: dict[str, Any], directory: str, filename: str
    ) -> None:
        self.total_classes += 1
        # Count methods
        methods = namespace.get("methods", [])
        self.total_methods += len(methods)

        # Count nested classes and update max depth
        nested_classes = namespace.get("nested_classes", [])
        self.total_nested_classes += len(nested_classes)

        # Process nested structures recursively
        for nested_class in nested_classes:
            self.update_from_namespace(nested_class, directory, filename)

        for method in methods:
            self.update_from_namespace(method, directory, filename)

    def as_dict(self) -> dict[str, Any]:
        """
        Convert statistics to a dictionary.

        Returns:
            dictionary representation of the statistics
        """
        return {
            "total_files": self.total_files,
            "total_directories": self.total_directories,
            "total_classes": self.total_classes,
            "total_functions": self.total_functions,
            "total_methods": self.total_methods,
            "total_nested_classes": self.total_nested_classes,
            "total_variables": self.total_variables,
            "max_nested_depth": self.nested_depth_max,
            "function_complexity": self.function_complexity,
        }


T = TypeVar("T")


class NamespaceFormatter(Generic[T]):
    """Base class for namespace formatters."""

    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the formatter with configuration.

        Args:
            config: The extractor configuration
        """
        self.config = config
        self.options = self._create_formatting_options()
        self.statistics = FormatStatistics()

    def _create_formatting_options(self) -> FormattingOptions:
        """
        Create formatting options based on configuration.

        Returns:
            Configured FormattingOptions object
        """
        options = FormattingOptions(
            group_by_type=False,
            group_by_module=True,
            group_by_package=True,
            sort_namespaces=True,
            sort_files=True,
            sort_directories=True,
            show_inheritance=True,
            show_decorators=True,
            show_docstrings=self.config.include_docstrings,
            indentation_size=self.config.indent_size,
        )

        # set up include types based on config
        include_types = {NamespaceType.CLASS, NamespaceType.FUNCTION}

        if self.config.include_private:
            # When private methods are included, we want to include all methods
            include_types.add(NamespaceType.METHOD)

        if self.config.include_module_vars:
            include_types.add(NamespaceType.VARIABLE)

        options.include_types = include_types

        return options

    def format_data(
        self, extracted_data: list[tuple[str, str, list[dict[str, Any]]]]
    ) -> T:
        """
        Format extracted data according to the formatter's logic.

        Args:
            extracted_data: list of tuples containing directory, filename, namespaces

        Returns:
            Formatted data in the target format
        """
        # Collect basic statistics
        total_items = sum(len(namespaces) for _, _, namespaces in extracted_data)

        # Process data with progress bar
        with tqdm(total=total_items, desc="Formatting namespaces") as pbar:
            formatted_data = self._format_data_impl(extracted_data, pbar)

        # Print statistics summary
        self._print_statistics_summary()

        return formatted_data

    @abstractmethod
    def _format_data_impl(
        self,
        extracted_data: list[tuple[str, str, list[dict[str, Any]]]],
        progress_bar: tqdm,
    ) -> T:
        """
        Implementation of the formatting logic.

        Args:
            extracted_data: list of tuples containing directory, filename, namespaces
            progress_bar: Progress bar for updating progress

        Returns:
            Formatted data in the target format
        """
        pass

    def _print_statistics_summary(self) -> None:
        """Print a summary of the collected statistics."""
        stats = self.statistics.as_dict()
        print("\nNamespace Statistics:")
        print(f"  Files processed: {stats['total_files']}")
        print(f"  Directories: {stats['total_directories']}")
        print(f"  Classes: {stats['total_classes']}")
        print(f"  Functions: {stats['total_functions']}")
        print(f"  Methods: {stats['total_methods']}")
        print(f"  Nested classes: {stats['total_nested_classes']}")
        if self.config.include_module_vars:
            print(f"  Variables: {stats['total_variables']}")

    def _filter_namespace(
        self, namespace: dict[str, Any], parent_path: str = ""
    ) -> bool:
        """
        Check if a namespace should be included based on filtering options.

        Args:
            namespace: The namespace dictionary
            parent_path: Path of the parent namespace

        Returns:
            True if the namespace should be included, False otherwise
        """
        namespace_type = namespace.get("type", "")
        name = namespace.get("name", "")

        # Check type filtering
        if (
            namespace_type == "class"
            and NamespaceType.CLASS not in self.options.include_types
        ):
            return False

        if namespace_type == "function":
            if namespace.get("parent") is None:
                # Top-level function
                if NamespaceType.FUNCTION not in self.options.include_types:
                    return False
            elif NamespaceType.METHOD not in self.options.include_types:
                return False

        # Check name pattern filtering (if specified)
        if self.options.name_patterns and all(
            pattern not in name for pattern in self.options.name_patterns
        ):
            return False

        # Check exclude patterns
        if any(pattern in name for pattern in self.options.exclude_name_patterns):
            return False

        # Check privacy based on config
        if (
            not self.config.include_private
            and name.startswith("_")
            and not name.startswith("__")
        ):
            return False

        # Check dunder methods based on config
        return bool(
            self.config.include_dunder
            or not name.startswith("__")
            or not name.endswith("__")
        )

    def _sort_namespaces(
        self, namespaces: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Sort a list of namespaces according to formatting options.

        Args:
            namespaces: list of namespace dictionaries

        Returns:
            Sorted list of namespaces
        """
        if not self.options.sort_namespaces:
            return namespaces

        # Helper function to get sort key
        def get_sort_key(namespace: dict[str, Any]) -> tuple[int, str]:
            namespace_type = namespace.get("type", "")
            name = namespace.get("name", "")

            # Define type order for sorting
            type_order = {"class": 0, "function": 1, "variable": 2}

            # Special handling for __init__ methods to appear first
            if namespace_type == "function" and name == "__init__":
                return (-1, name)

            return (type_order.get(namespace_type, 99), name)

        return sorted(namespaces, key=get_sort_key)


class DictionaryFormatter(
    NamespaceFormatter[dict[str, dict[str, list[dict[str, Any]]]]]
):
    """Formats namespace data as a nested dictionary structure."""

    def _format_data_impl(
        self,
        extracted_data: list[tuple[str, str, list[dict[str, Any]]]],
        progress_bar: tqdm,
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """
        Format extracted data into a hierarchical dictionary.

        Args:
            extracted_data: list of tuples containing directory, filename, namespaces
            progress_bar: Progress bar for updating progress

        Returns:
            dictionary with structure: {directory: {filename: [namespaces]}}
        """
        # Initialize result dictionary
        directory_data: dict[str, dict[str, list[dict[str, Any]]]] = {}

        # Track unique directories
        unique_directories = set()

        # Process each data item
        for directory, filename, namespaces in extracted_data:
            unique_directories.add(directory)

            # Initialize directory entry if needed
            if directory not in directory_data:
                directory_data[directory] = {}

            # Filter and process namespaces
            processed_namespaces = []
            for namespace in namespaces:
                if self._filter_namespace(namespace):
                    processed_namespaces.append(namespace)
                    # Update statistics
                    self.statistics.update_from_namespace(
                        namespace, directory, filename
                    )

                # Update progress
                progress_bar.update(1)

            # Only add file if it has namespaces after filtering
            if processed_namespaces:
                directory_data[directory][filename] = self._sort_namespaces(
                    processed_namespaces
                )

        # Update statistics
        self.statistics.total_files = sum(
            len(files) for files in directory_data.values()
        )
        self.statistics.total_directories = len(unique_directories)

        # Sort directories and files if configured
        if self.options.sort_directories:
            sorted_directory_data: dict[str, dict[str, list[dict[str, Any]]]] = {}
            for directory in sorted(directory_data.keys()):
                sorted_directory_data[directory] = {}

                if self.options.sort_files:
                    for filename in sorted(directory_data[directory].keys()):
                        sorted_directory_data[directory][filename] = directory_data[
                            directory
                        ][filename]
                else:
                    sorted_directory_data[directory] = directory_data[directory]

            return sorted_directory_data

        return directory_data


class HierarchicalFormatter(NamespaceFormatter[dict[str, Any]]):
    """
    Formats namespace data as a deeply nested hierarchical structure.

    This formatter reorganizes the data to represent the actual Python package
    hierarchy, with modules nested under packages and namespaces nested under modules.
    """

    def _format_data_impl(
        self,
        extracted_data: list[tuple[str, str, list[dict[str, Any]]]],
        progress_bar: tqdm,
    ) -> dict[str, Any]:
        """
        Format extracted data into a deeply nested hierarchical structure.

        Args:
            extracted_data: list of tuples containing directory, filename, namespaces
            progress_bar: Progress bar for updating progress

        Returns:
            dictionary with nested package/module/namespace hierarchy
        """
        # Initialize result structure
        hierarchy: dict[str, Any] = {
            "type": "root",
            "name": "root",
            "packages": {},
            "modules": {},
        }

        # Track statistics
        unique_directories = set()
        total_files = 0

        # Process each data item
        for directory, filename, namespaces in extracted_data:
            unique_directories.add(directory)

            # Skip empty files
            if not namespaces:
                progress_bar.update(len(namespaces))
                continue

            total_files += 1

            # Determine package path
            package_path = directory.replace(os.sep, ".")
            if package_path.startswith("."):
                package_path = package_path[1:]

            # Module name (filename without .py)
            module_name = os.path.splitext(filename)[0]

            # Build package hierarchy
            current_level = hierarchy
            if package_path and self.options.group_by_package:
                package_parts = package_path.split(".")
                for part in package_parts:
                    if not part:  # Skip empty parts
                        continue

                    if part not in current_level["packages"]:
                        current_level["packages"][part] = {
                            "type": "package",
                            "name": part,
                            "packages": {},
                            "modules": {},
                        }

                    current_level = current_level["packages"][part]

            # Add module
            if module_name not in current_level["modules"]:
                current_level["modules"][module_name] = {
                    "type": "module",
                    "name": module_name,
                    "filename": filename,
                    "classes": {},
                    "functions": [],
                    "variables": [],
                }

            module_data = current_level["modules"][module_name]

            # Process namespaces
            for namespace in namespaces:
                self._process_namespace(namespace, module_data, directory, filename)
                # Update progress
                progress_bar.update(1)

        # Update statistics
        self.statistics.total_files = total_files
        self.statistics.total_directories = len(unique_directories)

        # Sort if configured
        if self.options.sort_namespaces:
            self._sort_hierarchy(hierarchy)

        return hierarchy

    def _process_namespace(
        self,
        namespace: dict[str, Any],
        module_data: dict[str, Any],
        directory: str,
        filename: str,
    ) -> None:
        """
        Process a namespace and add it to the module data.

        Args:
            namespace: Namespace dictionary
            module_data: Module data dictionary to update
            directory: Directory containing the file
            filename: Name of the file
        """
        if not self._filter_namespace(namespace):
            return

        namespace_type = namespace.get("type", "")
        name = namespace.get("name", "")

        if namespace_type == "class":
            # Add class to module
            module_data["classes"][name] = {
                "type": "class",
                "name": name,
                "bases": namespace.get("bases", []),
                "decorators": namespace.get("decorators", []),
                "docstring": namespace.get("docstring", ""),
                "methods": [],
                "nested_classes": {},
            }

            # Process methods
            for method in namespace.get("methods", []):
                if self._filter_namespace(method, name):
                    module_data["classes"][name]["methods"].append(
                        {
                            "type": "method",
                            "name": method.get("name", ""),
                            "signature": method.get("signature", ""),
                            "decorators": method.get("decorators", []),
                            "is_async": method.get("is_async", False),
                            "docstring": method.get("docstring", ""),
                        }
                    )

                    # Update statistics
                    self.statistics.total_methods += 1

            # Process nested classes
            for nested_class in namespace.get("nested_classes", []):
                if self._filter_namespace(nested_class, name):
                    nested_name = nested_class.get("name", "")
                    module_data["classes"][name]["nested_classes"][nested_name] = {
                        "type": "nested_class",
                        "name": nested_name,
                        "bases": nested_class.get("bases", []),
                        "decorators": nested_class.get("decorators", []),
                        "docstring": nested_class.get("docstring", ""),
                        "methods": [],
                    }

                    # Process nested class methods
                    for method in nested_class.get("methods", []):
                        if self._filter_namespace(method, f"{name}.{nested_name}"):
                            module_data["classes"][name]["nested_classes"][nested_name][
                                "methods"
                            ].append(
                                {
                                    "type": "method",
                                    "name": method.get("name", ""),
                                    "signature": method.get("signature", ""),
                                    "decorators": method.get("decorators", []),
                                    "is_async": method.get("is_async", False),
                                    "docstring": method.get("docstring", ""),
                                }
                            )

                            # Update statistics
                            self.statistics.total_methods += 1

                    # Update statistics
                    self.statistics.total_nested_classes += 1

            # Update statistics
            self.statistics.total_classes += 1

        elif namespace_type == "function" and namespace.get("parent") is None:
            # Add function to module
            module_data["functions"].append(
                {
                    "type": "function",
                    "name": name,
                    "signature": namespace.get("signature", ""),
                    "decorators": namespace.get("decorators", []),
                    "is_async": namespace.get("is_async", False),
                    "docstring": namespace.get("docstring", ""),
                }
            )

            # Update statistics
            self.statistics.total_functions += 1

        elif namespace_type == "variable" and self.config.include_module_vars:
            # Add variable to module
            module_data["variables"].append(
                {"type": "variable", "name": name, "value": namespace.get("value", "")}
            )

            # Update statistics
            self.statistics.total_variables += 1

    def _sort_hierarchy(self, node: dict[str, Any]) -> None:
        """
        Sort a hierarchical node and its children recursively.

        Args:
            node: Node to sort
        """
        # Sort packages
        if "packages" in node:
            sorted_packages = {}
            for name in sorted(node["packages"].keys()):
                sorted_packages[name] = node["packages"][name]
                self._sort_hierarchy(sorted_packages[name])
            node["packages"] = sorted_packages

        # Sort modules
        if "modules" in node:
            sorted_modules = {}
            for name in sorted(node["modules"].keys()):
                sorted_modules[name] = node["modules"][name]

                # Sort classes
                if "classes" in sorted_modules[name]:
                    sorted_classes = {}
                    for class_name in sorted(sorted_modules[name]["classes"].keys()):
                        sorted_classes[class_name] = sorted_modules[name]["classes"][
                            class_name
                        ]

                        # Sort methods
                        if "methods" in sorted_classes[class_name]:
                            sorted_classes[class_name]["methods"] = sorted(
                                sorted_classes[class_name]["methods"],
                                key=lambda x: (
                                    0 if x["name"] == "__init__" else 1,
                                    x["name"],
                                ),
                            )

                        # Sort nested classes
                        if "nested_classes" in sorted_classes[class_name]:
                            sorted_nested = {}
                            for nested_name in sorted(
                                sorted_classes[class_name]["nested_classes"].keys()
                            ):
                                sorted_nested[nested_name] = sorted_classes[class_name][
                                    "nested_classes"
                                ][nested_name]

                                # Sort nested methods
                                if "methods" in sorted_nested[nested_name]:
                                    sorted_nested[nested_name]["methods"] = sorted(
                                        sorted_nested[nested_name]["methods"],
                                        key=lambda x: (
                                            0 if x["name"] == "__init__" else 1,
                                            x["name"],
                                        ),
                                    )

                            sorted_classes[class_name]["nested_classes"] = sorted_nested

                    sorted_modules[name]["classes"] = sorted_classes

                # Sort functions
                if "functions" in sorted_modules[name]:
                    sorted_modules[name]["functions"] = sorted(
                        sorted_modules[name]["functions"], key=lambda x: x["name"]
                    )

                # Sort variables
                if "variables" in sorted_modules[name]:
                    sorted_modules[name]["variables"] = sorted(
                        sorted_modules[name]["variables"], key=lambda x: x["name"]
                    )

            node["modules"] = sorted_modules


class FormatterFactory:
    """Factory for creating appropriate formatter instances."""

    @staticmethod
    def create_formatter(
        formatter_type: str, config: ExtractorConfig
    ) -> NamespaceFormatter:
        """
        Create a formatter instance based on the specified type.

        Args:
            formatter_type: Type of formatter to create
            config: Extractor configuration

        Returns:
            Formatter instance

        Raises:
            ValueError: If formatter_type is not recognized
        """
        if formatter_type == "dictionary":
            return DictionaryFormatter(config)
        elif formatter_type == "hierarchical":
            return HierarchicalFormatter(config)
        else:
            raise ValueError(f"Unknown formatter type: {formatter_type}")
