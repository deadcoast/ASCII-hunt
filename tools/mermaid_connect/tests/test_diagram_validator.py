#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import yaml
from mermaid_connect.config_manager import ConfigManager, ConfigurationError
from mermaid_connect.diagram_validator import DiagramValidator


class TestDiagramValidator(unittest.TestCase):
    def setUp(self) -> None:
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "config.yaml"

        # Create test config file
        config: dict[str, Any] = {
            "directories": {
                "base_dir": str(self.test_dir),
                "output_dir": str(self.test_dir / "output"),
                "cache_dir": str(self.test_dir / "cache"),
            },
            "styles": {
                "core_processing": {
                    "required": ["shape=rectangle"],
                    "forbidden": ["shape=circle"],
                }
            },
            "validation": {
                "syntax_check": True,
                "component_depth": 5,
                "circular_dependencies": True,
                "style_validation": True,
                "components": {},
                "dependencies": {},
            },
            "error_handling": {
                "max_retries": 3,
                "timeout": 30,
            },
            "logging": {
                "file": str(self.test_dir / "test.log"),
                "level": "INFO",
            },
            "reporting": {
                "format": "text",
                "detail_level": "high",
            },
            "performance": {
                "parallel": True,
                "max_workers": 4,
            },
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

        self.validator = DiagramValidator(self.config_file)

        # Create test diagram files
        self.valid_diagram = self.test_dir / "valid_diagram.mmd"
        self.invalid_diagram = self.test_dir / "invalid_diagram.mmd"
        self.combined_diagram = self.test_dir / "combined_diagram.mmd"

        # Valid diagram content
        valid_content = """graph TD
    A["Component A"] --> B["Component B"]
    B["Component B"] --> C["Component C"]"""

        # Invalid diagram content (missing quotes)
        invalid_content = """graph TD
    A[Component A] --> B["Component B"]
    B["Component B"] --> C[Component C]"""

        # Combined diagram content
        combined_content = """graph TD
    A["Component A"] --> B["Component B"]
    B["Component B"] --> C["Component C"]
    D["Component D"] --> E["Component E"]"""

        # Write test files
        self.valid_diagram.write_text(valid_content)
        self.invalid_diagram.write_text(invalid_content)
        self.combined_diagram.write_text(combined_content)

    def tearDown(self) -> None:
        """Clean up test environment after each test."""
        # Remove test files
        for file in [self.valid_diagram, self.invalid_diagram, self.combined_diagram]:
            if file.exists():
                file.unlink()

        # Remove test directory if empty
        if self.test_dir.exists() and not any(self.test_dir.iterdir()):
            self.test_dir.rmdir()

    def test_initialization(self) -> None:
        """Test validator initialization."""
        self.assertIsInstance(self.validator.config, ConfigManager)
        self.assertEqual(self.validator.base_dir, str(self.test_dir))
        self.assertTrue(hasattr(self.validator, "source_files"))
        self.assertTrue(hasattr(self.validator, "report"))

    def test_get_source_files(self) -> None:
        """Test source file collection."""
        source_files = self.validator._get_source_files()
        self.assertIsInstance(source_files, list)
        self.assertEqual(len(source_files), 2)  # valid and invalid diagrams
        self.assertNotIn("combined_diagram.mmd", source_files)

    def test_read_file_valid(self) -> None:
        """Test reading a valid file."""
        content = self.validator._read_file("valid_diagram.mmd")
        self.assertIsInstance(content, str)
        self.assertIn("Component A", content)
        self.assertIn("Component B", content)

    def test_read_file_invalid(self) -> None:
        """Test reading an invalid file."""
        with self.assertRaises(ConfigurationError):
            self.validator._read_file("nonexistent.mmd")

    def test_extract_components(self) -> None:
        """Test component extraction."""
        content = """graph TD
    A["Component A"] --> B["Component B"]"""
        components = self.validator._extract_components(content)
        self.assertIsInstance(components, set)
        self.assertEqual(len(components), 2)
        self.assertIn('A["Component A"]', components)
        self.assertIn('B["Component B"]', components)

    def test_validate_module_valid(self) -> None:
        """Test validation of a valid module."""
        combined_content = self.validator._read_file("combined_diagram.mmd")
        is_valid, errors = self.validator.validate_module(
            "valid_diagram.mmd", combined_content
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_module_invalid(self) -> None:
        """Test validation of an invalid module."""
        combined_content = self.validator._read_file("combined_diagram.mmd")
        is_valid, errors = self.validator.validate_module(
            "invalid_diagram.mmd", combined_content
        )
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_all(self) -> None:
        """Test complete validation process."""
        with patch("rich.console.Console.print") as mock_print:
            self.validator.validate_all()
            mock_print.assert_called()

    def test_error_handling(self) -> None:
        """Test error handling in validation process."""
        # Test with invalid configuration
        with patch("config_manager.ConfigManager") as mock_config:
            mock_config.side_effect = ConfigurationError("Test error")
            with self.assertRaises(ConfigurationError):
                DiagramValidator(str(self.test_dir))

    def test_parallel_processing(self) -> None:
        """Test parallel processing of validations."""
        # Mock the performance optimizer
        mock_optimizer = MagicMock()
        self.validator.performance_optimizer = mock_optimizer

        # Call validate_all to trigger parallel processing
        self.validator.validate_all()

        # Verify that process_in_parallel was called
        mock_optimizer.process_in_parallel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
