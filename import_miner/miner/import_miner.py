#!/usr/bin/env python3
"""
Advanced Import Management System (AIMS)

A sophisticated tool for analyzing, extracting, and managing Python imports
in a project-wide context, with integration to ImportMagic.
"""

import ast
import concurrent.futures
import datetime
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from typing import Any

import importmagic
import jedi
import networkx as nx
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AIMS")


class ImportAnalysisError(Exception):
    """Custom exception for import analysis errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    pass


class LogManager:
    """Manages the creation and organization of log files."""

    def __init__(self, root_dir: str) -> None:
        """Initialize the log manager.

        Args:
            root_dir: The root directory of the project.
        """
        self.root_dir = root_dir
        self.log_dir = os.path.join(root_dir, "import_log")
        self.current_session_dir = None
        self._setup_log_directory()

    def _setup_log_directory(self) -> None:
        """Create the log directory structure."""
        # Create main log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            logger.info(f"Created import log directory at {self.log_dir}")

        # Create dated session directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_dir = os.path.join(self.log_dir, f"session_{timestamp}")
        os.makedirs(self.current_session_dir)

        # Create subdirectories for different log types
        os.makedirs(os.path.join(self.current_session_dir, "linter_logs"))
        os.makedirs(os.path.join(self.current_session_dir, "import_analysis"))
        os.makedirs(os.path.join(self.current_session_dir, "reports"))

        logger.info(f"Created session directory at {self.current_session_dir}")

    def get_linter_log_path(self, filename: str) -> str:
        """Get the path for a linter log file.

        Args:
            filename: The name of the file to be analyzed.

        Returns:
            The path where the linter log should be stored.
        """
        base_name = os.path.basename(filename)
        safe_name = re.sub(r"[^\w\-_.]", "_", base_name)
        session_dir = self.current_session_dir or ""
        return os.path.join(session_dir, "linter_logs", f"{safe_name}.log")

    def get_import_analysis_path(self, filename: str) -> str:
        """Get the path for an import analysis file.

        Args:
            filename: The name of the file to be analyzed.

        Returns:
            The path where the import analysis should be stored.
        """
        base_name = os.path.basename(filename)
        safe_name = re.sub(r"[^\w\-_.]", "_", base_name)
        session_dir = self.current_session_dir or ""
        return os.path.join(session_dir, "import_analysis", f"{safe_name}.json")

    def get_report_path(self, report_name: str) -> str:
        """Get the path for a report file.

        Args:
            report_name: The name of the report.

        Returns:
            The path where the report should be stored.
        """
        session_dir = self.current_session_dir or ""
        return os.path.join(session_dir, "reports", f"{report_name}.txt")

    def get_session_summary_path(self) -> str:
        """Get the path for the session summary file.

        Returns:
            The path where the session summary should be stored.
        """
        session_dir = self.current_session_dir or ""
        return os.path.join(session_dir, "session_summary.json")


class CodebaseAnalyzer:
    """Analyzes the codebase to find Python files for import analysis."""

    def __init__(self, root_dir: str, exclude_dirs: list[str] | None = None) -> None:
        """Initialize the codebase analyzer.

        Args:
            root_dir: The root directory of the project.
            exclude_dirs: List of directories to exclude from analysis.
        """
        self.root_dir = root_dir
        self.exclude_dirs = exclude_dirs or [
            "venv",
            ".env",
            ".git",
            "__pycache__",
            "import_log",
        ]
        self.python_files = []

    def scan_codebase(self) -> list[str]:
        """Scan the codebase for Python files.

        Returns:
            A list of Python file paths.
        """
        logger.info(f"Scanning codebase at {self.root_dir} for Python files...")

        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    self.python_files.append(full_path)

        logger.info(f"Found {len(self.python_files)} Python files for analysis.")
        return self.python_files


class LintingEngine:
    """Performs deep code analysis using multiple linters."""

    def __init__(self, log_manager: LogManager) -> None:
        """Initialize the linting engine.

        Args:
            log_manager: The log manager for storing linter outputs.
        """
        self.log_manager = log_manager
        self._ensure_linters_installed()

    def _ensure_linters_installed(self) -> None:
        """Check and install required linters if missing."""
        required_packages = ["pylint", "flake8", "pyflakes", "mypy", "jedi"]

        # Check if each package is installed
        for package in required_packages:
            try:
                # Try to import the package
                __import__(package)
                logger.debug(f"Linter {package} is already installed")
            except ImportError:
                # If import fails, attempt to install it
                logger.info(f"Installing required linter: {package}")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    logger.info(f"Successfully installed {package}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install {package}: {e!s}")

    def _analyze_with_jedi(self, file_path: str, source_code: str) -> dict[str, Any]:
        """Use Jedi to perform deeper import analysis.

        Args:
            file_path: Path to the Python file.
            source_code: Source code content.

        Returns:
            Dictionary with Jedi analysis results.
        """

        jedi_results = {"missing_imports": [], "import_suggestions": []}

        # Create a Jedi Script object with the source code
        script = jedi.Script(code=source_code, path=file_path)

        # Find undefined names that might need imports
        for name in script.get_names():
            if name.is_definition() and name.type == "name" and not name.parent():
                try:
                    # Try to get completions for this name
                    completions = script.complete(name.line, name.column)
                    if completions:
                        for completion in completions:
                            if completion.type == "module":
                                module_path = completion.module_path
                                module_name = completion.module_name

                                # Log module path info for debugging
                                if module_path:
                                    logger.debug(
                                        f"Found module path for {name}: {module_path}"
                                    )

                                if module_name and module_name != "builtins":
                                    jedi_results["import_suggestions"].append(
                                        {
                                            "name": name.name,
                                            "module": module_name,
                                            "module_path": module_path,
                                            "line": name.line,
                                        }
                                    )
                except Exception as e:
                    logger.debug(f"Jedi error for {name.name}: {e!s}")

        return jedi_results

    def lint_file(self, file_path: str) -> str:
        """Lint a single Python file and store the results.

        Args:
            file_path: Path to the Python file.

        Returns:
            Path to the generated linter log file.
        """
        log_path = self.log_manager.get_linter_log_path(file_path)

        with open(log_path, "w") as log_file:
            # Run multiple linters for comprehensive analysis
            linters = [
                ["pylint", "--output-format=json", file_path],
                ["flake8", "--max-line-length=120", file_path],
                ["pyflakes", file_path],
                ["mypy", "--show-error-context", file_path],
            ]

            for linter_cmd in linters:
                log_file.write(f"\n\n--- {linter_cmd[0]} OUTPUT ---\n\n")
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", *linter_cmd],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    log_file.write(result.stdout)
                    log_file.write(result.stderr)
                except Exception as e:
                    log_file.write(f"Error running {linter_cmd[0]}: {e!s}")

        return log_path


class ImportExtractor:
    """Extracts and analyzes import statements from Python files."""

    def __init__(self, log_manager: LogManager) -> None:
        """Initialize the import extractor.

        Args:
            log_manager: The log manager for storing analysis results.
        """
        self.log_manager = log_manager
        self.symbol_graph = nx.DiGraph()

    def extract_imports_from_file(self, file_path: str) -> dict[str, Any]:
        """Extract import statements from a single Python file with Jedi integration.

        Args:
            file_path: Path to the Python file.

        Returns:
            Dictionary with comprehensive import analysis results.
        """
        analysis_result = {
            "file_path": file_path,
            "imports": [],
            "used_symbols": set(),
            "defined_symbols": set(),
            "potential_missing_imports": [],
            "unused_imports": [],
            "jedi_suggestions": [],  # New field for Jedi-specific suggestions
        }

        try:
            with open(file_path, encoding="utf-8") as file:
                source_code = file.read()

            # Parse the source code into an AST
            tree = ast.parse(source_code)

            # Extract imports using AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        alias = name.asname or name.name
                        analysis_result["imports"].append(
                            {
                                "type": "import",
                                "module": name.name,
                                "alias": alias,
                                "line": node.lineno,
                            }
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        alias = name.asname or name.name
                        analysis_result["imports"].append(
                            {
                                "type": "from",
                                "module": module,
                                "name": name.name,
                                "alias": alias,
                                "line": node.lineno,
                            }
                        )

                # Track symbol usage and definitions for deeper analysis
                self._analyze_symbol_usage(node, analysis_result)

            # Enhance analysis with Jedi
            try:
                import jedi

                # Create a Jedi Script object for the file
                script = jedi.Script(code=source_code, path=file_path)

                # Find undefined names that might need imports
                for name in analysis_result["used_symbols"]:
                    # Skip if it's already defined or imported
                    if name in analysis_result["defined_symbols"] or any(
                        imp.get("alias") == name for imp in analysis_result["imports"]
                    ):
                        continue

                    # Try to find the module for this name using Jedi
                    try:
                        # Create a simple usage of the name to let Jedi infer its type
                        completion_line = f"{name}"
                        temp_script = jedi.Script(code=completion_line)
                        completions = temp_script.complete(1, len(completion_line))

                        for completion in completions:
                            if completion.type in ("module", "class", "function"):
                                module_path = completion.module_path
                                module_name = completion.module_name

                                # Log module path info for debugging
                                if module_path:
                                    logger.debug(
                                        f"Found module path for {name}: {module_path}"
                                    )

                                if module_name and module_name != "builtins":
                                    analysis_result["jedi_suggestions"].append(
                                        {
                                            "symbol": name,
                                            "module": module_name,
                                            # Include module_path in suggestions
                                            "module_path": module_path,
                                            "type": completion.type,
                                            "import_statement": (
                                                f"from {module_name} import {name}"
                                                if "." in module_name
                                                else f"import {module_name}"
                                            ),
                                        }
                                    )
                    except Exception as e:
                        logger.debug(f"Jedi completion error for '{name}': {e!s}")

                # Use Jedi to find unused imports
                for imp in analysis_result["imports"]:
                    alias = imp.get("alias")
                    if alias and alias not in analysis_result["used_symbols"]:
                        # Double-check with Jedi's more advanced usage analysis
                        # This complements our AST-based analysis and can catch
                        # more complex cases
                        references = script.get_references(
                            line=imp.get("line", 1),
                            column=0,  # This is approximate
                            include_builtins=False,
                        )

                        # If Jedi finds no references either, it's likely unused
                        if len(references) <= 1:  # 1 reference is the import itself
                            if alias not in analysis_result["unused_imports"]:
                                analysis_result["unused_imports"].append(alias)

            except ImportError:
                logger.warning("Jedi not available. Using basic AST analysis only.")
            except Exception as e:
                logger.warning(f"Error during Jedi analysis: {e!s}")

            # Process the analysis to find potential issues using both AST and
            # Jedi results
            self._process_analysis_results(analysis_result)

            # Save the analysis result
            analysis_path = self.log_manager.get_import_analysis_path(file_path)
            with open(analysis_path, "w") as f:
                # Convert sets to lists for JSON serialization
                serializable_result = analysis_result.copy()
                serializable_result["used_symbols"] = list(
                    analysis_result["used_symbols"]
                )
                serializable_result["defined_symbols"] = list(
                    analysis_result["defined_symbols"]
                )
                json.dump(serializable_result, f, indent=2)

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing imports in {file_path}: {e!s}")
            raise ImportAnalysisError(f"Failed to analyze {file_path}: {e!s}") from e

    def _analyze_symbol_usage(
        self, node: ast.AST, analysis_result: dict[str, Any]
    ) -> None:
        """Analyze how symbols are used and defined in the AST node.

        Args:
            node: The AST node to analyze.
            analysis_result: The analysis result dictionary to update.
        """
        # Track defined symbols
        if isinstance(node, ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef):
            analysis_result["defined_symbols"].add(node.name)

        # Track variable assignments
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    analysis_result["defined_symbols"].add(target.id)

        # Track symbol usage
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                analysis_result["used_symbols"].add(node.id)

    def _process_analysis_results(self, analysis_result: dict[str, Any]) -> None:
        """Process the analysis results to identify import issues.

        Args:
            analysis_result: The analysis result dictionary to process.
        """
        # Identify imported symbols
        imported_symbols = set()
        for imp in analysis_result["imports"]:
            if imp["type"] == "import":
                imported_symbols.add(imp["alias"])
            else:  # from import
                imported_symbols.add(imp["alias"])

        # Find unused imports
        for symbol in imported_symbols:
            if symbol not in analysis_result["used_symbols"] and symbol != "*":
                if symbol not in analysis_result["unused_imports"]:
                    analysis_result["unused_imports"].append(symbol)

        # Find potentially missing imports, prioritizing Jedi suggestions
        jedi_suggested_symbols = {
            suggestion["symbol"]
            for suggestion in analysis_result.get("jedi_suggestions", [])
        }

        for symbol in analysis_result["used_symbols"]:
            if (
                symbol not in imported_symbols
                and symbol not in analysis_result["defined_symbols"]
                and not symbol.startswith("__")
            ):
                if symbol in jedi_suggested_symbols:
                    # Jedi has a suggestion for this symbol, so we don't add it to
                    # potential_missing_imports as we'll use the Jedi suggestion instead
                    continue
                else:
                    analysis_result["potential_missing_imports"].append(symbol)

    def build_import_dependency_graph(
        self, analysis_results: list[dict[str, Any]]
    ) -> None:
        """Build a dependency graph from import analysis results.

        Args:
            analysis_results: List of import analysis results for all files.
        """
        # Create a mapping of symbol names to the files that define them
        symbol_definitions = defaultdict(list)
        for result in analysis_results:
            file_path = result.get("file_path", "")
            if not file_path:
                continue

            for symbol in result["defined_symbols"]:
                symbol_definitions[symbol].append(file_path)

        # Build the graph
        for result in analysis_results:
            file_path = result.get("file_path", "")
            if not file_path:
                continue

            file_node = file_path
            self.symbol_graph.add_node(file_node, type="file")

            # Add symbols defined in this file
            for symbol in result["defined_symbols"]:
                symbol_node = f"symbol:{symbol}"
                self.symbol_graph.add_node(symbol_node, type="symbol")
                self.symbol_graph.add_edge(file_node, symbol_node, type="defines")

            # Add dependencies on symbols used in this file
            for symbol in result["used_symbols"]:
                symbol_node = f"symbol:{symbol}"
                self.symbol_graph.add_node(symbol_node, type="symbol")
                self.symbol_graph.add_edge(symbol_node, file_node, type="used_by")

                # If the symbol is defined elsewhere, add that connection
                if symbol in symbol_definitions:
                    for defining_file in symbol_definitions[symbol]:
                        if defining_file != file_path:  # Avoid self-loops
                            self.symbol_graph.add_edge(
                                defining_file, symbol_node, type="defines"
                            )

    def suggest_imports(
        self, file_path: str, analysis_results: list[dict[str, Any]]
    ) -> list[str]:
        """Suggest imports for a file based on the dependency graph.

        Args:
            file_path: Path to the Python file.
            analysis_results: List of import analysis results for all files.

        Returns:
            List of suggested import statements.
        """
        # Find the analysis result for this file
        file_result = None
        for r in analysis_results:
            if r.get("file_path") == file_path:
                file_result = r
                break

        if not file_result:
            return []

        # Start with potential missing imports from the file's analysis
        missing_symbols = file_result.get("potential_missing_imports", [])
        suggested_imports = []

        # Find where these symbols are defined in the project
        for symbol in missing_symbols:
            symbol_node = f"symbol:{symbol}"

            if symbol_node in self.symbol_graph:
                # Find files that define this symbol
                defining_files = []
                try:
                    # Using list(self.symbol_graph.edges(data=True)) ensures we get
                    # all three elements in each tuple
                    edges = list(self.symbol_graph.edges(data=True))
                    for edge in edges:
                        if len(edge) == 3:
                            source, target, data = edge
                            if (
                                target == symbol_node
                                and isinstance(data, dict)
                                and data.get("type") == "defines"
                                and isinstance(source, str)
                                and source.endswith(".py")
                            ):
                                defining_files.append(source)
                except Exception as e:
                    logger.error(f"Error processing graph edges: {e!s}")

                if defining_files:
                    # Get the most relevant defining file based on project structure
                    best_match = self._find_best_import_source(
                        file_path, defining_files
                    )

                    # Create import statement based on the best match
                    module_path = self._convert_path_to_module(best_match)
                    if module_path:
                        suggested_imports.append(f"from {module_path} import {symbol}")

        return suggested_imports

    def _find_best_import_source(
        self, target_file: str, source_files: list[str]
    ) -> str:
        """Find the best source file for importing a symbol.

        Args:
            target_file: The file that needs the import.
            source_files: Files that define the needed symbol.

        Returns:
            The best source file path for the import.
        """
        # Simple heuristic: prefer files in the same directory
        target_dir = os.path.dirname(target_file)

        for source in source_files:
            if os.path.dirname(source) == target_dir:
                return source

        # If no file in the same directory, return the first one
        return source_files[0] if source_files else ""

    def _convert_path_to_module(self, file_path: str) -> str:
        """Convert a file path to a Python module path.

        Args:
            file_path: The file path to convert.

        Returns:
            The Python module path corresponding to the file path.
        """
        if not file_path:
            return ""

        # Remove file extension
        if file_path.endswith(".py"):
            file_path = file_path[:-3]

        # Replace directory separators with dots
        module_path = file_path.replace(os.path.sep, ".")

        # Remove leading dots
        module_path = module_path.lstrip(".")

        return module_path


class IntegrationPipeline:
    """Integrates analysis results with ImportMagic."""

    def __init__(self, log_manager: LogManager) -> None:
        """Initialize the integration pipeline.

        Args:
            log_manager: The log manager for accessing analysis results.
        """
        self.log_manager = log_manager
        self.importmagic_index = importmagic.SymbolIndex()
        self._initialize_importmagic()

    def _initialize_importmagic(self) -> None:
        """Initialize the ImportMagic symbol index."""
        logger.info("Building ImportMagic symbol index...")
        # Handle importmagic.paths_from_interpreter() method not found
        try:
            paths = importmagic.paths_from_interpreter()  # type: ignore
        except AttributeError:
            # Fallback if the method doesn't exist
            paths = [os.path.dirname(p) for p in sys.path if os.path.isdir(p)]

        self.importmagic_index.build_index(paths=paths)
        logger.info("ImportMagic symbol index built.")

    def process_file_with_importmagic(
        self, file_path: str, suggested_imports: list[str]
    ) -> tuple[bool, dict[str, Any]]:
        """Process a file with ImportMagic, incorporating suggested imports.

        Args:
            file_path: Path to the Python file.
            suggested_imports: List of suggested import statements.

        Returns:
            Tuple of (success, stats) where stats is a dictionary of changes made.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            # Parse the source with ImportMagic
            scope = importmagic.Scope.from_source(source)
            unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

            # Add our custom suggested imports
            suggested_symbols = set()
            for import_stmt in suggested_imports:
                if import_stmt.startswith("from "):
                    # Extract the symbol name from "from module import symbol"
                    symbol = import_stmt.split("import ")[1].strip()
                    suggested_symbols.add(symbol)

            # Combine ImportMagic's findings with our suggestions
            all_unresolved = unresolved.union(suggested_symbols)

            # Create the imports manager
            imports = importmagic.Imports(self.importmagic_index, source)

            # Remove unused imports
            if unreferenced:
                try:
                    imports.remove(unreferenced)  # type: ignore
                except (TypeError, AttributeError) as e:
                    logger.warning(f"Failed to remove imports: {e!s}")

            # Add required imports
            if all_unresolved:
                try:
                    # Try as set first
                    imports.add(all_unresolved)  # type: ignore
                except (TypeError, AttributeError):
                    # Try as individual symbols
                    for symbol in all_unresolved:
                        try:
                            # Try with single symbol at a time
                            imports.add(symbol)  # type: ignore
                        except Exception as e:
                            logger.warning(
                                f"Failed to add import for symbol {symbol}: {e!s}"
                            )

            # Get the updated source code
            updated_source = (
                source  # Default to original in case all update methods fail
            )

            try:
                # Try without arguments first
                updated_source = imports.update_source()  # type: ignore
            except (TypeError, AttributeError):
                try:
                    # Try with source code argument
                    updated_source = imports.update_source(source)  # type: ignore
                except Exception as e:
                    logger.error(f"Failed to update source: {e!s}")

            # Write the changes back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_source)

            # Compute statistics
            stats = {
                "removed_imports": list(unreferenced) if unreferenced else [],
                "added_imports": list(all_unresolved) if all_unresolved else [],
                "removed_count": len(unreferenced) if unreferenced else 0,
                "added_count": len(all_unresolved) if all_unresolved else 0,
                "suggested_imports": suggested_imports,
            }

            return True, stats

        except Exception as e:
            logger.error(f"Error processing {file_path} with ImportMagic: {e!s}")
            return False, {"error": str(e)}


