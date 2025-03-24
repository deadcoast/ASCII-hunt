# 3. Architecture

## 3.1 Abstract Component Model

### Mathematical Foundation

The Abstract Component Model (ACM) provides a formal representation of UI elements that is independent of specific frameworks. We can define the model mathematically as follows:

Let $\mathcal{C}$ be the set of all UI components, where each component $c \in \mathcal{C}$ is represented by a tuple:

$c = (id, type, properties, children, relationships)$

Where:

- $id$ is a unique identifier
- $type \in \mathcal{T}$ represents the component type (e.g., button, window, text field)
- $properties$ is a map $P: K \rightarrow V$ from property keys to values
- $children \subseteq \mathcal{C}$ is an ordered set of child components
- $relationships$ is a set of tuples $(r, c')$ where $r \in \mathcal{R}$ is a relationship type and $c' \in \mathcal{C}$

The component hierarchy forms a tree structure $(\mathcal{C}, E)$ where:

- $E = {(p, c) \mid p \in \mathcal{C}, c \in children(p)}$

For component classification, we define a function $\phi: \mathcal{C} \rightarrow \mathcal{T}$ that maps components to their types based on their properties and structure.

### Implementation Architecture

The Abstract Component Model will be implemented as a class hierarchy with the following structure:

```python
class AbstractComponent:
    def __init__(self, component_id, component_type):
        self.id = component_id
        self.type = component_type
        self.properties = {}
        self.children = []
        self.parent = None
        self.relationships = []

    def add_property(self, key, value):
        self.properties[key] = value

    def add_child(self, component):
        component.parent = self
        self.children.append(component)

    def add_relationship(self, relationship_type, target_component):
        self.relationships.append((relationship_type, target_component))

    def get_descendants(self):
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_descendants())
        return result

    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'properties': self.properties,
            'children': [child.serialize() for child in self.children],
            'relationships': [(rel_type, comp.id) for rel_type, comp in self.relationships]
        }

    @classmethod
    def deserialize(cls, data, component_map=None):
        if component_map is None:
            component_map = {}

        component = cls(data['id'], data['type'])
        component.properties = data['properties'].copy()
        component_map[data['id']] = component

        for child_data in data['children']:
            child = cls.deserialize(child_data, component_map)
            component.add_child(child)

        # Defer relationship resolution until all components are created
        relationship_data = [(rel_type, target_id) for rel_type, target_id in data['relationships']]

        if len(relationship_data) > 0:
            for rel_type, target_id in relationship_data:
                if target_id in component_map:
                    component.add_relationship(rel_type, component_map[target_id])

        return component
```

### Component Type System

The ACM will define a comprehensive type system for UI elements:

1. **Container Components**:

   - Window: Top-level container with title bar and borders
   - Panel: Generic container for grouping elements
   - GroupBox: Container with a border and optional title
   - TabContainer: Container with selectable tabs

2. **Input Components**:

   - TextField: Single-line text input
   - TextArea: Multi-line text input
   - Checkbox: Binary selection control
   - RadioButton: Exclusive selection within a group
   - ComboBox: Dropdown selection control
   - Spinner: Numeric input with increment controls

3. **Action Components**:

   - Button: Clickable control that triggers an action
   - ToggleButton: Button with persistent state
   - MenuButton: Button that opens a menu
   - Hyperlink: Text that triggers navigation

4. **Display Components**:

   - Label: Static text display
   - ProgressBar: Visual indication of progress
   - Separator: Visual divider between sections
   - Icon: Symbolic visual element

### Property System

Each component type will have a defined set of properties:

```python
COMPONENT_PROPERTIES = {
    'Window': {
        'required': ['title', 'width', 'height'],
        'optional': ['minimizable', 'maximizable', 'closable', 'modal'],
        'defaults': {'minimizable': True, 'maximizable': True, 'closable': True, 'modal': False}
    },
    'Button': {
        'required': ['text'],
        'optional': ['enabled', 'default', 'width', 'height'],
        'defaults': {'enabled': True, 'default': False}
    },
    # Definitions for other component types...
}
```

The property system will include validation to ensure that components have all required properties and that property values are of the correct type.

### Relationship Types

The ACM will support various relationship types beyond parent-child:

1. **Functional Relationships**:

   - `controls`: Component controls the state of another (e.g., button controls dialog)
   - `references`: Component references another (e.g., label references field)
   - `triggers`: Component triggers action on another (e.g., button triggers form submission)

2. **Spatial Relationships**:

   - `alignsWith`: Component is aligned with another
   - `adjacentTo`: Component is adjacent to another
   - `overlaps`: Component overlaps with another

3. **Semantic Relationships**:

   - `describes`: Component provides description for another
   - `groups`: Component logically groups others without containing them
   - `alternatives`: Components are alternatives to each other (e.g., tabs)

### Transformation and Validation

The ACM will include utilities for transformation and validation:

```python
class ComponentValidator:
    def __init__(self, property_definitions=COMPONENT_PROPERTIES):
        self.property_definitions = property_definitions

    def validate_component(self, component):
        """Validate a component against its type definition."""
        if component.type not in self.property_definitions:
            return [f"Unknown component type: {component.type}"]

        errors = []
        type_def = self.property_definitions[component.type]

        # Check required properties
        for prop in type_def['required']:
            if prop not in component.properties:
                errors.append(f"Missing required property '{prop}' for {component.type}")

        # Check property types (would implement type checking here)

        # Recursively validate children
        for child in component.children:
            child_errors = self.validate_component(child)
            errors.extend([f"In child {child.id}: {err}" for err in child_errors])

        return errors

class ComponentTransformer:
    def __init__(self):
        self.transformations = {}

    def register_transformation(self, source_type, target_type, transform_func):
        """Register a transformation function between component types."""
        if source_type not in self.transformations:
            self.transformations[source_type] = {}
        self.transformations[source_type][target_type] = transform_func

    def transform(self, component, target_type):
        """Transform a component to a different type."""
        if component.type == target_type:
            return component

        if (component.type in self.transformations and
            target_type in self.transformations[component.type]):
            return self.transformations[component.type][target_type](component)

        raise ValueError(f"No transformation defined from {component.type} to {target_type}")
```

### Integration with Recognition Algorithms

The ACM will provide factories to create components from algorithm results:

```python
class ComponentFactory:
    def __init__(self, id_generator=None):
        self.id_generator = id_generator or (lambda: str(uuid.uuid4()))
        self.type_classifier = None  # To be set with trained classifier

    def create_from_flood_fill(self, flood_fill_result, grid):
        """Create a component from flood fill results."""
        component_id = self.id_generator()

        # Extract features for classification
        features = extract_component_features(flood_fill_result, grid)

        # Classify component type
        component_type = self.classify_component_type(features)

        # Create the component
        component = AbstractComponent(component_id, component_type)

        # Set basic properties
        bounding_box = flood_fill_result['bounding_box']
        component.add_property('x', bounding_box[0])
        component.add_property('y', bounding_box[1])
        component.add_property('width', bounding_box[2] - bounding_box[0] + 1)
        component.add_property('height', bounding_box[3] - bounding_box[1] + 1)

        # Extract and set component-specific properties
        self.extract_component_properties(component, flood_fill_result, grid)

        return component

    def classify_component_type(self, features):
        """Classify component type based on features."""
        if self.type_classifier:
            return self.type_classifier.predict([features])[0]

        # Fallback classification logic
        if features['has_border'] and features['has_title']:
            return 'Window'
        elif features['is_rectangular'] and features['contains_text']:
            if features['text_is_bracketed']:
                return 'Button'
            else:
                return 'Label'
        # More classification rules...

        return 'Unknown'

    def extract_component_properties(self, component, flood_fill_result, grid):
        """Extract component-specific properties based on content."""
        content = flood_fill_result.get('content', [])

        if component.type == 'Window':
            # Extract window title from first line
            if content and len(content) > 0:
                component.add_property('title', content[0].strip())

        elif component.type == 'Button':
            # Extract button text
            text = ' '.join(content).strip()
            # Remove brackets if present
            if text.startswith('[') and text.endswith(']'):
                text = text[1:-1].strip()
            component.add_property('text', text)

        # More property extraction for other types...
```

## 3.2 Modular Code Generation

### Mathematical Foundation

The Modular Code Generation system transforms the abstract component model into framework-specific code. We can define this transformation mathematically.

Let $M: \mathcal{C} \rightarrow \mathcal{S}$ be a mapping function that converts a component to its source code representation. This function is composed of several sub-functions:

$M(c) = F_t(c) = T_t(c) \cdot \bigoplus_{c' \in children(c)} M(c')$

Where:

- $F_t$ is the framework-specific mapping for component type $t = type(c)$
- $T_t$ is the template function for component type $t$ in the target framework
- $\bigoplus$ is a composition operator for combining child component code

The transformation preserves the hierarchy structure while translating the component properties and relationships to framework-specific constructs.

### Generator Architecture

The code generation system will follow a template-based approach with the following architecture:

```python
class CodeGenerator:
    def __init__(self):
        self.template_registry = {}
        self.helper_functions = {}
        self.imports = set()

    def register_template(self, component_type, template_func):
        """Register a template function for a component type."""
        self.template_registry[component_type] = template_func

    def register_helper(self, name, helper_func):
        """Register a helper function for templates."""
        self.helper_functions[name] = helper_func

    def add_import(self, import_statement):
        """Add an import statement to the generated code."""
        self.imports.add(import_statement)

    def generate(self, component, indent_level=0):
        """Generate code for a component and its children."""
        if component.type not in self.template_registry:
            raise ValueError(f"No template registered for component type: {component.type}")

        # Create template context
        context = {
            'component': component,
            'helpers': self.helper_functions,
            'indent': ' ' * (4 * indent_level)
        }

        # Apply template
        template_func = self.template_registry[component.type]
        code_parts = []

        # Generate component code
        component_code = template_func(context)
        code_parts.append(component_code)

        # Generate child components
        for child in component.children:
            child_code = self.generate(child, indent_level + 1)
            code_parts.append(child_code)

        return '\n'.join(code_parts)

    def generate_full_source(self, root_component):
        """Generate complete source code including imports."""
        component_code = self.generate(root_component)
        import_code = '\n'.join(sorted(self.imports))

        return f"{import_code}\n\n{component_code}"
```

### Template System

Templates will be implemented as functions that generate code strings:

```python
def register_python_templates(generator):
    """Register Python-specific templates."""

    # Window template
    def window_template(context):
        component = context['component']
        indent = context['indent']

        title = component.properties.get('title', 'Window')
        width = component.properties.get('width', 400)
        height = component.properties.get('height', 300)

        generator.add_import("import tkinter as tk")

        return f"""{indent}window = tk.Tk()
{indent}window.title("{title}")
{indent}window.geometry("{width}x{height}")"""

    # Button template
    def button_template(context):
        component = context['component']
        indent = context['indent']

        text = component.properties.get('text', 'Button')
        x = component.properties.get('x', 0)
        y = component.properties.get('y', 0)

        generator.add_import("import tkinter as tk")

        return f"""{indent}button = tk.Button(window, text="{text}")
{indent}button.place(x={x}, y={y})"""

    # Register templates
    generator.register_template('Window', window_template)
    generator.register_template('Button', button_template)
    # Register more templates...

    # Helper functions
    generator.register_helper('escape_string', lambda s: s.replace('"', '\\"'))
```

### Framework-Specific Adapters

The system will include adapters for different frameworks:

```python
class FrameworkAdapter:
    def __init__(self, name):
        self.name = name
        self.generator = CodeGenerator()
        self.property_mappers = {}

    def register_property_mapper(self, component_type, property_name, mapper_func):
        """Register a function to map an abstract property to framework-specific code."""
        if component_type not in self.property_mappers:
            self.property_mappers[component_type] = {}
        self.property_mappers[component_type][property_name] = mapper_func

    def map_property(self, component, property_name):
        """Map a component property to framework-specific code."""
        if (component.type in self.property_mappers and
            property_name in self.property_mappers[component.type]):
            return self.property_mappers[component.type][property_name](
                component.properties.get(property_name))
        return repr(component.properties.get(property_name))

    def generate_code(self, root_component):
        """Generate framework-specific code for the component tree."""
        return self.generator.generate_full_source(root_component)
```

Framework-specific adapters will be implemented for different UI libraries:

```python
def create_tkinter_adapter():
    """Create an adapter for Tkinter."""
    adapter = FrameworkAdapter("Tkinter")

    # Register Tkinter-specific templates
    register_python_templates(adapter.generator)

    # Register property mappers
    adapter.register_property_mapper('Window', 'modal',
                                    lambda v: f"window.transient(parent)" if v else "")
    adapter.register_property_mapper('Button', 'enabled',
                                    lambda v: f"button['state'] = tk.NORMAL" if v else
                                             f"button['state'] = tk.DISABLED")

    return adapter

def create_textual_adapter():
    """Create an adapter for Textual."""
    adapter = FrameworkAdapter("Textual")

    # Register Textual-specific templates
    # ... (similar implementation)

    return adapter
```

### Code Composition System

For complex layouts and component relationships, the system will include a composition engine:

```python
class CodeCompositionEngine:
    def __init__(self, generator):
        self.generator = generator

    def compose_container_with_children(self, container, child_codes):
        """Compose container code with its children."""
        container_type = container.type

        if container_type == 'Window':
            # For windows, we add child components into the window context
            return f"{container_code}\n\n" + "\n".join(child_codes)

        elif container_type == 'Panel':
            # For panels, we need to add child components as panel children
            panel_var = self._get_variable_name(container)
            adjusted_child_codes = [self._adjust_parent(code, panel_var)
                                  for code in child_codes]
            return f"{container_code}\n\n" + "\n".join(adjusted_child_codes)

        # Handle other container types...

    def _get_variable_name(self, component):
        """Get the variable name used for a component."""
        return f"{component.type.lower()}_{component.id}"

    def _adjust_parent(self, child_code, parent_var):
        """Adjust child code to use the correct parent variable."""
        # This would be framework-specific logic
        pass
```

## 3.3 Pluggable Backend Architecture

### Mathematical Foundation

The Pluggable Backend Architecture enables extending the system without modifying the core. Mathematically, we can represent this through a plugin system interface:

Let $\Pi$ be the set of all plugins, where each plugin $\pi \in \Pi$ provides:

- A set of component types $\mathcal{T}_\pi \subseteq \mathcal{T}$
- A set of template functions $\mathcal{F}_\pi : \mathcal{T}_\pi \rightarrow (C \rightarrow S)$
- A set of property mappers $\mathcal{P}_\pi : \mathcal{T}_\pi \times K \rightarrow (V \rightarrow S)$

The system integrates these plugins through registration, creating an extensible mapping: $M'(c) = \begin{cases} \mathcal{F}_\pi(type(c))(c) & \text{if } \exists \pi \in \Pi \text{ such that } type(c) \in \mathcal{T}_\pi \ M(c) & \text{otherwise} \end{cases}$

This allows the system to be extended with new component types, frameworks, and transformations without modifying the core logic.

### Plugin System Architecture

The plugin system will support dynamic loading and registration of backends:

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.component_types = {}
        self.generators = {}

    def register_plugin(self, plugin_id, plugin_instance):
        """Register a plugin with the system."""
        if plugin_id in self.plugins:
            raise ValueError(f"Plugin already registered: {plugin_id}")

        self.plugins[plugin_id] = plugin_instance

        # Register component types provided by this plugin
        for component_type in plugin_instance.get_component_types():
            if component_type in self.component_types:
                self.component_types[component_type].append(plugin_id)
            else:
                self.component_types[component_type] = [plugin_id]

        # Register generators provided by this plugin
        for generator_id, generator in plugin_instance.get_generators().items():
            self.generators[f"{plugin_id}.{generator_id}"] = generator

    def get_generator(self, generator_id):
        """Get a registered code generator."""
        if generator_id not in self.generators:
            raise ValueError(f"Unknown generator: {generator_id}")
        return self.generators[generator_id]

    def get_plugins_for_component(self, component_type):
        """Get plugins that support a specific component type."""
        return self.component_types.get(component_type, [])

    def load_plugin_from_file(self, plugin_path):
        """Dynamically load a plugin from a Python file."""
        module_name = os.path.basename(plugin_path).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'create_plugin'):
            raise ValueError(f"Invalid plugin module: {plugin_path}")

        plugin_instance = module.create_plugin()
        plugin_id = plugin_instance.get_id()

        self.register_plugin(plugin_id, plugin_instance)
        return plugin_id
