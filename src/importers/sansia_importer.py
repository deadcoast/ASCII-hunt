"""SANSIA format importer for ASCII art."""

from typing import Any

import z3  # type: ignore

from src.core.ascii_grid import ASCIIGrid
from src.core.component import Component


class SANSIAImporter:
    """Importer for SANSIA format ASCII art files."""

    def __init__(self) -> None:
        """Initialize the SANSIA importer."""
        self.solver: Any = z3.Solver()  # type: ignore
        self.variables: dict[str, Any] = {}
        self.components: list[Component] = []

    def import_file(self, filepath: str) -> ASCIIGrid:
        """Import SANSIA format file and convert to ASCIIGrid.

        Args:
            filepath: Path to SANSIA format file

        Returns:
            ASCIIGrid representation of the imported art
        """
        with open(filepath) as f:
            content = f.read()

        return self._parse_sansia(content)

    def _parse_sansia(self, content: str) -> ASCIIGrid:
        """Parse SANSIA format content.

        Args:
            content: SANSIA format string content

        Returns:
            ASCIIGrid representation
        """
        lines = content.strip().split("\n")
        grid_data: list[list[str]] = []
        current_component: dict[str, Any] | None = None

        for line in lines:
            if line.startswith("#"):
                if current_component:
                    self._process_component(current_component)
                current_component = {"type": line[1:].strip(), "constraints": []}
            elif line.startswith("constraint:"):
                if current_component:
                    current_component["constraints"].append(line[11:].strip())
            else:
                grid_data.append(list(line))

        if current_component:
            self._process_component(current_component)

        # Convert grid data to ASCIIGrid
        return ASCIIGrid(grid_data)

    def _process_component(self, component_data: dict[str, Any]) -> None:
        """Process component data and add constraints to solver.

        Args:
            component_data: Dictionary containing component information
        """
        component = Component(
            name=component_data["type"], constraints=component_data["constraints"]
        )
        self.components.append(component)

        # Add component constraints to Z3 solver
        for constraint in component_data["constraints"]:
            try:
                z3_constraint = self._parse_constraint(constraint)
                if z3_constraint is not None:
                    self.solver.add(z3_constraint)
            except Exception as e:
                print(f"Error parsing constraint: {constraint}")
                print(f"Z3 error: {e}")

    def _parse_constraint(self, constraint: str) -> Any | None:
        """Parse constraint string into Z3 constraint.

        Args:
            constraint: Constraint string in SANSIA format

        Returns:
            Z3 boolean expression or None if parsing fails
        """
        try:
            # Create variables if they don't exist
            for var in self._extract_variables(constraint):
                if var not in self.variables:
                    self.variables[var] = z3.Int(var)  # type: ignore

            # Replace variable names with Z3 variables
            z3_expr = constraint
            for var, z3_var in self.variables.items():
                z3_expr = z3_expr.replace(var, str(z3_var))

            return z3.parse_smt2_string(f"(assert {z3_expr}")[-1]  # type: ignore
        except Exception:
            return None

    def _extract_variables(self, constraint: str) -> list[str]:
        """Extract variable names from constraint string.

        Args:
            constraint: Constraint string

        Returns:
            List of variable names
        """
        # Simple variable extraction - assumes variables are alphanumeric
        import re

        return re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", constraint)

    def solve_constraints(self) -> dict[str, int] | None:
        """Solve the system of constraints.

        Returns:
            Dictionary mapping variable names to values, or None if unsatisfiable
        """
        if self.solver.check() == z3.sat:  # type: ignore
            model = self.solver.model()
            return {
                str(var): model[z3_var].as_long()
                for var, z3_var in self.variables.items()
                if model[z3_var] is not None
            }
        return None
