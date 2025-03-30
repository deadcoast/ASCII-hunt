from src.interface.adapters.tkinter_adapter import create_tkinter_adapter
from src.utils.plugins.plugin import Plugin


class TkinterPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__("tkinter", "Tkinter UI Framework", "1.0")
        self._setup()

    def _setup(self) -> None:
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


def create_plugin() -> TkinterPlugin:
    """Factory function to create the Tkinter plugin."""
    return TkinterPlugin()
