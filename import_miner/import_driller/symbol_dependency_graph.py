"""Symbol Dependency Graph Module.

This module provides functionality for analyzing Python project dependencies at a symbol level.
"""

import ast
from collections import defaultdict

import networkx as nx
from utils.file_utils import file_path_to_module_name, find_python_files


class SymbolDependencyGraph:
    def __init__(self, project_root):
        """
        Initialize the SymbolDependencyGraph with the project root directory.

        Args:
            project_root (str): The root directory of the project for which the
                                symbol dependency graph is to be built.
        """
        self.project_root = project_root
        self.dependency_graph = nx.DiGraph()
        self.symbol_to_module = {}
        self.module_to_symbols = defaultdict(set)

    def analyze_project(self):
        """
        Build complete symbol-level dependency graph for the entire project.

        This method analyzes every Python file in the project to extract
        defined symbols and their dependencies. It then builds a graph of
        symbol dependencies across the project.

        After building the graph, it runs a transitive reduction to optimize
        the graph. This is important because the graph can be huge and
        contains many redundant edges due to the transitive nature of imports.

        :return: None
        """
        for file_path in find_python_files(self.project_root):
            self._process_file(file_path)

        # Run transitive reduction to optimize the graph
        self.dependency_graph = nx.transitive_reduction(self.dependency_graph)

    def _process_file(self, file_path: str) -> None:
        """
        Process a single file to extract defined symbols and dependencies.

        Args:
            file_path (str): Path to the Python file to process.

        :return: None
        """
        with open(file_path) as f:
            code = f.read()

        module_name = file_path_to_module_name(file_path, self.project_root)
        tree = ast.parse(code)

        # Extract defined symbols
        defined_symbols = self._extract_defined_symbols(tree, module_name)

        # Extract symbol references and build dependency edges
        self._extract_symbol_references(tree, module_name, defined_symbols)

    def _extract_defined_symbols(self, tree: ast.AST, module_name: str) -> set[str]:
        """
        Extract all symbols defined in an AST.

        Args:
            tree (ast.AST): The AST to analyze
            module_name (str): The name of the module being analyzed

        Returns:
            Set[str]: Set of defined symbol names
        """
        defined_symbols = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                symbol_name = node.name
                defined_symbols.add(symbol_name)
                self.symbol_to_module[symbol_name] = module_name
                self.module_to_symbols[module_name].add(symbol_name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbol_name = target.id
                        defined_symbols.add(symbol_name)
                        self.symbol_to_module[symbol_name] = module_name
                        self.module_to_symbols[module_name].add(symbol_name)

        return defined_symbols

    def _extract_symbol_references(
        self, tree: ast.AST, module_name: str, defined_symbols: set[str]
    ) -> None:
        """
        Extract all symbol references from an AST and build dependency edges.

        Args:
            tree (ast.AST): The AST to analyze
            module_name (str): The name of the module being analyzed
            defined_symbols (Set[str]): Set of symbols defined in this module

        Returns:
            None
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                symbol_name = node.id
                if (
                    symbol_name in self.symbol_to_module
                    and symbol_name not in defined_symbols
                ):
                    source_module = self.symbol_to_module[symbol_name]
                    if source_module != module_name:
                        self.dependency_graph.add_edge(module_name, source_module)

    def _calculate_coupling_metric(
        self, source_module: str, target_module: str
    ) -> float:
        """
        Calculate the coupling metric between two modules.

        Args:
            source_module (str): The source module name
            target_module (str): The target module name

        Returns:
            float: The coupling metric value
        """
        # Count direct dependencies between modules
        direct_deps = len(
            list(
                nx.all_simple_paths(
                    self.dependency_graph, source_module, target_module, cutoff=1
                )
            )
        )

        # Count indirect dependencies
        indirect_deps = len(
            list(
                nx.all_simple_paths(
                    self.dependency_graph, source_module, target_module, cutoff=None
                )
            )
        )

        return direct_deps + (0.5 * indirect_deps)

    def _calculate_cohesion_metric(
        self, source_module: str, target_module: str
    ) -> float:
        """
        Calculate the cohesion metric between two modules.

        Args:
            source_module (str): The source module name
            target_module (str): The target module name

        Returns:
            float: The cohesion metric value
        """
        # Get symbols defined in both modules
        source_symbols = self.module_to_symbols[source_module]
        target_symbols = self.module_to_symbols[target_module]

        # Calculate symbol overlap
        common_symbols = len(source_symbols.intersection(target_symbols))
        total_symbols = len(source_symbols.union(target_symbols))

        return common_symbols / total_symbols if total_symbols > 0 else 0.0

    def find_optimal_import_path(
        self, target_file: str, symbol_name: str
    ) -> str | None:
        """
        Find the optimal module to import a symbol from using graph algorithms.

        Args:
            target_file (str): The file that needs the import.
            symbol_name (str): The name of the symbol to import.

        Returns:
            str: The optimal module to import the symbol from, or None if no
                module defines the symbol.
        """
        if symbol_name not in self.symbol_to_module:
            return None

        possible_sources = self.symbol_to_module[symbol_name]
        target_module = file_path_to_module_name(target_file, self.project_root)

        best_path = None
        min_distance = float("inf")

        # Find the import path that minimizes coupling and maximizes cohesion
        for source_module in possible_sources:
            # Skip circular imports
            path_exists = nx.has_path(
                self.dependency_graph, source_module, target_module
            )
            if path_exists:
                continue

            # Calculate coupling metric
            coupling_metric = self._calculate_coupling_metric(
                source_module, target_module
            )

            # Calculate cohesion metric
            cohesion_metric = self._calculate_cohesion_metric(
                source_module, target_module
            )

            # Combined distance (lower is better)
            distance = coupling_metric - cohesion_metric

            if distance < min_distance:
                min_distance = distance
                best_path = source_module

        return best_path
