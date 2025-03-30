#!/usr/bin/env python3

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console


@dataclass
class DirectoryConfig:
    base_dir: str
    output_dir: str
    temp_dir: str


@dataclass
class StyleConfig:
    required: list[str]
    forbidden: list[str]


@dataclass
class ValidationConfig:
    """Configuration for validation settings."""

    syntax_check: bool = True
    component_depth: int = 5
    circular_dependencies: bool = True
    style_validation: bool = True
    components: dict[str, bool | str | int] = field(default_factory=dict)
    dependencies: dict[str, bool | int] = field(default_factory=dict)
    styles: dict[str, bool] = field(default_factory=dict)


@dataclass
class ErrorConfig:
    strict_mode: bool
    max_errors: int
    stop_on_critical: bool
    log_all_errors: bool
    severity_levels: dict[str, list[str]]


@dataclass
class LoggingConfig:
    enabled: bool
    level: str
    format: str
    file: str
    rotate: bool
    max_size: str
    backup_count: int
    console: dict[str, bool | str]
    file_logging: dict[str, bool | str]


@dataclass
class ReportingConfig:
    format: str
    sections: list[str]
    output_formats: list[str]
    summary_stats: dict[str, bool]


@dataclass
class PerformanceConfig:
    parallel_processing: bool
    max_workers: int
    chunk_size: int
    cache_enabled: bool
    cache_ttl: int


class ConfigurationError(Exception):
    """Base class for configuration-related errors."""


class ConfigManager:
    """Manages configuration loading and access for the Mermaid diagram system."""

    def __init__(self, config_path: str | None = None) -> None:
        self.console = Console()
        self._config: dict[str, Any] = {}
        self._config_path = config_path or self._get_default_config_path()
        self.load_config()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        script_dir = Path(__file__).parent
        return str(script_dir / "config.yaml")

    def load_config(self) -> None:
        """Load configuration from YAML file with validation."""
        try:
            if not os.path.exists(self._config_path):
                raise ConfigurationError(
                    f"Configuration file not found: {self._config_path}"
                )

            with open(self._config_path) as f:
                self._config = yaml.safe_load(f)

            self._validate_config(self._config)
            self._initialize_config_objects()

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing configuration file: {e}") from e
        except Exception as e:
            raise ConfigurationError(
                f"Unexpected error loading configuration: {e}"
            ) from e

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate the configuration dictionary.

        Args:
            config: The configuration dictionary to validate.

        Raises:
            ConfigurationError: If required sections are missing.
        """
        required_sections = [
            "directories",
            "styles",
            "validation",
            "error_handling",
            "logging",
            "reporting",
            "performance",
        ]
        if missing_sections := [
            section for section in required_sections if section not in config
        ]:
            raise ConfigurationError(
                f"Missing required configuration sections: {', '.join(missing_sections)}"
            )

        # Validate directory paths
        self._validate_directories()

        # Validate style definitions
        self._validate_styles()

    def _validate_directories(self) -> None:
        """Validate directory configurations."""
        dirs_config = self._config.get("directories", {})
        required_dirs = {"base_dir", "output_dir", "temp_dir"}

        if missing_dirs := required_dirs - set(dirs_config.keys()):
            raise ConfigurationError(
                f"Missing required directory configurations: {missing_dirs}"
            )

    def _validate_styles(self) -> None:
        """Validate style configurations."""
        styles_config = self._config.get("styles", {})
        for style_name, style_data in styles_config.items():
            if not isinstance(style_data, dict):
                raise ConfigurationError(
                    f"Invalid style configuration for {style_name}"
                )
            if "required" not in style_data:
                raise ConfigurationError(
                    f"Missing required properties definition for style {style_name}"
                )
            if "forbidden" not in style_data:
                raise ConfigurationError(
                    f"Missing forbidden properties definition for style {style_name}"
                )

    def _initialize_config_objects(self) -> None:
        """Initialize configuration dataclass objects."""
        try:
            self.directories = DirectoryConfig(**self._config["directories"])
            self.validation = ValidationConfig(**self._config["validation"])
            self.error_handling = ErrorConfig(**self._config["error_handling"])
            self.logging = LoggingConfig(**self._config["logging"])
            self.reporting = ReportingConfig(**self._config["reporting"])
            self.performance = PerformanceConfig(**self._config["performance"])

            # Initialize styles
            self.styles = {
                name: StyleConfig(**data)
                for name, data in self._config["styles"].items()
            }

        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration structure: {e}") from e

    def get_style(self, style_name: str) -> StyleConfig | None:
        """Get style configuration by name."""
        return self.styles.get(style_name)

    def get_validation_rule(self, rule_path: str) -> Any:
        """Get validation rule by dot-notation path."""
        try:
            current = self._config["validation"]
            for key in rule_path.split("."):
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None

    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update configuration value at runtime."""
        try:
            if section not in self._config:
                raise ConfigurationError(f"Invalid configuration section: {section}")

            # Update in-memory configuration
            if isinstance(self._config[section], dict):
                self._config[section][key] = value
            else:
                setattr(self._config[section], key, value)

            # Re-initialize configuration objects
            self._initialize_config_objects()

        except Exception as e:
            raise ConfigurationError(f"Error updating configuration: {e}") from e

    def save_config(self) -> None:
        """Save current configuration back to file."""
        try:
            with open(self._config_path, "w") as f:
                yaml.safe_dump(self._config, f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {e}") from e

    def get_full_config(self) -> dict[str, Any]:
        """Get complete configuration dictionary."""
        return self._config.copy()

    def get_style_config(self, style_name: str) -> StyleConfig:
        """Get style configuration by name.

        Args:
            style_name (str): Name of the style configuration.

        Returns:
            StyleConfig: Style configuration object.

        Raises:
            ConfigurationError: If the style configuration does not exist.
        """
        if style_name not in self._config["styles"]:
            raise ConfigurationError(f"Style configuration not found: {style_name}")
        style_data = self._config["styles"][style_name]
        return StyleConfig(
            required=style_data.get("required", []),
            forbidden=style_data.get("forbidden", []),
        )

    def get_validation_config(self) -> dict[str, Any]:
        """Get validation configuration.

        Returns:
            Dict[str, Any]: Validation configuration dictionary.
        """
        return self._config["validation"]

    def get_error_handling_config(self) -> dict[str, Any]:
        """Get error handling configuration.

        Returns:
            Dict[str, Any]: Error handling configuration dictionary.
        """
        return self._config["error_handling"]

    def get_performance_config(self) -> dict[str, Any]:
        """Get performance configuration.

        Returns:
            Dict[str, Any]: Performance configuration dictionary.
        """
        return self._config["performance"]

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging configuration.

        Returns:
            Dict[str, Any]: Logging configuration dictionary.
        """
        return self._config["logging"]

    def get_reporting_config(self) -> dict[str, Any]:
        """Get reporting configuration.

        Returns:
            Dict[str, Any]: Reporting configuration dictionary.
        """
        return self._config["reporting"]

    def get_directories_config(self) -> dict[str, Any]:
        """Get directories configuration.

        Returns:
            Dict[str, Any]: Directories configuration dictionary.
        """
        return self._config["directories"]


def get_config(config_path: str | None = None) -> ConfigManager:
    """Get or create configuration manager instance."""
    return ConfigManager(config_path)