```

### Plugin Interface

Plugins will implement a standard interface:

```python
class Plugin:
    def __init__(self, plugin_id, name, version):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self._component_types = []
        self._generators = {}

    def get_id(self):
        """Get the plugin identifier."""
        return self.plugin_id

    def get_info(self):
        """Get plugin information."""
        return {
            'id': self.plugin_id,
            'name': self.name,
            'version': self.version
        }

    def get_component_types(self):
        """Get component types supported by this plugin."""
        return self._component_types

    def get_generators(self):
        """Get code generators provided by this plugin."""
        return self._generators

    def register_component_type(self, component_type):
        """Register a supported component type."""
        if component_type not in self._component_types:
            self._component_types.append(component_type)

    def register_generator(self, generator_id, generator):
        """Register a code generator."""
        self._generators[generator_id] = generator
```

### Framework-Specific Plugin Implementation

Each plugin can implement support for specific UI frameworks:

```python
class TkinterPlugin(Plugin):
    def __init__(self):
        super().__init__('tkinter', 'Tkinter UI Framework', '1.0')
        self._setup()

    def _setup(self):
        # Register supported component types
        for component_type in ['Window', 'Button', 'Label', 'TextField',
                              'Checkbox', 'RadioButton', 'Panel']:
            self.register_component_type(component_type)

        # Create and register the Tkinter code generator
        generator = create_tkinter_adapter()
        self.register_generator('generator', generator)

