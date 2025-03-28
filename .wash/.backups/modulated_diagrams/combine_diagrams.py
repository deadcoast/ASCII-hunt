#!/usr/bin/env python3

import os
import re
import sys


def read_file_content(file_path: str) -> str | None:
    """Read file content, stripping the graph TD header if present.

    Args:
        file_path: Path to the mermaid diagram file

    Returns:
        Stripped content of the file or None if file doesn't exist
    """
    try:
        with open(file_path) as f:
            content = f.read()
            # Remove 'graph TD' line if present
            content = re.sub(r"^graph TD\s*\n", "", content, flags=re.MULTILINE)
            return content.strip()
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found, skipping...")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e!s}")
        return None


def validate_main_file(content: str) -> bool:
    """Validate that the main.mmd file has required markers.

    Args:
        content: Content of main.mmd

    Returns:
        True if valid, False otherwise
    """
    required_markers = [
        "%% Cross-system Dependencies",
        "subgraph Core",
        "%% Style definitions",
    ]

    return all(marker in content for marker in required_markers)


def combine_diagrams(output_path: str = "combined_diagram.mmd") -> None:
    """Combine all diagram files into a single Mermaid diagram.

    Args:
        output_path: Path where the combined diagram should be written
    """
    # Directory containing the diagram files
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Order of files to process - matches architectural layers
    files = [
        "main.mmd",  # Contains the overall structure and styles
        "core.mmd",  # Core system components
        "dsl.mmd",  # DSL processing components
        "recognition.mmd",  # Recognition system components
        "modeling.mmd",  # Modeling system components
        "generation.mmd",  # Code generation components
        "plugins.mmd",  # Plugin system components
        "processing.mmd",  # Processing system components
        "interface.mmd",  # Interface components
        "patterns.mmd",  # Pattern system components
        "utils.mmd",  # Utility components
    ]

    # Read main file first
    main_file_path = os.path.join(current_dir, "main.mmd")
    main_content = read_file_content(main_file_path)

    if not main_content:
        print("Error: main.mmd is required but could not be read")
        sys.exit(1)

    if not validate_main_file(main_content):
        print("Error: main.mmd is missing required sections")
        sys.exit(1)

    # Find the position to insert subgraph contents (before the cross-system dependencies)
    parts = main_content.split("%% Cross-system Dependencies")
    if len(parts) != 2:
        print("Error: Could not find '%% Cross-system Dependencies' marker in main.mmd")
        sys.exit(1)

    header = parts[0]
    footer = "%% Cross-system Dependencies" + parts[1]

    # Combine the contents
    combined_parts: list[str] = [header]

    # Add each subgraph's content
    for file_name in files[1:]:  # Skip main.mmd as we already processed it
        file_path = os.path.join(current_dir, file_name)
        content = read_file_content(file_path)

        if content:
            # Remove the class definitions as they're already in main.mmd
            content = re.sub(
                r"%%\s*Apply.*\nclass.*\n?$", "", content, flags=re.MULTILINE
            )
            # Remove any trailing whitespace
            content = content.strip()
            combined_parts.append(content)

    combined_parts.append(footer)

    # Write the combined content
    output_file = os.path.join(current_dir, output_path)
    try:
        with open(output_file, "w") as f:
            f.write("\n\n".join(combined_parts))
        print(f"Successfully combined diagrams into {output_file}")
    except Exception as e:
        print(f"Error writing combined diagram: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    combine_diagrams()
