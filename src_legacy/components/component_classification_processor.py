class ComponentClassificationProcessor:
    def __init__(self):
        self.classifiers = {}
        self.default_classifier = None

    def register_classifier(self, component_type, classifier):
        """Register a classifier for a specific component type."""
        self.classifiers[component_type] = classifier

    def set_default_classifier(self, classifier):
        """Set the default classifier for components without a specific classifier."""
        self.default_classifier = classifier

    def process(self, components, context=None):
        """Classify components based on their features."""
        if context is None:
            context = {}

        # Process each component
        for component in components:
            # Get preliminary type information
            preliminary_type = component.get("type", "unknown")

            # Select appropriate classifier
            classifier = self.classifiers.get(preliminary_type, self.default_classifier)

            if classifier:
                # Classify the component
                classification_result = classifier.classify(component, context)

                if classification_result:
                    # Update component with classification result
                    component.update(classification_result)

        # Store in context for other stages
        context["component_classification_results"] = components

        return components
