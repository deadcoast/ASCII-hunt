#!/usr/bin/env python3

import os
import pathlib
import re
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Union

from config_manager import ConfigManager, ConfigurationError
from rich.console import Console

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Define valid configuration value types
ConfigValue = Union[bool, int, float, str, list[str], dict[str, Any]]


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""

    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    cache_size: int = 1000

    def __getitem__(self, key: str) -> ConfigValue:
        """Make the class subscriptable.

        Returns:
            ConfigValue: The value for the given key, restricted to valid configuration types.
        """
        return getattr(self, key)


class MermaidSyntaxValidator:
    """Validates Mermaid diagram syntax."""

    def __init__(self) -> None:
        """Initialize the validator."""

    def validate_syntax(self, content: str) -> tuple[bool, list[str]]:
        """Validate diagram syntax."""
        errors = []
        is_valid = content.strip().startswith("graph")
        if not is_valid:
            errors.append("Diagram must start with 'graph' keyword")
        return is_valid, errors


class StyleManager:
    """Manages and validates diagram styles."""

    def __init__(self) -> None:
        """Initialize the style manager."""

    def validate_styles(self, content: str) -> tuple[bool, list[str]]:
        """Validate diagram styles."""
        # Simple implementation - always return True for now
        return True, []


class DependencyAnalyzer:
    """Analyzes dependencies between diagram components."""

    def __init__(self) -> None:
        """Initialize the dependency analyzer."""
        self.dependencies: dict[str, set[str]] = {}

    def build_dependency_graph(self, content: str) -> None:
        """Build dependency graph from diagram content."""
        # Implementation to be added

    def validate_dependencies(self) -> tuple[bool, list[str]]:
        """Validate dependencies between components."""
        # Simple implementation - no circular dependencies check for now
        return True, []


class PerformanceOptimizer(Generic[K, V]):
    """Optimizes diagram processing performance."""

    def __init__(self) -> None:
        """Initialize the performance optimizer."""
        self._cache: dict[tuple[str, tuple[K, ...]], V] = {}

    def cached_operation(self, operation: Callable[..., V], *args: K) -> V:
        """Cache and return operation results."""
        key = (operation.__name__, args)
        if key not in self._cache:
            self._cache[key] = operation(*args)
        return self._cache[key]

    def process_in_parallel(
        self, items: list[K], operation: Callable[[K], None]
    ) -> None:
        """Process items in parallel if enabled."""
        # Simple sequential implementation for now
        for item in items:
            operation(item)

    def invalidate_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()


def create_utils(
    config: ConfigManager | None = None,
) -> tuple[
    MermaidSyntaxValidator,
    StyleManager,
    DependencyAnalyzer,
    PerformanceOptimizer[str, set[str]],
]:
    """Create utility class instances."""
    return (
        MermaidSyntaxValidator(),
        StyleManager(),
        DependencyAnalyzer(),
        PerformanceOptimizer[str, set[str]](),
    )


class ValidationReport:
    """Stores validation results and formats them according to design spec."""

    def __init__(self, config: ConfigManager) -> None:
        """Initialize the validation report."""
        self.config = config
        self.console = Console()
        self.inputs: list[str] = []
        self.outputs: list[str] = []
        self.validations: list[tuple[str, str, bool]] = []
        self.num_validated = 0
        self.num_failed = 0
        self.null_modules: list[str] = []
        self.errors: dict[str, list[str]] = {}
        # Get terminal width for dynamic separator
        self.term_width = shutil.get_terminal_size().columns
        self.SEPARATOR = f"<:{'-' * (self.term_width - 4)}:>"

    def add_error(self, module: str, error: str) -> None:
        """Add an error message for a module."""
        if module not in self.errors:
            self.errors[module] = []
        self.errors[module].append(error)

    def print_header(self, title: str) -> None:
        """Print section header with ASCII border."""
        width = len(title) + 4  # Add 4 for "# " and " *"
        border = "# " + "-" * (width - 2)

        self.console.print("")
        self.console.print(border)
        self.console.print(f"# {title} *")
        self.console.print(border)
        self.console.print("")

    def print_separator(self) -> None:
        """Print dynamic separator that adjusts to terminal width."""
        self.console.print("")
        self.console.print(self.SEPARATOR)
        self.console.print("")

    def add_input(self, module: str) -> None:
        """Add input module."""
        self.inputs.append(module)

    def add_output(self, module: str) -> None:
        """Add output module."""
        self.outputs.append(module)

    def add_validation(
        self, input_module: str, output_module: str, is_valid: bool
    ) -> None:
        """Add validation result."""
        self.validations.append((input_module, output_module, is_valid))
        if is_valid:
            self.num_validated += 1
        else:
            self.num_failed += 1
            self.null_modules.append(input_module)

    def print_inputs(self) -> None:
        """Print sys.INPUT section."""
        self.print_header("> sys.INPUT[IN]")
        for module in sorted(self.inputs):
            self.console.print(f"  > sys.[IN]: {module}")
        self.print_separator()

    def print_outputs(self) -> None:
        """Print sys.OUTPUT section."""
        self.print_header("> sys.OUTPUT[OUT]")
        for module in sorted(self.outputs):
            self.console.print(f"  > sys.[OUT]: {module}")
        self.print_separator()

    def print_validations(self) -> None:
        """Print sys.VALIDATION section."""
        self.print_header("> sys.VALIDATION")
        for input_mod, output_mod, is_valid in sorted(self.validations):
            status = "✅" if is_valid else "❌"
            result = "[VALIDATED]" if is_valid else "[--- NULL ---]"
            output = output_mod if is_valid else "--- NULL ---"
            self.console.print(
                f"  > sys.[IN]: {input_mod} | [OUT]: {output} {status} -> {result}"
            )
        self.print_separator()

    def print_report(self) -> None:
        """Print sys.REPORTS section."""
        self.print_header("> sys.REPORTS")
        self.console.print(f"  > sys.[✅]: {self.num_validated}")
        self.console.print(f"  > sys.[❌]: {self.num_failed}")
        self.console.print("")

        if self.errors:
            self.console.print("  > sys.report: init == [---ERRORS---]")
            self.console.print("")
            for module, error_list in sorted(self.errors.items()):
                for error in error_list:
                    self.console.print(f"    {module}: {error}")
            self.console.print("")

        self.console.print("  > sys.report: init == [---NULL OUTPUTS---]")
        self.console.print("")
        for module in sorted(self.null_modules):
            self.console.print(f"    {module}")
        self.print_separator()


