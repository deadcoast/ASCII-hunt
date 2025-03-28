class ConfigurationManager:
    def __init__(self):
        self.config = {}

    def load_config(self, config_path):
        """Load configuration from a file."""
        import json

        with open(config_path) as f:
            config_data = json.load(f)

        self.config.update(config_data)

    def save_config(self, config_path):
        """Save configuration to a file."""
        import json

        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self, section=None):
        """Get configuration data."""
        if section is not None:
            return self.config.get(section, {})
        return self.config

    def set_config(self, section, key, value):
        """Set a configuration value."""
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value

    def get_value(self, section, key, default=None):
        """Get a configuration value."""
        section_data = self.config.get(section, {})
        return section_data.get(key, default)
