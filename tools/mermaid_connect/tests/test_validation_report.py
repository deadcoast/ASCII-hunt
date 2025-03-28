#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from mermaid_connect.config_manager import ConfigManager
from mermaid_connect.validation_report import ValidationReport


class TestValidationReport(unittest.TestCase):
    """Test cases for ValidationReport class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "config.yaml"

        config = {
            "directories": {
                "base_dir": str(self.test_dir),
                "output_dir": str(self.test_dir / "output"),
            },
            "styles": {
                "required": ["style1", "style2"],
                "forbidden": ["style3", "style4"],
            },
            "validation": {"syntax": True, "dependencies": True},
            "error_handling": {"strict_mode": True, "ignore_warnings": False},
            "logging": {"level": "INFO", "file": str(self.test_dir / "validation.log")},
            "reporting": {
                "format": "detailed",
                "output": str(self.test_dir / "report.txt"),
            },
            "performance": {"parallel_processing": True, "cache_results": True},
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

        self.config = ConfigManager(str(self.config_file))
        self.report = ValidationReport()

    def test_initialization(self):
        """Test report initialization."""
        self.assertEqual(self.report.num_validated, 0)
        self.assertEqual(self.report.num_failed, 0)
        self.assertEqual(len(self.report.errors), 0)
        self.assertEqual(len(self.report.inputs), 0)
        self.assertEqual(len(self.report.outputs), 0)
        self.assertEqual(len(self.report.validations), 0)

    def test_add_error(self):
        """Test error recording."""
        error = "Test error"
        self.report.add_error(error)
        self.assertIn(error, self.report.errors)
        self.assertEqual(self.report.num_failed, 1)

    def test_add_input(self):
        """Test input recording."""
        input_path = "test_input.mmd"
        self.report.add_input(input_path)
        self.assertIn(input_path, self.report.inputs)

    def test_add_output(self):
        """Test output recording."""
        output_path = "test_output.mmd"
        self.report.add_output(output_path)
        self.assertIn(output_path, self.report.outputs)

    def test_add_validation(self):
        """Test validation recording."""
        validation = "Test validation"
        self.report.add_validation(validation)
        self.assertIn(validation, self.report.validations)
        self.assertEqual(self.report.num_validated, 1)

    def test_print_header(self):
        """Test header printing."""
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_header()
            mock_print.assert_called()

    def test_print_separator(self):
        """Test separator printing."""
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_separator()
            mock_print.assert_called()

    def test_print_inputs(self):
        """Test input section printing."""
        self.report.add_input("test.mmd")
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_inputs()
            mock_print.assert_called()

    def test_print_outputs(self):
        """Test output section printing."""
        self.report.add_output("test_output.mmd")
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_outputs()
            mock_print.assert_called()

    def test_print_validations(self):
        """Test validation section printing."""
        self.report.add_validation("Test validation")
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_validations()
            mock_print.assert_called()

    def test_print_report(self):
        """Test complete report printing."""
        self.report.add_input("test.mmd")
        self.report.add_output("test_output.mmd")
        self.report.add_validation("Test validation")
        self.report.add_error("Test error")
        with patch("rich.console.Console.print") as mock_print:
            self.report.print_report()
            self.assertGreater(mock_print.call_count, 4)

    def test_error_handling(self):
        """Test error handling in report methods."""
        with self.assertRaises(TypeError):
            self.report.add_error("")
        with self.assertRaises(TypeError):
            self.report.add_input("")
        with self.assertRaises(TypeError):
            self.report.add_output("")
        with self.assertRaises(TypeError):
            self.report.add_validation("")


if __name__ == "__main__":
    unittest.main()
