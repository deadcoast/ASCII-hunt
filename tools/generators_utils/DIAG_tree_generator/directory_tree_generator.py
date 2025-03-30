#!/usr/bin/env python3
"""Directory Tree Generator

This script parses a markdown directory tree and creates the corresponding
directory structure with appropriate directory.md files containing their
respective subtrees.
"""

import os
import re
import sys
from typing import Optional


class DirectoryTreeNode:
    """Represents a node (file or directory) in the directory tree."""

    def __init__(
        self,
        name: str,
        is_directory: bool,
        parent: Optional["DirectoryTreeNode"] = None,
    ) -> None:
        """Initialize a DirectoryTreeNode.

        Args:
            name: Name of the node (file or directory).
            is_directory: Whether this node represents a directory.
            parent: Parent node in the tree structure.
        """
        self.name = name
        self.is_directory = is_directory
        self.parent = parent
        self.children: list[DirectoryTreeNode] = []
        self.directory_md_file: str | None = None
        self.path: str = self._calculate_path()

    def _calculate_path(self) -> str:
        """Calculate the full path of this node.

        Returns:
            The full path from root to this node.
        """
        if self.parent is None:
            return self.name
        return os.path.join(self.parent.path, self.name)

    def add_child(self, child: "DirectoryTreeNode") -> None:
        """Add a child node to this node.

        Args:
            child: The child node to add.
        """
        self.children.append(child)
        child.parent = self

    def find_directory_md_file(self) -> str | None:
        """Find the corresponding directory.md file for this directory.

        Returns:
            The name of the directory.md file, or None if not applicable.
        """
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
        """Return string representation of the node.

        Returns:
            String representation showing type and path.
        """
        return f"{'Dir' if self.is_directory else 'File'}: {self.path}"


def parse_tree_line(line: str) -> tuple[int, str, bool]:
    """Parse a single line from the markdown tree.

    Args:
        line: A line from the markdown tree.

    Returns:
        Tuple of (indentation_level, name, is_directory).
    """
    indentation = len(match.group(1)) if (match := re.match(r"^(\s*)", line)) else 0
    # Extract name using regex
    # Looking for patterns like "├── - [ ] directory_name/" or "├── - [ ] file_name.md"
    name_match = re.search(r"[├└]── - \[ \] ([^\n]+)", line)
    if not name_match:
        return indentation, "", False

    name = name_match[1].strip()
    is_directory = name.endswith("/")

    return indentation, name, is_directory


def build_tree(markdown_lines: list[str]) -> DirectoryTreeNode:
    """Build a tree structure from the markdown tree lines.

    Args:
        markdown_lines: Lines from the markdown tree.

    Returns:
        The root node of the tree.
    """
    root = DirectoryTreeNode("", True)  # Root directory

    # Stack to track the current path in the tree
    # Each entry is (node, indentation_level)
    stack: list[tuple[DirectoryTreeNode, int]] = [(root, -1)]

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


def extract_subtree(markdown_lines: list[str], target_dir_line: int) -> list[str]:
    """Extract the subtree for a specific directory from the markdown tree.

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
    # with greater indentation until we reach another line with indentation
    # less than or equal to the target directory's indentation
    subtree_lines = [markdown_lines[target_dir_line]]

    for line in markdown_lines[target_dir_line + 1 :]:
        if not line.strip() or "```" in line:
            continue  # Skip empty lines and markdown code block markers

        current_indentation, _, _ = parse_tree_line(line)
        if current_indentation <= target_indentation:
            break  # End of subtree

        subtree_lines.append(line)

    return subtree_lines


def find_directory_lines(markdown_lines: list[str]) -> dict[str, int]:
    """Find all directory lines in the markdown tree and their line numbers.

    Args:
        markdown_lines: Lines from the markdown tree.

    Returns:
        Dictionary mapping directory paths to their line numbers.
    """
    directory_lines: dict[str, int] = {}
    current_path: list[str] = []
    indentation_stack: list[tuple[int, str]] = [(-1, "")]  # (indentation, path)

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


def _collect_directories(node: DirectoryTreeNode, path: str = "") -> list[str]:
    """Collect all directory paths in the tree.

    Args:
        node: The current node in the tree.
        path: The current path.

    Returns:
        List of directory paths.
    """
    directories = []
    current_path = os.path.join(path, node.name) if path else node.name

    if node.is_directory:
        directories.append(current_path)

    for child in node.children:
        if child.is_directory:
            directories.extend(_collect_directories(child, current_path))

    return directories


def create_directory_structure(markdown_tree: str, output_dir: str = "output") -> None:
    """Create the directory structure from the markdown tree.

    Args:
        markdown_tree: The markdown tree content.
        output_dir: The output directory where the structure will be created.
    """
    lines = markdown_tree.split("\n")
    root = build_tree(lines)
    directory_lines = find_directory_lines(lines)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create all directories first
    for directory in _collect_directories(root):
        if directory:  # Skip empty directory names
            os.makedirs(os.path.join(output_dir, directory), exist_ok=True)

    # Create directory.md files
    for directory, line_num in directory_lines.items():
        if not directory:  # Skip empty directory names
            continue

        subtree = extract_subtree(lines, line_num)
        if not subtree:  # Skip if no subtree found
            continue

        # Create directory.md file
        md_path = os.path.join(output_dir, directory, "directory.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("```\n")
            f.write("\n".join(subtree))
            f.write("\n```\n")


def main() -> None:
    """Main entry point of the script."""
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

        try:
            with open(input_file, encoding="utf-8") as f:
                markdown_tree = f.read()
            create_directory_structure(markdown_tree, output_dir)
            print(f"Directory structure created in {output_dir}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: directory_tree_generator.py <input_file> [output_dir]")
        sys.exit(1)


if __name__ == "__main__":
    main()
