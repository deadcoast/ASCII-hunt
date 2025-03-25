import ast
import json
import os
import re
import subprocess
from typing import Any


class CrossLanguageImportResolver:
    def __init__(self, project_root):
        """
        Initialize a CrossLanguageImportResolver.

        Args:
            project_root: The root directory of the project to analyze.

        Attributes:
            project_root: The root directory of the project to analyze.
            language_handlers: A dictionary mapping file extensions to analysis
                functions.
            symbol_map: A dictionary mapping file paths to dictionaries of
                defined symbols (keys) and their corresponding definition
                locations (values).
            cross_language_imports: A dictionary mapping import names to lists
                of tuples containing the file path and language of the import
                definition.
        """
        self.project_root = project_root
        self.language_handlers = {
            "py": self._analyze_python,
            "js": self._analyze_javascript,
            "rs": self._analyze_rust,
            "ts": self._analyze_typescript,
        }
        self.symbol_map = {}
        self.cross_language_imports = {}

    def analyze_project(self):
        # First pass: build a symbol map for each language
        """
        Analyze the project to identify cross-language imports and references.

        This method runs in two passes:

        1. The first pass iterates over all files in the project and analyzes
           them to build a symbol map for each language. This step is
           language-specific and is handled by the language handlers.
        2. The second pass iterates over the symbol maps and identifies
           cross-language imports and references. This step is handled by the
           `_resolve_cross_language_references` method.

        Note that this method assumes that all files in the project are
        analyzed. If some files are not analyzed (e.g. because they are
        excluded from the analysis), this method will not identify
        cross-language imports and references for those files.
        """
        for root, _, files in os.walk(self.project_root):
            for file in files:
                ext = file.split(".")[-1].lower()
                if ext in self.language_handlers:
                    file_path = os.path.join(root, file)
                    self.language_handlers[ext](file_path)

        # Second pass: identify cross-language imports and references
        self._resolve_cross_language_references()

    def _analyze_python(self, file_path):
        """
        Analyze a Python file and extract symbols and imports.

        Args:
            file_path: The path to the Python file to analyze.

        This method extracts defined symbols from the file and adds them to the
        symbol map. It also extracts imports and potential cross-language
        references and adds them to the cross_language_imports dictionary.
        """
        with open(file_path) as f:
            code = f.read()

        try:
            tree = ast.parse(code)

            # Extract defined symbols
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    symbol = node.name
                    self._add_symbol("python", file_path, symbol, node.lineno)

            # Extract imports and potential cross-language refs
            self._extract_python_imports(tree, file_path)

        except SyntaxError:
            pass

    def _analyze_javascript(self, file_path):
        """
        Analyze a JavaScript file to extract symbols and imports.

        Args:
            file_path: The path to the JavaScript file to analyze.

        This method uses a JavaScript parser, executed via a subprocess, to extract
        symbols and their line numbers from the JavaScript file. It then adds these
        symbols to the symbol map. Additionally, it extracts JavaScript import
        statements and processes them accordingly.
        """

        try:
            result = subprocess.run(
                ["node", "extract_js_symbols.js", file_path],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the JSON output
            symbols = json.loads(result.stdout)

            for symbol in symbols:
                self._add_symbol(
                    "javascript", file_path, symbol["name"], symbol["line"]
                )

            # Extract JS imports
            self._extract_js_imports(file_path)

        except Exception as e:
            print(f"Error analyzing JS file {file_path}: {e}")

    def _resolve_cross_language_references(self):
        """
        Look for cross-language bridges, e.g.:
        - Python calling JavaScript via a bridge
        - JavaScript importing Python modules via PyJs
        - Rust FFI interfaces to Python
        """

        bridges = self._identify_language_bridges()
        """
        This method looks for cross-language bridges, finds all references to these bridges,
        and tries to resolve what's being accessed across languages. It then adds the
        resolved information to the cross_language_imports dictionary.

        The cross_language_imports dictionary is keyed by source file paths and has
        the following structure:
        """
        for bridge in bridges:
            source_lang = bridge["source_language"]
            target_lang = bridge["target_language"]

            # Find all references to this bridge
            bridge_refs = self._find_bridge_references(bridge)

            for ref in bridge_refs:
                # Try to resolve what's being accessed across languages
                resolved = self._resolve_cross_language_symbol(
                    bridge, ref["source_file"], ref["target_symbol"]
                )

                if resolved:
                    self.cross_language_imports[ref["source_file"]] = {
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "target_file": resolved["file"],
                        "target_symbol": resolved["symbol"],
                        "bridge": bridge["name"],
                        "bridge_type": bridge["type"],
                        "bridge_file": str,
                        "bridge_line": int,
                        "bridge_column": int,
                        "bridge_args": list,
                        "bridge_kwargs": dict,
                        "bridge_kwargs_names": list,
                        "bridge_kwargs_values": list,
                        "bridge_kwargs_types": list,
                        "bridge_kwargs_defaults": list,
                        "bridge_kwargs_doc": str,
                    }

                if resolved:
                    self.cross_language_imports[ref["source_file"]] = {
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "target_file": resolved["file"],
                        "target_symbol": resolved["symbol"],
                        "bridge": bridge["name"],
                        "bridge_type": bridge["type"],
                        "bridge_file": bridge["file"],
                        "bridge_line": bridge["line"],
                        "bridge_column": bridge["column"],
                        "bridge_args": bridge["args"],
                        "bridge_kwargs": bridge["kwargs"],
                        "bridge_kwargs_names": bridge["kwargs_names"],
                        "bridge_kwargs_values": bridge["kwargs_values"],
                        "bridge_kwargs_types": bridge["kwargs_types"],
                        "bridge_kwargs_defaults": bridge["kwargs_defaults"],
                        "bridge_kwargs_doc": bridge["kwargs_doc"],
                        "bridge_kwargs_default_values": bridge["kwargs_default_values"],
                    }

        """
        Where "source_language" is the language of the source file, "target_language"
        is the language of the target file, "target_file" is the path to the target file,
        "target_symbol" is the symbol being accessed, and "bridge" is the name of the
        bridge being used.

        Note that this method assumes that the language handlers have already been
        executed and the symbol map is populated.
        """
        bridges = self._identify_language_bridges()

        for bridge in bridges:
            source_lang = bridge["source_language"]
            target_lang = bridge["target_language"]

            # Find all references to this bridge
            bridge_refs = self._find_bridge_references(bridge)

            for ref in bridge_refs:
                # Try to resolve what's being accessed across languages
                resolved = self._resolve_cross_language_symbol(
                    bridge, ref["source_file"], ref["target_symbol"]
                )

                if resolved:
                    self.cross_language_imports[ref["source_file"]] = {
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "target_file": resolved["file"],
                        "target_symbol": resolved["symbol"],
                        "bridge": bridge["name"],
                    }

    def _add_symbol(
        self, language: str, file_path: str, symbol: str, line_no: int
    ) -> None:
        """
        Add a symbol to the symbol map.

        Args:
            language: The language of the symbol (e.g., 'python', 'javascript').
            file_path: The path to the file containing the symbol.
            symbol: The name of the symbol.
            line_no: The line number where the symbol is defined.
        """
        if file_path not in self.symbol_map:
            self.symbol_map[file_path] = {"language": language, "symbols": {}}

        self.symbol_map[file_path]["symbols"][symbol] = line_no

    def _extract_python_imports(self, tree: ast.AST, file_path: str) -> None:
        """
        Extract import statements from a Python AST.

        Args:
            tree: The Python AST to analyze.
            file_path: The path to the file being analyzed.

        This method extracts both standard Python imports and potential
        cross-language imports using libraries like PyJS, ctypes, etc.
        """
        imports = []

        # Extract regular Python imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": name.name,
                            "alias": name.asname,
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append(
                        {
                            "type": "from",
                            "module": module,
                            "name": name.name,
                            "alias": name.asname,
                            "line": node.lineno,
                        }
                    )

        # Look for cross-language imports
        # 1. Check for JS bindings
        js_imports = self._extract_py_js_bindings(tree, file_path)
        if js_imports:
            imports.extend(js_imports)

        # 2. Check for Rust FFI calls
        rust_imports = self._extract_py_rust_bindings(tree, file_path)
        if rust_imports:
            imports.extend(rust_imports)

        # Store all found imports in the cross_language_imports dict with the file path as the key
        if imports:
            if file_path not in self.cross_language_imports:
                self.cross_language_imports[file_path] = []
            self.cross_language_imports[file_path].extend(imports)

    def _extract_py_js_bindings(
        self, tree: ast.AST, file_path: str
    ) -> list[dict[str, Any]]:
        """
        Extract JavaScript bindings from Python code.

        Looks for patterns like:
        - pyjs.require('module')
        - js.console.log(...)
        - Use of PyJSModule instances

        Args:
            tree: The Python AST to analyze.
            file_path: The path to the file being analyzed.

        Returns:
            A list of dictionaries containing information about the bindings.
        """
        bindings = []

        for node in ast.walk(tree):
            # Look for pyjs.require or similar patterns
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if hasattr(node.func, "attr") and node.func.attr == "require":
                    # Check if node.func.value is an ast.Name and has id attribute
                    if (
                        isinstance(node.func.value, ast.Name)
                        and hasattr(node.func.value, "id")
                        and node.func.value.id in ("pyjs", "js")
                    ):
                        # Check if we have string arguments
                        if (
                            node.args
                            and isinstance(node.args[0], ast.Str)
                            and hasattr(node.args[0], "s")
                        ):
                            bindings.append(
                                {
                                    "type": "js_import",
                                    "source": "pyjs",
                                    "module": node.args[0].s,
                                    "line": node.lineno,
                                    "language": "javascript",
                                }
                            )

        return bindings

    def _extract_py_rust_bindings(
        self, tree: ast.AST, file_path: str
    ) -> list[dict[str, Any]]:
        """
        Extract Rust bindings from Python code.

        Looks for patterns like:
        - ctypes.CDLL('libmyrust.so')
        - cffi usage with Rust libraries

        Args:
            tree: The Python AST to analyze.
            file_path: The path to the file being analyzed.

        Returns:
            A list of dictionaries containing information about the bindings.
        """
        bindings = []

        for node in ast.walk(tree):
            # Look for ctypes.CDLL or similar patterns
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if hasattr(node.func, "attr") and node.func.attr == "CDLL":
                    # Check if node.func.value is an ast.Name and has id attribute
                    if (
                        isinstance(node.func.value, ast.Name)
                        and hasattr(node.func.value, "id")
                        and node.func.value.id == "ctypes"
                    ):
                        # Check if we have string arguments
                        if (
                            node.args
                            and isinstance(node.args[0], ast.Str)
                            and hasattr(node.args[0], "s")
                        ):
                            # Extract the Rust library name from the .so file
                            lib_path = node.args[0].s
                            lib_name = os.path.basename(lib_path)
                            # Check if it's likely a Rust library
                            if "rust" in lib_name.lower() or lib_name.startswith("lib"):
                                bindings.append(
                                    {
                                        "type": "rust_import",
                                        "source": "ctypes",
                                        "module": lib_path,
                                        "line": node.lineno,
                                        "language": "rust",
                                    }
                                )

        return bindings

    def _extract_js_imports(self, file_path: str) -> None:
        """
        Extract import statements from a JavaScript file.

        Args:
            file_path: The path to the JavaScript file to analyze.

        This method extracts ES6 imports, CommonJS requires, and potential
        cross-language imports using libraries like PyJS, node-ffi, etc.
        """
        imports = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Extract ES6 imports
            es6_import_pattern = (
                r'import\s+(?:{[^}]*}|[^{}\n;]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
            )
            es6_imports = re.findall(es6_import_pattern, content)
            for module in es6_imports:
                imports.append(
                    {"type": "es6_import", "module": module, "language": "javascript"}
                )

            # Extract CommonJS requires
            cjs_require_pattern = r'(?:const|let|var)\s+(?:{[^}]*}|[^{}\n;]+)\s+=\s+require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            cjs_imports = re.findall(cjs_require_pattern, content)
            for module in cjs_imports:
                imports.append(
                    {
                        "type": "commonjs_import",
                        "module": module,
                        "language": "javascript",
                    }
                )

            # Look for Python imports
            py_import_pattern = r'new PyModule\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            py_imports = re.findall(py_import_pattern, content)
            for module in py_imports:
                imports.append(
                    {"type": "python_import", "module": module, "language": "python"}
                )

            # Look for Rust imports (e.g., via node-ffi)
            rust_import_pattern = r'ffi\.Library\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,'
            rust_imports = re.findall(rust_import_pattern, content)
            for module in rust_imports:
                imports.append(
                    {"type": "rust_import", "module": module, "language": "rust"}
                )

            # Store all found imports in the cross_language_imports dict
            if imports:
                if file_path not in self.cross_language_imports:
                    self.cross_language_imports[file_path] = []
                self.cross_language_imports[file_path].extend(imports)

        except Exception as e:
            print(f"Error extracting JS imports from {file_path}: {e}")

    def _analyze_rust(self, file_path: str) -> None:
        """
        Analyze a Rust file and extract symbols and imports.

        Args:
            file_path: The path to the Rust file to analyze.

        This method extracts defined symbols from the file and adds them to the
        symbol map. It also extracts imports and potential cross-language
        references and adds them to the cross_language_imports dictionary.
        """
        imports = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Extract public Rust functions and structs
            # These patterns are simplistic and might miss complex cases
            pub_fn_pattern = r"pub\s+fn\s+([a-zA-Z0-9_]+)"
            pub_functions = re.findall(pub_fn_pattern, content)

            pub_struct_pattern = r"pub\s+struct\s+([a-zA-Z0-9_]+)"
            pub_structs = re.findall(pub_struct_pattern, content)

            # Add found symbols to the symbol map
            line_no = 1
            for line in content.splitlines():
                # Simple line-by-line check - not the most accurate but works for basic cases
                for fn in pub_functions:
                    if f"pub fn {fn}" in line:
                        self._add_symbol("rust", file_path, fn, line_no)

                for struct in pub_structs:
                    if f"pub struct {struct}" in line:
                        self._add_symbol("rust", file_path, struct, line_no)

                line_no += 1

            # Look for FFI exports to Python
            py_ffi_pattern = (
                r"#\[pymodule\]|PyModule_AddFunctions|#\[pyclass\]|#\[pymethods\]"
            )
            if re.search(py_ffi_pattern, content):
                # This file likely contains Python FFI
                imports.append(
                    {
                        "type": "python_ffi",
                        "language": "python",
                        "ffi_type": "pyo3" if "#[pymodule]" in content else "cpython",
                    }
                )

            # Look for FFI exports to JavaScript
            js_ffi_pattern = r'extern "C" #\[no_mangle\]|#\[wasm_bindgen\]'
            if re.search(js_ffi_pattern, content):
                # This file likely contains JS FFI
                imports.append(
                    {
                        "type": "js_ffi",
                        "language": "javascript",
                        "ffi_type": "wasm_bindgen"
                        if "#[wasm_bindgen]" in content
                        else "c_ffi",
                    }
                )

            # Store imports in the cross_language_imports dict
            if imports:
                if file_path not in self.cross_language_imports:
                    self.cross_language_imports[file_path] = []
                self.cross_language_imports[file_path].extend(imports)

        except Exception as e:
            print(f"Error analyzing Rust file {file_path}: {e}")

    def _analyze_typescript(self, file_path: str) -> None:
        """
        Analyze a TypeScript file to extract symbols and imports.

        Args:
            file_path: The path to the TypeScript file to analyze.

        This method extracts symbols and imports from TypeScript code,
        including potential cross-language references via node-ffi, py-ts, etc.
        """
        imports = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Extract exported classes, functions, and variables
            # These patterns are simplistic and might miss complex cases
            export_class_pattern = r"export\s+class\s+([a-zA-Z0-9_]+)"
            export_classes = re.findall(export_class_pattern, content)

            export_fn_pattern = r"export\s+(?:function|const|let|var)\s+([a-zA-Z0-9_]+)"
            export_fns = re.findall(export_fn_pattern, content)

            # Add found symbols to the symbol map
            line_no = 1
            for line in content.splitlines():
                for cls in export_classes:
                    if f"export class {cls}" in line:
                        self._add_symbol("typescript", file_path, cls, line_no)

                for fn in export_fns:
                    if f"export function {fn}" in line or f"export const {fn}" in line:
                        self._add_symbol("typescript", file_path, fn, line_no)

                line_no += 1

            # Extract imports using the same patterns as JavaScript
            # Extract ES6 imports
            es6_import_pattern = (
                r'import\s+(?:{[^}]*}|[^{}\n;]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
            )
            es6_imports = re.findall(es6_import_pattern, content)
            for module in es6_imports:
                imports.append(
                    {"type": "es6_import", "module": module, "language": "typescript"}
                )

            # Look for Python imports
            py_import_pattern = r'import\s+\*\s+as\s+([a-zA-Z0-9_]+)\s+from\s+[\'"]python/([^\'"]+)[\'"]'
            py_imports = re.findall(py_import_pattern, content)
            for alias, module in py_imports:
                imports.append(
                    {
                        "type": "python_import",
                        "module": module,
                        "alias": alias,
                        "language": "python",
                    }
                )

            # Look for Rust imports
            rust_import_pattern = (
                r'import\s+\*\s+as\s+([a-zA-Z0-9_]+)\s+from\s+[\'"]rust/([^\'"]+)[\'"]'
            )
            rust_imports = re.findall(rust_import_pattern, content)
            for alias, module in rust_imports:
                imports.append(
                    {
                        "type": "rust_import",
                        "module": module,
                        "alias": alias,
                        "language": "rust",
                    }
                )

            # Store imports in the cross_language_imports dict
            if imports:
                if file_path not in self.cross_language_imports:
                    self.cross_language_imports[file_path] = []
                self.cross_language_imports[file_path].extend(imports)

        except Exception as e:
            print(f"Error analyzing TypeScript file {file_path}: {e}")

    def _identify_language_bridges(self) -> list[dict[str, Any]]:
        """
        Identify language bridges in the analyzed files.

        This method looks for patterns that indicate a bridge between
        different programming languages, such as:
        - Python-JavaScript bridges (PyJS, Node.js child_process, etc.)
        - Python-Rust bridges (PyO3, ctypes, etc.)
        - JavaScript-Rust bridges (neon, wasm-bindgen, etc.)

        Returns:
            A list of dictionaries containing information about the bridges.
        """
        bridges = []

        # Look for bridge files and patterns in the codebase
        for file_path, file_info in self.cross_language_imports.items():
            for import_info in file_info:
                # Skip if this isn't a cross-language import
                if "language" not in import_info or import_info.get(
                    "type", ""
                ).endswith("_import"):
                    continue

                # Determine source language based on file extension
                ext = file_path.split(".")[-1].lower()
                source_language = {
                    "py": "python",
                    "js": "javascript",
                    "ts": "typescript",
                    "rs": "rust",
                }.get(ext, "unknown")

                # Target language from the import info
                target_language = import_info.get("language", "unknown")

                # Skip if not a cross-language scenario
                if source_language == target_language or target_language == "unknown":
                    continue

                # Create a bridge entry
                bridge = {
                    "name": f"{source_language}-{target_language}",
                    "source_language": source_language,
                    "target_language": target_language,
                    "file": file_path,
                    "type": import_info.get("type", "unknown"),
                    "line": import_info.get("line", 0),
                    "column": 0,  # Column info often not available
                    "module": import_info.get("module", ""),
                    "args": [],
                    "kwargs": {},
                    "kwargs_names": [],
                    "kwargs_values": [],
                    "kwargs_types": [],
                    "kwargs_defaults": [],
                    "kwargs_doc": "",
                    "kwargs_default_values": {},
                }

                bridges.append(bridge)

        return bridges

    def _find_bridge_references(self, bridge: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Find all references to a given language bridge.

        Args:
            bridge: A dictionary containing information about the bridge.

        Returns:
            A list of dictionaries containing information about references
            to the bridge.
        """
        references = []

        # Search for references based on bridge type
        source_lang = bridge["source_language"]
        target_lang = bridge["target_language"]
        bridge_module = bridge.get("module", "")

        for file_path, file_data in self.symbol_map.items():
            # Skip if this file is not in the source language
            if file_data.get("language", "") != source_lang:
                continue

            # Look for imported modules in this file that match the bridge module
            if file_path in self.cross_language_imports:
                for import_info in self.cross_language_imports[file_path]:
                    if import_info.get("module") == bridge_module:
                        # This file refers to the bridge module
                        reference = {
                            "source_file": file_path,
                            "target_language": target_lang,
                            "target_symbol": import_info.get("name", ""),
                            "line": import_info.get("line", 0),
                        }
                        references.append(reference)

        return references

    def _resolve_cross_language_symbol(
        self, bridge: dict[str, Any], source_file: str, target_symbol: str
    ) -> dict[str, Any] | None:
        """
        Resolve a cross-language symbol reference.

        Args:
            bridge: A dictionary containing information about the bridge.
            source_file: The path to the file containing the reference.
            target_symbol: The name of the symbol being referenced.

        Returns:
            A dictionary containing information about the resolved symbol,
            or None if the symbol could not be resolved.
        """
        target_lang = bridge["target_language"]

        # Search for the symbol in files of the target language
        for file_path, file_data in self.symbol_map.items():
            # Skip if this file is not in the target language
            if file_data.get("language", "") != target_lang:
                continue

            # Check if the target symbol is defined in this file
            if target_symbol in file_data.get("symbols", {}):
                return {
                    "file": file_path,
                    "symbol": target_symbol,
                    "line": file_data["symbols"][target_symbol],
                }

        # Special handling for dynamic or namespace-style imports
        if "." in target_symbol:
            # Handle case where the symbol is a property of an imported module
            base_symbol, prop = target_symbol.split(".", 1)

            # Try to find the base symbol
            for file_path, file_data in self.symbol_map.items():
                if file_data.get("language", "") != target_lang:
                    continue

                if base_symbol in file_data.get("symbols", {}):
                    return {
                        "file": file_path,
                        "symbol": target_symbol,
                        "line": file_data["symbols"][
                            base_symbol
                        ],  # Use base symbol line number
                    }

        # Could not resolve the symbol
        return None
