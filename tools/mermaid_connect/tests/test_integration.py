#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

from tools.mermaid_connect.mc import DiagramValidator


class TestIntegration(unittest.TestCase):
    """Integration tests for the diagram validator."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "config.yaml"

        config: dict[str, Any] = {
            "directories": {
                "base_dir": str(self.test_dir),
                "output_dir": str(self.test_dir / "output"),
                "temp_dir": str(self.test_dir / "temp"),
            },
            "styles": {
                "core_processing": {
                    "required": ["fill:#f9f", "stroke:#333"],
                    "forbidden": ["stroke-dasharray"],
                },
                "component_styles": {
                    "required": ["fill:#fff"],
                    "forbidden": ["stroke-width:2px"],
                },
            },
            "validation": {
                "syntax": {
                    "check_brackets": True,
                    "check_quotes": True,
                },
                "components": {
                    "max_depth": 10,
                },
                "dependencies": {
                    "check_circular": True,
                },
                "styles": {
                    "validate_all": True,
                },
            },
            "error_handling": {
                "strict_mode": True,
                "max_errors": 10,
                "stop_on_critical": True,
                "log_all_errors": True,
                "severity_levels": {
                    "critical": ["syntax", "dependency"],
                    "warning": ["style"],
                },
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": str(self.test_dir / "validation.log"),
                "rotate": True,
                "max_size": "1MB",
                "backup_count": 3,
                "console": {
                    "enabled": True,
                    "color": True,
                },
                "file_logging": {
                    "enabled": True,
                    "append": True,
                },
            },
            "reporting": {
                "format": "detailed",
                "sections": ["summary", "errors", "warnings"],
                "output_formats": ["console", "file"],
                "summary_stats": {
                    "show_total": True,
                    "show_passed": True,
                    "show_failed": True,
                },
            },
            "performance": {
                "parallel_processing": True,
                "max_workers": 4,
                "chunk_size": 1000,
                "cache_enabled": True,
                "cache_ttl": 3600,
            },
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

        self.validator = DiagramValidator(str(self.config_file))

    def tearDown(self) -> None:
        """Clean up test environment after each test."""
        # Remove test files
        for file in self.test_dir.glob("*.mmd"):
            file.unlink()
        if self.test_dir.exists() and not any(self.test_dir.iterdir()):
            self.test_dir.rmdir()

    def test_component_extraction_and_validation(self) -> None:
        """Test component extraction and validation process."""
        self._extracted_from_test_style_validation_4(
            """
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
        """,
            "Component A",
        )

    def test_dependency_analysis(self) -> None:
        """Test dependency analysis in the complete workflow."""
        output_file = self._test_output(
            """
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
            C --> A["Component A"]
        """
        )
        # Verify validation results
        self.assertTrue(output_file.exists())
        self.assertIn("circular dependency", str(self.validator.report.errors))

    def test_style_validation(self) -> None:
        """Test style validation in the complete workflow."""
        self._extracted_from_test_style_validation_4(
            """
        graph TD
            A["Component A"] --> B["Component B"]
            style A fill:#f9f,stroke:#333,stroke-width:4px
        """,
            "style",
        )

    def test_error_handling(self) -> None:
        """Test error handling in the complete workflow."""
        # Test with non-existent file
        input_file = self.test_dir / "nonexistent.mmd"
        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify error handling
        self.assertIn("does not exist", str(self.validator.report.errors))

    def test_parallel_processing(self) -> None:
        """Test parallel processing in the complete workflow."""
        # Create multiple test files
        for i in range(3):
            input_file = self.test_dir / f"test{i}.mmd"
            input_file.write_text(
                f"""
            graph TD
                A{i}["Component A{i}"] --> B{i}["Component B{i}"]
            """
            )

        output_dir = self.test_dir / "output"
        self.validator.validate_diagrams(str(self.test_dir), str(output_dir))

        # Verify parallel processing results
        self.assertTrue((output_dir / "test0.mmd").exists())
        self.assertTrue((output_dir / "test1.mmd").exists())
        self.assertTrue((output_dir / "test2.mmd").exists())

    def _extracted_from_test_style_validation_4(self, arg0, arg1):
        output_file = self._test_output(arg0)
        self.assertTrue(output_file.exists())
        self.assertIn(arg1, output_file.read_text())

    def test_report_generation(self) -> None:
        """Test report generation in the complete workflow."""
        output_file = self._test_output(
            """
        graph TD
            A["Component A"] --> B["Component B"]
        """
        )
        self.validator.print_report()

    def test_end_to_end_validation(self):
        """Test complete validation workflow."""
        output_file = self._test_output(
            """
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
            style A fill:#f9f,stroke:#333,stroke-width:4px
        """
        )
        # Verify complete workflow
        self.assertTrue(output_file.exists())
        self.assertEqual(self.validator.report.num_validated, 1)
        self.assertEqual(self.validator.report.num_failed, 0)
        self.assertIn("Component A", output_file.read_text())
        self.assertIn("style", output_file.read_text())

    def _test_output(self, arg0):
        input_file = self.test_dir / "test.mmd"
        input_file.write_text(arg0)
        result = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(result))
        return result


if __name__ == "__main__":
    unittest.main()
