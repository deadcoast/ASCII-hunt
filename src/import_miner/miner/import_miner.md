# ImportMagic Integration Plan

## For Junior Python Developers

This plan will guide you through integrating ImportMagic into your Python development workflow to solve import-related challenges. By following these steps, you'll set up a tool that automatically manages imports, saving you time and reducing errors.

## Phase 1: Understanding ImportMagic

ImportMagic is a specialized Python library focused exclusively on managing imports. It helps you:

1. Automatically detect and add missing imports
2. Remove unused imports
3. Organize imports according to PEP 8 standards
4. Index your Python environment to suggest the correct import location

Unlike general linting tools, ImportMagic focuses solely on import management, making it more effective for this specific purpose.

## Phase 2: Basic Setup

### Step 1: Installation

In your terminal or command prompt, run:

```
pip install importmagic
```

For additional functionality, also install:

```
pip install epc jedi
```

### Step 2: Verify Installation

Create a simple test file to verify ImportMagic works correctly:

1. Create a file named `test_importmagic.py`
2. Add this content:

   ```python
   import importmagicindex = importmagic.SymbolIndex()index.build_index(paths=importmagic.paths_from_interpreter())print("ImportMagic successfully installed!")
   ```

3. Run the file: `python test_importmagic.py`

If it prints the success message without errors, you're ready to proceed.

## Phase 3: Creating a Basic Import Fixer Script

Let's create a simple script that fixes imports in your Python files. This script will be your entry point to using ImportMagic.

### Step 1: Create Your Import Fixer

Create a file named `fix_imports.py` with this content:

```python
#!/usr/bin/env python
"""
Import fixer script using ImportMagic
Usage: python fix_imports.py your_file.py
"""

import importmagic
import sys
import os


def fix_imports(filename):
    """Fix imports in the given Python file."""
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist.")
        return False

    # Read the file content
    with open(filename, 'r') as f:
        source = f.read()

    print(f"Processing {filename}...")

    # Build an index of available modules
    print("Building module index (may take a moment)...")
    index = importmagic.SymbolIndex()
    index.build_index(paths=importmagic.paths_from_interpreter())

    # Parse the source code
    scope = importmagic.Scope.from_source(source)

    # Find unresolved and unreferenced symbols
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

    if not unresolved and not unreferenced:
        print("No import issues found!")
        return True

    # Report what will be changed
    if unresolved:
        print(f"Found {len(unresolved)} missing imports: {', '.join(unresolved)}")

    if unreferenced:
        print(f"Found {len(unreferenced)} unused imports: {', '.join(unreferenced)}")

    # Update imports
    imports = importmagic.Imports(index, source)

    if unreferenced:
        imports.remove(unreferenced)

    if unresolved:
        imports.add(unresolved)

    # Get the updated source code
    updated_source = imports.update_source(source)

    # Write the changes back to the file
    with open(filename, 'w') as f:
        f.write(updated_source)

    print(f"Successfully updated {filename}")
    return True


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Please provide a Python file to fix.")
        print("Usage: python fix_imports.py <python_file>")
        return

    filename = sys.argv[1]
    fix_imports(filename)


if __name__ == "__main__":
    main()
```

### Step 2: Make It Executable

Make your script executable (Linux/Mac):

```
chmod +x fix_imports.py
```

### Step 3: Test It

Create a test file with import issues:

1. Create `test_broken.py` with content:

   ```python
   import os  # This import is unused

   def test_function():
       df = pd.DataFrame()  # Missing pandas import
       result = np.array([1, 2, 3])  # Missing numpy import
       return result
   ```

2. Run your fixer script:

   ```
   python fix_imports.py test_broken.py
   ```

3. Check the updated file - it should have added the missing imports and removed the unused one.

## Phase 4: Advanced Integration

Now that the basics work, let's create a more robust solution for your entire project.

### Step 1: Create a Project-Wide Fixer

Create a new file called `fix_project_imports.py`:

