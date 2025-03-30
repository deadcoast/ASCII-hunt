# File: namespace_extractor/parser.py
"""Parser module for extracting namespaces from Python files."""

import ast
import os
import re
import typing
from typing import Any

from tqdm import tqdm

from .config import ExtractorConfig


def find_python_files(start_path: str, config: ExtractorConfig) -> list[str]:
    """Find Python files by walking through directories recursively.

    Args:
        start_path: Starting directory or file path
        config: Configuration settings

    Returns:
        List of Python file paths
    """
    python_files = []

    # Handle the case where start_path is a file
    if os.path.isfile(start_path) and start_path.endswith(".py"):
        return [start_path]

    # Handle the case where start_path is a directory
    if os.path.isdir(start_path):
        # Get total file count for progress bar (if recursive)
        total_files = 0
        if config.recursive:
            for _, _, files in os.walk(start_path):
                total_files += sum(bool(f.endswith(".py")) for f in files)

        # Use a progress bar for file discovery
        with tqdm(
            total=total_files, desc="Discovering Python files", disable=total_files == 0
        ) as pbar:
            for root, _, files in os.walk(start_path):
                # Check recursion depth
                if config.max_recursion_depth >= 0:
                    relative_path = os.path.relpath(root, start_path)
                    current_depth = relative_path.count(os.sep) + (
                        0 if relative_path == "." else 1
                    )
                    if current_depth > config.max_recursion_depth:
                        continue

                # Check for excluded patterns
                if any(re.search(pattern, root) for pattern in config.exclude_patterns):
                    continue

                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)

                        # Check if file matches any exclude pattern
                        if any(
                            re.search(pattern, file)
                            for pattern in config.exclude_patterns
                        ):
                            continue

                        python_files.append(file_path)
                        pbar.update(1)

                # If not recursive, break after first level
                if not config.recursive:
                    break

    return python_files


def extract_function_signature(
    source_lines: list[str],
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    indent_level: int = 0,
) -> str:
    """Extract the signature of a function or method from the source code.

    Args:
        source_lines: List of source code lines
        node: AST node representing a function or method
        indent_level: Indentation level

    Returns:
        Function signature as string
    """
    try:
        # Get the line number (0-indexed)
        line_idx = node.lineno - 1

        # Start with the first line of the function
        line = source_lines[line_idx]

        # Extract the part from 'def' to the colon
        signature = line[indent_level:] if indent_level > 0 else line
        # Handle multiline function signatures
        paren_count = signature.count("(") - signature.count(")")
        bracket_count = signature.count("[") - signature.count("]")
        brace_count = signature.count("{") - signature.count("}")
        current_idx = line_idx

        while (
            paren_count > 0 or bracket_count > 0 or brace_count > 0
        ) and current_idx + 1 < len(source_lines):
            current_idx += 1
            next_line = source_lines[current_idx].strip()
            signature += f" {next_line}"
            paren_count += next_line.count("(") - next_line.count(")")
            bracket_count += next_line.count("[") - next_line.count("]")
            brace_count += next_line.count("{") - next_line.count("}")

        # Extract only up to the colon
        if ":" in signature:
            signature = signature.split(":", 1)[0]

        # Ensure we capture async keywords
        if isinstance(node, ast.AsyncFunctionDef) and not signature.strip().startswith(
            "async "
        ):
            signature = f"async {signature}"

        return signature

    except Exception as e:
        print(f"Error extracting function signature for {node.name}: {e!s}")
        return f"def {node.name}(...)"


