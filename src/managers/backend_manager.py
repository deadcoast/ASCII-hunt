"""Backend Manager Module.

Acts as a facade for the core processing engine, simplifying the interface
for the ApplicationController.
"""

from typing import Any

from src.interface.api.ascii_ui_translation_engine import ASCIIUITranslationEngine


class BackendManager:
    """Facade for backend processing operations."""

    def __init__(self) -> None:
        """Initializes the BackendManager, creating an instance of the engine."""
        self.engine = ASCIIUITranslationEngine()
        # Load plugins or configuration if needed
        # self.engine.load_plugins("path/to/plugins")
        # self.engine.load_config("path/to/config")

    def process_ascii_grid(self, grid_data: list[str]) -> list[dict[str, Any]]:
        """Processes the ASCII grid data to recognize components.

        Args:
            grid_data: A list of strings representing the ASCII grid.

        Returns:
            A list of dictionaries, each representing a recognized component.
            Returns an empty list if processing fails or no components are found.
        """
        ascii_text = "\n".join(grid_data)
        result = self.engine.process_ascii_ui(ascii_text)

        if result.get("success"):
            # The engine returns the full component model, extract components list
            component_model = result.get("component_model", {})
            # Assuming component_model might be a dict or an object with get_all_components
            if hasattr(component_model, "get_all_components"):
                return component_model.get_all_components()
            elif isinstance(component_model, dict):
                # Attempt to extract from dict structure if applicable
                return component_model.get("components", [])
            else:
                # Fallback if structure is unknown
                return []
        else:
            print(f"Error during processing: {result.get('error')}")
            return []

    def generate_code(
        self,
        components: list[dict[str, Any]],
        framework: str,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generates code for the given components using the specified framework.

        Args:
            components: The list of recognized components.
            framework: The target UI framework (e.g., 'tkinter', 'textual').
            options: Additional generation options.

        Returns:
            The generated code as a string, or an error message.
        """
        if options is None:
            options = {}

        # The ASCIIUITranslationEngine's process_ascii_ui handles generation.
        # We need to reconstruct the necessary context or call a specific generator.
        # For simplicity here, let's assume we might need to re-process
        # or directly call a generation part of the engine if available.

        # Option A: Re-process (less efficient if recognition was just done)
        # This requires grid_data which isn't passed here.
        # Need to adjust ApplicationController or this manager's state.

        # Option B: Call a specific generation method on the engine (if one exists)
        # generator = self.engine.get_generator(framework) # Hypothetical
        # return generator.generate(components, options)

        # Option C: Rerun process_ascii_ui with generation options (requires grid)
        # This seems the most likely way the engine is designed, but needs grid data.
        # For now, return an placeholder/error message.
        print(
            "Warning: generate_code in BackendManager needs grid data or direct access"
            " to a generator. Re-processing or direct generation not fully implemented."
        )

        # Simulate calling the engine's generation stage if possible
        # This assumes the components list *is* the component model needed,
        # or can be used to rebuild it.
        gen_options = {
            "target_framework": framework,
            "generator_options": options,
            # We might need to pass the component list/model explicitly if
            # the engine doesn't retain state from process_ascii_grid
            "component_model": {"components": components},  # Example structure
        }

        # process_ascii_ui likely needs the original text/grid, not just components.
        # Returning placeholder code.
        return (
            f"# Code generation for {framework} not fully implemented here.\n"
            f"# Received {len(components)} components."
        )
