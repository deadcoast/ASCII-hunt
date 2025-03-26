"""Import Extractor Module for analyzing Python imports."""

import ast


def extract_imports_from_content(content: str) -> list[str]:
    """Extract import statements from Python code content.

    Args:
        content (str): The Python code content to analyze.

    Returns:
        List[str]: A list of import statements found in the code.
    """
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(f"import {name.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    if name.name == "*":
                        imports.append(f"from {module} import *")
                    else:
                        imports.append(f"from {module} import {name.name}")
    except SyntaxError:
        # Handle invalid Python code gracefully
        pass

    return imports
