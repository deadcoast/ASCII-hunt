"""Code Generation Processor Module.

This module provides a processor for generating code based on recognized components.
"""

from typing import Any


class CodeGenerationProcessor:
    """A processor for generating code based on recognized components.

    This processor takes a component model and generates code for it using
    registered code generators.
    """

    def __init__(self) -> None:
        """Initialize the CodeGenerationProcessor class."""
        self.code_generators: dict[str, Any] = {}
        self.default_generator: str | None = None
        self.template_engines: dict[str, Any] = {}

    def register_code_generator(self, framework: str, generator: Any) -> None:
        """Register a code generator for a specific framework.

        Args:
            framework: The framework to generate code for (e.g., "react", "flutter").
            generator: The code generator to register.
        """
        self.code_generators[framework] = generator

        # Set as default if no default is set
        if self.default_generator is None:
            self.default_generator = framework

    def set_default_generator(self, framework: str) -> None:
        """Set the default code generator.

        Args:
            framework: The framework to use as default.
        """
        if framework in self.code_generators:
            self.default_generator = framework

    def register_template_engine(self, name: str, engine: Any) -> None:
        """Register a template engine.

        Template engines are used by code generators to render templates.

        Args:
            name: The name of the template engine.
            engine: The template engine to register.
        """
        self.template_engines[name] = engine

    def process(self, component_model: Any, context: dict[str, Any]) -> str:
        """Generate code for the given component model.

        Args:
            component_model: The component model to generate code for.
            context: The context dictionary containing options.

        Returns:
            The generated code as a string.
        """
        # Get target framework from context
        target_framework = context.get("target_framework", self.default_generator)
        if target_framework not in self.code_generators and self.default_generator:
            target_framework = self.default_generator

        # Get generator options
        generator_options = context.get("generator_options", {})

        # Get the appropriate code generator
        generator = self.code_generators.get(target_framework)
        if not generator:
            raise ValueError(
                f"No code generator available for framework: {target_framework}"
            )

        # Generate code
        try:
            generated_code = generator.generate_code(component_model, generator_options)

            # Store generated code in context
            context["generated_code"] = generated_code
            context["target_framework"] = target_framework

            return generated_code
        except Exception as e:
            error_msg = f"Error generating code: {e!s}"
            context["error"] = error_msg
            raise RuntimeError(error_msg) from e

    def get_available_frameworks(self) -> list[str]:
        """Get a list of available frameworks.

        Returns:
            A list of framework names.
        """
        return list(self.code_generators.keys())

    def get_template_engine(self, name: str) -> Any | None:
        """Get a registered template engine.

        Args:
            name: The name of the template engine.

        Returns:
            The template engine, or None if not found.
        """
        return self.template_engines.get(name)
