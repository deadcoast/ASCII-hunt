# System Architecture Diagrams

This directory contains modular Mermaid diagram files for the ASCII-hunt system architecture.

## Structure

```
system-architecture/
├── main.mmd              # Main diagram file that imports all modules
├── core.mmd             # Core System components and dependencies
├── dsl.mmd              # DSL Processing components and dependencies
├── recognition.mmd      # Recognition System components and dependencies
├── modeling.mmd         # Modeling System components and dependencies
├── generation.mmd       # Code Generation components and dependencies
├── plugins.mmd          # Plugin System components and dependencies
├── processing.mmd       # Processing System components and dependencies
├── interface.mmd        # Interface components and dependencies
├── patterns.mmd         # Pattern System components and dependencies
├── utils.mmd           # Utility components and dependencies
├── engine.mmd          # Engine components and dependencies
├── testing.mmd         # Testing infrastructure and test categories
├── error_handling.mmd  # Error handling flows and recovery actions
├── persistence.mmd     # Data storage and caching system
├── logging.mmd         # Logging system and management
├── combine_diagrams.py # Script to combine all diagrams
└── README.md           # This documentation file
```

## Subsystem Categories

The diagrams are organized into four main categories:

1. **Core Processing**

   - `core.mmd`: Core system functionality
   - `dsl.mmd`: Domain-specific language processing
   - `recognition.mmd`: Component recognition
   - `modeling.mmd`: Hierarchical modeling
   - `generation.mmd`: Code generation

2. **System Infrastructure**

   - `engine.mmd`: Processing engine
   - `plugins.mmd`: Plugin system
   - `processing.mmd`: Data processing
   - `patterns.mmd`: Pattern management

3. **User Interface & Integration**

   - `interface.mmd`: User interface components
   - `utils.mmd`: Utility functions
   - `persistence.mmd`: Data persistence

4. **System Support**
   - `testing.mmd`: Testing infrastructure
   - `error_handling.mmd`: Error management
   - `logging.mmd`: Logging system

## Usage

1. Each `.mmd` file contains a specific subsystem's components and their internal dependencies
2. The `main.mmd` file combines all subsystems and defines the overall layout
3. Styles are defined in `main.mmd` and applied consistently across all modules

## Combining Diagrams

### 1. Using the Python Script (Recommended)

```bash
# From the system-architecture directory
./combine_diagrams.py

# The script will generate combined_diagram.mmd
```

The script provides:

- Automatic module ordering based on dependencies
- Style consistency enforcement
- Validation of required sections
- Error handling and reporting
- Clean combination of cross-module dependencies

### 2. Manual Combination

If manual combination is needed, follow this order:

1. main.mmd (base structure and styles)
2. Core Processing:
   - core.mmd
   - dsl.mmd
   - recognition.mmd
   - modeling.mmd
   - generation.mmd
3. System Infrastructure:
   - engine.mmd
   - plugins.mmd
   - processing.mmd
   - patterns.mmd
4. User Interface & Integration:
   - interface.mmd
   - utils.mmd
   - persistence.mmd
5. System Support:
   - testing.mmd
   - error_handling.mmd
   - logging.mmd

## Style Guide

### Colors and Styling

