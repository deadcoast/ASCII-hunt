# Python Namespace Extractor

A comprehensive tool for extracting and documenting Python code structure. This modular Python package extracts namespaces (classes, functions, etc.) from Python files and formats them in a structured markdown document.

## Features

- **Recursive Directory Processing**: Automatically scan entire project directories
- **Enhanced Type Information Preservation**: Accurately capture complex type annotations
- **Nested Class Support**: Maintain proper class hierarchy in the output
- **Inheritance Information**: Display base classes for each class definition
- **Decorator Preservation**: Capture and display function/method decorators
- **Progress Reporting**: Visual feedback during processing with progress bars
- **Configuration System**: Customize extraction via YAML config files
- **Command-line Interface**: Flexible options for extraction control

## Installation

```bash
# Install from the project directory
pip install .

# Or install in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
# Process a single file
namespace-extractor output.md path/to/file.py

# Process a directory
namespace-extractor output.md path/to/project/

# Process multiple inputs
namespace-extractor output.md file1.py file2.py directory/
```

### Configuration Options

```bash
# Use a configuration file
namespace-extractor output.md path/to/project/ --config sample_config.yaml

# Enable recursive directory processing
namespace-extractor output.md path/to/project/ --recursive

# Include private methods (starting with _)
namespace-extractor output.md path/to/project/ --include-private

# Include dunder methods (__method__)
namespace-extractor output.md path/to/project/ --include-dunder

# Include docstrings
namespace-extractor output.md path/to/project/ --include-docstrings

# Set maximum recursion depth
namespace-extractor output.md path/to/project/ --depth 3

# Exclude files matching patterns
namespace-extractor output.md path/to/project/ --exclude "test_.*\.py" --exclude "__pycache__"

# Include module-level constants
namespace-extractor output.md path/to/project/ --include-vars
```

## Configuration File

Sample configuration file (YAML):

```yaml
include_private: true
include_dunder: false
include_docstrings: true
recursive: true
max_recursion_depth: -1 # -1 means no limit
output_format: "markdown"
indent_size: 4
exclude_patterns:
  - "__pycache__"
  - "venv"
  - "test_.*\\.py"
include_module_vars: true
show_file_path_prefix: true
```

## Project Structure

The project follows a modular design with clear separation of concerns:

- **Parser Module**: Handles file discovery, AST parsing, and namespace extraction
- **Formatter Module**: Processes and structures the extracted data
- **Output Module**: Generates the final markdown output
- **Config Module**: Manages configuration settings

## Output Format

The tool generates a markdown document with Python namespaces organized by directory and file, using the following format:

```python
##GUARD_!_RAIL##

"""
path/to/current/directory
"""
# component_model.py
class ComponentModel:
    def __init__(self):

    def get_grid_x(self, x=None):
    def get_grid_y(self, y=None):
    def get_grid_z(self, z=None):

##GUARD_!_RAIL##
```

## Dependencies

- Python 3.6+
- PyYAML (>=5.1)
- tqdm (>=4.50.0)
