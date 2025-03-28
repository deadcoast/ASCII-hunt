# Directory Tree Generator

This package contains scripts to generate a directory structure from a markdown directory tree, where each directory contains its own `{directory_name}_directory.md` file with a snippet of the directory tree relevant to that directory.

## Features

- Parses a markdown directory tree structure
- Creates the complete directory structure
- Generates directory.md files for each directory containing their respective subtree
- Intelligently determines directory.md file names from the tree or creates default names
- Preserves the exact formatting of the directory tree in the output files

## Files

1. `directory_tree_generator.py` - The main script that parses a directory tree and creates the structure
2. `directory_tree_runner.py` - A helper script that extracts the tree from an input file and runs the generator

## Installation

1. Save both Python scripts to your working directory.
2. Ensure you have Python 3.6+ installed.
3. No additional dependencies are required.

## Usage

### Basic Usage

```bash
python directory_tree_runner.py <input_file> [output_directory]
```

- `<input_file>`: Path to a file containing the markdown directory tree
- `[output_directory]`: Optional output directory (defaults to "generated_structure")

### Example

1. Create a file named `tree.md` with your directory tree structure:

```
├── src/
│   ├── - [ ] adapters/
│   │   ├── - [ ] adapter_directory.md
│   │   └── - [ ] tkinter_adapter.md
...
```

2. Run the script:

```bash
python directory_tree_runner.py tree.md my_project
```

3. This will create the directory structure under `my_project/` with each directory containing its own directory.md file.

### Advanced Usage

You can also use the `directory_tree_generator.py` script directly:

```bash
python directory_tree_generator.py <tree_file> [output_directory]
```

This is useful if you have a file that contains only the tree structure without additional content.

## How It Works

1. The script parses the markdown tree to identify directories and files
2. For each directory, it extracts the relevant subtree (the directory and all its immediate children)
3. It creates the directory structure while maintaining the hierarchy
4. For each directory, it creates a directory.md file with the subtree content

## Customization

If you need to modify the behavior:

- Edit `directory_tree_generator.py` to change how directory.md files are named or formatted
- Edit `directory_tree_runner.py` to change how the tree is extracted from input files

## Troubleshooting

- If the directory structure isn't created correctly, ensure your markdown tree follows the expected format with proper indentation and directory markers (ending with /)
- If directory.md files are missing or have incorrect content, check that the tree extraction is working correctly

## License

This software is provided as-is without any warranties or guarantees.
