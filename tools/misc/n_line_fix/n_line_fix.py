#!/usr/bin/env python3
"""Markdown Newline Format Fixer

This script fixes Markdown documents with escaped newline characters by converting them
to proper newline characters. It's specifically designed for Markdown files and uses
a YAML configuration file to specify input/output paths and processing options.

The script handles both '\n' and '\n\n' patterns, replacing them with actual newlines
to restore proper document formatting.

Requirements:
    - PyYAML: pip install pyyaml

Usage:
    python n_line_fix.py --config config.yaml
    python n_line_fix.py --create-config
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml


def fix_newlines_in_markdown(text):
    """Replace escaped newline characters with actual newlines in Markdown content.

    Args:
        text (str): The Markdown text with escaped newline characters.

    Returns:
        str: Text with proper newline formatting.
    """
    # First, handle the '\n\n' pattern (must be done before single '\n')
    text = text.replace("\\n\\n", "\n\n")

    # Then replace the single '\n' pattern
    text = text.replace("\\n", "\n")

    # Replace underscore character that appears to be escaped in code
    text = text.replace("_", "_")

    # Replace any remaining escaped characters
    text = text.replace("\\*", "*")
    text = text.replace("\\_", "_")

    # Clean up any instances of multiple spaces at line beginnings
    text = re.sub(r"\n\s{2,}", "\n", text)

    return text


def create_backup(file_path, backup_dir=None):
    """Create a backup of the specified file.

    Args:
        file_path (str): Path to the file to back up.
        backup_dir (str, optional): Directory to store backups.
                                   If None, creates backup in same directory.

    Returns:
        str: Path to the backup file.
    """
    file_path = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if backup_dir:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(exist_ok=True, parents=True)
        backup_path = backup_dir / f"{file_path.name}.{timestamp}.bak"
    else:
        backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")

    shutil.copy2(file_path, backup_path)
    return str(backup_path)


def process_single_file(file_path, output_dir=None, make_backup=True, backup_dir=None):
    """Process a single Markdown file to fix its newline characters.

    Args:
        file_path (str): Path to the input Markdown file.
        output_dir (str, optional): Directory to write the output file.
                                    If None, overwrites the input file.
        make_backup (bool): Whether to create a backup of the original file.
        backup_dir (str, optional): Directory to store backups.

    Returns:
        bool: True if successful, False otherwise.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: Input file '{file_path}' does not exist.")
        return False

    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        output_path = output_dir / file_path.name
    else:
        output_path = file_path

    # Create backup if requested
    if make_backup and output_path == file_path:
        try:
            backup_path = create_backup(file_path, backup_dir)
            print(f"Created backup at: {backup_path}")
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")

    try:
        # Read the input file
        with open(file_path, encoding="utf-8") as infile:
            content = infile.read()

        # Fix the newlines
        fixed_content = fix_newlines_in_markdown(content)

        # If content hasn't changed, report and exit
        if content == fixed_content:
            print(f"No changes needed for '{file_path}'")
            return True

        # Write to the output file
        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write(fixed_content)

        print(f"Successfully fixed newlines in '{file_path}' → '{output_path}'")
        return True

    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")
        return False


def process_directory(
    directory_path, output_dir=None, recursive=False, make_backup=True, backup_dir=None
):
    """Process all Markdown files in a directory.

    Args:
        directory_path (str): Path to the directory containing files to process.
        output_dir (str, optional): Directory to write output files.
        recursive (bool): Whether to process subdirectories as well.
        make_backup (bool): Whether to create backups of original files.
        backup_dir (str, optional): Directory to store backups.

    Returns:
        tuple: (success_count, failure_count)
    """
    directory_path = Path(directory_path)

    if not directory_path.is_dir():
        print(f"Error: '{directory_path}' is not a directory.")
        return 0, 0

    success_count = 0
    failure_count = 0

    # Process files in the current directory
    for item in directory_path.iterdir():
        if item.is_file() and item.suffix.lower() in (".md", ".markdown"):
            # For directory processing, maintain structure in output dir if specified
            if output_dir:
                out_dir = Path(output_dir)
                out_dir.mkdir(exist_ok=True, parents=True)
            else:
                out_dir = None

            if process_single_file(item, out_dir, make_backup, backup_dir):
                success_count += 1
            else:
                failure_count += 1

    # Process subdirectories if recursive is True
    if recursive:
        for item in directory_path.iterdir():
            if item.is_dir():
                # Create corresponding output subdirectory if needed
                subdir_output = Path(output_dir) / item.name if output_dir else None
                sub_success, sub_failure = process_directory(
                    item, subdir_output, recursive, make_backup, backup_dir
                )
                success_count += sub_success
                failure_count += sub_failure

    return success_count, failure_count


