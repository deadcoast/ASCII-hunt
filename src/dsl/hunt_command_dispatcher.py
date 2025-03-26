"""### track - _Scan and map ASCII canvas_
Concept: The core parser. 'hunt' moves across the canvas to identify characters, patterns, and regions of interest. It's the entry point for finding UI elements or zones.

Functions / Usage Ideas:
- Perform a full grid scan for visual components.
- Target glyphs, borders, labels, or boxes.
- Set up for downstream 'skin', 'pluck', or 'gather'.

Example:
```hunt
track boxes:true labels:true
```

- skin _Extract character + coordinate data_
Concept: 'skin' performs raw data extraction after a 'hunt', pulling characters and their coordinates from matched regions.

Functions / Usage Ideas:
- Collect bounding boxes and inner contents.
- Extract character-level information for each region.
- Prepare inputs for tagging, gathering, or analysis.

Example:
```hunt
skin region:main
```

- gather _Organize and structure data_
Concept: Takes extracted elements and assembles them into logical, tagged UI components. Think of it as structuring your raw hunt/skin output.

Functions / Usage Ideas:
- Create a component tree or hierarchy.
- Add tags like 'button', 'input', 'header'.
- Apply spatial grouping heuristics.

Example:
```hunt
gather tags:true group:vertical
```

- harvest  _Bulk collect from multiple layers_
Concept: Combines data from multiple 'hunt' or 'skin' passes, or pulls all data across a canvas or layered views.

Functions / Usage Ideas:
- Aggregate output from multiple grid scans.
- Merge 'skin' data into one source.
- Useful in batch or composite analysis.

Example:
```hunt
harvest from:all_layers
```

boil  _Refine or simplify data structure_
Concept: After 'gather' or 'cook', use 'boil' to strip down, reduce, or normalize structures. It's a post-processing or reduction step, helping keep output lean.

Functions / Usage Ideas:
- Minify the Python output.
- Deduplicate or flatten nested tags.
- Drop debug fields, keep core essentials.

Example:
```hunt
boil mode:minimal
```

- cook  _Emit Python code from structured data_
Concept: Converts structured elements from 'gather' into runnable Python code, typically UI generation or layout functions.

Functions / Usage Ideas:
- Generate tkinter, curses, or custom layout code.
- Translate tagged components into widgets.
- Optionally include styling or behavior hooks.

Example:
```hunt
cook format:tkinter
```

- 'rack' _Preview or simulate output_
Concept: 'rack' provides a visual or simulated pass of the gathered data — think dry run or rendering layer.

Functions / Usage Ideas:
- Simulate layout output before generation.
- Visually debug gathered UI structures.
- Show transformations step by step.

Example:
```hunt
rack mode:ascii
```

- scout  _Log, trace, and debug flow_
Concept: Enables logging, tracing, and inspection of the DSL pipeline. Use it to debug 'hunt' sequences and internal state.

Functions / Usage Ideas:
- Log character matches, region counts.
- Inspect transformations across stages.
- Useful for visual or programmatic tracing.

Example:
```hunt
scout level:verbose
```

- 'trap' _Set trigger conditions or constraints_
Concept: Think of 'trap' as a pre-emptive boundary, rule, or breakpoint. It doesn't *crash* (that's `snare`), but it prevents undesired patterns or captures anomalies early.

Functions / Usage Ideas:
- Define "illegal zones" or disallowed characters.
- Assert certain preconditions before 'hunt'/'skin'.
- Lint-style warnings — not critical, but notable.
- Set a watchpoint on certain coordinates.

Example:
```hunt
trap "window must have border"
```
- scent' _Soft warnings or partial matches_
Concept: 'scent' is a non-fatal warning system. It flags suspicious patterns or incomplete structures that may still be usable.

Functions / Usage Ideas:
- Highlight elements missing borders or labels.
- Trigger soft alerts for malformed regions.
- Log issues without halting processing.

Example:
```hunt
scent check:unlabeled_boxes
```

---

### 'snare' - _Critical error handling_
Concept: 'snare' represents a fatal condition — the pipeline fails, and processing halts. Use this to guard against critical misconfigurations.

Functions / Usage Ideas:
- Halt if required structures are missing.
- Validate critical layout constraints.
- Crash intentionally with meaningful error messages.

Example:
```hunt
snare "missing sidebar region"
```

---

'pluck' _Selective extraction_
Concept: Unlike 'skin' (bulk extraction), 'pluck' is precision targeting — grab a single element, based on a refined filter (e.g. label, coordinates, proximity, tag).

Functions / Usage Ideas:
- Pull just the first matching label from a 'hunt'.
- Get only center points or specific glyphs.
- Use for focused transformations or rewrites.

Example:
```hunt
pluck label:"Submit"
```

- Hunt and Gather: Thematically rich (especially with "gather" implying data extraction)
but acronym-wise "HAG" has rougher vibes, unless you lean into it tongue-in-cheek.
- Could also frame "Gather" as a *second phase* or submodule of the full toolchain.
  ```
  from hunt import gather
  ```
  or
  ```
  hunt -> gather -> generate
  ```

"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol, TypeVar, cast, runtime_checkable

from .hunt_error import DSLFatalError
from .hunt_grid import HuntGrid
from .hunt_utils import (assert_constraints, bulk_merge, extract_target,
                         generate_code, organize_tags, setup_logging,
                         simplify_output, visualize_output, warn_soft)


@runtime_checkable
class DSLCommand(Protocol):
    """Protocol for DSL command functions."""

    _dsl_command: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


T = TypeVar("T", bound=Callable[..., Any])


def dsl_command(command_name: str) -> Callable[[T], T]:
    """Decorator to mark a method as a DSL command handler.

    Args:
        command_name (str): Name of the command

    Returns:
        Callable: Decorated function
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            return func(self, *args, **kwargs)

        # Create a new function object that includes the _dsl_command attribute
        new_func = cast("T", wrapper)
        new_func._dsl_command = command_name
        return new_func

    return decorator


