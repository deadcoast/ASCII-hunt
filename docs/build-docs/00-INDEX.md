# Index

1. [Python Stack](docs/build-docs/hunt-02.python/)
   - [01-python-stack.md](docs/build-docs/hunt-02.python/02-1.python-stack.md)
   - [02-python-front-end.md](docs/build-docs/hunt-02.python/02-2.python-front-end.md)
   - [03-python-back-end.md](docs/build-docs/hunt-02.python/02-3.python-back-end.md)
   - 1.1 **NumPy**: For grid analysis and mathematical operations
   - 1.2 **OpenCV**: For pattern recognition and contour detection
   - 1.3 **NetworkX**: For relationship modeling between UI elements
   - 1.4 **PyQt5/PySide**: For the canvas UI (PySide is essentially the official Qt for Python, offering similar functionality to PyQt5 with different licensing)
2. [Algorithms](docs/build-docs/hunt-04.algorithms/)
   - [01-algorithms.md](docs/build-docs/hunt-04.algorithms/04-1.algorithms.md)
   - [02-algorithm-architecture.md](docs/build-docs/hunt-04.algorithms/04-2.algorithm-architecture.md)
   - 2.1 **Flood Fill Algorithm**: Essential for identifying enclosed spaces within boxes and determining component boundaries.
   - 2.2 **Connected Component Analysis**: Critical for grouping related characters that form logical UI elements like buttons or input fields.
   - 2.3 **Hierarchical Clustering**: Necessary for establishing the nesting relationship between components (e.g., which buttons are inside which panels).
   - 2.4 **Decision Trees**: Valuable for classification of UI elements based on surrounding character patterns and context.
   - 2.5 **Dynamic Programming**: Important for optimizing recognition of repeated patterns and efficiently processing large ASCII interfaces.
3. [Architecture](docs/build-docs/hunt-01.system_architecture/)
   - [01-system-architecture.md](docs/build-docs/hunt-01.system_architecture/01-1.sys-architecture.md)
   - [02-system-interpreter.md](docs/build-docs/hunt-01.system_architecture/01-2.interpreter.md)
   - [03-system-integration.md](docs/build-docs/hunt-01.system_architecture/01-3.integration.md)
   - 3.1 **Abstract Component Model**: The foundation of the system - a representation of UI elements independent of any specific UI framework.
   - 3.2 **Modular Code Generation**: Built on top of the Abstract Component Model, this allows generating code for different frameworks from the same abstract representation.
   - 3.3 **Pluggable Backend Architecture**: The system design that enables adding new code generators without modifying core logic.
   - 4.2 **Component Mapping DSL**: A simple language for mapping recognized components to code templates.
4. [Front End](docs/build-docs/hunt-01.system_architecture/02-2.python-front-end/)
   - [01-python-front-end.md](docs/build-docs/hunt-01.system_architecture/02-2.python-front-end.md)
   - Plan the front end in detail and how it will integrate with the back end.
5. [Back End](docs/build-docs/hunt-01.system_architecture/02-3.python-back-end/)
   - [01-python-back-end.md](docs/build-docs/hunt-01.system_architecture/02-3.python-back-end.md)
   - Structure out the comprehensive back end, how it will operate, and how it will complete its task.
6. [DSL](docs/build-docs/hunt-03.dsl/)
   - [01-dsl-intro.md](docs/build-docs/hunt-03.dsl/03-1.dsl-intro.md)
   - [02-dsl-specifications.md](docs/build-docs/hunt-03.dsl/03-2.dsl-specifications.md)
   - [03-dsl-rules.md](docs/build-docs/hunt-03.dsl/03-3.dsl-rules.md)
   - [04-dsl-dictionary.md](docs/build-docs/hunt-03.dsl/03-4.dsl-dictionary.md)
   - 6.1 **Recognition DSL**: A declarative language for defining patterns and rules for recognizing UI elements in the ASCII grid.
   - Currently, I have been working on a language to operate with LaTeX. It will be perfect for this framework.
   - `hunt` : Tab spaced Syntax, with a heavy focus on Bracket encapsulation.
   - `hag` priortizes encapsulating simple commands in a strict "Hierarchal Alignment" Sytax of.
   - `<perp>` - Perpetual Component Definition 2. `[INIT]` - Initiate an asset or tool 3. `{param}` - Paramaters assignment 4. `(val)` - Values of the paramater 5. EXEC - Execute the code block
   - Finalize bracket-level grammar rules (`<>`, `[]`, `{}`, `()`, `><`)
   - Select Advanced parser implementation
   - Finalize a platform for CLI interpreter, Jupyter plugin, Python Library, Custom Built CLI
   - Create a Markdown spec sheet (I can help generate that too!)
   - **Map DSL to Python Decorators / Classes** so you can register block handlers (`[prime]`, `{bind}` etc.)
   - **Create a lightweight interpreter** or static analyzer for validating bracket nesting + structure.