def load_config(config_path):
    """Load and validate the YAML configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration settings.
    """
    try:
        # Ensure we have an absolute path to work with
        config_path = os.path.abspath(config_path)

        if not os.path.exists(config_path):
            print(f"Error: Configuration file not found at '{config_path}'")
            sys.exit(1)

        with open(config_path, encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        # Get the directory containing the config file
        config_dir = os.path.dirname(config_path)

        # Check if the base path is specified, make it absolute if it's relative
        if "path" not in config or not config["path"]:
            print("Error: 'path' option is required in the configuration file.")
            sys.exit(1)

        base_path = config["path"]
        if not os.path.isabs(base_path):
            base_path = os.path.join(config_dir, base_path)
            config["path"] = base_path

        # Validate that the base path exists
        if not os.path.exists(base_path):
            print(f"Error: Base path '{base_path}' does not exist.")
            sys.exit(1)

        # Set defaults for missing configuration options
        if "files" not in config:
            config["files"] = []

        if "directories" not in config:
            config["directories"] = []

        if "options" not in config:
            config["options"] = {}

        # Set output_dir to None if not specified, or join with base_path if relative
        if "output_dir" not in config or not config["output_dir"]:
            config["output_dir"] = None
        else:
            config["output_dir"] = os.path.join(base_path, config["output_dir"])

        options = config["options"]
        if "recursive" not in options:
            options["recursive"] = False

        if "make_backup" not in options:
            options["make_backup"] = True

        if "backup_dir" not in options or not options["backup_dir"]:
            options["backup_dir"] = None
        else:
            options["backup_dir"] = os.path.join(base_path, options["backup_dir"])

        # Convert file paths to absolute paths by joining with the base path
        full_files = []
        for file_path in config["files"]:
            full_path = os.path.join(base_path, file_path)
            full_files.append(full_path)
        config["files"] = full_files

        # Convert directory paths to absolute paths by joining with the base path
        full_dirs = []
        for dir_path in config["directories"]:
            full_path = os.path.join(base_path, dir_path)
            full_dirs.append(full_path)
        config["directories"] = full_dirs

        return config

    except Exception as e:
        print(f"Error loading configuration file: {e}")
        sys.exit(1)


def create_sample_config(output_path):
    """Create a sample YAML configuration file.

    Args:
        output_path (str): Path where the sample config will be saved.

    Returns:
        bool: True if successful, False otherwise.
    """
    sample_config = """# Markdown Newline Fixer Configuration

# Path to your markdown files that need fixing
path: "/your/actual/path/to/documents"

# Files to process (list individual markdown files - these are relative to the path above)
files:
  - "README.md"
  - "chapter1.md"

# Output directory (where fixed files will be saved - relative to the path above)
# If not specified or left empty, original files will be overwritten
output_dir: "fixed_docs"

# Directories to process (will process all .md and .markdown files - relative to the path above)
directories:
  - "chapters"
  - "appendices"

# Global options
options:
  recursive: true          # Process subdirectories
  make_backup: true        # Create backups before modifying files
  backup_dir: "backups"    # Optional: central location for all backups (relative to path)
"""
    try:
        with open(output_path, "w", encoding="utf-8") as config_file:
            config_file.write(sample_config)
        return True
    except Exception as e:
        print(f"Error creating sample configuration: {e}")
        return False


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Fix newline formatting in Markdown files"
    )

    # Add argument for configuration file
    parser.add_argument("--config", type=str, help="Path to YAML configuration file")

    # Add option to generate a sample configuration file
    parser.add_argument(
        "--create-config",
        type=str,
        nargs="?",
        const="n_line_fix_config.yaml",
        help="Create a sample configuration file at the specified path or default location",
    )

    args = parser.parse_args()

    # Generate sample configuration if requested
    if args.create_config:
        config_path = args.create_config
        if create_sample_config(config_path):
            print(
                f"Sample configuration file created at: {os.path.abspath(config_path)}"
            )
            return 0
        return 1

    # Require configuration file
    if not args.config:
        parser.print_help()
        print(
            "\nError: Configuration file is required. Use --create-config to generate a sample."
        )
        return 1

    # Load configuration
    config = load_config(args.config)

    # Process individual files
    total_success = 0
    total_failure = 0

    options = config["options"]
    backup_dir = options.get("backup_dir")
    output_dir = config.get("output_dir")

    print("Processing individual files...")
    for file_path in config["files"]:
        if process_single_file(
            file_path, output_dir, options["make_backup"], backup_dir
        ):
            total_success += 1
        else:
            total_failure += 1

    # Process directories
    print("\nProcessing directories...")
    for dir_path in config["directories"]:
        success, failure = process_directory(
            dir_path,
            output_dir,
            options["recursive"],
            options["make_backup"],
            backup_dir,
        )

        total_success += success
        total_failure += failure

    # Print summary
    print(
        f"\nSummary: Successfully processed {total_success} files. Failed to process {total_failure} files."
    )

    return 0 if total_failure == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