class DiagramValidator:
    """Validates diagram files and their contents."""

    def __init__(self, base_dir: str) -> None:
        """Initialize the validator."""
        try:
            self.config = ConfigManager()
            self.base_dir = base_dir
            self.source_files = self._get_source_files()
            self.report = ValidationReport(self.config)

            # Initialize utilities
            (
                self.syntax_validator,
                self.style_manager,
                self.dependency_analyzer,
                self.performance_optimizer,
            ) = create_utils()

        except Exception as e:
            raise ConfigurationError(f"Initialization error: {e!s}") from e

    def _get_source_files(self) -> list[str]:
        """Get all .mmd files except combined_diagram.mmd."""
        try:
            return [
                f
                for f in os.listdir(self.base_dir)
                if f.endswith(".mmd") and f != "combined_diagram.mmd"
            ]
        except OSError as e:
            raise ConfigurationError(
                f"Error accessing directory {self.base_dir}: {e!s}"
            ) from e

    def _read_file(self, filename: str) -> str:
        """Read file content."""
        try:
            file_path = os.path.join(self.base_dir, filename)
            if not os.path.isfile(file_path):
                raise ConfigurationError(f"File not found: {file_path}")

            content = pathlib.Path(file_path).read_text()
            # Validate syntax using the utility
            is_valid, errors = self.syntax_validator.validate_syntax(content)
            if not is_valid:
                raise ConfigurationError(f"Syntax errors in {filename}: {errors}")

            return content
        except OSError as e:
            raise ConfigurationError(f"Error reading file {filename}: {e!s}") from e

    def validate_module(
        self, module_name: str, combined_content: str
    ) -> tuple[bool, list[str]]:
        """Validate a single module."""
        try:
            errors: list[str] = []
            module_content = self._read_file(module_name)

            # Extract components
            components = self.performance_optimizer.cached_operation(
                self._extract_components, module_content
            )

            # Record input components
            for comp in components:
                self.report.add_input(f"{module_name}:{comp}")

            # Validate components in combined content
            for comp in components:
                if comp in combined_content:
                    self.report.add_output(f"{module_name}:{comp}")
                    self.report.add_validation(
                        f"{module_name}:{comp}", f"{module_name}:{comp}", True
                    )
                else:
                    errors.append(f"Missing component in combined: {comp}")
                    self.report.add_validation(f"{module_name}:{comp}", "NULL", False)

            return not errors, errors

        except Exception as e:
            self.report.add_error(module_name, str(e))
            return False, [str(e)]

    def _extract_components(self, content: str) -> set[str]:
        """Extract component definitions."""
        try:
            components = set()
            for line in content.split("\n"):
                if match := re.match(r'^(\w+)\["([^"]+)"', line):
                    components.add(f'{match[1]}["{match[2]}"]')
            return components
        except Exception as e:
            raise ConfigurationError(f"Error extracting components: {e!s}") from e

    def validate_all(self) -> None:
        """Validate all source modules."""
        try:
            combined_content = self._read_file("combined_diagram.mmd")

            def validate_module_wrapper(module: str) -> None:
                try:
                    self.validate_module(module, combined_content)
                except Exception as e:
                    self.report.add_error(module, f"Module validation failed: {e!s}")

            # Process modules
            self.performance_optimizer.process_in_parallel(
                self.source_files, validate_module_wrapper
            )

            # Generate report
            self.report.print_inputs()
            self.report.print_outputs()
            self.report.print_validations()
            self.report.print_report()

        except Exception as e:
            self.report.console.print(f"[red]Error during validation: {e!s}")


def main() -> None:
    """Main entry point."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        validator = DiagramValidator(base_dir)
        validator.validate_all()
    except Exception as e:
        console = Console()
        console.print(f"[red]Fatal error: {e!s}")
        raise


if __name__ == "__main__":
    main()