- Each subsystem category has its own color scheme:
  - Core Processing: Shades of blue (#e6f3ff)
  - System Infrastructure: Shades of green (#e6ffe6)
  - UI & Integration: Shades of orange (#ffe6cc)
  - System Support: Shades of purple (#f2e6ff)

### Layout Guidelines

- Use `direction TB` (top to bottom) for main flows
- Group related components in subgraphs
- Use consistent naming conventions
- Keep component names clear and concise

## Modifying the Diagrams

1. **Adding New Components**

   - Add to the appropriate subsystem file
   - Follow the established style guidelines
   - Update cross-module dependencies in main.mmd

2. **Adding New Subsystems**

   - Create a new .mmd file
   - Add to the appropriate category
   - Update combine_diagrams.py
   - Add cross-module dependencies

3. **Updating Dependencies**
   - Direct dependencies: Use solid arrows (`-->`)
   - Data flow: Use dotted arrows (`-.->`)
   - Add dependencies in the respective files

## Validation

The system performs automatic validation:

- Required sections presence
- Style consistency
- Cross-module dependency integrity
- File structure correctness

## Best Practices

1. **Maintainability**

   - Keep subsystems focused and cohesive
   - Document complex dependencies
   - Use meaningful component names

2. **Collaboration**

   - Work on separate subsystem files
   - Review changes for style consistency
   - Test combined diagram after changes

3. **Version Control**
   - Commit individual subsystem changes
   - Include meaningful commit messages
   - Review diffs before committing

# Mermaid Diagram Validator and Combiner

A robust Python script for validating and combining modular Mermaid diagrams with comprehensive reporting.

## Overview

This script combines two essential functions:

1. Combining multiple modular Mermaid diagrams into a single unified diagram
2. Validating that all components are correctly transferred during combination

The script uses the Rich library for beautiful terminal output and provides detailed step-by-step reporting of the entire process.

## Process Flow

The script operates in four distinct steps:

### STEP 1: Input Collection (`> sys.INPUT[IN] *`)

- Scans all modular Mermaid diagram files (\*.mmd)
- Extracts and catalogs all components
- Displays real-time component collection in the terminal
- Creates a baseline inventory for validation

### STEP 2: Output Collection (`> sys.OUTPUT[OUT] *`)

- Combines all modular diagrams into `combined_diagram.mmd`
- Extracts components from the combined diagram
- Displays components as they're processed
- Maintains component relationships and styles

### STEP 3: Validation (`> sys.VALIDATION *`)

- Compares input and output component lists
- Validates each component's transfer
- Provides visual status indicators (✅/❌)
- Shows detailed validation results

### STEP 4: Reporting (`> sys.REPORTS *`)

- Generates validation statistics
- Lists any failed/null components
- Provides a comprehensive validation summary
- Shows total counts of successes and failures

## Terminal Output Format

### Headers

Each section uses consistent ASCII border formatting:

```
# -----------------
# > SECTION_TITLE *
# -----------------
```

### Dynamic Separator

Sections are separated by a dynamic-width separator that adjusts to terminal size:

```
<:----------------------------------------:>
```

### Static Labels

- `[IN]`: Input component indicator
- `[OUT]`: Output component indicator
- `[VALIDATED]`: Success indicator
- `[--- NULL ---]`: Failure indicator

### Dynamic Values

- `{input_module}`: Source component name
- `{output_module}`: Combined diagram component name
- `{STATUS}`: ✅ or ❌
- `{RESULT}`: [VALIDATED] or [--- NULL ---]
- `{num_validated}`: Total successful validations
- `{num_failed}`: Total failed validations

## Example Output

```
<:----------------------------------------:>

# -----------------
# > sys.INPUT[IN] *
# -----------------

> sys.[IN]: core.mmd:ASCIIGrid["ASCIIGrid\n(hunt.core.grid)"]

<:----------------------------------------:>

# -------------------
# > sys.OUTPUT[OUT] *
# -------------------

> sys.[OUT]: core.mmd:ASCIIGrid["ASCIIGrid\n(hunt.core.grid)"]

<:----------------------------------------:>

# ------------------
# > sys.VALIDATION *
# ------------------

> sys.[IN]: core.mmd | [OUT]: core.mmd ✅ -> [VALIDATED]

<:----------------------------------------:>

# ---------------
# > sys.REPORTS *
# ---------------

> sys.[✅]: 1
> sys.[❌]: 0

> sys.report: init == [---NULL OUTPUTS---]

<:----------------------------------------:>
```

## Implementation Details

### DiagramProcessor Class

The main class that handles all processing:

- `collect_inputs()`: STEP 1 - Collects and displays input components
- `combine_and_collect_outputs()`: STEP 2 - Combines diagrams and shows outputs
- `validate_components()`: STEP 3 - Validates component transfer
- `generate_report()`: STEP 4 - Generates final validation report

### Helper Methods

- `_extract_components()`: Extracts component definitions
- `_extract_dependencies()`: Extracts component relationships
- `_extract_styles()`: Extracts component styles
- `print_header()`: Formats section headers
- `print_separator()`: Prints dynamic separators

## Testing

The script includes comprehensive tests that validate:

- Input collection accuracy
- Diagram combination correctness
- Component validation logic
- Report generation accuracy
- Null output handling
- Successful validation cases

Each test ensures proper formatting and accurate reporting of results.

## Usage

```bash
python3 validate_combined.py
```

The script will process all `.mmd` files in the current directory (except `combined_diagram.mmd`), combine them, validate the combination, and generate a detailed report.
