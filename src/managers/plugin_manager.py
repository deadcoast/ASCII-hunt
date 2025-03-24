"""Plugin Manager Module."""

import os
import glob
import importlib

from managers.python_tkinter_generator import PythonTkinterGenerator
from managers.hunt_code_generator import HuntCodeGenerator
from managers.dsl_code_generator import DSLCodeGenerator
from managers.code_generator import CodeGenerator
from managers.layout_management import LayoutManager
from managers.functional_relationship_manager import FunctionalRelationshipManager
from managers.cache_manager import CacheManager
from managers.component_overlay_manager import ComponentOverlayManager
from components.component_model_representation import ComponentModel

from components.abstract_component import AbstractComponent


class PluginManager:
    def __init__(self):
        """
        Initialize the PluginManager.

        The PluginManager is responsible for managing the plugins, which provide
        functionality to the system. It keeps track of the plugins and provides
        an interface to register and retrieve plugins.

        :ivar plugins: A dictionary mapping plugin names to plugin instances.
        :ivar extension_points: A dictionary mapping extension point names to
            extension point instances.
        """
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
            "layout_manager": LayoutManager(
                layout_handlers={
                    "default": self.default_layout_handler,
                    "grid": self.grid_layout_handler,
                    "flex": self.flex_layout_handler,
                    "absolute": self.absolute_layout_handler,
                    "relative": self.relative_layout_handler,
                    "sticky": self.sticky_layout_handler,
                    "pack": self.pack_layout_handler,
                    "place": self.place_layout_handler,
                },
            ),
            "functional_relationship_manager": FunctionalRelationshipManager(
                relationship_patterns=[
                    self.parent_child_pattern,
                    self.sibling_pattern,
                    self.ancestor_pattern,
                    self.descendant_pattern,
                ],
            ),
            "cache_manager": CacheManager(
                max_size=100,
            ),
            "component_overlay_manager": ComponentOverlayManager(
                grid_widget=self.grid_widget,
                components=self.components,
                selected_component=self.selected_component,
                highlight_colors=self.highlight_colors,
            ),
            "component_model": ComponentModel(),
            "abstract_component": AbstractComponent(
                properties={
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "color": "#000000",
                },
                children=[],
                parent=None,
                type="",
                id="",
                name="",
                description="",
                visible=True,
                enabled=True,
                focusable=True,
                focusable_in_parent=True,
                focusable_in_window=True,
                focusable_in_application=True,
                focusable_in_system=True,
                focusable_in_screen=True,
            ),
        }
        self.extension_points = {
            "python_tkinter": PythonTkinterGenerator(
                template_registry={
                    "Window": self.window_template,
                    "Button": self.button_template,
                    "Label": self.label_template,
                    "Entry": self.entry_template,
                    "Text": self.text_template,
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
            "layout_manager": LayoutManager(
                layout_handlers={
                    "default": self.default_layout_handler,
                    "grid": self.grid_layout_handler,
                    "flex": self.flex_layout_handler,
                    "absolute": self.absolute_layout_handler,
                    "relative": self.relative_layout_handler,
                    "sticky": self.sticky_layout_handler,
                    "pack": self.pack_layout_handler,
                    "place": self.place_layout_handler,
                },
            ),
            "functional_relationship_manager": FunctionalRelationshipManager(
                relationship_patterns=[
                    self.parent_child_pattern,
                    self.sibling_pattern,
                    self.ancestor_pattern,
                    self.descendant_pattern,
                ],
            ),
            "cache_manager": CacheManager(
                max_size=100,
            ),
            "component_overlay_manager": ComponentOverlayManager(
                grid_widget=self.grid_widget,
                components=self.components,
                selected_component=self.selected_component,
                highlight_colors=self.highlight_colors,
            ),
            "component_model": ComponentModel(),
            "abstract_component": AbstractComponent(
                properties={
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                    "color": "#000000",
                },
                children=[],
                parent=None,
                type="",
                id="",
                name="",
                description="",
                visible=True,
                enabled=True,
                focusable=True,
                focusable_in_parent=True,
                focusable_in_window=True,
                focusable_in_application=True,
                focusable_in_system=True,
                focusable_in_screen=True,
            ),
        }

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
        else:
            raise ValueError(f"Invalid plugin file: {plugin_path}")

    def load_plugin_from_directory(self, plugin_dir):
        """Load all plugins from a directory."""
        for plugin_path in glob.glob(os.path.join(plugin_dir, "*.py")):
            self.load_plugin_from_file(plugin_path)

        # Create plugin instance
        module_name = os.path.basename(plugin_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
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
        else:
            raise ValueError(f"Invalid plugin file: {plugin_path}")