```python
#!/usr/bin/env python
"""
Project-wide import fixer using ImportMagic
Usage: python fix_project_imports.py project_directory
"""

import importmagic
import sys
import os
import time


def fix_file_imports(filename, index):
    """Fix imports in a single Python file."""
    # Skip non-Python files
    if not filename.endswith('.py'):
        return False

    # Read the file content
    try:
        with open(filename, 'r') as f:
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
        print(f"{filename}: Removing {len(unreferenced)} imports: {', '.join(unreferenced)}")
        changes_made = True

    if not changes_made:
        return False

    # Update imports
    imports = importmagic.Imports(index, source)

    if unreferenced:
        imports.remove(unreferenced)

    if unresolved:
        imports.add(unresolved)

    # Get the updated source code
    updated_source = imports.update_source(source)

    # Write the changes back to the file
    with open(filename, 'w') as f:
        f.write(updated_source)

    return True


def process_directory(directory_path, index):
    """Process all Python files in the directory and subdirectories."""
    files_fixed = 0
    files_processed = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                files_processed += 1

                if files_processed % 10 == 0:
                    print(f"Processed {files_processed} files so far...")

                if fix_file_imports(filepath, index):
                    files_fixed += 1

    return files_processed, files_fixed


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Please provide a project directory to process.")
        print("Usage: python fix_project_imports.py <project_directory>")
        return

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    start_time = time.time()

    # Build an index of available modules
    print("Building module index (may take a moment)...")
    index = importmagic.SymbolIndex()
    index.build_index(paths=importmagic.paths_from_interpreter())

    print(f"Processing Python files in {directory}...")
    files_processed, files_fixed = process_directory(directory, index)

    end_time = time.time()
    duration = end_time - start_time

    print("\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files fixed: {files_fixed}")
    print(f"Time taken: {duration:.2f} seconds")


if __name__ == "__main__":
    main()
```

### Step 2: Make It Executable

```
chmod +x fix_project_imports.py
```

### Step 3: Test on Your Project

```
python fix_project_imports.py your_project_directory
```

## Phase 5: Integration with Your Development Workflow

Now let's integrate ImportMagic into your daily development workflow.

### Option 1: Pre-commit Hook Setup

1. Create a pre-commit hook file in your project:

   Navigate to your project's `.git/hooks/` directory and create a file named `pre-commit`:

   ```bash
   #!/bin/bash

   # Store the files that have been staged
   staged_python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

   if [ -n "$staged_python_files" ]; then
       echo "Fixing imports in staged Python files..."

       # For each staged Python file
       for file in $staged_python_files; do
           if [ -f "$file" ]; then
               python /path/to/your/fix_imports.py "$file"
               git add "$file"  # Add the fixed file back to staging
           fi
       done
   fi

   exit 0
   ```

2. Make it executable:

   ```
   chmod +x .git/hooks/pre-commit
   ```

### Option 2: Create a Makefile Command

If your project uses a Makefile, add this target:

```makefile
fix-imports:
	@echo "Fixing imports in project Python files..."
	@python /path/to/your/fix_project_imports.py .
```

Then you can run `make fix-imports` anytime.

### Option 3: Add to Your Development Scripts

If you're using Poetry, npm, or another package manager with scripts, add it to your scripts:

For Poetry (pyproject.toml):

```toml
[tool.poetry.scripts]
fix-imports = "scripts:fix_imports"
```

With a corresponding script in your project.

## Phase 6: Creating an Import Helper Module

For more advanced usage, create a reusable module in your project:

Create `import_helper.py` in your project's utilities folder:

