class CodeGenerationProcessor:
    def __init__(self):
        self.framework_generators = {}

    def register_framework_generator(self, framework_name, generator):
        """Register a code generator for a specific framework."""
        self.framework_generators[framework_name] = generator

    def process(self, component_model, context=None):
        """Generate code for the given component model."""
        if context is None:
            context = {}

        # Get target framework
        framework = context.get("target_framework", "default")

        # Check if we have a generator for this framework
        if framework not in self.framework_generators:
            raise ValueError(f"No code generator registered for framework: {framework}")

        # Get generator options from context
        options = context.get("generator_options", {})

        # Generate code
        generator = self.framework_generators[framework]
        generated_code = generator.generate(component_model, options)

        # Store in context for other stages
        context["generated_code"] = generated_code

        return generated_code
