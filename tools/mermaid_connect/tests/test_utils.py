#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml

from tools.mermaid_connect.config_manager import ConfigManager
from tools.mermaid_connect.utils import (
    DependencyAnalyzer,
    MermaidSyntaxValidator,
    PerformanceOptimizer,
    StyleManager,
    create_utils,
)


class TestMermaidSyntaxValidator(unittest.TestCase):
    """Test cases for MermaidSyntaxValidator class."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "config.yaml"

        config: dict[str, Any] = {
            "directories": {
                "base_dir": str(self.test_dir),
                "output_dir": str(self.test_dir / "output"),
                "temp_dir": str(self.test_dir / "temp"),
            },
            "styles": {
                "default": {
                    "required": ["style1", "style2"],
                    "forbidden": [],
                }
            },
            "validation": {
                "syntax_check": True,
                "component_depth": 5,
                "circular_dependencies": True,
                "style_validation": True,
            },
            "error_handling": {
                "strict_mode": True,
                "max_errors": 10,
                "stop_on_critical": True,
                "log_all_errors": True,
                "severity_levels": {
                    "critical": ["syntax", "dependencies"],
                    "warning": ["style", "performance"],
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
                "console": {"enabled": True, "format": "simple"},
                "file_logging": {"enabled": True, "format": "detailed"},
            },
            "reporting": {
                "format": "detailed",
                "sections": ["summary", "errors", "warnings"],
                "output_formats": ["text", "json"],
                "summary_stats": {"show_timing": True, "show_counts": True},
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

        self.config = ConfigManager(str(self.config_file))
        self.validator = MermaidSyntaxValidator()

    def test_validate_syntax_valid(self) -> None:
        """Test validation of valid Mermaid syntax."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
        """
        is_valid = self.validator.validate_syntax(content)
        self.assertTrue(is_valid)

    def test_validate_syntax_invalid(self) -> None:
        """Test validation of invalid Mermaid syntax."""
        self._extracted_from_test_validate_empty_content_3(
            """graph TD
            A["Component A"] --> B["Component B
            B --> C["Component C"]
        """
        )

    def test_validate_empty_content(self) -> None:
        """Test validation of empty content."""
        self._extracted_from_test_validate_empty_content_3("")

    # TODO Rename this here and in `test_validate_syntax_invalid` and `test_validate_empty_content`
    def _extracted_from_test_validate_empty_content_3(self, arg0):
        content = arg0
        is_valid = self.validator.validate_syntax(content)
        self.assertFalse(is_valid)


class TestStyleManager(unittest.TestCase):
    """Test cases for StyleManager class."""

    def setUp(self) -> None:
        """Set up test environment."""
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
                "forbidden": [],  # Empty list instead of specific styles
            },
            "validation": {
                "syntax_check": True,
                "component_depth": 5,
                "circular_dependencies": True,
                "style_validation": True,
            },
            "error_handling": {"max_retries": 3, "timeout": 30},
            "logging": {"level": "INFO", "file": str(self.test_dir / "test.log")},
            "reporting": {"format": "text", "detail_level": "high"},
            "performance": {"parallel": True, "max_workers": 4},
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

        self.config = ConfigManager(str(self.config_file))
        self.style_manager = StyleManager()

    def test_validate_styles_valid(self):
        """Test validation of valid styles."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
            style A fill:#f9f,stroke:#333
            style B fill:#fff
        """
        is_valid = self.style_manager.validate_styles(content)
        self.assertTrue(is_valid)

    def test_validate_styles_invalid(self):
        """Test validation of invalid styles."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
            style A stroke-dasharray:5
            style B stroke-width:2px
        """
        is_valid = self.style_manager.validate_styles(content)
        self.assertFalse(is_valid)

    def test_validate_no_styles(self):
        """Test validation of content without styles."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
        """
        is_valid = self.style_manager.validate_styles(content)
        self.assertTrue(is_valid)


class TestDependencyAnalyzer(unittest.TestCase):
    """Test cases for DependencyAnalyzer class."""

    def setUp(self):
        """Set up test environment."""
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
                "forbidden": [],  # Empty list instead of specific styles
            },
            "validation": {
                "syntax_check": True,
                "component_depth": 5,
                "circular_dependencies": True,
                "style_validation": True,
            },
            "error_handling": {"max_retries": 3, "timeout": 30},
            "logging": {"level": "INFO", "file": str(self.test_dir / "test.log")},
            "reporting": {"format": "text", "detail_level": "high"},
            "performance": {"parallel": True, "max_workers": 4},
        }

        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

        self.config = ConfigManager(str(self.config_file))
        self.analyzer = DependencyAnalyzer()

    def test_validate_dependencies_valid(self):
        """Test validation of valid dependencies."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
        """
        is_valid, errors = self.analyzer.validate_dependencies(content)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_dependencies_circular(self):
        """Test validation of circular dependencies."""
        content = """graph TD
            A["Component A"] --> B["Component B"]
            B --> C["Component C"]
            C --> A["Component A"]
        """
        is_valid, errors = self.analyzer.validate_dependencies(content)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestPerformanceOptimizer(unittest.TestCase):
    """Test cases for PerformanceOptimizer class."""

    def setUp(self):
        """Set up test environment."""
        self.optimizer = PerformanceOptimizer()

    def test_cached_operation(self):
        """Test caching of operation results."""
        # First call
        operation = lambda: "test"
        result1 = self.optimizer.cached_operation("test_key", operation)
        # Second call should return cached result
        result2 = self.optimizer.cached_operation("test_key", operation)
        self.assertEqual(result1, result2)

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # Store in cache
        operation = lambda: "test"
        self.optimizer.cached_operation("test_key", operation)
        # Invalidate cache
        self.optimizer.invalidate_cache()
        # Should recompute
        new_operation = lambda: "new_test"
        result = self.optimizer.cached_operation("test_key", new_operation)
        self.assertEqual(result, "new_test")


class TestCreateUtils(unittest.TestCase):
    """Test cases for create_utils function."""

    def test_create_utils(self):
        """Test utility creation function."""
        utils = create_utils()
        self.assertIsInstance(utils[0], MermaidSyntaxValidator)
        self.assertIsInstance(utils[1], StyleManager)
        self.assertIsInstance(utils[2], DependencyAnalyzer)
        self.assertIsInstance(utils[3], PerformanceOptimizer)


if __name__ == "__main__":
    unittest.main()
