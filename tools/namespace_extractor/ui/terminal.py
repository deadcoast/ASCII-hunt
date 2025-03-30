# File: namespace_extractor/ui/terminal.py
"""
Rich terminal interface for namespace extractor.

This module provides an enhanced terminal user interface for the namespace extractor
using the Rich library, offering visual improvements, progress tracking, and interactive
filtering capabilities.
"""

import os
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ..config import ExtractorConfig, FormatterType, NamespaceType, OutputFormat


class TerminalUI:
    """Rich terminal interface for namespace extractor."""

    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the terminal UI.

        Args:
            config: The current configuration
        """
        self.config = config
        self.console = Console()
        self.result_data: Any = None

    def show_banner(self) -> None:
        """Display a welcome banner for the application."""
        self.console.print("\n")
        self.console.print(
            Panel.fit(
                Text("Python Namespace Extractor", style="bold blue"),
                subtitle="Extract and analyze Python code structure",
                border_style="blue",
            )
        )
        self.console.print("\n")

    def create_progress_context(self) -> Progress:
        """
        Create a Rich progress context for tracking operations.

        Returns:
            Progress context for use in with statements
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        )

    def configure_extraction(self) -> ExtractorConfig:
        """
        Interactive configuration setup for extraction.

        Returns:
            Updated configuration
        """
        self.console.print("[bold]Configure Extraction[/bold]")

        # Basic options
        self.config.include_private = Confirm.ask(
            "Include private methods?", default=self.config.include_private
        )

        self.config.include_dunder = Confirm.ask(
            "Include dunder methods?", default=self.config.include_dunder
        )

        self.config.include_docstrings = Confirm.ask(
            "Include docstrings?", default=self.config.include_docstrings
        )

        self.config.include_module_vars = Confirm.ask(
            "Include module variables?", default=self.config.include_module_vars
        )

        # Directory options
        self.config.recursive = Confirm.ask(
            "Process directories recursively?", default=self.config.recursive
        )

        if self.config.recursive:
            depth = Prompt.ask(
                "Maximum recursion depth (-1 for unlimited)",
                default=str(self.config.max_recursion_depth),
            )
            self.config.max_recursion_depth = int(depth)

        # Formatter options
        formatter_choices = {
            "1": FormatterType.DICTIONARY,
            "2": FormatterType.HIERARCHICAL,
        }

        formatter_choice = Prompt.ask(
            "Select formatter type", choices=list(formatter_choices.keys()), default="1"
        )
        self.config.formatter_type = formatter_choices[formatter_choice]

        # Output options
        output_choices = {
            "1": OutputFormat.MARKDOWN,
            "2": OutputFormat.JSON,
            "3": OutputFormat.YAML,
        }

        output_choice = Prompt.ask(
            "Select output format", choices=list(output_choices.keys()), default="1"
        )
        self.config.output_format = output_choices[output_choice]

        # Apply changes
        self.config.__post_init__()

        return self.config

    def save_as_profile(self) -> None:
        """Save current configuration as a named profile."""
        if Confirm.ask("Save current configuration as a profile?"):
            profile_name = Prompt.ask("Enter profile name")

            if not profile_name:
                self.console.print(
                    "[yellow]Profile name cannot be empty. Not saving.[/yellow]"
                )
                return

            profiles_dir = os.path.join(
                os.path.expanduser("~"), ".namespace_extractor", "profiles"
            )
            os.makedirs(profiles_dir, exist_ok=True)

            profile_path = os.path.join(profiles_dir, f"{profile_name}.yaml")

            from ..config import save_config

            save_config(self.config, profile_path)

            self.console.print(f"[green]Profile saved as '{profile_name}'[/green]")

    def load_profile(self) -> ExtractorConfig | None:
        """
        Load a saved configuration profile.

        Returns:
            Loaded configuration or None if canceled
        """
        profiles_dir = os.path.join(
            os.path.expanduser("~"), ".namespace_extractor", "profiles"
        )

        if not os.path.exists(profiles_dir):
            self.console.print("[yellow]No saved profiles found.[/yellow]")
            return None

        profiles = [f for f in os.listdir(profiles_dir) if f.endswith(".yaml")]

        if not profiles:
            self.console.print("[yellow]No saved profiles found.[/yellow]")
            return None

        # Display available profiles
        self.console.print("[bold]Available Profiles:[/bold]")
        for i, profile in enumerate(profiles, 1):
            name = profile[:-5]  # Remove .yaml extension
            self.console.print(f"{i}. {name}")

        self.console.print("0. Cancel")

        choice = Prompt.ask(
            "Select a profile to load",
            choices=[str(i) for i in range(len(profiles) + 1)],
            default="0",
        )

        if choice == "0":
            return None

        profile_path = os.path.join(profiles_dir, profiles[int(choice) - 1])

        from ..config import load_config

        config = load_config(profile_path)

        self.console.print(
            f"[green]Loaded profile: {profiles[int(choice) - 1][:-5]}[/green]"
        )

        return config

    def display_summary(self, statistics: dict[str, Any]) -> None:
        """
        Display a summary of extraction results.

        Args:
            statistics: Dictionary containing extraction statistics
        """
        table = Table(title="Extraction Summary")

        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Files Processed", str(statistics.get("total_files", 0)))
        table.add_row("Directories", str(statistics.get("total_directories", 0)))
        table.add_row("Classes", str(statistics.get("total_classes", 0)))
        table.add_row("Functions", str(statistics.get("total_functions", 0)))
        table.add_row("Methods", str(statistics.get("total_methods", 0)))
        table.add_row("Nested Classes", str(statistics.get("total_nested_classes", 0)))

        if self.config.include_module_vars:
            table.add_row("Variables", str(statistics.get("total_variables", 0)))

        self.console.print(table)

    def display_results_preview(
        self,
        formatted_data: dict[str, Any] | dict[str, dict[str, list[dict[str, Any]]]],
    ) -> None:
        """
        Display a preview of the extraction results.

        Args:
            formatted_data: Formatted namespace data
        """
        self.result_data = formatted_data

        if self.config.formatter_type == FormatterType.DICTIONARY:
            self._display_dictionary_preview(formatted_data)
        elif self.config.formatter_type == FormatterType.HIERARCHICAL:
            self._display_hierarchical_preview(formatted_data)

    def _display_dictionary_preview(
        self, formatted_data: dict[str, dict[str, list[dict[str, Any]]]]
    ) -> None:
        """
        Display a preview of dictionary-formatted data.

        Args:
            formatted_data: Dictionary-formatted data
        """
        tree = Tree("Extraction Results", guide_style="bold bright_blue")

        # Limit to first few directories for preview
        preview_count = min(5, len(formatted_data))

        for i, (directory, files) in enumerate(formatted_data.items()):
            if i >= preview_count:
                remaining = len(formatted_data) - preview_count
                tree.add(f"... {remaining} more directories")
                break

            dir_node = tree.add(directory or "[root]")

            # Limit files per directory
            file_preview_count = min(5, len(files))
            for j, (filename, namespaces) in enumerate(files.items()):
                if j >= file_preview_count:
                    remaining = len(files) - file_preview_count
                    dir_node.add(f"... {remaining} more files")
                    break

                namespace_counts: dict[str, int] = {}
                for ns in namespaces:
                    ns_type = ns.get("type", "unknown")
                    namespace_counts[ns_type] = namespace_counts.get(ns_type, 0) + 1

                summary = ", ".join(
                    f"{count} {ns_type}(s)"
                    for ns_type, count in namespace_counts.items()
                )
                dir_node.add(f"{filename} [{summary}]")

        self.console.print(tree)

    def _display_hierarchical_preview(self, formatted_data: dict[str, Any]) -> None:
        """
        Display a preview of hierarchically-formatted data.

        Args:
            formatted_data: Hierarchically-formatted data
        """
        tree = Tree("Package Structure", guide_style="bold bright_blue")

        # Process packages
        packages = formatted_data.get("packages", {})
        modules = formatted_data.get("modules", {})

        # Add packages
        package_preview_count = min(5, len(packages))
        for i, (package_name, package_data) in enumerate(packages.items()):
            if i >= package_preview_count:
                remaining = len(packages) - package_preview_count
                tree.add(f"... {remaining} more packages")
                break

            package_node = tree.add(f"{package_name}/")
            self._add_package_to_tree(package_data, package_node, depth=1)

        # Add root modules
        module_preview_count = min(5, len(modules))
        for i, (module_name, module_data) in enumerate(modules.items()):
            if i >= module_preview_count:
                remaining = len(modules) - module_preview_count
                tree.add(f"... {remaining} more modules")
                break

            module_node = tree.add(f"{module_name}.py")
            self._add_module_summary(module_data, module_node)

        self.console.print(tree)

    def _add_package_to_tree(
        self, package_data: dict[str, Any], parent_node: Tree, depth: int = 1
    ) -> None:
        """
        Add package data to a tree node.

        Args:
            package_data: Package data dictionary
            parent_node: Parent tree node
            depth: Current depth level
        """
        if depth > 2:  # Limit depth for preview
            return

        # Add sub-packages
        packages = package_data.get("packages", {})
        package_preview_count = min(3, len(packages))

        for i, (package_name, sub_package) in enumerate(packages.items()):
            if i >= package_preview_count:
                remaining = len(packages) - package_preview_count
                parent_node.add(f"... {remaining} more packages")
                break

            package_node = parent_node.add(f"{package_name}/")
            self._add_package_to_tree(sub_package, package_node, depth + 1)

        # Add modules
        modules = package_data.get("modules", {})
        module_preview_count = min(3, len(modules))

        for i, (module_name, module_data) in enumerate(modules.items()):
            if i >= module_preview_count:
                remaining = len(modules) - module_preview_count
                parent_node.add(f"... {remaining} more modules")
                break

            module_node = parent_node.add(f"{module_name}.py")
            self._add_module_summary(module_data, module_node)

    def _add_module_summary(
        self, module_data: dict[str, Any], module_node: Tree
    ) -> None:
        """
        Add module summary to a tree node.

        Args:
            module_data: Module data dictionary
            module_node: Module tree node
        """
        classes = module_data.get("classes", {})
        functions = module_data.get("functions", [])
        variables = module_data.get("variables", [])

        if classes:
            class_text = f"{len(classes)} class(es)"
            if len(classes) <= 3:
                class_text += f": {', '.join(classes.keys())}"
            module_node.add(class_text)

        if functions:
            self._tree_node_summary(functions, " function(s)", module_node)
        if variables and self.config.include_module_vars:
            self._tree_node_summary(variables, " variable(s)", module_node)

    def _tree_node_summary(
        self, arg0: list[dict[str, Any]], arg1: str, module_node: Tree
    ) -> None:
        """
        Add module summary to a tree node.

        Args:
            arg0: Module data dictionary
            arg1: Module node
        """
        func_text = f"{len(arg0)}{arg1}"
        if len(arg0) <= 3:
            func_text += f": {', '.join(f['name'] for f in arg0)}"
        module_node.add(func_text)

    def interactive_filter(self) -> None:
        """Allow interactive filtering of the displayed results."""
        if not self.result_data:
            self.console.print("[yellow]No data available for filtering.[/yellow]")
            return

        self.console.print("[bold]Interactive Filtering[/bold]")
        self.console.print("Specify criteria to filter the results.")

        # Filter options
        filter_options = [
            "Filter by name pattern",
            "Filter by namespace type",
            "Filter by directory",
            "Reset filters",
            "Back to main menu",
        ]

        for i, option in enumerate(filter_options, 1):
            self.console.print(f"{i}. {option}")

        choice = Prompt.ask(
            "Select a filter option",
            choices=[str(i) for i in range(1, len(filter_options) + 1)],
            default="5",
        )

        choice_idx = int(choice) - 1

        if choice_idx == 0:  # Name pattern
            pattern = Prompt.ask("Enter name pattern to include")
            self.config.formatting_options.name_patterns.append(pattern)
            self.console.print(f"[green]Added pattern filter: {pattern}[/green]")

        elif choice_idx == 1:  # Namespace type
            type_options = {
                "1": NamespaceType.CLASS,
                "2": NamespaceType.FUNCTION,
                "3": NamespaceType.METHOD,
                "4": NamespaceType.NESTED_CLASS,
                "5": NamespaceType.VARIABLE,
            }

            for key, value in type_options.items():
                self.console.print(f"{key}. {value.value}")

            type_choice = Prompt.ask(
                "Select namespace type to include/exclude",
                choices=list(type_options.keys()),
            )

            selected_type = type_options[type_choice]

            if selected_type in self.config.formatting_options.include_types:
                self.config.formatting_options.include_types.remove(selected_type)
                self.console.print(f"[yellow]Excluded {selected_type.value}[/yellow]")
            else:
                self.config.formatting_options.include_types.add(selected_type)
                self.console.print(f"[green]Included {selected_type.value}[/green]")

        elif choice_idx == 2:  # Directory
            if self.config.formatter_type == FormatterType.DICTIONARY:
                directories = list(self.result_data.keys())

                # Display directories
                for i, directory in enumerate(directories, 1):
                    self.console.print(f"{i}. {directory or '[root]'}")

                dir_choice = Prompt.ask(
                    "Select directory to focus on",
                    choices=[str(i) for i in range(1, len(directories) + 1)],
                )

                selected_dir = directories[int(dir_choice) - 1]

                # Update display to show only the selected directory
                self._display_dictionary_preview(
                    {selected_dir: self.result_data[selected_dir]}
                )
            else:
                self.console.print(
                    "[yellow]Directory filter not shown in hierarchical view.[/yellow]"
                )

        elif choice_idx == 3:  # Reset filters
            self.config.formatting_options.name_patterns = []
            self.config.formatting_options.exclude_name_patterns = []
            self.config.formatting_options.include_types = {
                NamespaceType.CLASS,
                NamespaceType.FUNCTION,
                NamespaceType.METHOD,
                NamespaceType.NESTED_CLASS,
                NamespaceType.VARIABLE,
            }
            self.console.print("[green]All filters reset.[/green]")

            # Re-display with reset filters
            self.display_results_preview(self.result_data)