class ReportGenerator:
    """Generates reports on import analysis and changes."""

    def __init__(self, log_manager: LogManager) -> None:
        """Initialize the report generator.

        Args:
            log_manager: The log manager for accessing logs and saving reports.
        """
        self.log_manager = log_manager

    def generate_file_report(self, file_path: str, stats: dict[str, Any]) -> str:
        """Generate a report for a single file.

        Args:
            file_path: Path to the Python file.
            stats: Statistics about the changes made.

        Returns:
            Path to the generated report file.
        """
        report_name = os.path.basename(file_path).replace(".py", "")
        report_path = self.log_manager.get_report_path(f"file_{report_name}")

        with open(report_path, "w") as f:
            f.write(f"Import Analysis Report for {file_path}\n")
            f.write("=" * 80 + "\n\n")

            f.write("Summary:\n")
            f.write(f"- Removed imports: {stats.get('removed_count', 0)}\n")
            f.write(f"- Added imports: {stats.get('added_count', 0)}\n\n")

            if stats.get("removed_imports"):
                f.write("Removed Imports:\n")
                for imp in stats["removed_imports"]:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get("added_imports"):
                f.write("Added Imports:\n")
                for imp in stats["added_imports"]:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get("suggested_imports"):
                f.write("Custom Suggested Imports:\n")
                for imp in stats["suggested_imports"]:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get("error"):
                f.write(f"Error: {stats['error']}\n\n")

        return report_path

    def generate_session_summary(
        self, all_stats: list[tuple[str, dict[str, Any]]]
    ) -> str:
        """Generate a summary report for the entire session.

        Args:
            all_stats: List of (file_path, stats) tuples for all processed files.

        Returns:
            Path to the generated summary file.
        """
        summary_path = self.log_manager.get_session_summary_path()

        # Calculate aggregate statistics
        total_files = len(all_stats)
        successful_files = sum(1 for _, stats in all_stats if not stats.get("error"))
        total_removed = sum(stats.get("removed_count", 0) for _, stats in all_stats)
        total_added = sum(stats.get("added_count", 0) for _, stats in all_stats)

        # Find files with most issues
        files_by_issues = sorted(
            all_stats,
            key=lambda x: (x[1].get("removed_count", 0) + x[1].get("added_count", 0)),
            reverse=True,
        )

        with open(summary_path, "w") as f:
            f.write("Advanced Import Management System (AIMS) Session Summary\n")
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            f.write("Overall Statistics:\n")
            f.write(f"- Total files processed: {total_files}\n")
            f.write(f"- Successfully processed files: {successful_files}\n")
            f.write(f"- Failed files: {total_files - successful_files}\n")
            f.write(f"- Total imports removed: {total_removed}\n")
            f.write(f"- Total imports added: {total_added}\n\n")

            if files_by_issues:
                f.write("Files with Most Import Issues:\n")
                for file_path, stats in files_by_issues[:10]:  # Top 10 files
                    issues = stats.get("removed_count", 0) + stats.get("added_count", 0)
                    if issues > 0:
                        f.write(
                            f"- {file_path}: {issues} issues "
                            f"({stats.get('removed_count', 0)} removed, "
                            f"{stats.get('added_count', 0)} added)\n"
                        )
                f.write("\n")

            f.write("Files with Errors:\n")
            error_count = 0
            for file_path, stats in all_stats:
                if stats.get("error"):
                    f.write(f"- {file_path}: {stats['error']}\n")
                    error_count += 1

            if error_count == 0:
                f.write("- No errors encountered.\n")

        # Also save as JSON for programmatic access
        with open(summary_path + ".json", "w") as f:
            summary_data = {
                "date": datetime.datetime.now().isoformat(),
                "total_files": total_files,
                "successful_files": successful_files,
                "failed_files": total_files - successful_files,
                "total_removed": total_removed,
                "total_added": total_added,
                "file_stats": {path: stats for path, stats in all_stats},
            }
            json.dump(summary_data, f, indent=2)

        return summary_path


