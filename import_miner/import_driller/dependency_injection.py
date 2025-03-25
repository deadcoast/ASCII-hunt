import ast
import importlib.abc
import importlib.util
import sys
from ast import NodeTransformer


class DependencyInjectionImportHook(importlib.abc.Loader, importlib.abc.MetaPathFinder):
    def __init__(self):
        """
        Initialize this import hook, creating empty maps for dependency injection and cached modules.

        The maps are:
            dependency_map: Maps module names to dictionaries of dependency substitutions.
            module_cache: Maps module names to their cached module instances.
            module_source_map: Maps module names to their source code.
        """
        self.dependency_map = {}
        self.module_cache = {}
        self.module_source_map = {}
        self._injected_deps = {}  # Store for injected dependencies

    def register(self):
        """Register this import hook to the front of sys.meta_path."""

        sys.meta_path.insert(0, self)

    def configure_dependency(self, module_name, dependency_name, substitute):
        """
        Configure a dependency substitution for a specific module.

        Args:
            module_name (str): The name of the module for which the dependency is being configured.
            dependency_name (str): The name of the dependency to be substituted.
            substitute (Any): The substitute object or value for the dependency.

        This function updates the dependency map to reflect the substitution of
        a given dependency for a specific module, allowing for custom dependency injection.
        """

        if module_name not in self.dependency_map:
            self.dependency_map[module_name] = {}

        self.dependency_map[module_name][dependency_name] = substitute

    def find_spec(self, fullname, path, target=None):
        # Check if we need to apply dependency injection
        """
        Find the module spec for a given module name.

        This function checks if we need to apply dependency injection for the given module name.
        If so, it returns a new spec that uses our custom loader to inject dependencies.
        If not, it returns the original spec if available, or None otherwise.
        """

        if fullname in self.dependency_map:
            # Create a spec for this module
            if fullname in self.module_cache:
                # Already loaded, return cached module
                return self.module_cache[fullname].__spec__

            # Check if we can get the original spec
            original_spec = self._find_original_spec(fullname, path, target)
            if original_spec:
                # Create a new spec that uses our loader
                original_spec.loader = self
                return original_spec

        return None

    def _find_original_spec(self, fullname, path, target):
        """
        Find the original module spec for a given module name.

        This function iterates through sys.meta_path to find the original spec for the given module name.
        If it finds one, it returns the original spec. If it doesn't find one, it returns None.
        """
        for finder in sys.meta_path:
            if finder is self:
                continue

            spec = finder.find_spec(fullname, path, target)
            if spec:
                return spec

        return None

    def create_module(self, spec):
        # Let the default machinery create the module
        """
        Create a module for the given specification.

        This function allows the default module creation machinery to handle
        the process. It does not perform any custom module creation logic.

        Args:
            spec (importlib.machinery.ModuleSpec): The specification for the module to be created.

        Returns:
            None: Always returns None as the default machinery handles module creation.
        """

        return None

    def exec_module(self, module):
        # Get the original source code
        """
        Execute a module with potential import transformations.

        This method retrieves the original source code of a module, transforms
        its import statements, and then executes the transformed source code.
        The module is then cached for future use.

        Args:
            module (ModuleType): The module to execute.

        If the original source code cannot be retrieved, it falls back to
        executing the module using the regular loading mechanism.
        """

        original_source = self._get_module_source(module.__name__)
        if not original_source:
            # Fallback to regular loading
            self._exec_original_module(module)
            return

        # Parse and transform the source code
        transformed_source = self._transform_imports(original_source, module.__name__)

        # Execute the transformed source
        # Make sure module.__file__ is not None before using as filename argument
        module_file = (
            module.__file__
            if hasattr(module, "__file__") and module.__file__ is not None
            else "<unknown>"
        )
        compiled = compile(transformed_source, module_file, "exec")
        exec(compiled, module.__dict__)

        # Cache the module
        self.module_cache[module.__name__] = module

    def _exec_original_module(self, module):
        """
        Execute a module using the original loading mechanism.

        This is a fallback method when source code transformation is not possible.

        Args:
            module (ModuleType): The module to execute.
        """
        try:
            # Find the original spec
            original_spec = self._find_original_spec(module.__name__, None, None)
            if original_spec and original_spec.loader:
                # Use the original loader to execute the module
                original_spec.loader.exec_module(module)
            else:
                # If we can't find an original loader, raise an error
                raise ImportError(
                    f"Could not find original loader for {module.__name__}"
                )
        except Exception as e:
            # Handle any exceptions that might occur during execution
            raise ImportError(f"Error executing module {module.__name__}: {e!s}")

    def _get_module_source(self, module_name):
        """
        Retrieve the source code of a module.

        This method attempts to retrieve the original source code for a given module name.
        It first checks the cache to see if the source code has already been retrieved.
        If not, it attempts to get the source file path from the module spec.
        If it can get the file path, it reads the source code from the file and caches it.
        If it cannot retrieve the source code, it returns None.

        Args:
            module_name (str): The name of the module for which to retrieve the source code.

        Returns:
            str: The source code of the module, or None if it cannot be retrieved.
        """
        if module_name in self.module_source_map:
            return self.module_source_map[module_name]

        try:
            # Try to get the source file path
            spec = self._find_original_spec(module_name, None, None)
            if spec and spec.origin:
                with open(spec.origin) as f:
                    source = f.read()

                self.module_source_map[module_name] = source
                return source
        except Exception:
            pass

        return None

    def _transform_imports(self, source, module_name):
        """
        Transform the source code of a module by injecting dependencies.

        This method takes source code and transforms it by removing unnecessary imports
        and injecting dependencies. It does this by parsing the source code into an AST,
        transforming the AST, and generating source code from the transformed AST.

        It also adds a hook to expose the injected dependencies through the hook object.

        Args:
            source (str): The source code of the module to transform.
            module_name (str): The name of the module to transform.

        Returns:
            str: The transformed source code.
        """

        class ImportTransformer(NodeTransformer):
            def __init__(self, hook, module_name):
                """
                Initialize the ImportTransformer.

                Args:
                    hook: The hook object.
                    module_name: The name of the module to transform.
                """
                self.hook = hook
                self.module_name = module_name
                self.dependencies = hook.dependency_map.get(module_name, {})

            def visit_Import(self, node):
                """
                Remove import statements that are being replaced by injected dependencies.
                If all imports in the statement are being replaced, remove the entire statement.
                Otherwise, return the statement with the replaced imports removed.
                """
                new_names = []
                for name in node.names:
                    if name.name in self.dependencies:
                        # Skip this import, we'll inject it
                        pass
                    else:
                        new_names.append(name)

                if not new_names:
                    return None  # Remove the import statement

                node.names = new_names
                return node

            def visit_ImportFrom(self, node):
                """
                Remove import from statements that are being replaced by injected dependencies.
                If all imports in the statement are being replaced, remove the entire statement.
                Otherwise, return the statement with the replaced imports removed.
                """
                if node.module in self.dependencies:
                    # This entire import is being substituted
                    return None

                new_names = []
                for name in node.names:
                    import_name = (
                        f"{node.module}.{name.name}" if node.module else name.name
                    )
                    if import_name in self.dependencies:
                        # Skip this specific import
                        pass
                    else:
                        new_names.append(name)

                if not new_names:
                    return None  # Remove the import statement

                node.names = new_names
                return node

            def visit_Name(self, node):
                """
                Replace variable references with injected dependencies.

                This method traverses the AST and replaces variable references that
                match injected dependencies with the injected values.

                Args:
                    node (ast.Name): The AST node representing a name.

                Returns:
                    The original node if no substitution is needed, or a new node
                    with the substituted value.
                """
                # Initialize injection_code at method level to ensure it's always defined
                injection_code = ""

                if isinstance(node.ctx, ast.Load) and node.id in self.dependencies:
                    # Replace this name with the injected dependency
                    new_node = None

                    # Generate AST node for the injected dependency
                    dep_value = self.dependencies[node.id]
                    if isinstance(dep_value, (int, float, bool, str, type(None))):
                        # For simple types, create a Constant node
                        if hasattr(ast, "Constant"):  # Python 3.8+
                            new_node = ast.Constant(value=dep_value, kind=None)
                        else:  # Python 3.7 and below
                            if isinstance(dep_value, str):
                                new_node = ast.Str(s=dep_value)
                            elif isinstance(dep_value, (int, float)):
                                new_node = ast.Num(n=dep_value)
                            elif isinstance(dep_value, bool):
                                new_node = ast.NameConstant(value=dep_value)
                            elif dep_value is None:
                                new_node = ast.NameConstant(value=None)
                    else:
                        # For complex objects, create a call to a hook method
                        hook_name = f"__injected_dep_{node.id}"

                        # Store the dependency in the hook for later retrieval
                        self.hook._injected_deps[hook_name] = dep_value

                        # Create AST for calling the hook method
                        attr = ast.Attribute(
                            value=ast.Name(id="__import_hook", ctx=ast.Load()),
                            attr="_get_injected_dep",
                            ctx=ast.Load(),
                        )
                        new_node = ast.Call(
                            func=attr,
                            args=[
                                ast.Str(s=hook_name)
                                if not hasattr(ast, "Constant")
                                else ast.Constant(value=hook_name, kind=None)
                            ],
                            keywords=[],
                        )

                        # Generate code to add the hook to the module's globals
                        injection_code = (
                            "__import_hook = __import__('sys').meta_path[0]"
                        )

                    # Add the code to inject the hook as a global variable if needed
                    if injection_code:
                        self.hook.module_source_map[f"{self.module_name}_injection"] = (
                            injection_code
                        )

                    # Make sure new_node is not None before calling ast.copy_location
                    if new_node is not None:
                        ast.copy_location(new_node, node)
                        return new_node
                return node

        # Parse the source into an AST
        tree = ast.parse(source)

        # Transform the AST
        transformer = ImportTransformer(self, module_name)
        transformed_tree = transformer.visit(tree)

        # Add dependency injection code at the module start
        if module_name in self.dependency_map:
            injection_code = []
            for dep_name, substitute in self.dependency_map[module_name].items():
                var_name = f"__injected_{dep_name}__"
                if isinstance(substitute, str):
                    # It's a module name, import it
                    injection_code.append(
                        ast.parse(f"{var_name} = __import__('{substitute}')").body[0]
                    )
                else:
                    # It's an actual object, expose it through the hook
                    injection_code.append(
                        ast.parse(
                            f"{var_name} = sys.meta_path[0]._get_injected_dep('{module_name}.{var_name}')"
                        ).body[0]
                    )

            # Add the injection code at the beginning of the module
        transformed_tree.body = injection_code + transformed_tree.body

        # Add necessary imports
        transformed_tree.body.insert(0, ast.parse("import sys").body[0])

        # Generate source from the transformed AST
        return ast.unparse(transformed_tree)

    def _get_injected_dep(self, key):
        """
        Get an injected dependency from the hook's storage.

        Args:
            key (str): The identifier for the injected dependency.

        Returns:
            The injected dependency value.
        """
        return self._injected_deps.get(key)
