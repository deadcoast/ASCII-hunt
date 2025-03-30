"""DSL Command Dispatcher Module.

This module provides a DSLCommandDispatcher class for executing DSL commands.
The DSLCommandDispatcher class can be used to execute DSL commands and manage
the command registry.

### track - _Scan and map ASCII canvas_
Concept: The core parser. 'hunt' moves across the canvas to identify characters,
patterns, and regions of interest. It's the entry point for finding UI elements
or zones.

Functions / Usage Ideas:
- Perform a full grid scan for visual components.
- Target glyphs, borders, labels, or boxes.
- Set up for downstream 'skin', 'pluck', or 'gather'.

Example:
```hunt
track boxes:true labels:true
```

- skin _Extract character + coordinate data_
Concept: 'skin' performs raw data extraction after a 'hunt', pulling characters
and their coordinates from matched regions.

Functions / Usage Ideas:
- Collect bounding boxes and inner contents.
- Extract character-level information for each region.
- Prepare inputs for tagging, gathering, or analysis.

Example:
```hunt
skin region:main
```

- gather _Organize and structure data_
Concept: Takes extracted elements and assembles them into logical, tagged UI
components. Think of it as structuring your raw hunt/skin output.

Functions / Usage Ideas:
- Create a component tree or hierarchy.
- Add tags like 'button', 'input', 'header'.
- Apply spatial grouping heuristics.

Example:
```hunt
gather tags:true group:vertical
```

- harvest  _Bulk collect from multiple layers_
Concept: Combines data from multiple 'hunt' or 'skin' passes, or pulls all data
across a canvas or layered views.

Functions / Usage Ideas:
- Aggregate output from multiple grid scans.
- Merge 'skin' data into one source.
- Useful in batch or composite analysis.

Example:
```hunt
harvest from:all_layers
```

boil  _Refine or simplify data structure_
Concept: After 'gather' or 'cook', use 'boil' to strip down, reduce, or
normalize structures. It's a post-processing or reduction step, helping keep
output lean.

Functions / Usage Ideas:
- Minify the Python output.
- Deduplicate or flatten nested tags.
- Drop debug fields, keep core essentials.

Example:
```hunt
boil mode:minimal
```

- cook  _Emit Python code from structured data_
Concept: Converts structured elements from 'gather' into runnable Python code,
typically UI generation or layout functions.

Functions / Usage Ideas:
- Generate tkinter, curses, or custom layout code.
- Translate tagged components into widgets.
- Optionally include styling or behavior hooks.

Example:
```hunt
cook format:tkinter
```

- 'rack' _Preview or simulate output_
Concept: 'rack' provides a visual or simulated pass of the gathered data — think
dry run or rendering layer.

Functions / Usage Ideas:
- Simulate layout output before generation.
- Visually debug gathered UI structures.
- Show transformations step by step.

Example:
```hunt
rack mode:ascii
```

- scout  _Log, trace, and debug flow_
Concept: Enables logging, tracing, and inspection of the DSL pipeline. Use it to
debug 'hunt' sequences and internal state.

Functions / Usage Ideas:
- Log character matches, region counts.
- Inspect transformations across stages.
- Useful for visual or programmatic tracing.

Example:
```hunt
scout level:verbose
```

- 'trap' _Set trigger conditions or constraints_
Concept: Think of 'trap' as a pre-emptive boundary, rule, or breakpoint. It
doesn't *crash* (that's `snare`), but it prevents undesired patterns or
captures anomalies early.

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
Concept: 'scent' is a non-fatal warning system. It flags suspicious
patterns/structures.

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
Concept: 'snare' represents a fatal condition — the pipeline fails, and
processing halts

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
Concept: Unlike 'skin' (bulk extraction), 'pluck' is precision targeting — grab
a single element, based on a refined filter (e.g. label, coordinates,
proximity, tag).

Functions / Usage Ideas:
- Pull just the first matching label from a 'hunt'.
- Get only center points or specific glyphs.
- Use for focused transformations or rewrites.

Example:
```hunt
pluck label:"Submit"
```

- Dsl and Gather: Thematically rich (especially with "gather" implying data
  extraction)
but acronym-wise "HAG" has rougher vibes, unless you lean into it
tongue-in-cheek.
- Could also frame "Gather" as a *second phase* or submodule of the full
  toolchain.
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
from typing import Any, NoReturn, Protocol, TypeVar, cast, runtime_checkable

from src.core.dsl.dsl_error import DSLFatalError
from src.interface.ui.dsl_grid import DslGrid
from src.utils.dsl_utils import (
    assert_constraints,
    bulk_merge,
    extract_target,
    generate_code,
    organize_tags,
    simplify_output,
    visualize_output,
    warn_soft,
)

# Define common types

CommandParams = dict[str, str | int | float | bool | list[str] | dict[str, Any]]
CommandResult = dict[str, Any] | list[dict[str, Any]] | list[str] | str | bool | None


@runtime_checkable
class DSLCommand(Protocol):
    """Protocol for DSL command functions."""

    _dsl_command: str

    def __call__(
        self,
        params: CommandParams,
        context: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute the command with given parameters and context.

        Args:
            params (CommandParams): Command parameters.
            context (dict[str, Any] | None, optional): Execution context.
                Defaults to None.

        Returns:
            CommandResult: Result of the command execution.
        """
        ...