# Directory Tree

```
src/
├── core/
│   ├── dsl/
│   │   ├── __init__.py
│   │   ├── dsl_command_dispatcher.py
│   │   ├── dsl_error.py
│   │   ├── dsl_error_handler.py
│   │   └── dsl_interpreter.py
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── code_generator.py
│   │   ├── dsl_code_generator.py
│   │   └── python_tkinter_generator.py
│   ├── grid/
│   │   ├── __init__.py
│   │   └── ascii_grid.py
│   ├── recognition/
│   │   ├── __init__.py
│   │   ├── dsl_parser.py
│   │   ├── dsl_pattern_registry.py
│   │   └── dsl_recognition_processor.py
│   ├── __init__.py
│   └── py.typed
├── engine/
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── component_analysis.py
│   │   ├── component_analysis_two.py
│   │   ├── decision_tree.py
│   │   ├── decision_tree_classifier.py
│   │   ├── spatial_analysis.py
│   │   └── temporal_reasoning.py
│   ├── modeling/
│   │   ├── __init__.py
│   │   ├── component_model_representation.py
│   │   ├── component_properties.py
│   │   └── drawing_mode.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ascii_processor.py
│   │   ├── contour_detection_processor.py
│   │   ├── feature_extraction_processor.py
│   │   ├── flood_fill_data_processor.py
│   │   ├── flood_fill_processor.py
│   │   ├── processing_pipeline.py
│   │   └── transformation_pipeline.py
│   ├── __init__.py
│   └── py.typed
├── interface/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── framework_adapter.py
│   │   ├── tkinter_adapter.py
│   │   └── tkinter_plugin.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── application_controller.py
│   │   ├── ascii_ui_translation_engine.py
│   │   ├── cli.py
│   │   ├── dsl_visualizer.py
│   │   └── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── ascii_grid_widget.py
│   │   ├── code_composition_engine.py
│   │   ├── component_template_engine.py
│   │   ├── content_switcher.py
│   │   ├── dsl_grid.py
│   │   ├── property_editor_widget.py
│   │   ├── tabbed_content.py
│   │   ├── tabbed_content.tcss
│   │   └── tabs.py
│   ├── __init__.py
│   └── py.typed
├── patterns/
│   ├── definitions/
│   │   ├── __init__.py
│   │   ├── ascii_examples.py
│   │   ├── code_template.py
│   │   ├── component_properties_template.py
│   │   ├── pattern_learner.py
│   │   ├── pattern_matcher.py
│   │   ├── pattern_optimizer.py
│   │   ├── tabbed_content_example.py
│   │   └── tk_mapping_template.py
│   ├── matching/
│   │   ├── __init__.py
│   │   ├── flood_fill_processor.py
│   │   ├── grid_transformer.py
│   │   ├── hierarchical_clustering.py
│   │   └── parsing_algorithms.py
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── dsl_parser.py
│   │   ├── dsl_pattern_registry.py
│   │   ├── dsl_recognition_processor.py
│   │   └── pattern_recognition_processor.py
│   ├── __init__.py
│   └── py.typed
├── processing/
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── neuromorphic_analysis.py
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── component_mapping.py
│   │   ├── component_overlay_manager.py
│   │   └── flood_fill_component.py
│   ├── validation/
│   │   ├── __init__.py
│   │   └── component_classification_processor.py
│   ├── __init__.py
│   └── py.typed
├── utils/
│   ├── cache/
│   │   └── __init__.py
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── functional_relationship_manager.py
│   │   ├── performance_monitor.py
│   │   ├── qitia_analyzer.py
│   │   └── sansia_importer.py
│   ├── plugins/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── ascii_utils.py
│   ├── cache_manager.py
│   ├── extension_point.py
│   ├── dsl_utils.py
│   ├── plugin.py
│   ├── plugin_manager.py
│   ├── py.typed
│   └── storage_providers.py
├── __init__.py
└── generate_tree.py
```
