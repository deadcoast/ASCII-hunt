#!/usr/bin/env python
"""
Project-wide import fixer using ImportMagic
Usage: python fix_project_imports.py project_directory
Import helper module.
Provides functions to fix imports in Python files using ImportMagic.
"""

import logging
import os
import sys
import time

import importmagic

logger = logging.getLogger(__name__)


# Create a global index for better performance
_global_index = None  # Will be initialized to SymbolIndex on first use

# Keep track of the index location for potential caching
_index_path = "/Users/deadcoast/CursorProjects/ASCII-hunt/import_miner/_global_index.py"


def get_symbol_index():
    """Get or create a global symbol index."""
    global _global_index

    if _global_index is None:
        logger.info("Building ImportMagic symbol index...")
        _global_index = importmagic.SymbolIndex()
        # Add type ignore for paths_from_interpreter
        try:
            _global_index.build_index(paths=importmagic.paths_from_interpreter())  # type: ignore
        except AttributeError:
            # Fallback if the method doesn't exist
            paths = [os.path.dirname(p) for p in sys.path if os.path.isdir(p)]
            _global_index.build_index(paths=paths)
        except Exception as e:
            logger.error(f"Error building symbol index: {e}")
            # Create a minimal index to avoid further errors
            _global_index = importmagic.SymbolIndex()
            _global_index.build_index(paths=[])
        logger.info("Symbol index built.")

    return _global_index


def fix_imports_in_file(filename):
    """Fix imports in a single Python file."""
    # Get the global index
    index = get_symbol_index()

    # Read the file content
    try:
        with open(filename, encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        logger.error(f"Could not read {filename} - not a text file or wrong encoding.")
        return False, "Encoding error."
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return False, f"Error: {e!s}"

    # Parse the source code
    scope = importmagic.Scope.from_source(source)

    # Find unresolved and unreferenced symbols
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

    if not unresolved and not unreferenced:
        return False, "No import issues found."

    # Build statistics
    stats = {
        "added": len(unresolved) if unresolved else 0,
        "removed": len(unreferenced) if unreferenced else 0,
        "added_imports": list(unresolved) if unresolved else [],
        "removed_imports": list(unreferenced) if unreferenced else [],
    }

    # Update imports
    imports = importmagic.Imports(index, source)

    if unreferenced:
        try:
            imports.remove(unreferenced)  # type: ignore
        except (TypeError, AttributeError) as e:
            logger.warning(f"Failed to remove imports: {e}")

    if unresolved:
        try:
            imports.add(unresolved)  # type: ignore
        except (TypeError, AttributeError) as e:
            logger.warning(f"Failed to add imports: {e}")

    # Get the updated source code
    try:
        updated_source = imports.update_source()  # type: ignore
    except (TypeError, AttributeError):
        # Try with source parameter
        updated_source = imports.update_source(source)  # type: ignore

    # Write the changes back to the file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_source)
    except Exception as e:
        logger.error(f"Error writing to {filename}: {e}")
        return False, f"Error: {e!s}"

    return True, stats


def fix_imports_in_string(source_code):
    """Fix imports in a Python source code string."""
    # Get the global index
    index = get_symbol_index()

    # Parse the source code
    scope = importmagic.Scope.from_source(source_code)

    # Find unresolved and unreferenced symbols
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

    if not unresolved and not unreferenced:
        return source_code, False, "No import issues found."

    # Build statistics
    stats = {
        "added": len(unresolved) if unresolved else 0,
        "removed": len(unreferenced) if unreferenced else 0,
        "added_imports": list(unresolved) if unresolved else [],
        "removed_imports": list(unreferenced) if unreferenced else [],
    }

    # Update imports
    imports = importmagic.Imports(index, source_code)

    if unreferenced:
        try:
            imports.remove(unreferenced)  # type: ignore
        except (TypeError, AttributeError) as e:
            logger.warning(f"Failed to remove imports: {e}")

    if unresolved:
        try:
            imports.add(unresolved)  # type: ignore
        except (TypeError, AttributeError) as e:
            logger.warning(f"Failed to add imports: {e}")

    # Get the updated source code
    try:
        updated_source = imports.update_source()  # type: ignore
    except (TypeError, AttributeError):
        # Try with source_code parameter
        updated_source = imports.update_source(source_code)  # type: ignore

    return updated_source, True, stats


def fix_file_imports(filename, index):
    """Fix imports in a single Python file."""
    # Skip non-Python files
    if not filename.endswith(".py"):
        return False

    # Read the file content
    try:
        with open(filename, encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        print(f"Error: Could not read {filename} - not a text file or wrong encoding.")
        return False
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return False

    # Parse the source code
    try:
        scope = importmagic.Scope.from_source(source)
    except SyntaxError:
        print(f"Error: Syntax error in {filename} - skipping.")
        return False

    # Find unresolved and unreferenced symbols
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

    if not unresolved and not unreferenced:
        # No issues found
        return False

    # Report what will be changed
    changes_made = False

    if unresolved:
        print(f"{filename}: Adding {len(unresolved)} imports: {', '.join(unresolved)}")
        changes_made = True

    if unreferenced:
        print(
            f"{filename}: Removing {len(unreferenced)} imports: {', '.join(unreferenced)}"
        )
        changes_made = True

    if not changes_made:
        return False

    # Update imports
    imports = importmagic.Imports(index, source)

    if unreferenced:
        try:
            imports.remove(unreferenced)  # type: ignore
        except (TypeError, AttributeError) as e:
            print(f"Error removing imports: {e}")

    if unresolved:
        try:
            imports.add(unresolved)  # type: ignore
        except (TypeError, AttributeError) as e:
            print(f"Error adding imports: {e}")

    # Get the updated source code
    try:
        updated_source = imports.update_source()  # type: ignore
    except (TypeError, AttributeError):
        # Try with source parameter
        updated_source = imports.update_source(source)  # type: ignore

    # Write the changes back to the file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_source)
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
        return False

    return True


def process_directory(directory_path, index):
    """Process all Python files in the directory and subdirectories."""
    files_fixed = 0
    files_processed = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                files_processed += 1

                if files_processed % 10 == 0:
                    print(f"Processed {files_processed} files so far...")

                if fix_file_imports(filepath, index):
                    files_fixed += 1

    return files_processed, files_fixed


def main() -> int:
    """Main function.

    Returns:
        int: 0 for success, 1 for error
    """
    if len(sys.argv) < 2:
        print("Please provide a project directory to process.")
        print("Usage: python fix_project_imports.py <project_directory>")
        return 1

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return 1

    start_time = time.time()

    # Build an index of available modules
    print("Building module index (may take a moment)...")
    index = importmagic.SymbolIndex()
    try:
        index.build_index(paths=importmagic.paths_from_interpreter())  # type: ignore
    except AttributeError:
        # Fallback if the method doesn't exist
        paths = [os.path.dirname(p) for p in sys.path if os.path.isdir(p)]
        index.build_index(paths=paths)
    except Exception as e:
        print(f"Error building index: {e}")
        print("Continuing with empty index...")
        index.build_index(paths=[])

    try:
        print(f"Processing Python files in {directory}...")
        files_processed, files_fixed = process_directory(directory, index)
    except Exception as e:
        print(f"Error processing directory: {e}")
        return 1

    end_time = time.time()
    duration = end_time - start_time

    print("\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")
    print(f"Time taken: {duration:.2f} seconds")

    return 0


if __name__ == "__main__":
    main()
