"""Framework Adapter Module."""

from collections.abc import Callable
from typing import Any

from src.core.generation.code_generator import CodeGenerator


class FrameworkAdapter:
    def __init__(self, name: str) -> None:
        """Initialize the FrameworkAdapter.

        :param name: The name of the framework.
        :type name: str
        """
        self.name = name
        self.generator = CodeGenerator()
        self.property_mappers: dict[str, dict[str, Callable]] = {}
        self.templates: dict[str, Callable] = {}
        self.transformers: dict[str, Callable] = {}
        self.validators: dict[str, Callable] = {}

        self.register_python_templates(self.generator)
        self.register_property_mappers()
        self.register_transformations()
        self.register_code_generator()
        self.register_property_mappers()
        self.register_property_validators()
        self.register_component_transformers()
        self.register_code_generator()
        self.register_property_mappers()
        self.register_property_validators()
        self.register_component_transformers()
        self.register_code_generator()

    def register_transformations(self) -> None:
        """Register component transformations."""

    def register_code_generator(self) -> None:
        """Register code generator configurations."""

    def register_property_validators(self) -> None:
        """Register property validators."""

    def register_component_transformers(self) -> None:
        """Register component transformers."""

    def register_python_templates(self, generator: CodeGenerator) -> None:
        """Register Python-specific UI component templates.

        :param generator: The code generator instance.
        """
        self.templates = {
            "window": self.window_template,
            "button": self.button_template,
            "label": self.label_template,
            "text_input": self.text_input_template,
            "checkbox": self.checkbox_template,
            "radio_button": self.radio_button_template,
            "text_area": self.text_area_template,
            "dropdown": self.dropdown_template,
            "slider": self.slider_template,
            "progress_bar": self.progress_bar_template,
            "tab_view": self.tab_view_template,
            "dialog": self.dialog_template,
            "list_view": self.list_view_template,
            "table_view": self.table_view_template,
            "tree_view": self.tree_view_template,
            "chart": self.chart_template,
            "calendar": self.calendar_template,
            "file_picker": self.file_picker_template,
            "image": self.image_template,
        }

        for name, template in self.templates.items():
            self.generator.register_template(name, template)

    def register_property_mappers(self) -> None:
        """Register property mappers for different UI components."""
        self.property_mappers = {
            "Window": {
                "modal": lambda v: "window.transient(parent)" if v else "",
            },
            "Button": {
                "enabled": lambda v: (
                    "button['state'] = tk.NORMAL"
                    if v
                    else "button['state'] = tk.DISABLED"
                ),
            },
            "Label": {
                "text": lambda v: f"label.config(text='{v}')",
            },
            "TextInput": {
                "value": lambda v: f"entry.insert(0, '{v}')",
            },
            "Checkbox": {
                "checked": lambda v: (
                    "checkbox.select()" if v else "checkbox.deselect()"
                ),
            },
            "RadioButton": {
                "selected": lambda v: "radio.select()" if v else "radio.deselect()",
            },
            "TextArea": {
                "value": lambda v: f"text_area.insert(1.0, '{v}')",
            },
            "Dropdown": {
                "value": lambda v: f"dropdown.set('{v}')",
            },
            "Slider": {
                "value": lambda v: f"slider.set({v})",
            },
            "ProgressBar": {
                "value": lambda v: f"progress_bar.set({v})",
            },
            "TabView": {
                "selected": lambda v: f"tab_view.select_tab('{v}')",
            },
            "Dialog": {
                "title": lambda v: f"dialog.title('{v}')",
            },
            "ListView": {
                "items": lambda v: f"list_view.items = {v}",
            },
            "TableView": {
                "data": lambda v: f"table_view.data = {v}",
            },
            "TreeView": {
                "data": lambda v: f"tree_view.data = {v}",
            },
            "Chart": {
                "data": lambda v: f"chart.data = {v}",
            },
            "Calendar": {
                "selected_date": lambda v: f"calendar.selected_date = {v}",
            },
            "FilePicker": {
                "selected_file": lambda v: f"file_picker.selected_file = {v}",
            },
            "Image": {
                "source": lambda v: f"image.source = {v}",
            },
        }

    def register_property_mapper(
        self, component_type: str, property_name: str, mapper_func: Callable
    ) -> None:
        """Register a property mapper for the given component type and property name.

        :param component_type: The type of component to register the mapper for.
        :param property_name: The name of the property to register the mapper for.
        :param mapper_func: A function that takes a value and returns a string
                            representing the framework-specific code required to
                            set the property to the given value.
        """
        if component_type not in self.property_mappers:
            self.property_mappers[component_type] = {}
        self.property_mappers[component_type][property_name] = mapper_func

    def map_property(self, component: Any, property_name: str) -> str:
        """Map a property of a component to framework-specific code.

        This method takes a component and a property name as input and
        returns a string representing the framework-specific code required
        to set the property to the given value.

        If a property mapper is registered for the given component type and
        property name, the mapper function is called with the value of the
        property as an argument. The return value of the mapper function is
        used as the output of this method.

        If no property mapper is registered, the value of the property is
        converted to a string using the built-in repr() function and returned
        as the output of this method.

        :param component: The component for which to map a property.
        :param property_name: The name of the property to map.
        :return: A string representing the framework-specific code required
                to set the property to the given value.
        """
        component_type = getattr(component, "type", None) or component.get("type")
        properties = getattr(component, "properties", None) or component.get(
            "properties", {}
        )

        if (
            component_type in self.property_mappers
            and property_name in self.property_mappers[component_type]
        ):
            mapper = self.property_mappers[component_type][property_name]
            return mapper(properties.get(property_name))

        return repr(properties.get(property_name))

    def generate_code(self, root_component: dict[str, Any]) -> str:
        """Generate framework-specific code for the given component tree.

        This method takes a component tree as input and returns a string
        representing the framework-specific code required to create the
        component tree.

        :param root_component: The root component of the component tree.
        :return: A string representing the framework-specific code required
                to create the component tree.
        """
        return self.generator.generate_full_source(root_component)

    def create_tkinter_adapter(self) -> "FrameworkAdapter":
        """Create a FrameworkAdapter instance configured for Tkinter.

        :return: A FrameworkAdapter instance configured for Tkinter.
        """
        adapter = self._configure_framework("Tkinter")
        # Register property mappers
        adapter.register_property_mapper(
            "Window", "modal", lambda v: "window.transient(parent)" if v else ""
        )

        return adapter

    def create_textual_adapter(self) -> "FrameworkAdapter":
        """Create a FrameworkAdapter instance configured for Textual.

        :return: A FrameworkAdapter instance configured for Textual.
        """
        return FrameworkAdapter("Textual")

    def create_pyqt_adapter(self) -> "FrameworkAdapter":
        """Create a FrameworkAdapter instance configured for PyQt.

        :return: A FrameworkAdapter instance configured for PyQt.
        """
        return self._configure_framework("PyQt")

    def create_wxpython_adapter(self) -> "FrameworkAdapter":
        """Create a FrameworkAdapter instance configured for wxPython.

        :return: A FrameworkAdapter instance configured for wxPython.
        """
        return self._configure_framework("wxPython")

    def _configure_framework(self, arg0: str) -> "FrameworkAdapter":
        """Create a FrameworkAdapter instance configured for the given framework.

        :param arg0: The name of the framework to configure the adapter for.
        :return: A FrameworkAdapter instance configured for the given framework.
        """
        result = FrameworkAdapter(arg0)
        result.register_python_templates(result.generator)
        result.register_property_mappers()
        result.register_transformations()
        result.register_code_generator()
        result.register_property_mappers()
        result.register_property_validators()
        result.register_component_transformers()
        result.register_code_generator()
        return result

    # Template methods
    def window_template(self, context: dict[str, Any]) -> str:
        """Generate window template code."""
        return "window = tk.Tk()"

    def button_template(self, context: dict[str, Any]) -> str:
        """Generate button template code."""
        return "button = tk.Button(window)"

    def label_template(self, context: dict[str, Any]) -> str:
        """Generate label template code."""
        return "label = tk.Label(window)"

    def text_input_template(self, context: dict[str, Any]) -> str:
        """Generate text input template code."""
        return "text_input = tk.Entry(window)"

    def checkbox_template(self, context: dict[str, Any]) -> str:
        """Generate checkbox template code."""
        return "checkbox = tk.Checkbutton(window)"

    def radio_button_template(self, context: dict[str, Any]) -> str:
        """Generate radio button template code."""
        return "radio_button = tk.Radiobutton(window)"

    def text_area_template(self, context: dict[str, Any]) -> str:
        """Generate text area template code."""
        return "text_area = tk.Text(window)"

    def dropdown_template(self, context: dict[str, Any]) -> str:
        """Generate dropdown template code."""
        return "dropdown = ttk.Combobox(window)"

    def slider_template(self, context: dict[str, Any]) -> str:
        """Generate slider template code."""
        return "slider = ttk.Scale(window)"

    def progress_bar_template(self, context: dict[str, Any]) -> str:
        """Generate progress bar template code."""
        return "progress_bar = ttk.Progressbar(window)"

    def tab_view_template(self, context: dict[str, Any]) -> str:
        """Generate tab view template code."""
        return "tab_view = ttk.Notebook(window)"

    def dialog_template(self, context: dict[str, Any]) -> str:
        """Generate dialog template code."""
        return "dialog = tk.Toplevel(window)"

    def list_view_template(self, context: dict[str, Any]) -> str:
        """Generate list view template code."""
        return "list_view = tk.Listbox(window)"

    def table_view_template(self, context: dict[str, Any]) -> str:
        """Generate table view template code."""
        return "table_view = ttk.Treeview(window)"

    def tree_view_template(self, context: dict[str, Any]) -> str:
        """Generate tree view template code."""
        return "tree_view = ttk.Treeview(window)"

    def chart_template(self, context: dict[str, Any]) -> str:
        """Generate chart template code."""
        return "# Chart implementation"

    def calendar_template(self, context: dict[str, Any]) -> str:
        """Generate calendar template code."""
        return "# Calendar implementation"

    def file_picker_template(self, context: dict[str, Any]) -> str:
        """Generate file picker template code."""
        return "file_picker = tk.filedialog.askopenfilename()"

    def image_template(self, context: dict[str, Any]) -> str:
        """Generate image template code."""
        return "image = tk.PhotoImage()"

    def __getitem__(self, key: str) -> Callable | dict[str, Callable]:
        """Support dictionary-style access to registered items."""
        if key in self.templates:
            return self.templates[key]
        if key in self.property_mappers:
            return self.property_mappers[key]
        if key in self.transformers:
            return self.transformers[key]
        if key in self.validators:
            return self.validators[key]
        raise KeyError(f"No item registered for key: {key}")