```python
"""
Import helper module.
Provides functions to fix imports in Python files using ImportMagic.
"""

import importmagic
import os
import logging

logger = logging.getLogger(__name__)

# Create a global index for better performance
_global_index = None


def get_symbol_index():
    """Get or create a global symbol index."""
    global _global_index

    if _global_index is None:
        logger.info("Building ImportMagic symbol index...")
        _global_index = importmagic.SymbolIndex()
        _global_index.build_index(paths=importmagic.paths_from_interpreter())
        logger.info("Symbol index built.")

    return _global_index


def fix_imports_in_file(filename):
    """Fix imports in a single Python file."""
    # Get the global index
    index = get_symbol_index()

    # Read the file content
    with open(filename, 'r') as f:
        source = f.read()

    # Parse the source code
    scope = importmagic.Scope.from_source(source)

    # Find unresolved and unreferenced symbols
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()

    if not unresolved and not unreferenced:
        return False, "No import issues found."

    # Build statistics
    stats = {
        'added': len(unresolved) if unresolved else 0,
        'removed': len(unreferenced) if unreferenced else 0,
        'added_imports': list(unresolved) if unresolved else [],
        'removed_imports': list(unreferenced) if unreferenced else []
    }

    # Update imports
    imports = importmagic.Imports(index, source)

    if unreferenced:
        imports.remove(unreferenced)

    if unresolved:
        imports.add(unresolved)

    # Get the updated source code
    updated_source = imports.update_source(source)

    # Write the changes back to the file
    with open(filename, 'w') as f:
        f.write(updated_source)

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
        'added': len(unresolved) if unresolved else 0,
        'removed': len(unreferenced) if unreferenced else 0,
        'added_imports': list(unresolved) if unresolved else [],
        'removed_imports': list(unreferenced) if unreferenced else []
    }

    # Update imports
    imports = importmagic.Imports(index, source_code)

    if unreferenced:
        imports.remove(unreferenced)

    if unresolved:
        imports.add(unresolved)

    # Get the updated source code
    updated_source = imports.update_source(source_code)

    return updated_source, True, stats
```

You can then import and use this helper in your other Python files.

## Phase 7: Documentation and Best Practices

### Create Documentation for Your Team

Create a simple `import_management.md` file in your project documentation:

```markdown
# Import Management with ImportMagic

This project uses ImportMagic to automatically manage Python imports. Here's how to use it:

## Available Tools

1. **Fix imports in a single file:**
```

python tools/fix_imports.py path/to/your/file.py

```

2. **Fix imports in the entire project:**
```

python tools/fix_project_imports.py .

```

3. **Use the pre-commit hook:**
Import issues in staged Python files are automatically fixed when you commit.

## Best Practices

1. Run the project-wide fixer before major commits
2. Don't disable the pre-commit hook
3. Report any issues with the import fixing process

## Import Style Guide

We follow these import conventions:
- Standard library imports first
- Third-party library imports second
- Local module imports last
- Alphabetical ordering within each group
- Avoid wildcard imports (from module import *)
```

### Schedule Regular Import Audits

Set up a regular schedule (maybe monthly) to run the import fixer across your entire codebase to catch any accumulated issues.

## Phase 8: Troubleshooting Guide

Create a troubleshooting guide for common ImportMagic issues:

```markdown
# ImportMagic Troubleshooting

## Common Issues and Solutions

### 1. Missing imports not being detected

**Problem:** ImportMagic doesn't add imports for some modules you're using.

**Solution:**

- Make sure the module is installed in your environment
- Try rebuilding the symbol index
- Check if you're using a very uncommon or internal module

### 2. Script is too slow

**Problem:** The import fixer takes too long to run.

**Solution:**

- Build the index once and reuse it for multiple files
- Use the `--start-at-<module>` flag if available
- Run it only on changed files, not the entire project

### 3. Incorrect imports are being added

**Problem:** ImportMagic adds imports from the wrong module.

**Solution:**

- Be more specific in your code (e.g., use fully qualified names)
- Add explicit imports for ambiguous names
```

## Final Notes

This integration plan should give you a comprehensive approach to using ImportMagic in your Python projects. By following these steps, you'll have a robust system for managing imports that will save you time and prevent many common import-related errors.

Remember that ImportMagic is just one tool in your development toolkit. Combine it with good coding practices and regular code reviews for the best results.