T = TypeVar("T", bound=Callable[..., CommandResult])


def dsl_command(command_name: str) -> Callable[[T], T]:
    """Decorator to mark a method as a DSL command handler.

    Args:
        command_name (str): Name of the command

    Returns:
        Callable: Decorated function
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(
            self: "DSLCommandDispatcher",
            params: CommandParams,
            context: dict[str, Any] | None = None,
        ) -> CommandResult:
            return func(self, params, context) if context else func(self, params)

        # Create a new function object that includes the _dsl_command attribute
        new_func = cast("DSLCommand", wrapper)
        new_func._dsl_command = command_name
        return cast("T", new_func)

    return decorator


class DSLCommandDispatcher:
    """DSL Command Dispatcher."""

    def __init__(self) -> None:
        """Initialize a DSLCommandDispatcher.

        This creates an empty command registry. You must register commands
        before they can be executed.
        """
        self.command_registry: dict[str, DSLCommand] = {}
        self.dsl_grid = DslGrid()

    def __getitem__(self, key: str) -> DSLCommand:
        """Get a command handler by name.

        Args:
            key (str): Command name

        Returns:
            DSLCommand: Command handler

        Raises:
            DSLFatalError: If command not found
        """
        if key not in self.command_registry:
            msg = f"Command '{key}' not found in registry"
            raise DSLFatalError(msg)
        return self.command_registry[key]

    def register_command(self, name: str, handler: DSLCommand) -> None:
        """Register a command handler.

        Args:
            name (str): Command name
            handler (DSLCommand): Command handler function
        """
        self.command_registry[name] = handler

    def execute_command(
        self,
        command: str,
        params: CommandParams,
        context: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute a registered command.

        Args:
            command (str): Command name
            params (CommandParams): Command parameters
            context (dict[str, Any] | None, optional): Execution context.
                Defaults to None.

        Returns:
            CommandResult: Command result

        Raises:
            DSLFatalError: If command not found
        """
        if command not in self.command_registry:
            msg = f"Command '{command}' not found in registry"
            raise DSLFatalError(msg)

        handler = self.command_registry[command]
        return handler(params) if context is None else handler(params, context)

    @dsl_command("hunt")
    def handle_hunt(self, params: CommandParams) -> CommandResult:
        """Handle the 'hunt' command."""
        return self.dsl_grid.scan(params)

    @dsl_command("skin")
    def handle_skin(self, params: CommandParams) -> CommandResult:
        """Handle the 'skin' command."""
        return extract_target(params)

    @dsl_command("gather")
    def handle_gather(self, params: CommandParams) -> CommandResult:
        """Handle the 'gather' command."""
        return organize_tags(params)

    @dsl_command("harvest")
    def handle_harvest(self, params: CommandParams) -> CommandResult:
        """Handle the 'harvest' command."""
        return bulk_merge(params)

    @dsl_command("pluck")
    def handle_pluck(self, params: CommandParams) -> CommandResult:
        """Handle the 'pluck' command."""
        return extract_target(params)

    @dsl_command("trap")
    def handle_trap(self, params: CommandParams) -> CommandResult:
        """Handle the 'trap' command."""
        return assert_constraints(params)

    @dsl_command("scent")
    def handle_scent(self, params: CommandParams) -> CommandResult:
        """Handle the 'scent' command."""
        return warn_soft(params)

    @dsl_command("snare")
    def handle_snare(self, params: CommandParams) -> NoReturn:
        """Handle the 'snare' command."""
        message = str(params.get("message", "Fatal error"))
        raise DSLFatalError(message)

    @dsl_command("rack")
    def handle_rack(self, params: CommandParams) -> CommandResult:
        """Handle the 'rack' command."""
        return visualize_output(params)

    @dsl_command("track")
    def handle_track(self, params: CommandParams) -> CommandResult:
        """Handle the 'track' command."""
        return self.dsl_grid.scan(params)

    @dsl_command("boil")
    def handle_boil(self, params: CommandParams) -> CommandResult:
        """Handle the 'boil' command."""
        return simplify_output(params)

    @dsl_command("cook")
    def handle_cook(self, params: CommandParams) -> CommandResult:
        """Handle the 'cook' command."""
        return generate_code(params)
