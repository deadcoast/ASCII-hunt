import importlib.abc
import importlib.machinery
import importlib.util
import inspect
from collections.abc import Callable, Sequence
from types import ModuleType
from typing import TypeVar

T = TypeVar("T")


class AdvancedImportFinder(importlib.abc.MetaPathFinder):
    def __init__(self) -> None:
        """Initialize an AdvancedImportFinder object.

        The object stores information about the call graph (import_graph), the callers
        of each module (caller_map), and the usage of each symbol (symbol_usage).

        :return: None
        """
        self.import_graph: dict[str, list[str]] = {}
        self.caller_map: dict[str, list[str]] = {}
        self.symbol_usage: dict[str, list[dict[str, object]]] = {}

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        """Find the specification for a module.

        This method is called by the import machinery to find the specification
        for a module. It records the caller of the module and updates the import
        graph.

        :param fullname: The full name of the module to find
        :param path: The path to the module
        :param target: The target of the import
        :return: The specification for the module
        """
        # Get the call stack to identify who's importing this module
        frame = inspect.currentframe()
        if frame is None:
            return None

        frame = frame.f_back
        while frame and not frame.f_code.co_filename.endswith(".py"):
            frame = frame.f_back

        if frame:
            caller = frame.f_code.co_filename
            if fullname not in self.caller_map:
                self.caller_map[fullname] = []
            if caller not in self.caller_map[fullname]:
                self.caller_map[fullname].append(caller)

            # Record in the import graph
            if caller not in self.import_graph:
                self.import_graph[caller] = []
            if fullname not in self.import_graph[caller]:
                self.import_graph[caller].append(fullname)

        # Let normal import machinery take over
        return None


class SymbolTracker:
    def __init__(self) -> None:
        """Initialize the symbol tracker.

        This object intercepts module imports and wraps symbols in tracked modules
        to record their usage.

        :return: None
        """
        self.original_import = __import__
        self.tracked_modules: dict[str, ModuleType] = {}
        # Initialize symbol_usage dictionary to track usage of symbols
        self.symbol_usage: dict[str, list[dict[str, object]]] = {}

    def install(self) -> None:
        """Install this tracker to intercept module imports.

        This function replaces the global __import__ function with a tracked version
        that wraps symbols in tracked modules to record their usage.
        """

        def tracked_import(
            name: str,
            globals_: dict[str, object] | None = None,
            locals_: dict[str, object] | None = None,
            fromlist: Sequence[str] = (),
            level: int = 0,
        ) -> ModuleType:
            """Intercept module imports and wrap symbols in tracked modules to record
            their usage.

            This function replaces the global __import__ function and is called
            by the import machinery for every module import. It wraps symbols in
            tracked modules so that their usage can be recorded.

            :param name: The name of the module to import
            :param globals_: Global namespace to use
            :param locals_: Local namespace to use
            :param fromlist: List of items to import
            :param level: Relative import level
            :return: The imported module
            """
            module = self.original_import(name, globals_, locals_, fromlist, level)

            if name not in self.tracked_modules and isinstance(module, ModuleType):
                self.tracked_modules[name] = module
                self._wrap_module_attributes(module)

            return module

        __builtins__["__import__"] = tracked_import

    def _wrap_module_attributes(self, module: ModuleType) -> None:
        """Wrap module attributes to track their usage.

        :param module: The module whose attributes should be wrapped
        """
        for attr_name in dir(module):
            if attr_name.startswith("__"):
                continue

            try:
                original_attr = getattr(module, attr_name)

                if callable(original_attr):
                    # Wrap function/method
                    setattr(
                        module,
                        attr_name,
                        self._create_wrapper(original_attr, module.__name__, attr_name),
                    )
            except (AttributeError, ImportError):
                pass

    def _create_wrapper(
        self, func: Callable[..., T], module_name: str, attr_name: str
    ) -> Callable[..., T]:
        """Create a wrapper function to track the usage of a given module attribute.

        This wrapper records the caller file name, line number, and argument count
        for each call of the attribute. The recorded information is stored in the
        `symbol_usage` dictionary.

        :param func: The original function to wrap
        :param module_name: The name of the module the attribute belongs to
        :param attr_name: The name of the attribute to wrap
        :return: The wrapped function
        """

        def wrapper(*args: object, **kwargs: object) -> T:
            """Record the usage of the given module attribute with full call context.

            This wrapper records the caller file name, line number, and argument count
            for each call of the attribute. The recorded information is stored in the
            `symbol_usage` dictionary.

            :return: The result of the wrapped function
            """
            frame = inspect.currentframe()
            if frame is not None:
                frame = frame.f_back
                if frame:
                    caller = frame.f_code.co_filename
                    line = frame.f_lineno

                    key = f"{module_name}.{attr_name}"
                    if key not in self.symbol_usage:
                        self.symbol_usage[key] = []

                    self.symbol_usage[key].append(
                        {
                            "caller": caller,
                            "line": line,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        }
                    )

            return func(*args, **kwargs)

        return wrapper
