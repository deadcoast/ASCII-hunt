#!/usr/bin/env python3


from rich.console import Console


class ValidationReport:
    """Report class for validation results."""

    def __init__(self):
        """Initialize a new validation report."""
        self.console = Console()
        self.inputs = []
        self.outputs = []
        self.validations = []
        self.errors = []
        self.num_validated = 0
        self.num_failed = 0

    def add_error(self, error: str) -> None:
        """Add an error to the report.

        Args:
            error: Error message.
        """
        self.errors.append(error)
        self.num_failed += 1

    def add_input(self, input_path: str) -> None:
        """Add an input file to the report.

        Args:
            input_path: Path to input file.
        """
        self.inputs.append(input_path)

    def add_output(self, output_path: str) -> None:
        """Add an output file to the report.

        Args:
            output_path: Path to output file.
        """
        self.outputs.append(output_path)

    def add_validation(self, validation: str) -> None:
        """Add a validation result to the report.

        Args:
            validation: Validation result message.
        """
        self.validations.append(validation)
        self.num_validated += 1

    def print_header(self) -> None:
        """Print the report header."""
        self.console.print("[bold blue]Mermaid Diagram Validation Report[/bold blue]")
        self.print_separator()

    def print_separator(self) -> None:
        """Print a section separator."""
        self.console.print("-" * 80)

    def print_inputs(self) -> None:
        """Print the input files section."""
        self.console.print("[bold green]Input Files:[/bold green]")
        for input_path in self.inputs:
            self.console.print(f"  - {input_path}")
        self.print_separator()

    def print_outputs(self) -> None:
        """Print the output files section."""
        self.console.print("[bold green]Output Files:[/bold green]")
        for output_path in self.outputs:
            self.console.print(f"  - {output_path}")
        self.print_separator()

    def print_validations(self) -> None:
        """Print the validations section."""
        self.console.print("[bold green]Validation Results:[/bold green]")
        for validation in self.validations:
            self.console.print(f"  - {validation}")
        self.print_separator()

    def print_report(self) -> None:
        """Print the complete report."""
        self.print_header()
        self.print_inputs()
        self.print_outputs()
        self.print_validations()

        self.console.print("[bold]Summary:[/bold]")
        self.console.print(f"  Validated: {self.num_validated}")
        self.console.print(f"  Failed: {self.num_failed}")

        if self.errors:
            self.console.print("\n[bold red]Errors:[/bold red]")
            for error in self.errors:
                self.console.print(f"  - {error}")
        self.print_separator()