def main() -> int:
    """Run the AIMS tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Advanced Import Management System for Python projects"
    )
    parser.add_argument(
        "project_dir", help="The root directory of the Python project to analyze"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        default=["venv", ".env", ".git", "__pycache__", "import_log"],
        help="Directories to exclude from analysis",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze imports but don't modify files"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run analysis in parallel for better performance",
    )

    args = parser.parse_args()

    # Validate project directory
    if not os.path.isdir(args.project_dir):
        logger.error(
            f"Project directory {args.project_dir} "
            f"does not exist or is not a directory."
        )
        return 1

    # Set up components
    log_manager = LogManager(args.project_dir)
    codebase_analyzer = CodebaseAnalyzer(args.project_dir, args.exclude_dirs)
    linting_engine = LintingEngine(log_manager)
    import_extractor = ImportExtractor(log_manager)
    integration_pipeline = IntegrationPipeline(log_manager)
    report_generator = ReportGenerator(log_manager)

    # Step 1: Find all Python files in the project
    python_files = codebase_analyzer.scan_codebase()

    if not python_files:
        logger.warning("No Python files found in the project directory.")
        return 0

    # Step 2: Run linters on all files
    logger.info("Running linters on all Python files...")

    if args.parallel:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            linter_futures = {}
            for file_path in python_files:
                # Handle lint_file method possibly not existing
                try:
                    linter_futures[
                        executor.submit(linting_engine.lint_file, file_path)
                    ] = file_path
                except AttributeError:
                    logger.warning(f"Linting not available for {file_path}")

            for future in tqdm(
                concurrent.futures.as_completed(linter_futures),
                total=len(linter_futures),
                desc="Linting files",
            ):
                file_path = linter_futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error linting {file_path}: {e!s}")
    else:
        for file_path in tqdm(python_files, desc="Linting files"):
            # Handle lint_file method possibly not existing
            try:
                linting_engine.lint_file(file_path)
            except AttributeError:
                logger.warning(f"Linting not available for {file_path}")
            except Exception as e:
                logger.error(f"Error linting {file_path}: {e!s}")

    # Step 3: Extract and analyze imports
    logger.info("Extracting and analyzing imports...")

    all_analysis_results = []

    if args.parallel:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extraction_futures = {}
            for file_path in python_files:
                # Handle extract_imports_from_file method possibly not existing
                try:
                    extraction_futures[
                        executor.submit(
                            import_extractor.extract_imports_from_file, file_path
                        )
                    ] = file_path
                except AttributeError:
                    logger.warning(f"Import extraction not available for {file_path}")

            for future in tqdm(
                concurrent.futures.as_completed(extraction_futures),
                total=len(extraction_futures),
                desc="Analyzing imports",
            ):
                file_path = extraction_futures[future]
                try:
                    result = future.result()
                    all_analysis_results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing imports in {file_path}: {e!s}")
    else:
        for file_path in tqdm(python_files, desc="Analyzing imports"):
            # Handle extract_imports_from_file method possibly not existing
            try:
                result = import_extractor.extract_imports_from_file(file_path)
                all_analysis_results.append(result)
            except AttributeError:
                logger.warning(f"Import extraction not available for {file_path}")
            except Exception as e:
                logger.error(f"Error analyzing imports in {file_path}: {e!s}")

    # Step 4: Build the import dependency graph
    logger.info("Building import dependency graph...")
    try:
        import_extractor.build_import_dependency_graph(all_analysis_results)
    except AttributeError:
        logger.warning("Import dependency graph generation not available")

    # Step 5: Process files with ImportMagic and suggested imports
    logger.info("Processing files with ImportMagic and suggested imports...")

    all_stats = []

    for file_path in tqdm(python_files, desc="Fixing imports"):
        try:
            # Get suggested imports based on our analysis
            suggested_imports = import_extractor.suggest_imports(
                file_path, all_analysis_results
            )

            if args.dry_run:
                # Just record what would have been done
                stats = {"suggested_imports": suggested_imports, "dry_run": True}
                all_stats.append((file_path, stats))
            else:
                # Actually apply the changes
                success, stats = integration_pipeline.process_file_with_importmagic(
                    file_path, suggested_imports
                )
                all_stats.append((file_path, stats))

                # Generate a report for this file
                report_generator.generate_file_report(file_path, stats)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e!s}")
            all_stats.append((file_path, {"error": str(e)}))

    # Step 6: Generate a session summary report
    logger.info("Generating session summary report...")
    summary_path = report_generator.generate_session_summary(all_stats)

    logger.info(
        f"Import analysis and processing complete. Summary available at: {summary_path}"
    )

    # Indicate success
    return 0


if __name__ == "__main__":
    sys.exit(main())
