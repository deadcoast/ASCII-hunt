"""Framework Adapter Module."""

from generators.code_generator import CodeGenerator


class FrameworkAdapter:
    def __init__(self, name):
        """
        Initialize the FrameworkAdapter.

        :param name: The name of the framework.
        :type name: str
        """
        self.name = name
        self.generator = CodeGenerator()
        self.property_mappers = {}

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

    def register_python_templates(self, generator):
        """Register Python-specific templates."""
        self.generator.register_template("window", self.window_template)
        self.generator.register_template("button", self.button_template)
        self.generator.register_template("label", self.label_template)
        self.generator.register_template("text_input", self.text_input_template)
        self.generator.register_template("checkbox", self.checkbox_template)
        self.generator.register_template("radio_button", self.radio_button_template)
        self.generator.register_template("text_area", self.text_area_template)
        self.generator.register_template("dropdown", self.dropdown_template)
        self.generator.register_template("slider", self.slider_template)
        self.generator.register_template("progress_bar", self.progress_bar_template)
        self.generator.register_template("tab_view", self.tab_view_template)
        self.generator.register_template("dialog", self.dialog_template)
        self.generator.register_template("list_view", self.list_view_template)
        self.generator.register_template("table_view", self.table_view_template)
        self.generator.register_template("tree_view", self.tree_view_template)
        self.generator.register_template("chart", self.chart_template)
        self.generator.register_template("calendar", self.calendar_template)
        self.generator.register_template("file_picker", self.file_picker_template)
        self.generator.register_template("image", self.image_template)

    def register_property_mappers(self):
        """Register property mappers for the framework."""
        self.property_mappers = {
            "Window": {
                "modal": lambda v: f"window.transient(parent)" if v else "",
            },
            "Button": {
                "enabled": lambda v: (
                    f"button['state'] = tk.NORMAL"
                    if v
                    else f"button['state'] = tk.DISABLED"
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
                    f"checkbox.select()" if v else f"checkbox.deselect()"
                ),
            },
            "RadioButton": {
                "selected": lambda v: f"radio.select()" if v else f"radio.deselect()",
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

    def register_property_mapper(self, component_type, property_name, mapper_func):
        """Register a function to map an abstract property to framework-specific code."""
        if component_type not in self.property_mappers:
            self.property_mappers[component_type] = {}
        self.property_mappers[component_type][property_name] = mapper_func

    def map_property(self, component, property_name):
        """Map a component property to framework-specific code."""
        if (
            component.type in self.property_mappers
            and property_name in self.property_mappers[component.type]
        ):
            return self.property_mappers[component.type][property_name](
                component.properties.get(property_name)
            )
        return repr(component.properties.get(property_name))

    def generate_code(self, root_component):
        """Generate framework-specific code for the component tree."""
        return self.generator.generate_full_source(root_component)

    def create_tkinter_adapter():
        """Create an adapter for Tkinter."""
        adapter = FrameworkAdapter("Tkinter")

        # Register Tkinter-specific templates
        adapter.register_python_templates(adapter.generator)
        adapter.register_property_mappers()
        adapter.register_transformations()
        adapter.register_code_generator()
        adapter.register_property_mappers()
        adapter.register_property_validators()
        adapter.register_component_transformers()
        adapter.register_code_generator()

        # Register property mappers
        adapter.register_property_mapper(
            "Window", "modal", lambda v: f"window.transient(parent)" if v else ""
        )

        return adapter

    def create_textual_adapter():
        """Create an adapter for Textual."""
        adapter = FrameworkAdapter("Textual")

        # Register Textual-specific templates
        return adapter

    def create_pyqt_adapter():
        """Create an adapter for PyQt."""
        adapter = FrameworkAdapter("PyQt")

        adapter.register_python_templates(adapter.generator)
        adapter.register_property_mappers()
        adapter.register_transformations()
        adapter.register_code_generator()
        adapter.register_property_mappers()
        adapter.register_property_validators()
        adapter.register_component_transformers()
        adapter.register_code_generator()

        # Register PyQt-specific templates
        return adapter

    def create_wxpython_adapter():
        """Create an adapter for wxPython."""
        adapter = FrameworkAdapter("wxPython")

        adapter.register_python_templates(adapter.generator)
        adapter.register_property_mappers()
        adapter.register_transformations()
        adapter.register_code_generator()
        adapter.register_property_mappers()
        adapter.register_property_validators()
        adapter.register_component_transformers()
        adapter.register_code_generator()

        # Register wxPython-specific templates
        return adapter

    # Window template
    def window_template(context):
        """Generate a template for a window component."""
        component = context["component"]
        indent = context["indent"]
        code = f"{indent}window = tk.Tk()\n"
        code += (
            f"{indent}window.title('{component.properties.get('title', 'Untitled')}')\n"
        )
        code += f"{indent}window.geometry('{component.properties.get('width', 800)}x{component.properties.get('height', 600)}')\n"
        return code

    def map_property(self, component, property_name):
        """Map a component property to framework-specific code."""
        if (
            component.type in self.property_mappers
            and property_name in self.property_mappers[component.type]
        ):
            return self.property_mappers[component.type][property_name](
                component.properties.get(property_name)
            )
        return repr(component.properties.get(property_name))

    def generate_code(self, root_component):
        """Generate framework-specific code for the component tree."""
        return self.generator.generate_full_source(root_component)

    def create_tkinter_adapter():
        """Create an adapter for Tkinter."""
        adapter = FrameworkAdapter("Tkinter")

        # Register Tkinter-specific templates
        adapter.register_python_templates(adapter.generator)
        adapter.register_property_mappers()
        adapter.register_transformations()
        adapter.register_code_generator()
        adapter.register_property_mappers()
        adapter.register_property_validators()
        adapter.register_component_transformers()
        adapter.register_code_generator()

        # Register property mappers
        adapter.register_property_mapper(
            "Window",
            "modal",
            lambda v: f"window.transient(parent)" if v else "",
        )
        adapter.register_property_mapper(
            "Button",
            "enabled",
            lambda v: (
                f"button['state'] = tk.NORMAL"
                if v
                else f"button['state'] = tk.DISABLED"
            ),
        )

        return adapter
