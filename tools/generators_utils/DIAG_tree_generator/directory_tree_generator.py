#!/usr/bin/env python3
"""
Directory Tree Generator

This script parses a markdown directory tree and creates the corresponding
directory structure with appropriate directory.md files containing their
respective subtrees.
"""

import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Set


class DirectoryTreeNode:
    """Represents a node (file or directory) in the directory tree."""

    def __init__(self, name: str, is_directory: bool, parent=None):
        self.name = name
        self.is_directory = is_directory
        self.parent = parent
        self.children = []
        self.directory_md_file = (
            None  # Name of the corresponding directory.md file if exists
        )
        self.path = self._calculate_path()

    def _calculate_path(self) -> str:
        """Calculate the full path of this node."""
        if self.parent is None:
            return self.name
        return os.path.join(self.parent.path, self.name)

    def add_child(self, child):
        """Add a child node to this node."""
        self.children.append(child)
        child.parent = self

    def find_directory_md_file(self) -> Optional[str]:
        """Find the corresponding directory.md file for this directory."""
        if not self.is_directory:
            return None

        # Check if any child is a directory.md file
        for child in self.children:
            if not child.is_directory and "_directory.md" in child.name.lower():
                return child.name

        # Default to directory_name_directory.md
        dir_name = self.name.rstrip("/")
        return f"{dir_name}_directory.md"

    def __repr__(self) -> str:
        return f"{'Dir' if self.is_directory else 'File'}: {self.path}"


def parse_tree_line(line: str) -> Tuple[int, str, bool]:
    """
    Parse a single line from the markdown tree.

    Args:
        line: A line from the markdown tree.

    Returns:
        Tuple of (indentation_level, name, is_directory).
    """
    # Calculate indentation level (counting spaces before any content)
    match = re.match(r"^(\s*)", line)
    if match:
        indentation = len(match.group(1))
    else:
        indentation = 0

    # Extract name using regex
    # Looking for patterns like "├── - [ ] directory_name/" or "├── - [ ] file_name.md"
    name_match = re.search(r"[├└]── - \[ \] ([^\n]+)", line)
    if not name_match:
        return indentation, "", False

    name = name_match.group(1).strip()
    is_directory = name.endswith("/")

    return indentation, name, is_directory


def build_tree(markdown_lines: List[str]) -> DirectoryTreeNode:
    """
    Build a tree structure from the markdown tree lines.

    Args:
        markdown_lines: Lines from the markdown tree.

    Returns:
        The root node of the tree.
    """
    root = DirectoryTreeNode("", True)  # Root directory

    # Stack to track the current path in the tree
    # Each entry is (node, indentation_level)
    stack = [(root, -1)]

    for line in markdown_lines:
        if not line.strip() or "```" in line:
            continue  # Skip empty lines and markdown code block markers

        indentation, name, is_directory = parse_tree_line(line)
        if not name:
            continue  # Skip lines that don't contain valid node information

        # Pop from stack until we find a parent with lower indentation
        while stack and indentation <= stack[-1][1]:
            stack.pop()

        if not stack:
            # If stack is empty, we've popped too much
            # This shouldn't happen with well-formed input
            stack.append((root, -1))

        # Create new node and add to parent
        parent, _ = stack[-1]
        node = DirectoryTreeNode(name, is_directory, parent)
        parent.add_child(node)

        # If this is a directory, push it onto the stack
        if is_directory:
            stack.append((node, indentation))

    return root


def extract_subtree(markdown_lines: List[str], target_dir_line: int) -> List[str]:
    """
    Extract the subtree for a specific directory from the markdown tree.

    Args:
        markdown_lines: Lines from the markdown tree.
        target_dir_line: Line number (index) of the target directory.

    Returns:
        List of lines that form the subtree for the target directory.
    """
    if target_dir_line >= len(markdown_lines):
        return []

    # Get the indentation level of the target directory
    target_indentation, _, _ = parse_tree_line(markdown_lines[target_dir_line])

    # The subtree includes the target directory line and all subsequent lines
    # with greater indentation until we reach another line with indentation less than
    # or equal to the target directory's indentation
    subtree_lines = [markdown_lines[target_dir_line]]

    for line in markdown_lines[target_dir_line + 1 :]:
        if not line.strip() or "```" in line:
            continue  # Skip empty lines and markdown code block markers

        current_indentation, _, _ = parse_tree_line(line)
        if current_indentation <= target_indentation:
            break  # End of subtree

        subtree_lines.append(line)

    return subtree_lines


