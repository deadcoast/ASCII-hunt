"""Plugin Manager Module."""

import glob
import importlib
import importlib.util
import os
from collections.abc import Callable
from importlib.util import module_from_spec, spec_from_file_location
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec

from managers.code_generator import CodeGenerator
from managers.dsl_code_generator import DSLCodeGenerator
from managers.hunt_code_generator import HuntCodeGenerator
from managers.python_tkinter_generator import PythonTkinterGenerator
from src.components.abstract_component import AbstractComponent
from src.components.component_model_representation import ComponentModel
from src.managers.cache_manager import CacheManager
from src.managers.component_overlay_manager import ComponentOverlayManager
from src.managers.functional_relationship_manager import \
    FunctionalRelationshipManager
from src.managers.layout_management import LayoutManager


class PluginManager:
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

    def __init__(self):
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
        def create_button(self, parent: Any, text: str, command: Callable[[], None]) -> Any:
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
        def create_radiobutton(self, parent: Any, text: str, variable: Any, value: Any) -> Any:
            return tk.Radiobutton(parent, text=text, variable=variable, value=value)
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
        def create_scale(self, parent: Any, from_: float, to: float, orient: str) -> Any:
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
        self.plugins = {
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
            "hunt": HuntCodeGenerator(
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

        # Initialize extension points with the same configuration
        self.extension_points = self.plugins.copy()

    def register_plugin(self, plugin_name, plugin):
        """Register a plugin."""
        self.plugins[plugin_name] = plugin
        self.extension_points[plugin_name] = plugin.get_extensions(
            self.extension_points
        )

        # Register plugin with extension points
        for ext_point, ext_impl in plugin.get_extensions(self.extension_points).items():
            self.register_extension(ext_point, plugin_name, ext_impl)

    def get_plugins(self):
        """Get all registered plugins."""
        return self.plugins

    def get_plugin(self, plugin_name):
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)

    def get_extension_points(self):
        """Get all registered extension points."""
        return self.extension_points

    def get_extension_point(self, ext_point_name):
        """Get an extension point by name."""
        return self.extension_points.get(ext_point_name)

    def get_extensions(self, ext_point_name):
        """Get all extensions for an extension point."""
        return self.extension_points.get(ext_point_name, {}).values()

    def register_extension_point(self, ext_point_name, ext_point):
        """Register an extension point."""
        self.extension_points[ext_point_name] = ext_point

    def register_extension(self, ext_point_name, plugin_name, ext_impl):
        """Register an extension for an extension point."""
        if ext_point_name not in self.extension_points:
            raise ValueError(f"Unknown extension point: {ext_point_name}")

        self.extension_points[ext_point_name].register_extension(plugin_name, ext_impl)

    def get_extension(self, ext_point_name, plugin_name):
        """Get an extension for an extension point and plugin."""
        return self.extension_points.get(ext_point_name, {}).get(plugin_name)

    def get_extensions_for_plugin(self, plugin_name):
        """Get all extensions for a plugin."""
        return {
            ext_point_name: self.get_extensions(ext_point_name)
            for ext_point_name in self.extension_points
        }

    def get_plugin_for_extension(self, ext_point_name, ext_impl):
        """Get the plugin for an extension."""
        for plugin_name, plugin in self.plugins.items():
            if plugin.get_extension(ext_point_name, ext_impl):
                return plugin_name
        return None

    def get_plugins_for_extension_point(self, ext_point_name):
        """Get all plugins for an extension point."""
        return {
            plugin_name: self.get_extensions_for_plugin(plugin_name)
            for plugin_name in self.plugins
        }

    def get_extension_points_for_plugin(self, plugin_name):
        """Get all extension points for a plugin."""
        return {
            ext_point_name: self.get_extensions(ext_point_name)
            for ext_point_name in self.extension_points
        }

    def get_plugins_for_extension(self, ext_point_name):
        """Get all plugins for an extension."""
        return {
            plugin_name: self.get_extensions_for_plugin(plugin_name)
            for plugin_name in self.plugins
        }

    def load_plugin(self, plugin_path: str) -> ModuleType | None:
        """Load a plugin from the specified path."""
        try:
            spec = spec_from_file_location("plugin", plugin_path)
            if spec is None or spec.loader is None:
                print(
                    f"Failed to load plugin at {plugin_path}: Invalid module specification"
                )
                return None

            # Create module from spec and ensure it's not None
            module = module_from_spec(cast("ModuleSpec", spec))

            # Execute the module if loader exists
            if spec.loader is not None:
                spec.loader.exec_module(module)

            return module

        except Exception as e:
            print(f"Error loading plugin at {plugin_path}: {e!s}")
            return None

    def load_plugin_from_file(self, plugin_path):
        """Load a plugin from a file."""
        import importlib.util
        import sys

        # Add plugin directory to sys.path
        plugin_dir = os.path.dirname(plugin_path)
        sys.path.insert(0, plugin_dir)

        # Load module from file
        module_name = os.path.basename(plugin_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ValueError(
                f"Failed to load plugin at {plugin_path}: Invalid module specification"
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Create plugin instance
        if hasattr(module, "create_plugin"):
            plugin = module.create_plugin(
                extension_points=self.extension_points,
                plugins=self.plugins,
                grid_widget=self.grid_widget,
                components=self.components,
                selected_component=self.selected_component,
                highlight_colors=self.highlight_colors,
                layout_manager=self.layout_manager,
                functional_relationship_manager=self.functional_relationship_manager,
                cache_manager=self.cache_manager,
                component_overlay_manager=self.component_overlay_manager,
                abstract_component=self.abstract_component,
            )
            plugin_name = plugin.get_name(
                extension_points=self.extension_points,
                plugins=self.plugins,
                grid_widget=self.grid_widget,
                components=self.components,
                selected_component=self.selected_component,
                highlight_colors=self.highlight_colors,
                layout_manager=self.layout_manager,
                functional_relationship_manager=self.functional_relationship_manager,
                cache_manager=self.cache_manager,
                component_overlay_manager=self.component_overlay_manager,
                abstract_component=self.abstract_component,
            )

            # Register plugin
            self.register_plugin(plugin_name, plugin)

            return plugin_name
        raise ValueError(f"Invalid plugin file: {plugin_path}")

    def load_plugin_from_directory(self, plugin_dir):
        """Load all plugins from a directory."""
        plugin_paths = glob.glob(os.path.join(plugin_dir, "*.py"))
        loaded_plugins = []

        for plugin_path in plugin_paths:
            try:
                # Create plugin instance
                module_name = os.path.basename(plugin_path).replace(".py", "")
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)
                if spec is None or spec.loader is None:
                    print(
                        f"Failed to load plugin at {plugin_path}: Invalid module specification"
                    )
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Create plugin instance
                if hasattr(module, "create_plugin"):
                    plugin = module.create_plugin(
                        extension_points=self.extension_points,
                        plugins=self.plugins,
                        grid_widget=self.grid_widget,
                        components=self.components,
                        selected_component=self.selected_component,
                        highlight_colors=self.highlight_colors,
                        layout_manager=self.layout_manager,
                        functional_relationship_manager=self.functional_relationship_manager,
                        cache_manager=self.cache_manager,
                        component_overlay_manager=self.component_overlay_manager,
                        abstract_component=self.abstract_component,
                    )
                    plugin_name = plugin.get_name(
                        extension_points=self.extension_points,
                        plugins=self.plugins,
                        grid_widget=self.grid_widget,
                        components=self.components,
                        selected_component=self.selected_component,
                        highlight_colors=self.highlight_colors,
                        layout_manager=self.layout_manager,
                        functional_relationship_manager=self.functional_relationship_manager,
                        cache_manager=self.cache_manager,
                        component_overlay_manager=self.component_overlay_manager,
                        abstract_component=self.abstract_component,
                    )

                    # Register plugin
                    self.register_plugin(plugin_name, plugin)
                    loaded_plugins.append(plugin_name)
                else:
                    raise ValueError(f"Invalid plugin file: {plugin_path}")
            except Exception as e:
                print(f"Error loading plugin at {plugin_path}: {e!s}")
                continue

        return loaded_plugins
