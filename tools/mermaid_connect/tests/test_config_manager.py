#!/usr/bin/env python3

import unittest
from pathlib import Path

from mermaid_connect.config_manager import (
    ConfigManager,
    ConfigurationError,
    StyleConfig,
)


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(__file__).parent / "test_data"
        self.config_file = self.test_dir / "config.yaml"
        self.config_manager = ConfigManager(str(self.config_file))

    def test_load_config(self):
        """Test loading configuration from file."""
        self.assertIsNotNone(self.config_manager._config)
        self.assertIn("directories", self.config_manager._config)
        self.assertIn("styles", self.config_manager._config)

    def test_get_style_config(self):
        """Test retrieving style configuration."""
        style_config = self.config_manager.get_style_config("core_processing")
        self.assertIsInstance(style_config, StyleConfig)
        self.assertEqual(len(style_config.required), 2)
        self.assertEqual(len(style_config.forbidden), 1)

    def test_invalid_style_name(self):
        """Test retrieving non-existent style configuration."""
        with self.assertRaises(ConfigurationError):
            self.config_manager.get_style_config("nonexistent_style")

    def test_get_validation_config(self):
        """Test retrieving validation configuration."""
        validation_config = self.config_manager.get_validation_config()
        self.assertTrue(validation_config["syntax"]["check_brackets"])
        self.assertTrue(validation_config["syntax"]["check_quotes"])
        self.assertEqual(validation_config["components"]["max_depth"], 10)

    def test_get_error_handling_config(self):
        """Test retrieving error handling configuration."""
        error_config = self.config_manager.get_error_handling_config()
        self.assertTrue(error_config["strict_mode"])
        self.assertEqual(error_config["max_errors"], 10)
        self.assertIn("syntax", error_config["severity_levels"]["critical"])

    def test_get_performance_config(self):
        """Test retrieving performance configuration."""
        perf_config = self.config_manager.get_performance_config()
        self.assertTrue(perf_config["parallel_processing"])
        self.assertEqual(perf_config["max_workers"], 4)
        self.assertEqual(perf_config["chunk_size"], 1000)

    def test_get_logging_config(self):
        """Test retrieving logging configuration."""
        log_config = self.config_manager.get_logging_config()
        self.assertTrue(log_config["enabled"])
        self.assertEqual(log_config["level"], "INFO")
        self.assertTrue(log_config["console"]["enabled"])

    def test_get_reporting_config(self):
        """Test retrieving reporting configuration."""
        report_config = self.config_manager.get_reporting_config()
        self.assertEqual(report_config["format"], "detailed")
        self.assertIn("summary", report_config["sections"])
        self.assertTrue(report_config["summary_stats"]["show_total"])

    def test_get_directories_config(self):
        """Test retrieving directories configuration."""
        dir_config = self.config_manager.get_directories_config()
        self.assertEqual(dir_config["base_dir"], "./test")
        self.assertEqual(dir_config["output_dir"], "./test/output")
        self.assertEqual(dir_config["temp_dir"], "./test/temp")

    def test_style_config_required_properties(self):
        """Test style config required properties."""
        style_config = self.config_manager.get_style_config("core_processing")
        self.assertIn("fill:#f9f", style_config.required)
        self.assertIn("stroke:#333", style_config.required)

    def test_style_config_forbidden_properties(self):
        """Test style config forbidden properties."""
        style_config = self.config_manager.get_style_config("core_processing")
        self.assertIn("stroke-dasharray", style_config.forbidden)

    def test_multiple_style_configs(self):
        """Test retrieving multiple style configurations."""
        core_style = self.config_manager.get_style_config("core_processing")
        component_style = self.config_manager.get_style_config("component_styles")

        self.assertNotEqual(core_style.required, component_style.required)
        self.assertNotEqual(core_style.forbidden, component_style.forbidden)

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with self.assertRaises(ConfigurationError):
            ConfigManager("nonexistent_config.yaml")

    def test_missing_required_sections(self):
        """Test handling of missing required configuration sections."""
        invalid_config = {}
        with self.assertRaises(ConfigurationError):
            self.config_manager._validate_config(invalid_config)


if __name__ == "__main__":
    unittest.main()
