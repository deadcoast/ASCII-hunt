from plugins.plugin_base import Plugin
from src.adapters.tkinter_adapter import create_tkinter_adapter


class TkinterPlugin(Plugin):
    def __init__(self):
        super().__init__("tkinter", "Tkinter UI Framework", "1.0")
        self._setup()

    def _setup(self):
        # Register supported component types
        for component_type in [
            "Window",
            "Button",
            "Label",
            "TextField",
            "Checkbox",
            "RadioButton",
            "Panel",
        ]:
            self.register_component_type(component_type)

        # Create and register the Tkinter code generator
        generator = create_tkinter_adapter()
        self.register_generator("generator", generator)


def create_plugin():
    """Factory function to create the Tkinter plugin."""
    return TkinterPlugin()
