#!/usr/bin/env python3

import os
import re
from pathlib import Path

from rich.console import Console

from mermaid_connect.config_manager import ConfigManager, ConfigurationError
from mermaid_connect.utils import (
    DependencyAnalyzer,
    MermaidSyntaxValidator,
    PerformanceOptimizer,
    StyleManager,
    create_utils,
)
from mermaid_connect.validation_report import ValidationReport


class DiagramValidator:
    """Validates Mermaid diagrams against configuration rules."""

    def __init__(self, config_path: str | Path):
        """Initialize the validator with configuration.

        Args:
            config_path: Path to the configuration file.

        Raises:
            ConfigurationError: If initialization fails.
        """
        try:
            self.config_path = Path(config_path)
            self.config = ConfigManager(self.config_path)
            self.base_dir = Path(self.config.directories.base_dir)
            self.output_dir = Path(self.config.directories.output_dir)
            self.temp_dir = Path(self.config.directories.temp_dir)
            self.console = Console()
            self.report = ValidationReport(self.config)
            self.utils = create_utils(self.config)
            self.syntax_validator = MermaidSyntaxValidator()
            self.style_manager = StyleManager()
            self.dependency_analyzer = DependencyAnalyzer()
            self.performance_optimizer = PerformanceOptimizer()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize validator: {e}")

    def _get_source_files(self) -> list[Path]:
        """Get all source files in the base directory.

        Returns:
            List of paths to source files.
        """
        return list(self.base_dir.glob("**/*.mmd"))

    def _read_file(self, file_path: str | Path) -> str:
        """Read the contents of a file.

        Args:
            file_path: Path to the file.

        Returns:
            Contents of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text()

    def _extract_components(self, content: str) -> list[str]:
        """Extract components from diagram content.

        Args:
            content: Diagram content.

        Returns:
            List of component names.
        """
        # Simple implementation - extract node names from graph definition
        components = []
        for line in content.split("\n"):
            if "-->" in line or "--" in line:
                parts = line.split("-->") if "-->" in line else line.split("--")
                components.extend([p.strip() for p in parts])
        return list(set(components))

    def validate_module(self, file_path: str | Path) -> ValidationReport:
        """Validate a single module.

        Args:
            file_path: Path to the module file.

        Returns:
            ValidationReport for the module.
        """
        report = ValidationReport()
        try:
            content = self._read_file(file_path)
            report.add_input(f"Processing file: {file_path}")

            # Syntax validation
            syntax_valid = self.syntax_validator.validate_syntax(content)
            report.add_validation(
                f"Syntax validation: {'passed' if syntax_valid else 'failed'}"
            )

            # Style validation
            style_valid = self.style_manager.validate_styles(content)
            report.add_validation(
                f"Style validation: {'passed' if style_valid else 'failed'}"
            )

            # Component extraction and validation
            components = self._extract_components(content)
            report.add_output(f"Found {len(components)} components")

            # Dependency analysis
            deps_valid, errors = self.dependency_analyzer.validate_dependencies(
                components
            )
            for error in errors:
                report.add_error(error)

            report.add_validation(
                f"Dependency validation: {'passed' if deps_valid else 'failed'}"
            )

        except Exception as e:
            report.add_error(str(e))

        return report

    def validate_all(self) -> list[ValidationReport]:
        """Validate all diagram files.

        Returns:
            List of validation reports.
        """
        reports = []
        files = self._get_source_files()

        for file_path in files:
            try:
                report = self.validate_module(file_path)
                reports.append(report)

            except Exception as e:
                report = ValidationReport()
                report.add_input(str(file_path))
                report.add_error(str(e))
                reports.append(report)

        return reports

    def validate_diagram(self, input_path: str, output_path: str) -> bool:
        """
        Validate a single diagram file.

        Args:
            input_path: Path to input diagram file
            output_path: Path to output diagram file

        Returns:
            bool: True if validation passed, False otherwise
        """
        try:
            # Add to report
            self.report.add_input(input_path)
            self.report.add_output(output_path)

            # Validate paths
            if not os.path.exists(input_path):
                self.report.add_error(input_path, "Input file does not exist")
                return False

            # Read input file
            with open(input_path) as f:
                content = f.read()

            # Validate content
            if not content.strip():
                self.report.add_error(input_path, "Input file is empty")
                return False

            # Check for mermaid syntax
            if not re.search(r"```mermaid", content):
                self.report.add_error(input_path, "No mermaid syntax block found")
                return False

            # Extract mermaid diagram
            match = re.search(r"```mermaid\n(.*?)```", content, re.DOTALL)
            if not match:
                self.report.add_error(input_path, "Could not extract mermaid diagram")
                return False

            diagram = match.group(1)

            # Validate diagram
            is_valid = self.utils.validate_diagram(diagram)
            if not is_valid:
                self.report.add_error(input_path, "Invalid mermaid syntax")
                return False

            # Write output
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(diagram)

            # Add validation result
            self.report.add_validation(input_path, output_path, True)
            return True

        except Exception as e:
            self.report.add_error(input_path, f"Validation error: {e}")
            self.report.add_validation(input_path, output_path, False)
            return False

    def validate_diagrams(
        self, input_dir: str, output_dir: str, pattern: str = "*.md"
    ) -> None:
        """
        Validate all diagrams in a directory.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files
            pattern: Glob pattern for finding files
        """
        try:
            # Validate directories
            if not os.path.isdir(input_dir):
                raise ValueError(f"Input directory does not exist: {input_dir}")

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Find all files matching pattern
            for root, _, files in os.walk(input_dir):
                for file in files:
                    if not re.match(pattern.replace("*", ".*"), file):
                        continue

                    # Get paths
                    input_path = os.path.join(root, file)
                    rel_path = os.path.relpath(input_path, input_dir)
                    output_path = os.path.join(output_dir, rel_path)

                    # Validate diagram
                    self.validate_diagram(input_path, output_path)

        except Exception as e:
            self.console.print(f"[red]Error validating diagrams: {e}")

    def print_report(self) -> None:
        """Print validation report."""
        try:
            self.report.print_inputs()
            self.report.print_outputs()
            self.report.print_validations()
            self.report.print_report()
        except Exception as e:
            self.console.print(f"[red]Error printing report: {e}")


def main():
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