def extract_decorators(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[str]:
    """Extract decorator names from a function or class node.

    Args:
        node: AST node to extract decorators from

    Returns:
        List of decorator names
    """

    def get_attribute_parts(node: ast.Attribute | ast.Name) -> list[str]:
        """Helper function to extract parts from an attribute chain.

        Args:
            node: AST node to extract parts from

        Returns:
            List of attribute parts
        """
        parts: list[str] = []
        current: ast.Attribute | ast.Name = node

        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = typing.cast(ast.Attribute | ast.Name, current.value)

        if isinstance(current, ast.Name):
            parts.insert(0, current.id)

        return parts

    decorator_parts: list[str] = []

    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            decorator_parts.append(decorator.id)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                decorator_parts.append(decorator.func.id)
            elif isinstance(decorator.func, ast.Attribute):
                parts = get_attribute_parts(decorator.func)
                if parts:
                    decorator_parts.append(".".join(parts))
        elif isinstance(decorator, ast.Attribute):
            parts = get_attribute_parts(decorator)
            if parts:
                decorator_parts.append(".".join(parts))

    return decorator_parts


def extract_namespaces(
    file_path: str, config: ExtractorConfig
) -> tuple[str, str, list[dict[str, Any]]]:
    """Extract namespaces (classes and functions) from a Python file.

    Args:
        file_path: Path to the Python file
        config: Configuration settings

    Returns:
        Tuple containing directory path, filename, and list of extracted namespaces
    """
    try:
        # Get directory and filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Read the Python file
        with open(file_path, encoding="utf-8") as file:
            source_code = file.read()
            source_lines = source_code.splitlines()

        # Parse the Python code
        tree = ast.parse(source_code)

        # Extract namespaces
        namespaces = []

        # Process module-level variables if configured
        if config.include_module_vars:
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            namespaces.append(
                                {
                                    "type": "variable",
                                    "name": target.id,
                                    "value": (
                                        ast.unparse(node.value)
                                        if hasattr(ast, "unparse")
                                        else None
                                    ),
                                }
                            )

        # Helper function to process class and function nodes
        def process_node(
            node: ast.AST, parent: str | None = None, level: int = 0
        ) -> dict[str, Any] | None:
            """Process an AST node to extract namespace information.

            Args:
                node: AST node to process
                parent: Name of the parent namespace
                level: Current indentation level

            Returns:
                Dictionary containing namespace information or None if node skipped
            """
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Skip private methods if configured
                if (
                    not config.include_private
                    and node.name.startswith("_")
                    and not node.name.startswith("__")
                ):
                    return None

                # Skip dunder methods if configured
                if (
                    not config.include_dunder
                    and node.name.startswith("__")
                    and node.name.endswith("__")
                ):
                    return None

                # Extract decorators
                decorators = extract_decorators(node)

                # Extract the function signature
                signature = extract_function_signature(
                    source_lines, node, level * config.indent_size
                )

                # Extract docstring if configured
                docstring = None
                if config.include_docstrings:
                    docstring = ast.get_docstring(node)

                # Determine if it's async
                is_async = isinstance(node, ast.AsyncFunctionDef)

                func_info = {
                    "type": "function",
                    "name": node.name,
                    "signature": signature,
                    "parent": parent,
                    "decorators": decorators,
                    "docstring": docstring,
                    "is_async": is_async,
                }

                return func_info

            if isinstance(node, ast.ClassDef):
                # Skip private classes if configured
                if (
                    not config.include_private
                    and node.name.startswith("_")
                    and not node.name.startswith("__")
                ):
                    return None

                # Extract decorators
                decorators = extract_decorators(node)

                # Extract base classes
                bases = []
                for base in node.bases:
                    if hasattr(ast, "unparse"):  # Python 3.9+
                        bases.append(ast.unparse(base))
                    elif isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        # Handle module.Class format
                        parts: list[str] = []
                        current: ast.Attribute | ast.Name = base
                        while isinstance(current, ast.Attribute):
                            parts.insert(0, current.attr)
                            current = typing.cast(
                                ast.Attribute | ast.Name, current.value
                            )
                        if isinstance(current, ast.Name):
                            parts.insert(0, current.id)
                        bases.append(".".join(parts))

                # Extract docstring if configured
                docstring = None
                if config.include_docstrings:
                    docstring = ast.get_docstring(node)

                methods: list[dict[str, Any]] = []
                nested_classes: list[dict[str, Any]] = []
                class_info: dict[str, Any] = {
                    "type": "class",
                    "name": node.name,
                    "parent": parent,
                    "bases": bases,
                    "decorators": decorators,
                    "methods": methods,
                    "nested_classes": nested_classes,
                    "level": level,
                    "docstring": docstring,
                }

                # Process class body
                for child_node in node.body:
                    result = process_node(child_node, node.name, level + 1)
                    if result:
                        if result["type"] == "function":
                            methods.append(result)
                        elif result["type"] == "class":
                            nested_classes.append(result)

                return class_info

            return None

        # Process top-level nodes
        for node in ast.iter_child_nodes(tree):
            result = process_node(node)
            if result:
                namespaces.append(result)

        return directory, filename, namespaces

    except Exception as e:
        print(f"Error processing file {file_path}: {e!s}")
        return "", os.path.basename(file_path), []


def parse_files(
    file_paths: list[str], config: ExtractorConfig
) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """Parse multiple Python files with a progress bar.

    Args:
        file_paths: List of Python file paths to parse
        config: Configuration settings

    Returns:
        List of tuples with parsed data
    """
    results = []

    # Use tqdm to show progress
    with tqdm(total=len(file_paths), desc="Parsing Python files") as pbar:
        for file_path in file_paths:
            try:
                data = extract_namespaces(file_path, config)
                results.append(data)
            except Exception as e:
                print(f"Error processing {file_path}: {e!s}")
            finally:
                pbar.update(1)

    return results
