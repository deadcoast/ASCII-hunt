"""Plugin Manager Module."""

import importlib
import importlib.util
import logging
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Callable
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

# Setup logger
logger = logging.getLogger(__name__)

# Project Imports moved here
from managers.code_generator import CodeGenerator
from managers.dsl_code_generator import DSLCodeGenerator, DslCodeGenerator
from managers.python_tkinter_generator import PythonTkinterGenerator
from src.core.components.abstract_component import AbstractComponent
from src.engine.modeling.component_model_representation import ComponentModel
from src.processing.transform.component_overlay_manager import ComponentOverlayManager
from src.utils.cache_manager import CacheManager
from src.utils.helpers.functional_relationship_manager import (
    FunctionalRelationshipManager,
)
from src.utils.helpers.layout_management import LayoutManager

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec


# Define ExtensionPoint class before PluginManager
class ExtensionPoint(ABC):
    """Abstract base class for defining extension points."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of the extension point."""
        raise NotImplementedError


class PluginManager:
    """Manages plugin discovery, registration, and access."""

    components: list[Any]
    selected_component: Any | None
    highlight_colors: dict[str, str]
    grid_widget: Any | None
    layout_handlers: dict[str, Any]
    relationship_patterns: list[Any]
    mapping_source: dict[str, Any]
    layout_manager: LayoutManager
    functional_relationship_manager: FunctionalRelationshipManager
    cache_manager: CacheManager
    component_overlay_manager: ComponentOverlayManager
    abstract_component: AbstractComponent

    # Additional template attributes
    checkbutton_template: str
    radiobutton_template: str
    listbox_template: str
    canvas_template: str
    frame_template: str
    menu_template: str
    scrollbar_template: str
    scale_template: str
    spinbox_template: str
    treeview_template: str
    toplevel_template: str
    message_template: str
    labelframe_template: str

    # Layout handlers
    default_layout_handler: Callable[[], None]
    grid_layout_handler: Callable[[], None]
    flex_layout_handler: Callable[[], None]
    absolute_layout_handler: Callable[[], None]
    relative_layout_handler: Callable[[], None]
    sticky_layout_handler: Callable[[], None]
    pack_layout_handler: Callable[[], None]
    place_layout_handler: Callable[[], None]

    # Relationship patterns
    parent_child_pattern: Callable[[], None]
    sibling_pattern: Callable[[], None]
    ancestor_pattern: Callable[[], None]
    descendant_pattern: Callable[[], None]

    # Templates
    window_template: str
    button_template: str
    label_template: str
    entry_template: str
    text_template: str
    default_template: str

    def __init__(self) -> None:
        """Initialize the PluginManager.

        The PluginManager is responsible for managing the plugins, which provide
        functionality to the system. It keeps track of the plugins and provides
        an interface to register and retrieve plugins.
        """
        # Initialize instance attributes
        self.components = []
        self.selected_component = None
        self.highlight_colors = {
            "selected": "#ff0000",
            "hover": "#00ff00",
            "active": "#0000ff",
        }
        self.grid_widget = None
        self.layout_handlers = {}
        self.relationship_patterns = []
        self.mapping_source = {}

        # Initialize managers
        self.layout_manager = LayoutManager()
        self.functional_relationship_manager = FunctionalRelationshipManager()
        self.cache_manager = CacheManager(max_size=100)
        self.component_overlay_manager = ComponentOverlayManager(
            grid_widget=self.grid_widget
        )
        self.abstract_component = AbstractComponent(
            component_id="default_id", component_type="default_type"
        )

        # Initialize layout handlers
        self.default_layout_handler = lambda: None
        self.grid_layout_handler = lambda: None
        self.flex_layout_handler = lambda: None
        self.absolute_layout_handler = lambda: None
        self.relative_layout_handler = lambda: None
        self.sticky_layout_handler = lambda: None
        self.pack_layout_handler = lambda: None
        self.place_layout_handler = lambda: None

        # Initialize relationship patterns
        self.parent_child_pattern = lambda: None
        self.sibling_pattern = lambda: None
        self.ancestor_pattern = lambda: None
        self.descendant_pattern = lambda: None

        # Initialize template attributes
        self.window_template = """
        def create_window(self, title: str, width: int, height: int) -> Any:
            window = tk.Tk()
            window.title(title)
            window.geometry(f"{width}x{height}")
            return window
        """

        self.button_template = """
        def create_button(
            self, parent: Any, text: str, command: Callable[[], None]
        ) -> Any:
            return tk.Button(parent, text=text, command=command)
        """

        self.label_template = """
        def create_label(self, parent: Any, text: str) -> Any:
            return tk.Label(parent, text=text)
        """

        self.entry_template = """
        def create_entry(self, parent: Any) -> Any:
            return tk.Entry(parent)
        """

        self.text_template = """
        def create_text(self, parent: Any) -> Any:
            return tk.Text(parent)
        """

        self.default_template = """
        def create_default(self, parent: Any) -> Any:
            return tk.Frame(parent)
        """

        # Initialize additional templates
        self.checkbutton_template = """
        def create_checkbutton(self, parent: Any, text: str, variable: Any) -> Any:
            return tk.Checkbutton(parent, text=text, variable=variable)
        """

        self.radiobutton_template = """
        def create_radiobutton(
            self, parent: Any, text: str, variable: Any, value: Any
        ) -> Any:
            return tk.Radiobutton(
                parent, text=text, variable=variable, value=value
            )
        """

        self.listbox_template = """
        def create_listbox(self, parent: Any) -> Any:
            return tk.Listbox(parent)
        """

        self.canvas_template = """
        def create_canvas(self, parent: Any, width: int, height: int) -> Any:
            return tk.Canvas(parent, width=width, height=height)
        """

        self.frame_template = """
        def create_frame(self, parent: Any) -> Any:
            return tk.Frame(parent)
        """

        self.menu_template = """
        def create_menu(self, parent: Any) -> Any:
            return tk.Menu(parent)
        """

        self.scrollbar_template = """
        def create_scrollbar(self, parent: Any, orient: str) -> Any:
            return tk.Scrollbar(parent, orient=orient)
        """

        self.scale_template = """
        def create_scale(
            self, parent: Any, from_: float, to: float, orient: str
        ) -> Any:
            return tk.Scale(parent, from_=from_, to=to, orient=orient)
        """

        self.spinbox_template = """
        def create_spinbox(self, parent: Any, from_: float, to: float) -> Any:
            return tk.Spinbox(parent, from_=from_, to=to)
        """

        self.treeview_template = """
        def create_treeview(self, parent: Any) -> Any:
            return ttk.Treeview(parent)
        """

        self.toplevel_template = """
        def create_toplevel(self, parent: Any) -> Any:
            return tk.Toplevel(parent)
        """

        self.message_template = """
        def create_message(self, parent: Any, text: str) -> Any:
            return tk.Message(parent, text=text)
        """

        self.labelframe_template = """
        def create_labelframe(self, parent: Any, text: str) -> Any:
            return tk.LabelFrame(parent, text=text)
        """

        # Initialize plugins dictionary
        self.plugins: dict[str, Any] = {
            "python_tkinter": PythonTkinterGenerator(
                template_registry={
                    "Window": self.window_template,
                    "Button": self.button_template,
                    "Label": self.label_template,
                    "Entry": self.entry_template,
                    "Text": self.text_template,
                    "Checkbutton": self.checkbutton_template,
                    "Radiobutton": self.radiobutton_template,
                    "Listbox": self.listbox_template,
                    "Canvas": self.canvas_template,
                    "Frame": self.frame_template,
                    "Menu": self.menu_template,
                    "Scrollbar": self.scrollbar_template,
                    "Scale": self.scale_template,
                    "Spinbox": self.spinbox_template,
                    "Treeview": self.treeview_template,
                    "Toplevel": self.toplevel_template,
                    "Message": self.message_template,
                    "LabelFrame": self.labelframe_template,
                },
                default_template=self.default_template,
            ),
            "hunt": DslCodeGenerator(
                template_registry={
                    "Window": self.window_template,
                    "Button": self.button_template,
                    "Label": self.label_template,
                    "Entry": self.entry_template,
                    "Text": self.text_template,
                },
                default_template=self.default_template,
            ),
            "dsl": DSLCodeGenerator(
                mapping_source=self.mapping_source,
            ),
            "code_generator": CodeGenerator(
                template_registry={
                    "Window": self.window_template,
                    "Button": self.button_template,
                    "Label": self.label_template,
                    "Entry": self.entry_template,
                    "Text": self.text_template,
                },
                default_template=self.default_template,
            ),
            "layout_manager": self.layout_manager,
            "functional_relationship_manager": self.functional_relationship_manager,
            "cache_manager": self.cache_manager,
            "component_overlay_manager": self.component_overlay_manager,
            "component_model": ComponentModel(),
            "abstract_component": self.abstract_component,
        }
        self.extension_points: dict[str, ExtensionPoint] = {}
        self.extensions: dict[str, dict[str, Any]] = {}

    def register_plugin(self, plugin_name: str, plugin: Any) -> None:
        """Register a plugin."""
        self.plugins[plugin_name] = plugin
        self.extension_points[plugin_name] = plugin.get_extensions(
            self.extension_points
        )

        # Register plugin with extension points
        for ext_point, ext_impl in plugin.get_extensions(self.extension_points).items():
            self.register_extension(ext_point, plugin_name, ext_impl)

    def get_plugins(self) -> dict[str, Any]:
        """Get all registered plugins."""
        return self.plugins

    def get_plugin(self, plugin_name: str) -> Any | None:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)

    def get_extension_points(self) -> dict[str, ExtensionPoint]:
        """Get all registered extension points."""
        return self.extension_points

    def get_extension_point(self, ext_point_name: str) -> ExtensionPoint | None:
        """Get an extension point by name."""
        return self.extension_points.get(ext_point_name)

    def get_extensions(self, ext_point_name: str) -> dict[str, Any]:
        """Get all extensions for a specific extension point."""
        return self.extensions.get(ext_point_name, {})

    def register_extension_point(
        self, ext_point_name: str, ext_point: ExtensionPoint
    ) -> None:
        """Register an extension point."""
        if not isinstance(ext_point, ExtensionPoint):
            msg = "ext_point must be an instance of ExtensionPoint"
            raise TypeError(msg)
        self.extension_points[ext_point_name] = ext_point

    def register_extension(
        self, ext_point_name: str, plugin_name: str, ext_impl: Any
    ) -> None:
        """Register an extension implementation for a specific point and plugin."""
        if ext_point_name not in self.extension_points:
            msg = f"Unknown extension point: {ext_point_name}"
            raise ValueError(msg)
        if plugin_name not in self.plugins:
            msg = f"Unknown plugin: {plugin_name}"
            raise ValueError(msg)

        if ext_point_name not in self.extensions:
            self.extensions[ext_point_name] = {}
        self.extensions[ext_point_name][plugin_name] = ext_impl

    def get_extension(self, ext_point_name: str, plugin_name: str) -> Any | None:
        """Get a specific extension implementation."""
        return self.extensions.get(ext_point_name, {}).get(plugin_name)

    def get_extensions_for_plugin(self, plugin_name: str) -> dict[str, Any]:
        """Get all extensions registered by a specific plugin."""
        plugin_extensions = {}
        for ext_point_name, plugins in self.extensions.items():
            if plugin_name in plugins:
                plugin_extensions[ext_point_name] = plugins[plugin_name]
        return plugin_extensions

    def get_plugin_for_extension(
        self, ext_point_name: str, ext_impl: Any
    ) -> str | None:
        """Find the plugin that registered a specific extension implementation."""
        if ext_point_name in self.extensions:
            for plugin_name, implementation in self.extensions[ext_point_name].items():
                if implementation == ext_impl:
                    return plugin_name
        return None

    def get_plugins_for_extension_point(self, ext_point_name: str) -> list[str]:
        """Get a list of plugin names that provide extensions for a point."""
        return list(self.extensions.get(ext_point_name, {}).keys())

    def get_extension_points_for_plugin(self, plugin_name: str) -> list[str]:
        """Get a list of extension point names that a plugin provides extensions for."""
        ext_points = []
        for ext_point_name, plugins in self.extensions.items():
            if plugin_name in plugins:
                ext_points.append(ext_point_name)
        return ext_points

    def get_plugins_for_extension(self, ext_point_name: str) -> list[str]:
        """Get list of plugins providing extensions for the given point."""
        # This seems identical to get_plugins_for_extension_point, maybe consolidate?
        return list(self.extensions.get(ext_point_name, {}).keys())

    def load_plugin(self, plugin_path: str) -> ModuleType | None:
        """Load a plugin from a given path."""
        plugin_file = Path(plugin_path)
        module_name = plugin_file.stem
        spec: ModuleSpec | None = None
        plugin_module: ModuleType | None = None
        try:
            spec = spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                logger.error(
                    "Could not create spec or loader for plugin: %s", plugin_path
                )
                return None
            # If spec and loader exist, proceed
            plugin_module = module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            # Assuming plugin registration happens upon import
        except ImportError:
            logger.exception("Error importing plugin %s", plugin_path)
            return None
        except Exception:
            logger.exception("Unexpected error loading plugin %s", plugin_path)
            return None
        else:
            # Success case: return the loaded module
            return plugin_module

    def load_plugin_from_file(self, plugin_path: str) -> ModuleType | None:
        """Load a plugin module from a specific file path."""
        plugin_file = Path(plugin_path)
        if not plugin_file.is_file() or plugin_file.suffix != ".py":
            logger.error("Invalid plugin file path: %s", plugin_path)
            return None

        module_name = plugin_file.stem
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)

        if spec and spec.loader:
            module: ModuleType | None = None
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Here, you might call a specific registration function if needed
                logger.info("Successfully loaded plugin: %s", module_name)
            except Exception:
                logger.exception("Failed to load plugin module %s", module_name)
                return None
            else:
                return module
        else:
            logger.error("Could not create module spec for %s", plugin_path)
            return None

    def load_plugin_from_directory(self, plugin_dir: str) -> list[ModuleType]:
        """Load all plugins from a specified directory."""
        loaded_modules: list[ModuleType] = []
        plugin_directory = Path(plugin_dir)
        if not plugin_directory.is_dir():
            logger.error("Plugin directory not found: %s", plugin_dir)
            return loaded_modules

        for finder, name, ispkg in pkgutil.iter_modules([str(plugin_directory)]):
            if ispkg:
                continue
            try:
                full_module_name = name
                # Added path=None for find_spec consistency
                spec = finder.find_spec(full_module_name, None)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    logger.info("Successfully loaded plugin from directory: %s", name)
                    loaded_modules.append(module)
                else:
                    logger.warning("Could not find spec/loader for module %s", name)
            except Exception:
                # Use logger instance and remove redundant exception variable
                logger.exception("Failed to load plugin %s from %s", name, plugin_dir)

        return loaded_modules
