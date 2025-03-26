import symexec


class DynamicImportTracer:
    def __init__(self):
        """Initialize the DynamicImportTracer.

        This sets up a symbolic execution engine to trace dynamic imports
        within Python files. The traced dynamic imports are stored in a
        dictionary for further analysis.

        Attributes:
            symbolic_engine: An instance of symexec.Engine for executing
                            files symbolically.
            dynamic_imports: A dictionary to store information about
                            dynamic imports detected during execution.
        """
        self.symbolic_engine = symexec.Engine()
        self.dynamic_imports = {}

    def trace_dynamic_imports(self, file_path):
        # Set up tracing for __import__, importlib functions, etc.
        """Trace dynamic imports within a Python file using symbolic execution.

        This method sets up hooks for import-related functions and executes
        the specified file symbolically to detect dynamic import statements.
        Detected dynamic imports, along with their context, are stored in a
        dictionary for further analysis.

        Args:
            file_path (str): The path to the Python file to be analyzed.

        Returns:
            dict: A dictionary containing information about detected dynamic
                  imports, including their location, conditional paths, and
                  variable states.
        """
        self.symbolic_engine.hook_function("__import__", self._import_callback)
        self.symbolic_engine.hook_function(
            "importlib.import_module", self._import_callback
        )

        # Execute the file symbolically
        self.symbolic_engine.execute_file(file_path)

        return self.dynamic_imports

    def _import_callback(self, args, execution_context):
        """Callback function for handling import function calls during symbolic execution.

        This function is hooked into symbolic execution to capture dynamic import
        statements made via __import__ and importlib.import_module. It extracts the
        import name and records the location, conditional path, and variable state
        associated with each import.

        Args:
            args: A list of arguments passed to the import function, where the first
                argument is expected to be the import name.
            execution_context: The execution context providing information about
                            the current execution state, including location,
                            path constraints, and variable state.

        Side Effects:
            Updates the `dynamic_imports` dictionary with details about the dynamic
            import, including its location, conditional path constraints, and variables.
        """
        import_name = args[0].concrete_value

        # Get call site information
        callsite = execution_context.get_current_location()

        # Record the dynamic import
        self.dynamic_imports[import_name] = {
            "location": callsite,
            "conditional_path": execution_context.get_path_constraints(),
            "variable_state": execution_context.get_variable_state(),
        }