```python
#!/usr/bin/env python3
"""
Advanced Import Management System (AIMS)

A sophisticated tool for analyzing, extracting, and managing Python imports
in a project-wide context, with integration to ImportMagic.
"""

import os
import sys
import time
import logging
import datetime
import re
import subprocess
import shutil
import json
import importmagic
import ast
from pathlib import Path
from collections import defaultdict, Counter
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
import concurrent.futures
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AIMS")


class ImportAnalysisException(Exception):
    """Custom exception for import analysis errors."""
    pass


class LogManager:
    """Manages the creation and organization of log files."""

    def __init__(self, root_dir: str):
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
        safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
        return os.path.join(self.current_session_dir, "linter_logs", f"{safe_name}.log")

    def get_import_analysis_path(self, filename: str) -> str:
        """Get the path for an import analysis file.

        Args:
            filename: The name of the file to be analyzed.

        Returns:
            The path where the import analysis should be stored.
        """
        base_name = os.path.basename(filename)
        safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
        return os.path.join(self.current_session_dir, "import_analysis", f"{safe_name}.json")

    def get_report_path(self, report_name: str) -> str:
        """Get the path for a report file.

        Args:
            report_name: The name of the report.

        Returns:
            The path where the report should be stored.
        """
        return os.path.join(self.current_session_dir, "reports", f"{report_name}.txt")

    def get_session_summary_path(self) -> str:
        """Get the path for the session summary file.

        Returns:
            The path where the session summary should be stored.
        """
        return os.path.join(self.current_session_dir, "session_summary.json")


class CodebaseAnalyzer:
    """Analyzes the codebase to find Python files for import analysis."""

    def __init__(self, root_dir: str, exclude_dirs: Optional[List[str]] = None):
        """Initialize the codebase analyzer.

        Args:
            root_dir: The root directory of the project.
            exclude_dirs: List of directories to exclude from analysis.
        """
        self.root_dir = root_dir
        self.exclude_dirs = exclude_dirs or ["venv", ".env", ".git", "__pycache__", "import_log"]
        self.python_files = []

    def scan_codebase(self) -> List[str]:
        """Scan the codebase for Python files.

        Returns:
            A list of Python file paths.
        """
        logger.info(f"Scanning codebase at {self.root_dir} for Python files...")

        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    self.python_files.append(full_path)

        logger.info(f"Found {len(self.python_files)} Python files for analysis.")
        return self.python_files


class LintingEngine:
    """Performs deep code analysis using multiple linters."""

    def __init__(self, log_manager: LogManager):
        """Initialize the linting engine.

        Args:
            log_manager: The log manager for storing linter outputs.
        """
        self.log_manager = log_manager
        self._ensure_linters_installed()

    def _ensure_linters_installed(self) -> None:
        """Check and install required linters if missing."""
        required_packages = ["pylint", "flake8", "pyflakes", "mypy"]

        for package in required_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", package, "--version"],
                    capture_output=True,
                    check=False
                )
            except FileNotFoundError:
                logger.warning(f"{package} not found. Installing...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True
                )

    def lint_file(self, file_path: str) -> str:
        """Lint a single Python file and store the results.

        Args:
            file_path: Path to the Python file.

        Returns:
            Path to the generated linter log file.
        """
        log_path = self.log_manager.get_linter_log_path(file_path)

        with open(log_path, 'w') as log_file:
            # Run multiple linters for comprehensive analysis
            linters = [
                ["pylint", "--output-format=json", file_path],
                ["flake8", "--max-line-length=120", file_path],
                ["pyflakes", file_path],
                ["mypy", "--show-error-context", file_path]
            ]

            for linter_cmd in linters:
                log_file.write(f"\n\n--- {linter_cmd[0]} OUTPUT ---\n\n")
                try:
                    result = subprocess.run(
                        [sys.executable, "-m"] + linter_cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    log_file.write(result.stdout)
                    log_file.write(result.stderr)
                except Exception as e:
                    log_file.write(f"Error running {linter_cmd[0]}: {str(e)}")

        return log_path


class ImportExtractor:
    """Extracts and analyzes import statements from Python files."""

    def __init__(self, log_manager: LogManager):
        """Initialize the import extractor.

        Args:
            log_manager: The log manager for storing analysis results.
        """
        self.log_manager = log_manager
        self.symbol_graph = nx.DiGraph()

    def extract_imports_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract import statements from a single Python file.

        Args:
            file_path: Path to the Python file.

        Returns:
            Dictionary with import analysis results.
        """
        analysis_result = {
            "file_path": file_path,
            "imports": [],
            "used_symbols": set(),
            "defined_symbols": set(),
            "potential_missing_imports": [],
            "unused_imports": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()

            # Parse the source code into an AST
            tree = ast.parse(source_code)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        alias = name.asname or name.name
                        analysis_result["imports"].append({
                            "type": "import",
                            "module": name.name,
                            "alias": alias,
                            "line": node.lineno
                        })

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        alias = name.asname or name.name
                        analysis_result["imports"].append({
                            "type": "from",
                            "module": module,
                            "name": name.name,
                            "alias": alias,
                            "line": node.lineno
                        })

                # Track symbol usage and definitions for deeper analysis
                self._analyze_symbol_usage(node, analysis_result)

            # Process the analysis to find potential issues
            self._process_analysis_results(analysis_result)

            # Save the analysis result
            analysis_path = self.log_manager.get_import_analysis_path(file_path)
            with open(analysis_path, 'w') as f:
                # Convert sets to lists for JSON serialization
                serializable_result = analysis_result.copy()
                serializable_result["used_symbols"] = list(analysis_result["used_symbols"])
                serializable_result["defined_symbols"] = list(analysis_result["defined_symbols"])
                json.dump(serializable_result, f, indent=2)

            return analysis_result

        except Exception as e:
            logger.error(f"Error analyzing imports in {file_path}: {str(e)}")
            raise ImportAnalysisException(f"Failed to analyze {file_path}: {str(e)}")

    def _analyze_symbol_usage(self, node: ast.AST, analysis_result: Dict[str, Any]) -> None:
        """Analyze how symbols are used and defined in the AST node.

        Args:
            node: The AST node to analyze.
            analysis_result: The analysis result dictionary to update.
        """
        # Track defined symbols
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
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

    def _process_analysis_results(self, analysis_result: Dict[str, Any]) -> None:
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
                analysis_result["unused_imports"].append(symbol)

        # Find potentially missing imports
        for symbol in analysis_result["used_symbols"]:
            if (symbol not in imported_symbols and
                symbol not in analysis_result["defined_symbols"] and
                not symbol.startswith("__")):
                analysis_result["potential_missing_imports"].append(symbol)

    def build_import_dependency_graph(self, analysis_results: List[Dict[str, Any]]) -> None:
        """Build a graph of symbol dependencies across the project.

        Args:
            analysis_results: List of import analysis results for all files.
        """
        # First pass: collect all defined symbols and their source files
        symbol_definitions = {}
        for result in analysis_results:
            file_path = result["file_path"]
            for symbol in result["defined_symbols"]:
                if symbol not in symbol_definitions:
                    symbol_definitions[symbol] = []
                symbol_definitions[symbol].append(file_path)

        # Second pass: build the dependency graph
        for result in analysis_results:
            file_node = result["file_path"]
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

    def suggest_imports(self, file_path: str, analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Suggest imports for a file based on the dependency graph.

        Args:
            file_path: Path to the Python file.
            analysis_results: List of import analysis results for all files.

        Returns:
            List of suggested import statements.
        """
        # Find the analysis result for this file
        file_result = next(
            (r for r in analysis_results if r["file_path"] == file_path), None
        )

        if not file_result:
            return []

        # Start with potential missing imports from the file's analysis
        missing_symbols = file_result["potential_missing_imports"]
        suggested_imports = []

        # Find where these symbols are defined in the project
        for symbol in missing_symbols:
            symbol_node = f"symbol:{symbol}"

            if symbol_node in self.symbol_graph:
                # Find files that define this symbol
                defining_files = [
                    source for source, target, data
                    in self.symbol_graph.edges(data=True)
                    if (target == symbol_node and
                        data.get("type") == "defines" and
                        isinstance(source, str) and
                        source.endswith(".py"))
                ]

                if defining_files:
                    # Get the most relevant defining file based on project structure
                    best_match = self._find_best_import_source(file_path, defining_files)

                    # Create import statement based on the best match
                    module_path = self._convert_path_to_module(best_match)
                    if module_path:
                        suggested_imports.append(f"from {module_path} import {symbol}")

        return suggested_imports

    def _find_best_import_source(self, target_file: str, source_files: List[str]) -> str:
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

    def __init__(self, log_manager: LogManager):
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
        self.importmagic_index.build_index(paths=importmagic.paths_from_interpreter())
        logger.info("ImportMagic symbol index built.")

    def process_file_with_importmagic(
        self, file_path: str, suggested_imports: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process a file with ImportMagic, incorporating suggested imports.

        Args:
            file_path: Path to the Python file.
            suggested_imports: List of suggested import statements.

        Returns:
            Tuple of (success, stats) where stats is a dictionary of changes made.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
                imports.remove(unreferenced)

            # Add required imports
            if all_unresolved:
                imports.add(all_unresolved)

            # Get the updated source code
            updated_source = imports.update_source(source)

            # Write the changes back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_source)

            # Compute statistics
            stats = {
                'removed_imports': list(unreferenced) if unreferenced else [],
                'added_imports': list(all_unresolved) if all_unresolved else [],
                'removed_count': len(unreferenced) if unreferenced else 0,
                'added_count': len(all_unresolved) if all_unresolved else 0,
                'suggested_imports': suggested_imports
            }

            return True, stats

        except Exception as e:
            logger.error(f"Error processing {file_path} with ImportMagic: {str(e)}")
            return False, {'error': str(e)}


class ReportGenerator:
    """Generates reports on import analysis and changes."""

    def __init__(self, log_manager: LogManager):
        """Initialize the report generator.

        Args:
            log_manager: The log manager for accessing logs and saving reports.
        """
        self.log_manager = log_manager

    def generate_file_report(self, file_path: str, stats: Dict[str, Any]) -> str:
        """Generate a report for a single file.

        Args:
            file_path: Path to the Python file.
            stats: Statistics about the changes made.

        Returns:
            Path to the generated report file.
        """
        report_name = os.path.basename(file_path).replace('.py', '')
        report_path = self.log_manager.get_report_path(f"file_{report_name}")

        with open(report_path, 'w') as f:
            f.write(f"Import Analysis Report for {file_path}\n")
            f.write("=" * 80 + "\n\n")

            f.write("Summary:\n")
            f.write(f"- Removed imports: {stats.get('removed_count', 0)}\n")
            f.write(f"- Added imports: {stats.get('added_count', 0)}\n\n")

            if stats.get('removed_imports'):
                f.write("Removed Imports:\n")
                for imp in stats['removed_imports']:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get('added_imports'):
                f.write("Added Imports:\n")
                for imp in stats['added_imports']:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get('suggested_imports'):
                f.write("Custom Suggested Imports:\n")
                for imp in stats['suggested_imports']:
                    f.write(f"- {imp}\n")
                f.write("\n")

            if stats.get('error'):
                f.write(f"Error: {stats['error']}\n\n")

        return report_path

    def generate_session_summary(self, all_stats: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Generate a summary report for the entire session.

        Args:
            all_stats: List of (file_path, stats) tuples for all processed files.

        Returns:
            Path to the generated summary file.
        """
        summary_path = self.log_manager.get_session_summary_path()

        # Calculate aggregate statistics
        total_files = len(all_stats)
        successful_files = sum(1 for _, stats in all_stats if not stats.get('error'))
        total_removed = sum(stats.get('removed_count', 0) for _, stats in all_stats)
        total_added = sum(stats.get('added_count', 0) for _, stats in all_stats)

        # Find files with most issues
        files_by_issues = sorted(
            all_stats,
            key=lambda x: (x[1].get('removed_count', 0) + x[1].get('added_count', 0)),
            reverse=True
        )

        with open(summary_path, 'w') as f:
            f.write("Advanced Import Management System (AIMS) Session Summary\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("Overall Statistics:\n")
            f.write(f"- Total files processed: {total_files}\n")
            f.write(f"- Successfully processed files: {successful_files}\n")
            f.write(f"- Failed files: {total_files - successful_files}\n")
            f.write(f"- Total imports removed: {total_removed}\n")
            f.write(f"- Total imports added: {total_added}\n\n")

            if files_by_issues:
                f.write("Files with Most Import Issues:\n")
                for file_path, stats in files_by_issues[:10]:  # Top 10 files
                    issues = stats.get('removed_count', 0) + stats.get('added_count', 0)
                    if issues > 0:
                        f.write(f"- {file_path}: {issues} issues ({stats.get('removed_count', 0)} "
                                f"removed, {stats.get('added_count', 0)} added)\n")
                f.write("\n")

            f.write("Files with Errors:\n")
            error_count = 0
            for file_path, stats in all_stats:
                if stats.get('error'):
                    f.write(f"- {file_path}: {stats['error']}\n")
                    error_count += 1

            if error_count == 0:
                f.write("- No errors encountered.\n")

        # Also save as JSON for programmatic access
        with open(summary_path + ".json", 'w') as f:
            summary_data = {
                'date': datetime.datetime.now().isoformat(),
                'total_files': total_files,
                'successful_files': successful_files,
                'failed_files': total_files - successful_files,
                'total_removed': total_removed,
                'total_added': total_added,
                'file_stats': {path: stats for path, stats in all_stats}
            }
            json.dump(summary_data, f, indent=2)

        return summary_path


def main():
    """Main function to run the AIMS script."""
    import argparse

    parser = argparse.ArgumentParser(
        description=("Advanced Import Management System (AIMS) - "
                    "Analyze and fix Python imports across your project.")
    )
    parser.add_argument(
        "project_dir",
        help="The root directory of the Python project to analyze"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="*",
        default=["venv", ".env", ".git", "__pycache__", "import_log"],
        help="Directories to exclude from analysis"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze imports but don't modify files"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run analysis in parallel for better performance"
    )

    args = parser.parse_args()

    # Validate project directory
    if not os.path.isdir(args.project_dir):
        logger.error(f"Project directory {args.project_dir} does not exist or is not a directory.")
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
            linter_futures = {
                executor.submit(linting_engine.lint_file, file_path): file_path
                for file_path in python_files
            }

            for future in tqdm(
                concurrent.futures.as_completed(linter_futures),
                total=len(python_files),
                desc="Linting files"
            ):
                file_path = linter_futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error linting {file_path}: {str(e)}")
    else:
        for file_path in tqdm(python_files, desc="Linting files"):
            try:
                linting_engine.lint_file(file_path)
            except Exception as e:
                logger.error(f"Error linting {file_path}: {str(e)}")

    # Step 3: Extract and analyze imports
    logger.info("Extracting and analyzing imports...")

    all_analysis_results = []

    if args.parallel:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            extraction_futures = {
                executor.submit(import_extractor.extract_imports_from_file, file_path): file_path
                for file_path in python_files
            }

            for future in tqdm(
                concurrent.futures.as_completed(extraction_futures),
                total=len(python_files),
                desc="Analyzing imports"
            ):
                file_path = extraction_futures[future]
                try:
                    result = future.result()
                    all_analysis_results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing imports in {file_path}: {str(e)}")
    else:
        for file_path in tqdm(python_files, desc="Analyzing imports"):
            try:
                result = import_extractor.extract_imports_from_file(file_path)
                all_analysis_results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing imports in {file_path}: {str(e)}")

    # Step 4: Build the import dependency graph
    logger.info("Building import dependency graph...")
    import_extractor.build_import_dependency_graph(all_analysis_results)

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
                stats = {
                    'suggested_imports': suggested_imports,
                    'dry_run': True
                }
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
            logger.error(f"Error processing {file_path}: {str(e)}")
            all_stats.append((file_path, {'error': str(e)}))

    # Step 6: Generate a session summary report
    logger.info("Generating session summary report...")
    summary_path = report_generator.generate_session_summary(all_stats)

    logger.info(f"Import analysis and processing complete. Summary available at: {summary_path}")

    # Indicate success
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Installation and Usage Guide

To use the Advanced Import Management System (AIMS), follow these steps:

### Prerequisites

Ensure you have Python 3.6+ installed with pip. The script will attempt to install required dependencies automatically, but you may want to set up a virtual environment first:

```bash
python -m venv aims-env
source aims-env/bin/activate  # On Windows: aims-env\Scripts\activate
```

### Initial Setup

1. Save the script as `aims.py` in your project directory or a dedicated tools directory.
2. Install the required packages:

   ```bash
   pip install importmagic networkx tqdm
   ```

3. Make the script executable (on Linux/Mac):

   ```bash
   chmod +x aims.py
   ```

### Basic Usage

Run the script on your project directory:

```bash
python aims.py /path/to/your/project
```

This will:

1. Create an organized log directory structure at `/path/to/your/project/import_log`
2. Scan for all Python files in the project
3. Run linters on each file
4. Extract and analyze import patterns
5. Build a dependency graph
6. Fix imports using ImportMagic enhanced with project-specific knowledge
7. Generate detailed reports

### Advanced Usage

For larger projects or special requirements, use these options:

```bash
# Exclude additional directories
python aims.py /path/to/your/project --exclude-dirs node_modules build dist

