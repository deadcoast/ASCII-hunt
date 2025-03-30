# File: namespace_extractor/config.py
"""Configuration module for the namespace extractor.

This module provides configuration management for the namespace extractor,
including loading from YAML files, validation, and conversion between
different configuration representations.
"""

import argparse
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import yaml


class FormatterType(Enum):
    """Available formatter types."""

    DICTIONARY = "dictionary"
    HIERARCHICAL = "hierarchical"


class OutputFormat(Enum):
    """Available output formats."""

    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"


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


@dataclass
class ExtractorConfig:
    """Configuration class for the namespace extractor."""

    # Basic extraction options
    include_private: bool = True
    include_dunder: bool = False
    include_docstrings: bool = False
    include_module_vars: bool = False

    # Directory traversal options
    recursive: bool = True
    max_recursion_depth: int = -1  # -1 means no limit
    exclude_patterns: list[str] = field(default_factory=list)

    # Formatting options
    formatter_type: FormatterType = FormatterType.DICTIONARY
    output_format: OutputFormat = OutputFormat.MARKDOWN
    indent_size: int = 4
    show_file_path_prefix: bool = True

    # Advanced formatting options
    formatting_options: FormattingOptions = field(default_factory=FormattingOptions)

    def __post_init__(self) -> None:
        """Validate configuration and set up derived values."""
        # Convert string values to enum values if necessary
        if isinstance(self.formatter_type, str):
            self.formatter_type = FormatterType(self.formatter_type)

        if isinstance(self.output_format, str):
            self.output_format = OutputFormat(self.output_format)

        # Update formatting options based on main config
        self.formatting_options.show_docstrings = self.include_docstrings
        self.formatting_options.indentation_size = self.indent_size

        # Update include_types based on include_private and include_module_vars
        if (
            not self.include_private
            and NamespaceType.METHOD in self.formatting_options.include_types
        ):
            self.formatting_options.include_types.remove(NamespaceType.METHOD)

        if (
            not self.include_module_vars
            and NamespaceType.VARIABLE in self.formatting_options.include_types
        ):
            self.formatting_options.include_types.remove(NamespaceType.VARIABLE)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to a dictionary for serialization.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "include_private": self.include_private,
            "include_dunder": self.include_dunder,
            "include_docstrings": self.include_docstrings,
            "include_module_vars": self.include_module_vars,
            "recursive": self.recursive,
            "max_recursion_depth": self.max_recursion_depth,
            "exclude_patterns": self.exclude_patterns,
            "formatter_type": self.formatter_type.value,
            "output_format": self.output_format.value,
            "indent_size": self.indent_size,
            "show_file_path_prefix": self.show_file_path_prefix,
            "formatting_options": {
                "group_by_type": self.formatting_options.group_by_type,
                "group_by_module": self.formatting_options.group_by_module,
                "group_by_package": self.formatting_options.group_by_package,
                "sort_namespaces": self.formatting_options.sort_namespaces,
                "sort_files": self.formatting_options.sort_files,
                "sort_directories": self.formatting_options.sort_directories,
                "include_types": [
                    t.value for t in self.formatting_options.include_types
                ],
                "name_patterns": self.formatting_options.name_patterns,
                "exclude_name_patterns": self.formatting_options.exclude_name_patterns,
                "show_inheritance": self.formatting_options.show_inheritance,
                "show_decorators": self.formatting_options.show_decorators,
                "show_docstrings": self.formatting_options.show_docstrings,
                "include_line_numbers": self.formatting_options.include_line_numbers,
                "max_docstring_length": self.formatting_options.max_docstring_length,
                "indentation_size": self.formatting_options.indentation_size,
            },
        }


def load_config(config_path: str | None = None) -> ExtractorConfig:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        ExtractorConfig object with settings
    """
    config = ExtractorConfig()

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, encoding="utf-8") as file:
                if yaml_config := yaml.safe_load(file):
                    _formatting_options(yaml_config, config, config_path)
        except Exception as e:
            print(f"Error loading configuration: {e!s}")

    return config


def _formatting_options(
    yaml_config: dict[str, Any], config: ExtractorConfig, config_path: str
) -> None:
    """Handle formatting_options separately."""
    formatting_options = yaml_config.pop(
        "formatting_options",
        {
            "group_by_type": False,
            "group_by_module": True,
            "group_by_package": True,
            "sort_namespaces": True,
            "sort_files": True,
            "sort_directories": True,
            "include_types": [
                NamespaceType.CLASS,
                NamespaceType.FUNCTION,
                NamespaceType.METHOD,
                NamespaceType.NESTED_CLASS,
                NamespaceType.VARIABLE,
            ],
            "name_patterns": [
                ".*",
            ],
            "exclude_name_patterns": [
                ".*",
            ],
            "show_inheritance": True,
            "show_decorators": True,
            "show_docstrings": False,
            "include_line_numbers": False,
        },
    )
    yaml_config["formatting_options"] = formatting_options

    # Update main config attributes
    for key, value in yaml_config.items():
        if hasattr(config, key):
            setattr(config, key, value)

    # Handle include_types specially
    if "include_types" in formatting_options:
        include_types = set()
        for type_str in formatting_options.pop("include_types", []):
            try:
                include_types.add(NamespaceType(type_str))
            except ValueError:
                print(f"Warning: Unknown namespace type: {type_str}")

        if include_types:
            config.formatting_options.include_types = include_types

    # Update formatting options
    for key, value in formatting_options.items():
        if hasattr(config.formatting_options, key):
            setattr(config.formatting_options, key, value)

    # Re-run validation
    config.__post_init__()

    print(f"Loaded configuration from {config_path}")


def save_config(config: ExtractorConfig, config_path: str) -> None:
    """
    Save configuration to a YAML file.

    Args:
        config: Configuration to save
        config_path: Path to save the configuration to
    """
    try:
        # Convert config to dictionary
        config_dict = config.to_dict()

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

        # Write to file
        with open(config_path, "w", encoding="utf-8") as file:
            yaml.dump(config_dict, file, default_flow_style=False, sort_keys=False)

        print(f"Configuration saved to {config_path}")
    except Exception as e:
        print(f"Error saving configuration: {e!s}")


def update_config_from_args(
    config: ExtractorConfig, args: argparse.Namespace
) -> ExtractorConfig:
    """
    Update configuration from command-line arguments.

    Args:
        config: Base configuration
        args: Command-line arguments namespace

    Returns:
        Updated configuration
    """
    # Update basic options
    if hasattr(args, "recursive") and args.recursive:
        config.recursive = args.recursive

    if hasattr(args, "include_private") and args.include_private:
        config.include_private = args.include_private

    if hasattr(args, "include_dunder") and args.include_dunder:
        config.include_dunder = args.include_dunder

    if hasattr(args, "include_docstrings") and args.include_docstrings:
        config.include_docstrings = args.include_docstrings
        config.formatting_options.show_docstrings = args.include_docstrings

    if hasattr(args, "depth") and args.depth >= 0:
        config.max_recursion_depth = args.depth

    if hasattr(args, "exclude") and args.exclude:
        config.exclude_patterns.extend(args.exclude)

    if hasattr(args, "include_vars") and args.include_vars:
        config.include_module_vars = args.include_vars

    # Update formatter and output options
    if hasattr(args, "formatter") and args.formatter:
        config.formatter_type = FormatterType(args.formatter)

    if hasattr(args, "output_format") and args.output_format:
        config.output_format = OutputFormat(args.output_format)

    # Re-run validation
    config.__post_init__()

    return config