def create_plugin():
    """Factory function to create the Tkinter plugin."""
    return TkinterPlugin()
```

### Configuration and Extension System

The system will include configuration capabilities for plugins:

```python
class PluginConfiguration:
    def __init__(self):
        self.config = {}

    def set_plugin_config(self, plugin_id, config_dict):
        """Set configuration for a plugin."""
        self.config[plugin_id] = config_dict

    def get_plugin_config(self, plugin_id):
        """Get configuration for a plugin."""
        return self.config.get(plugin_id, {})

    def load_config_file(self, config_path):
        """Load configuration from a file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        for plugin_id, plugin_config in config_data.items():
            self.set_plugin_config(plugin_id, plugin_config)

    def save_config_file(self, config_path):
        """Save configuration to a file."""
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
```

### Extension Points

The system will define standard extension points for plugins:

```python
class ExtensionRegistry:
    def __init__(self):
        self.extensions = {}

    def register_extension(self, extension_point, plugin_id, extension):
        """Register an extension for a specific extension point."""
        if extension_point not in self.extensions:
            self.extensions[extension_point] = {}

        self.extensions[extension_point][plugin_id] = extension

    def get_extensions(self, extension_point):
        """Get all extensions for a specific extension point."""
        return self.extensions.get(extension_point, {})

    def get_extension(self, extension_point, plugin_id):
        """Get a specific extension."""
        extensions = self.get_extensions(extension_point)
        return extensions.get(plugin_id)
```

### Component Transformation Pipeline

The pluggable architecture will support component transformation pipelines:

```python
class TransformationPipeline:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.transforms = []

    def add_transform(self, transform_id, plugin_id, params=None):
        """Add a transformation to the pipeline."""
        self.transforms.append({
            'transform_id': transform_id,
            'plugin_id': plugin_id,
            'params': params or {}
        })

    def process(self, component):
        """Process a component through the transformation pipeline."""
        result = component

        for transform_config in self.transforms:
            plugin_id = transform_config['plugin_id']
            transform_id = transform_config['transform_id']
            params = transform_config['params']

            plugins = self.plugin_manager.plugins
            if plugin_id not in plugins:
                raise ValueError(f"Unknown plugin: {plugin_id}")

            plugin = plugins[plugin_id]
            extensions = plugin.get_extensions('transforms')

            if transform_id not in extensions:
                raise ValueError(f"Unknown transform: {transform_id}")

            transform = extensions[transform_id]
            result = transform.transform(result, **params)

        return result
```

## 3.4 Component Mapping DSL

### Mathematical Foundation

The Component Mapping DSL provides a declarative way to specify mappings between components and code templates. We can formalize this as follows:

Let $D$ be the language of the DSL, and $I : D \rightarrow (C \rightarrow S)$ be an interpretation function that maps DSL expressions to component transformation functions.

For a DSL expression $d \in D$, the interpretation generates a function $f_d = I(d)$ such that $f_d : C \rightarrow S$ maps components to source code.

DSL expressions can be composed through operations:

- Sequential composition: $(d_1 ; d_2)$ interpreted as $f_{d_1} \cdot f_{d_2}$
- Conditional application: $(d_1 \text{ if } p \text{ else } d_2)$ interpreted as $\lambda c . p(c) ? f_{d_1}(c) : f_{d_2}(c)$
- Repetition: $(d^*)$ interpreted as $\lambda c . \bigoplus_{c' \in children(c)} f_d(c')$

The DSL provides a concise way to specify complex transformations without writing general-purpose code.

### DSL Grammar

The Component Mapping DSL will use a syntax designed for readability and expressiveness:

```
# EBNF Grammar for Component Mapping DSL

mapping ::= "component" component_type ":" NEWLINE INDENT mappings DEDENT
mappings ::= (property_mapping | children_mapping | template)+
property_mapping ::= "property" property_name "=" expression
children_mapping ::= "children" ":" NEWLINE INDENT child_mappings DEDENT
child_mappings ::= (child_mapping)+
child_mapping ::= component_type "=>" expression
template ::= "template" ":" NEWLINE INDENT template_code DEDENT
expression ::= literal | reference | function_call | conditional
reference ::= "$" (property_name | "parent" "." property_name | "index" | "type")
function_call ::= function_name "(" [arguments] ")"
arguments ::= expression ("," expression)*
conditional ::= "if" condition "then" expression "else" expression
literal ::= STRING | NUMBER | "true" | "false" | "null"
```

Example DSL code:

```
component Button:
    property text = $text
    property enabled = $enabled
    property width = compute_width($text)
    property height = 30

    template:
        <button class="btn {if $enabled then 'active' else 'disabled'}"
                style="width: {$width}px; height: {$height}px;">
            {$text}
        </button>
```

### DSL Parser Implementation

The DSL parser will convert the mapping definitions to executable code:

```python
class DSLParser:
    def __init__(self):
        self.functions = {}

    def register_function(self, name, func):
        """Register a function for use in expressions."""
        self.functions[name] = func

    def parse(self, source):
        """Parse DSL source and return a mapping object."""
        # Lexical analysis and parsing implementation
        # This would convert the DSL source to an abstract syntax tree
        ast = self._parse_source(source)

        # Build a mapping object from the AST
        return self._build_mapping(ast)

    def _parse_source(self, source):
        """Parse DSL source into an abstract syntax tree."""
        # Implement parsing logic
        # This could use a library like PLY, lark, or a recursive descent parser
        pass

    def _build_mapping(self, ast):
        """Build a mapping object from an AST."""
        mappings = {}

        for component_mapping in ast:
            component_type = component_mapping['type']
            property_mappings = {}
            template = None
            children_mappings = {}

            for item in component_mapping['mappings']:
                if item['kind'] == 'property':
                    property_mappings[item['name']] = self._build_expression(item['expression'])
                elif item['kind'] == 'template':
                    template = item['code']
                elif item['kind'] == 'children':
                    for child_mapping in item['mappings']:
                        children_mappings[child_mapping['type']] = self._build_expression(
                            child_mapping['expression'])

            mappings[component_type] = ComponentMapping(
                component_type,
                property_mappings,
                template,
                children_mappings
            )

        return Mapping(mappings)

    def _build_expression(self, expr_ast):
        """Build an executable expression from an AST."""
        if expr_ast['kind'] == 'literal':
            return lambda ctx: expr_ast['value']

        elif expr_ast['kind'] == 'reference':
            path = expr_ast['path']

            if path[0] == 'parent':
                return lambda ctx: ctx.get('parent', {}).get(path[1], None)
            elif path[0] == 'index':
                return lambda ctx: ctx.get('index', 0)
            elif path[0] == 'type':
                return lambda ctx: ctx.get('component', {}).get('type', None)
            else:
                return lambda ctx: ctx.get('component', {}).get('properties', {}).get(path[0], None)

        elif expr_ast['kind'] == 'function_call':
            func_name = expr_ast['name']
            arg_exprs = [self._build_expression(arg) for arg in expr_ast['arguments']]

            if func_name not in self.functions:
                raise ValueError(f"Unknown function: {func_name}")

            func = self.functions[func_name]

            return lambda ctx: func(*[arg_expr(ctx) for arg_expr in arg_exprs])

        elif expr_ast['kind'] == 'conditional':
            condition = self._build_expression(expr_ast['condition'])
            then_expr = self._build_expression(expr_ast['then'])
            else_expr = self._build_expression(expr_ast['else'])

            return lambda ctx: then_expr(ctx) if condition(ctx) else else_expr(ctx)

        raise ValueError(f"Unknown expression type: {expr_ast['kind']}")
```

### Mapping Execution Engine

The mapping execution engine will apply the mappings to components:

```python
class Mapping:
    def __init__(self, component_mappings):
        self.component_mappings = component_mappings

    def apply(self, component, context=None):
        """Apply the mapping to a component and generate code."""
        if context is None:
            context = {}

        component_type = component.type

        if component_type not in self.component_mappings:
            raise ValueError(f"No mapping defined for component type: {component_type}")

        mapping = self.component_mappings[component_type]
        return mapping.apply(component, context)

class ComponentMapping:
    def __init__(self, component_type, property_mappings, template, children_mappings):
        self.component_type = component_type
        self.property_mappings = property_mappings
        self.template = template
        self.children_mappings = children_mappings

    def apply(self, component, parent_context=None):
        """Apply the mapping to a component and generate code."""
        # Create context for expression evaluation
        context = {'component': component, 'parent': parent_context}

        # Evaluate property mappings
        properties = {}
        for prop_name, prop_expr in self.property_mappings.items():
            properties[prop_name] = prop_expr(context)

        # Process template
        if self.template:
            template_engine = TemplateEngine()
            code = template_engine.render(self.template, {
                'component': component,
                'properties': properties
            })
        else:
            code = None

        # Process children if any
        children_code = []

        for i, child in enumerate(component.children):
            child_context = dict(context)
            child_context['index'] = i

            child_type = child.type

            if child_type in self.children_mappings:
                child_mapping_expr = self.children_mappings[child_type]
                child_mapping = child_mapping_expr(child_context)

                if child_mapping:
                    child_code = child_mapping.apply(child, context)
                    children_code.append(child_code)

        # Combine code from this component and its children
        if code and children_code:
            # Insert children at placeholder or append
            if '{children}' in code:
                final_code = code.replace('{children}', '\n'.join(children_code))
            else:
                final_code = code + '\n' + '\n'.join(children_code)
        elif code:
            final_code = code
        elif children_code:
            final_code = '\n'.join(children_code)
        else:
            final_code = ''

        return final_code
```

### Template Engine

The template engine will render templates with component properties:

```python
class TemplateEngine:
    def __init__(self):
        self.expression_pattern = re.compile(r'\{([^}]+)\}')

    def render(self, template, data):
        """Render a template with the provided data."""
        def replace_expr(match):
            expr = match.group(1).strip()

            # Handle special case for children
            if expr == 'children':
                return '{children}'

            # Simple expression evaluation
            try:
                result = self._evaluate_expression(expr, data)
                return str(result)
            except Exception as e:
                return f"{{Error: {str(e)}}}"

        return self.expression_pattern.sub(replace_expr, template)

    def _evaluate_expression(self, expr, data):
        """Evaluate a simple expression within template."""
        # For simplicity, we're using a straightforward approach
        # A more robust implementation would use a proper expression parser

        if expr.startswith('component.'):
            path = expr[10:].split('.')
            value = data['component']

            for key in path:
                if hasattr(value, key):
                    value = getattr(value, key)
                elif isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return value

        elif expr.startswith('properties.'):
            key = expr[11:]
            return data['properties'].get(key)

        # Support for simple conditionals
        elif ' if ' in expr and ' else ' in expr:
            condition, rest = expr.split(' if ', 1)
            then_part, else_part = rest.split(' else ', 1)

            condition_value = self._evaluate_expression(condition, data)

            if condition_value:
                return self._evaluate_expression(then_part, data)
            else:
                return self._evaluate_expression(else_part, data)

        # Handle literals
        elif expr == 'true':
            return True
        elif expr == 'false':
            return False
        elif expr == 'null' or expr == 'none':
            return None
        elif expr.isdigit():
            return int(expr)
        elif expr.replace('.', '', 1).isdigit() and expr.count('.') <= 1:
            return float(expr)
        elif expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]

        return f"{{Unknown: {expr}}}"
```

### DSL Standard Library

The DSL will include a standard library of functions for common operations:

```python
class DSLStandardLibrary:
    @staticmethod
    def register_standard_functions(parser):
        """Register standard functions with a DSL parser."""
        # String functions
        parser.register_function('concat', lambda *args: ''.join(str(arg) for arg in args))
        parser.register_function('format', lambda fmt, *args: fmt.format(*args))
        parser.register_function('uppercase', lambda s: str(s).upper())
        parser.register_function('lowercase', lambda s: str(s).lower())
        parser.register_function('capitalize', lambda s: str(s).capitalize())

        # Math functions
        parser.register_function('add', lambda a, b: a + b)
        parser.register_function('subtract', lambda a, b: a - b)
        parser.register_function('multiply', lambda a, b: a * b)
        parser.register_function('divide', lambda a, b: a / b if b != 0 else 0)
        parser.register_function('max', max)
        parser.register_function('min', min)
        parser.register_function('round', round)

        # Collection functions
        parser.register_function('length', len)
        parser.register_function('join', lambda sep, items: sep.join(items))
        parser.register_function('map', lambda func, items: [func(item) for item in items])
        parser.register_function('filter', lambda func, items: [item for item in items if func(item)])

        # Type conversion
        parser.register_function('str', str)
        parser.register_function('int', lambda v: int(float(v)) if isinstance(v, (int, float, str)) else 0)
        parser.register_function('float', lambda v: float(v) if isinstance(v, (int, float, str)) else 0.0)
        parser.register_function('bool', lambda v: bool(v))

        # UI-specific functions
        parser.register_function('compute_width', lambda text, char_width=8: len(str(text)) * char_width)
        parser.register_function('compute_height', lambda lines=1, line_height=20: lines * line_height)
        parser.register_function('css_class', lambda enabled, cls: cls if enabled else '')
```

### DSL Integration with Code Generation

The DSL will integrate with the code generation system:

```python
class DSLCodeGenerator:
    def __init__(self, mapping_source):
        self.parser = DSLParser()
        DSLStandardLibrary.register_standard_functions(self.parser)

        # Parse the mapping source
        self.mapping = self.parser.parse(mapping_source)

    def generate(self, component):
        """Generate code for a component using the DSL mappings."""
        return self.mapping.apply(component)

    def register_custom_function(self, name, func):
        """Register a custom function for use in mapping expressions."""
        self.parser.register_function(name, func)
```

### Framework-Specific DSL Templates

The system will include pre-defined DSL templates for supported frameworks:

```python
# Tkinter DSL mapping template
TKINTER_MAPPING = """
component Window:
    property title = $title
    property width = $width or 400
    property height = $height or 300

    template:
        window = tk.Tk()
        window.title("{$title}")
        window.geometry("{$width}x{$height}")
        {children}
        window.mainloop()

