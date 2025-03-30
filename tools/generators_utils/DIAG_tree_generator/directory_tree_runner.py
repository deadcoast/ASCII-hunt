#!/usr/bin/env python3
"""Directory Tree Runner

This script extracts the directory tree from the provided input file
and runs the directory tree generator script to create the directory structure.
"""

import os
import re
import sys
import tempfile

from directory_tree_generator import create_directory_structure


def extract_tree_from_file(file_path):
    """Extract the directory tree from the input file.

    Args:
        file_path: Path to the input file.

    Returns:
        The directory tree as a string.
    """
    with open(file_path) as f:
        content = f.read()

    if matches := re.findall(r"```(.*?)```", content, re.DOTALL):
        return matches[0].strip()

    # If no code blocks found, return the entire content
    return content


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python directory_tree_runner.py <input_file> [output_dir]")
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "generated_structure"
    # Extract the directory tree from the input file
    tree_content = extract_tree_from_file(input_file)

    # Write the tree to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as tmp:
        tmp.write(tree_content)
        temp_file_path = tmp.name

    try:
        # Create the directory structure
        create_directory_structure(tree_content, output_dir)
        print(f"Directory structure created in '{output_dir}'")
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


if __name__ == "__main__":
    main()
