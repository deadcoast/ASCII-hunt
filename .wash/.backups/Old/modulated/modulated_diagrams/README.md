# System Architecture Diagrams

This directory contains modular Mermaid diagram files for the ASCII-hunt system architecture.

## Structure

```
system-architecture/
├── main.mmd           # Main diagram file that imports all modules
├── core.mmd          # Core System components and dependencies
├── dsl.mmd           # DSL Processing components and dependencies
├── recognition.mmd   # Recognition System components and dependencies
├── modeling.mmd      # Modeling System components and dependencies
├── generation.mmd    # Code Generation components and dependencies
├── combine_diagrams.py # Script to combine all diagrams
└── README.md         # This documentation file
```

## Usage

1. Each `.mmd` file contains a specific subsystem's components and their internal dependencies
2. The `main.mmd` file combines all subsystems and defines the overall layout
3. Styles are defined in `main.mmd` and applied in each module file

## Combining Diagrams

There are two ways to generate the complete diagram:

### 1. Using the Python Script

```bash
# From the system-architecture directory
./combine_diagrams.py

# The script will generate combined_diagram.mmd
```

The script:

- Combines all module files in the correct order
- Handles duplicate style definitions
- Preserves the overall structure from main.mmd
- Outputs a single, ready-to-use Mermaid diagram file

### 2. Manual Combination

If you prefer to combine manually, copy the contents in this order:

1. main.mmd (first for styles and layout)
2. core.mmd
3. dsl.mmd
4. recognition.mmd
5. modeling.mmd
6. generation.mmd

## Benefits

- **Maintainability**: Each subsystem is in its own file
- **Readability**: Smaller, focused files are easier to understand
- **Reusability**: Modules can be reused in different diagrams
- **Version Control**: Easier to track changes per subsystem
- **Collaboration**: Different team members can work on different subsystems

## Style Guide

- All components use consistent styling defined in `main.mmd`
- Each subsystem has its own color scheme
- Text is black for maximum readability
- Boxes have grey borders (#333) with 2px width

## Modifying the Diagram

1. To modify a subsystem, edit its corresponding `.mmd` file
2. Run `./combine_diagrams.py` to regenerate the combined diagram
3. The script will automatically handle:
   - Proper file ordering
   - Style consistency
   - Cross-system dependencies