def find_directory_lines(markdown_lines: List[str]) -> Dict[str, int]:
    """
    Find all directory lines in the markdown tree and their corresponding line numbers.

    Args:
        markdown_lines: Lines from the markdown tree.

    Returns:
        Dictionary mapping directory paths to their line numbers.
    """
    directory_lines = {}
    current_path = []
    indentation_stack = [(-1, "")]  # (indentation, path)

    for i, line in enumerate(markdown_lines):
        if not line.strip() or "```" in line:
            continue  # Skip empty lines and markdown code block markers

        indentation, name, is_directory = parse_tree_line(line)
        if not name:
            continue  # Skip lines that don't contain valid node information

        # Pop from indentation stack until we find a parent with lower indentation
        while indentation_stack and indentation <= indentation_stack[-1][0]:
            indentation_stack.pop()
            if current_path:
                current_path.pop()

        # Calculate the current path
        if indentation_stack:
            current_path_str = os.path.join(indentation_stack[-1][1], name)
        else:
            current_path_str = name

        # If this is a directory, add to the result and push onto the stack
        if is_directory:
            directory_lines[current_path_str] = i
            indentation_stack.append((indentation, current_path_str))
            current_path.append(current_path_str)

    return directory_lines


def create_directory_structure(markdown_tree: str, output_dir: str = "output"):
    """
    Create the directory structure with directory.md files from the markdown tree.

    Args:
        markdown_tree: The markdown tree as a string.
        output_dir: The base output directory where the structure will be created.
    """
    # Split the tree into lines
    markdown_lines = markdown_tree.splitlines()

    # Find all directory lines
    directory_lines = find_directory_lines(markdown_lines)

    # Build the tree structure
    root = build_tree(markdown_lines)

    # Collect all directory nodes in the tree
    directories = []
    directory_paths = set()

    def collect_directories(node, path=""):
        if node.is_directory:
            full_path = os.path.join(path, node.name)
            directories.append((node, full_path))
            directory_paths.add(full_path)

        for child in node.children:
            child_path = os.path.join(path, node.name) if node.name else path
            collect_directories(child, child_path)

    collect_directories(root)

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each directory
    for node, path in directories:
        if not node.name:
            continue  # Skip root

        # Determine the directory name (remove trailing slash)
        dir_name = node.name.rstrip("/")

        # Determine the directory.md file name
        directory_md_name = node.find_directory_md_file()

        # Calculate the full path to the directory
        dir_path = os.path.join(output_dir, path.strip("/"))

        # Create the directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Extract the subtree for this directory
        full_path_in_tree = path.strip("/") + ("/" if path else "")
        if full_path_in_tree in directory_lines:
            line_num = directory_lines[full_path_in_tree]
            subtree_lines = extract_subtree(markdown_lines, line_num)

            # Write the subtree to the directory.md file
            md_file_path = os.path.join(dir_path, directory_md_name)
            with open(md_file_path, "w") as f:
                f.write("```\n")
                f.write("\n".join(subtree_lines))
                f.write("\n```\n")

            print(f"Created {md_file_path}")


def main():
    """Main entry point for the script."""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            return

        with open(input_file, "r") as f:
            markdown_tree = f.read()
    else:
        print(
            "Please provide the path to a markdown file containing the directory tree."
        )
        return

    output_dir = "generated_structure"
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    create_directory_structure(markdown_tree, output_dir)
    print(f"Directory structure created in '{output_dir}'")


if __name__ == "__main__":
    main()
