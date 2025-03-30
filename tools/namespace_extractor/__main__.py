"""Main entry point for the namespace extractor."""

import argparse
import logging
import sys
from pathlib import Path

from .config import ExtractorConfig, load_config
from .formatter import FormatterFactory
from .output import OutputGeneratorFactory
from .parser import find_python_files, parse_files

# Get a logger for this module
logger = logging.getLogger(__name__)


def check_file_exists(file_path: str) -> None:
    """Check if a file exists, exit if not."""
    if not Path(file_path).exists():
        logger.error("File not found: %s", file_path)  # Use logger and format string
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract namespaces from Python files."
    )
    parser.add_argument("output", help="Output file path")
    parser.add_argument("inputs", nargs="+", help="Input files or directories")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--recursive", action="store_true", help="Process directories recursively"
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private methods (starting with _)",
    )
    parser.add_argument(
        "--include-dunder",
        action="store_true",
        help="Include dunder methods (__method__)",
    )
    parser.add_argument(
        "--include-docstrings",
        action="store_true",
        help="Include first line of docstrings",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Regex patterns to exclude (can be used multiple times)",
    )
    parser.add_argument(
        "--depth", type=int, default=-1, help="Max recursion depth (-1 for unlimited)"
    )
    parser.add_argument(
        "--include-vars", action="store_true", help="Include module-level constants"
    )
    parser.add_argument(
        "--formatter",
        choices=["dictionary", "hierarchical"],
        default="dictionary",
        help="Formatter type to use for structuring the data",
    )
    parser.add_argument(
        "--output-format",
        choices=["markdown", "json", "yaml"],
        default="markdown",
        help="Output format for the extracted namespaces",
    )

    return parser.parse_args()


def _update_config_from_args(config: ExtractorConfig, args: argparse.Namespace) -> None:
    """Update configuration object based on command-line arguments."""
    # Map simple boolean flags
    arg_to_config_map = {
        "recursive": "recursive",
        "include_private": "include_private",
        "include_dunder": "include_dunder",
        "include_docstrings": "include_docstrings",
        "include_vars": "include_module_vars",
    }
    for arg_name, config_attr in arg_to_config_map.items():
        if getattr(args, arg_name, False):
            setattr(config, config_attr, True)

    # Handle other specific arguments
    if args.depth >= 0:
        config.max_recursion_depth = args.depth
    if args.exclude:
        # Ensure exclude_patterns exists if loading from a minimal config
        if not hasattr(config, "exclude_patterns") or config.exclude_patterns is None:
            config.exclude_patterns = []
        config.exclude_patterns.extend(args.exclude)


def main() -> None:
    """Main function to process files and generate namespace output."""
    # Configure logging for the root logger (can be overridden by specific loggers)
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s: %(message)s",
        stream=sys.stdout,
    )

    try:
        _default_args()
    except (OSError, ValueError, argparse.ArgumentError):
        logger.exception(
            "An error occurred during processing"
        )  # Use logger, no f-string, no redundant e
        sys.exit(1)
    except Exception:
        logger.exception("An unexpected error occurred")  # Use logger, no f-string
        sys.exit(1)


def _default_args() -> None:
    """Parse args, load config, find files, process, and generate output."""
    args = parse_arguments()

    config = load_config(args.config)
    _update_config_from_args(config, args)

    all_files = []
    for input_path_str in args.inputs:
        input_path = Path(input_path_str)
        if input_path.is_file():
            if input_path.suffix == ".py":
                all_files.append(str(input_path))
        elif input_path.is_dir():
            python_files = find_python_files(str(input_path), config)
            all_files.extend(python_files)
        else:
            logger.warning("Path not found or invalid: %s", input_path)

    if not all_files:
        logger.warning("No Python files found to process.")
        sys.exit(1)  # Exit with non-zero code

    logger.info("Found %d Python files to process", len(all_files))

    extracted_data = parse_files(all_files, config)
    formatter = FormatterFactory.create_formatter(args.formatter, config)
    formatted_data = formatter.format_data(extracted_data)
    output_generator = OutputGeneratorFactory.create_output_generator(
        args.output_format, config, formatter.options
    )
    content = output_generator.generate(formatted_data)
    output_generator.save_to_file(content, args.output)

    logger.info("Namespace extraction completed successfully")


if __name__ == "__main__":
    main()
