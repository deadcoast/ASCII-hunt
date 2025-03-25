import dis
import importlib.abc
import importlib.util
import marshal
import py_compile
import types


class CompilerIntegratedImportAnalyzer:
    def __init__(self):
        """
        Initialize the CompilerIntegratedImportAnalyzer.

        This constructor sets up the initial state with empty dictionaries for
        caching bytecode and tracking import dependencies.

        Attributes:
            bytecode_cache (dict): A cache to store bytecode for analyzed files.
            import_dependencies (dict): A mapping of file paths to their import analysis results.
        """

        self.bytecode_cache = {}
        self.import_dependencies = {}

    def analyze_file(self, file_path):
        # Compile the file to bytecode
        """
        Analyze a file for its import dependencies.

        Args:
            file_path: The path to the file to analyze.

        Returns:
            A dictionary containing the import information for the file.
            The dictionary has the following keys:
                - imports: A list of import statements present in the file.
                - used_symbols: A set of symbols that are used in the file.
                - defined_symbols: A set of symbols that are defined in the file.
        """
        bytecode = self._compile_to_bytecode(file_path)
        if not bytecode:
            return None

        # Analyze bytecode for import patterns
        import_info = self._analyze_bytecode(bytecode, file_path)

        # Store in dependencies map
        self.import_dependencies[file_path] = import_info

        return import_info

    def _compile_to_bytecode(self, file_path):
        """
        Compile a Python file to bytecode and return the bytecode object.

        Args:
            file_path: The path to the Python file to compile.

        Returns:
            The bytecode object if compilation is successful, otherwise None.

        Raises:
            Compilation errors if the file cannot be compiled.
        """

        try:
            # Try to compile the file
            py_compile.compile(file_path, doraise=True)

            # Get the .pyc path
            if file_path.endswith(".py"):
                pyc_path = importlib.util.cache_from_source(file_path)
            else:
                pyc_path = file_path + "c"

            # Read the bytecode
            with open(pyc_path, "rb") as fc:
                fc.read(16)  # Skip header
                return marshal.load(fc)

        except Exception as e:
            print(f"Error compiling {file_path}: {e}")
            return None

    def _analyze_bytecode(self, code_obj, file_path):
        """
        Analyze bytecode for a given code object and file path.

        This method uses the `dis` module to analyze the bytecode instructions in
        the given code object. It identifies different types of imports and
        stores the information in a dictionary with the following keys:
            - static_imports: List of static import statements.
            - dynamic_imports: List of dynamic import statements.
            - lazy_imports: List of lazy import statements.
            - conditional_imports: List of conditional import statements.
            - import_chains: List of import chains.

        Args:
            code_obj: The code object to analyze.
            file_path: The path to the file containing the code object.

        Returns:
            A dictionary containing the import information for the code object.
        """
        import_info = {
            "static_imports": [],
            "dynamic_imports": [],
            "lazy_imports": [],
            "conditional_imports": [],
            "import_chains": [],
        }

        # Analyze the bytecode instructions
        self._analyze_code_object(code_obj, import_info, set())

        # Identify import chains
        self._find_import_chains(import_info)

        return import_info

    def _analyze_code_object(self, code_obj, import_info, visited):
        """
        Analyze a code object for import patterns and update import information.

        This method examines the bytecode instructions of the provided code
        object to identify different types of import statements, such as
        static, dynamic, lazy, and conditional imports. It updates the
        import_info dictionary with details of each identified import.

        Args:
            code_obj: The code object to analyze for imports.
            import_info: A dictionary to store identified import information,
                categorized into static, dynamic, lazy, and conditional imports.
            visited: A set used to track visited code objects and avoid
                redundant analysis of the same object.
        """

        if id(code_obj) in visited:
            return

        visited.add(id(code_obj))

        # Analyze the bytecode instructions
        instructions = list(dis.get_instructions(code_obj))

        i = 0
        while i < len(instructions):
            inst = instructions[i]

            # Look for IMPORT_NAME instruction
            if inst.opname == "IMPORT_NAME":
                module_name = inst.argval

                # Check if this is a conditional import
                is_conditional = self._is_conditional_import(instructions, i)

                # Check if this is a lazy import
                is_lazy = self._is_lazy_import(instructions, i)

                if is_conditional:
                    import_info["conditional_imports"].append(
                        {
                            "module": module_name,
                            "condition": self._extract_condition(instructions, i),
                        }
                    )
                elif is_lazy:
                    import_info["lazy_imports"].append(
                        {
                            "module": module_name,
                            "function": self._extract_function_context(instructions, i),
                        }
                    )
                else:
                    import_info["static_imports"].append(module_name)

            # Look for __import__ calls (dynamic imports)
            elif inst.opname == "LOAD_NAME" and inst.argval == "__import__":
                dynamic_import = self._extract_dynamic_import(instructions, i)
                if dynamic_import:
                    import_info["dynamic_imports"].append(dynamic_import)

            i += 1

        # Recursively analyze nested code objects
        for const in code_obj.co_consts:
            if isinstance(const, types.CodeType):
                self._analyze_code_object(const, import_info, visited)

    def _find_import_chains(self, import_info):
        """
        Identify import chains based on the collected import information.

        An import chain occurs when module A imports module B, which imports module C,
        and so on. This method analyzes the import dependencies to identify such chains.

        Args:
            import_info: A dictionary containing the collected import information.

        Returns:
            None. The method updates the import_chains list in the import_info dictionary.
        """
        # Get all imports
        all_imports = (
            import_info.get("static_imports", [])
            + [imp.get("module") for imp in import_info.get("dynamic_imports", [])]
            + [imp.get("module") for imp in import_info.get("lazy_imports", [])]
            + [imp.get("module") for imp in import_info.get("conditional_imports", [])]
        )

        # Here we would traverse the dependency graph to find chains
        # For now, just store all imports as potential chain starts
        chains = []
        for module in all_imports:
            if module:
                chains.append({"start": module, "chain": [module]})

        import_info["import_chains"] = chains

    def _is_conditional_import(self, instructions, index):
        """
        Determine if an import statement is conditional (e.g., inside an if statement).

        Args:
            instructions: The list of bytecode instructions.
            index: The index of the current instruction in the list.

        Returns:
            bool: True if the import is conditional, False otherwise.
        """
        # Look for jump instructions before the import
        for i in range(max(0, index - 10), index):
            inst = instructions[i]
            if inst.opname.startswith(("POP_JUMP_IF", "JUMP_IF")):
                return True
        return False

    def _is_lazy_import(self, instructions, index):
        """
        Determine if an import statement is lazy (e.g., inside a function definition).

        Args:
            instructions: The list of bytecode instructions.
            index: The index of the current instruction in the list.

        Returns:
            bool: True if the import is lazy, False otherwise.
        """
        # Check if this import is inside a function
        # This is a simplified approximation; a real implementation would be more complex
        function_depths = 0
        for i in range(0, index):
            inst = instructions[i]
            if inst.opname == "MAKE_FUNCTION":
                function_depths += 1
            elif inst.opname == "CALL_FUNCTION":
                function_depths = max(0, function_depths - 1)

        return function_depths > 0

    def _extract_condition(self, instructions, index):
        """
        Extract the condition for a conditional import.

        Args:
            instructions: The list of bytecode instructions.
            index: The index of the current instruction in the list.

        Returns:
            str: A string representation of the condition, or an empty string if not found.
        """
        # Look for variable names in jump conditions
        for i in range(max(0, index - 10), index):
            inst = instructions[i]
            if (
                inst.opname in ("LOAD_NAME", "LOAD_GLOBAL")
                and i + 1 < len(instructions)
                and instructions[i + 1].opname.startswith(("POP_JUMP_IF", "JUMP_IF"))
            ):
                return inst.argval
        return ""

    def _extract_function_context(self, instructions, index):
        """
        Extract the function context for a lazy import.

        Args:
            instructions: The list of bytecode instructions.
            index: The index of the current instruction in the list.

        Returns:
            str: The name of the function containing the import, or an empty string if not found.
        """
        # Find the most recent function definition
        function_name = ""
        for i in range(0, index):
            inst = instructions[i]
            if (
                inst.opname == "STORE_NAME"
                and i > 0
                and instructions[i - 1].opname == "MAKE_FUNCTION"
            ):
                function_name = inst.argval

        return function_name

    def _extract_dynamic_import(self, instructions, index):
        """
        Extract information about a dynamic import (using __import__).

        Args:
            instructions: The list of bytecode instructions.
            index: The index of the current instruction in the list.

        Returns:
            dict: A dictionary with information about the dynamic import, or None if not a valid dynamic import.
        """
        # Look for the module name in subsequent instructions
        if index + 2 < len(instructions):
            next_inst = instructions[index + 1]
            if next_inst.opname in ("LOAD_CONST"):
                module_name = next_inst.argval
                return {"module": module_name, "type": "dynamic"}

        return None