class HuntCommandDispatcher:
    def __init__(self):
        """Initialize a HuntCommandDispatcher.

        This creates an empty command registry. You must register commands
        before they can be executed.
        """
        self.command_registry: dict[str, Callable] = {}
        self.hunt_grid = HuntGrid()

    def __getitem__(self, key: str) -> Any:
        """Get a command handler by name.

        Args:
            key (str): Command name

        Returns:
            Any: Command handler

        Raises:
            DSLFatalError: If command not found
        """
        if key not in self.command_registry:
            raise DSLFatalError(f"Command '{key}' not found")
        return self.command_registry[key]

    def register_command(self, name: str, handler: Callable) -> None:
        """Register a command with a specified handler.

        Args:
            name (str): The name of the command to register.
            handler (callable): A function or method that handles the execution
                of the command. It should accept two arguments: params (the
                parameters for the command) and context (optional context
                information).
        """
        self.command_registry[name] = handler

    def execute_command(
        self,
        command: str,
        params: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Execute a registered command.

        Args:
            command (str): Command name to execute
            params (Dict[str, Any]): Command parameters
            context (Optional[Dict[str, Any]]): Optional execution context

        Returns:
            Any: Command result

        Raises:
            DSLFatalError: If command not found
        """
        if command not in self.command_registry:
            raise DSLFatalError(f"Command '{command}' not found")
        return self.command_registry[command](params, context)

    @dsl_command("hunt")
    def handle_hunt(self, params: dict[str, Any]) -> Any:
        """Handle the hunt command."""
        return self.hunt_grid.scan(params)

    @dsl_command("skin")
    def handle_skin(self, params: dict[str, Any]) -> Any:
        """Handle the skin command."""
        return self.hunt_grid.extract(params)

    @dsl_command("gather")
    def handle_gather(self, params: dict[str, Any]) -> Any:
        """Handle the gather command."""
        return organize_tags(params)

    @dsl_command("harvest")
    def handle_harvest(self, params: dict[str, Any]) -> Any:
        """Handle the harvest command."""
        return bulk_merge(params)

    @dsl_command("pluck")
    def handle_pluck(self, params: dict[str, Any]) -> Any:
        """Handle the pluck command."""
        return extract_target(params)

    @dsl_command("trap")
    def handle_trap(self, params: dict[str, Any]) -> Any:
        """Handle the trap command."""
        return assert_constraints(params)

    @dsl_command("scent")
    def handle_scent(self, params: dict[str, Any]) -> Any:
        """Handle the scent command."""
        return warn_soft(params)

    @dsl_command("snare")
    def handle_snare(self, params: dict[str, Any]) -> Any:
        """Handle the snare command."""
        raise DSLFatalError(self[params["message"]])

    @dsl_command("rack")
    def handle_rack(self, params: dict[str, Any]) -> Any:
        """Handle the rack command."""
        return visualize_output(params)

    @dsl_command("track")
    def handle_track(self, params: dict[str, Any]) -> Any:
        """Handle the track command."""
        return setup_logging(params)

    @dsl_command("boil")
    def handle_boil(self, params: dict[str, Any]) -> Any:
        """Handle the boil command."""
        return simplify_output(params)

    @dsl_command("cook")
    def handle_cook(self, params: dict[str, Any]) -> Any:
        """Handle the cook command."""
        return generate_code(params)
