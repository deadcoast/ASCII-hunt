"""Command-line interface for the ASCII UI Translation Engine."""

from src.data_stack.ascii_ui_translation_engine import ASCIIUITranslationEngine


def create_cli():
    """Create the command-line interface for the ASCII UI Translation Engine.

    This function creates an argparse ArgumentParser instance with the
    following commands:

    - process: Process an ASCII UI file.
    - list-frameworks: List supported frameworks.
    - load-plugins: Load plugins from a directory.

    Returns:
        argparse.ArgumentParser: The CLI parser
    """
    import argparse

    parser = argparse.ArgumentParser(description="ASCII UI Translation Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process an ASCII UI file")
    process_parser.add_argument("input_file", help="Input ASCII UI file")
    process_parser.add_argument("--output", "-o", help="Output file for generated code")
    process_parser.add_argument(
        "--framework",
        "-f",
        default="default",
        help="Target framework for code generation",
    )
    process_parser.add_argument("--config", "-c", help="Configuration file")
    process_parser.add_argument("--components", "-c", help="Components file")
    process_parser.add_argument("--grid", "-g", help="Grid file")
    process_parser.add_argument("--model", "-m", help="Model file")
    process_parser.add_argument("--analysis", "-a", help="Analysis file")
    process_parser.add_argument("--output", "-o", help="Output file")
    process_parser.add_argument("--plugins", "-p", help="Plugins file")

    # List frameworks command

    list_frameworks_parser = subparsers.add_parser(
        "list-frameworks", help="List supported frameworks"
    )

    # Load plugins command
    load_plugins_parser = subparsers.add_parser(
        "load-plugins", help="Load plugins from a directory"
    )
    load_plugins_parser.add_argument("plugin_dir", help="Plugin directory")

    return parser


def extend_cli_for_hunt(parser):
    """Extend command-line interface for HUNT DSL."""
    # Add HUNT-specific commands
    dsl_parser = parser.add_parser("hunt", help="Work with HUNT patterns")
    dsl_subparsers = dsl_parser.add_subparsers(dest="dsl_command", help="HUNT command")

    # Parse HUNT file command
    parse_parser = dsl_subparsers.add_parser("parse", help="Parse HUNT file")
    parse_parser.add_argument("dsl_file", help="HUNT pattern file")
    parse_parser.add_argument("--output", "-o", help="Output file for parsed AST")

    # Apply HUNT patterns command
    apply_parser = dsl_subparsers.add_parser(
        "apply", help="Apply HUNT patterns to ASCII UI"
    )
    apply_parser.add_argument("input_file", help="Input ASCII UI file")
    apply_parser.add_argument("dsl_file", help="HUNT pattern file")
    apply_parser.add_argument(
        "--output", "-o", help="Output file for recognized components"
    )

    # Generate HUNT patterns command
    generate_parser = dsl_subparsers.add_parser(
        "generate", help="Generate HUNT patterns from components"
    )
    generate_parser.add_argument("components_file", help="Components JSON file")
    generate_parser.add_argument(
        "--output", "-o", help="Output file for generated HUNT patterns"
    )

    return parser


def main():
    """Main entry point for the command line interface."""
    parser = create_cli()
    args = parser.parse_args()

    # Create engine
    engine = ASCIIUITranslationEngine()

    if args.command == "process":
        # Load configuration if specified
        if args.config:
            engine.load_config(args.config)

        # Read input file
        with open(args.input_file) as f:
            ascii_text = f.read()

        # Process ASCII UI
        options = {"target_framework": args.framework}

        response = engine.process_ascii_ui(ascii_text, options)

        if response["success"]:
            # Output generated code
            generated_code = response["generated_code"]

            if args.output:
                with open(args.output, "w") as f:
                    f.write(generated_code)
            else:
                print(generated_code)

            # Print performance metrics
            print("\nPerformance metrics:")
            for stage, metrics in response["performance_metrics"].items():
                if "execution_time" in metrics:
                    print(f"  {stage}: {metrics['execution_time']:.4f} seconds")
        else:
            print(f"Error: {response['error']}")

    elif args.command == "list-frameworks":
        # List supported frameworks
        frameworks = engine.get_supported_frameworks()

        print("Supported frameworks:")
        for framework in frameworks:
            print(f"  {framework}")

    elif args.command == "load-plugins":
        # Load plugins
        loaded_plugins = engine.load_plugins(args.plugin_dir)

        print(f"Loaded {len(loaded_plugins)} plugins:")
        for plugin in loaded_plugins:
            print(f"  {plugin}")


if __name__ == "__main__":
    main()
