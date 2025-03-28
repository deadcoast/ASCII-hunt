#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

import yaml
from mermaid_connect.diagram_validator import DiagramValidator


class TestIntegration(unittest.TestCase):
    """Integration tests for the diagram validator."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "config.yaml"

        config = {
            "directories": {
                "base_dir": str(self.test_dir),
                "output_dir": str(self.test_dir / "output"),
                "temp_dir": str(self.test_dir / "temp"),
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

        self.validator = DiagramValidator(str(self.config_file))

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove test files
        for file in self.test_dir.glob("*.mmd"):
            file.unlink()
        if self.test_dir.exists() and not any(self.test_dir.iterdir()):
            self.test_dir.rmdir()

    def test_component_extraction_and_validation(self):
        """Test component extraction and validation process."""
        # Create test files
        input_file = self.test_dir / "test.mmd"
        input_file.write_text("""
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
        """)

        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify validation results
        self.assertTrue(output_file.exists())
        self.assertIn("Component A", output_file.read_text())

    def test_dependency_analysis(self):
        """Test dependency analysis in the complete workflow."""
        # Create test files
        input_file = self.test_dir / "test.mmd"
        input_file.write_text("""
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
            C --> A["Component A"]
        """)

        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify validation results
        self.assertTrue(output_file.exists())
        self.assertIn("circular dependency", str(self.validator.report.errors))

    def test_style_validation(self):
        """Test style validation in the complete workflow."""
        # Create test files
        input_file = self.test_dir / "test.mmd"
        input_file.write_text("""
        graph TD
            A["Component A"] --> B["Component B"]
            style A fill:#f9f,stroke:#333,stroke-width:4px
        """)

        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify validation results
        self.assertTrue(output_file.exists())
        self.assertIn("style", output_file.read_text())

    def test_error_handling(self):
        """Test error handling in the complete workflow."""
        # Test with non-existent file
        input_file = self.test_dir / "nonexistent.mmd"
        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify error handling
        self.assertIn("does not exist", str(self.validator.report.errors))

    def test_parallel_processing(self):
        """Test parallel processing in the complete workflow."""
        # Create multiple test files
        for i in range(3):
            input_file = self.test_dir / f"test{i}.mmd"
            input_file.write_text(f"""
            graph TD
                A{i}["Component A{i}"] --> B{i}["Component B{i}"]
            """)

        output_dir = self.test_dir / "output"
        self.validator.validate_diagrams(str(self.test_dir), str(output_dir))

        # Verify parallel processing results
        self.assertTrue((output_dir / "test0.mmd").exists())
        self.assertTrue((output_dir / "test1.mmd").exists())
        self.assertTrue((output_dir / "test2.mmd").exists())

    def test_report_generation(self):
        """Test report generation in the complete workflow."""
        # Create test file
        input_file = self.test_dir / "test.mmd"
        input_file.write_text("""
        graph TD
            A["Component A"] --> B["Component B"]
        """)

        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))
        self.validator.print_report()

        # Verify report contents
        self.assertEqual(self.validator.report.num_validated, 1)
        self.assertEqual(self.validator.report.num_failed, 0)

    def test_end_to_end_validation(self):
        """Test complete validation workflow."""
        # Create test files
        input_file = self.test_dir / "test.mmd"
        input_file.write_text("""
        graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
            style A fill:#f9f,stroke:#333,stroke-width:4px
        """)

        output_file = self.test_dir / "output.mmd"
        self.validator.validate_diagram(str(input_file), str(output_file))

        # Verify complete workflow
        self.assertTrue(output_file.exists())
        self.assertEqual(self.validator.report.num_validated, 1)
        self.assertEqual(self.validator.report.num_failed, 0)
        self.assertIn("Component A", output_file.read_text())
        self.assertIn("style", output_file.read_text())


if __name__ == "__main__":
    unittest.main()