# Analyze without modifying files (dry run)
python aims.py /path/to/your/project --dry-run

# Use parallel processing for faster analysis
python aims.py /path/to/your/project --parallel
```

### Integration with Development Workflow

#### Add to Git Hooks

Create a pre-commit hook by adding this to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python /path/to/aims.py $(git rev-parse --show-toplevel) --dry-run

# Ask for confirmation before actually fixing imports
read -p "Fix imports in project? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python /path/to/aims.py $(git rev-parse --show-toplevel)
fi
```

#### Add to Makefile

Add this target to your Makefile:

```makefile
.PHONY: fix-imports

fix-imports:
	@echo "Running Advanced Import Management System..."
	@python tools/aims.py . --parallel
```

#### Add to CI/CD Pipeline

For GitLab CI/CD, add this to `.gitlab-ci.yml`:

```yaml
import-analysis:
  stage: lint
  script:
    - pip install importmagic networkx tqdm
    - python tools/aims.py . --dry-run
  artifacts:
    paths:
      - import_log/
```

## Benefits of This Approach

This implementation offers several key advantages:

1. **Deep Code Analysis**: Uses multiple linters and AST parsing to thoroughly understand the codebase.
2. **Graph-Based Analysis**: Builds a dependency graph to understand relationships between modules.
3. **Intelligent Import Suggestions**: Doesn't just fix syntax issues but identifies the correct sources for imports.
4. **Comprehensive Logging**: Creates organized, dated logs for auditing and troubleshooting.
5. **Non-Intrusive**: Works with existing codebases without requiring structural changes.
6. **Performance Optimization**: Parallel processing option for faster analysis of large projects.

By following this plan, junior developers can integrate a sophisticated import management system that enhances code quality and maintainability while providing detailed insights into the project's import structure.

```

```