component Button:
    property text = $text or "Button"
    property x = $x or 0
    property y = $y or 0
    property width = compute_width($text, 10)
    property height = 30
    property command = $command

    template:
        button_{$id} = tk.Button(window, text="{$text}", width={$width // 10})
        button_{$id}.place(x={$x}, y={$y})
        {if $command then "button_{$id}.config(command=" + $command + ")" else ""}

component Label:
    property text = $text or ""
    property x = $x or 0
    property y = $y or 0

    template:
        label_{$id} = tk.Label(window, text="{$text}")
        label_{$id}.place(x={$x}, y={$y})
"""

# Textual DSL mapping template
TEXTUAL_MAPPING = """
component Window:
    property title = $title

    template:
        class {capitalize($title)}App(App):
            CSS = \"\"\"
            Screen {
                align: center middle;
            }
            \"\"\"

            def compose(self) -> ComposeResult:
                {children}

        if __name__ == "__main__":
            app = {capitalize($title)}App()
            app.run()

component Button:
    property text = $text or "Button"

    template:
        yield Button("{$text}", id="{lowercase($text)}_button")

component Label:
    property text = $text or ""

    template:
        yield Label("{$text}")
"""
```

### DSL Mapping Management

For managing and switching between different mappings:

```python
class MappingRegistry:
    def __init__(self):
        self.mappings = {}

    def register_mapping(self, name, mapping_source):
        """Register a mapping with the registry."""
        parser = DSLParser()
        DSLStandardLibrary.register_standard_functions(parser)

        mapping = parser.parse(mapping_source)
        self.mappings[name] = mapping

    def get_mapping(self, name):
        """Get a registered mapping."""
        if name not in self.mappings:
            raise ValueError(f"Unknown mapping: {name}")
        return self.mappings[name]

    def generate_code(self, component, mapping_name):
        """Generate code for a component using a specific mapping."""
        mapping = self.get_mapping(mapping_name)
        return mapping.apply(component)
```
