class PatternRecognitionProcessor:
    def __init__(self):
        self.pattern_matchers = {}

    def register_pattern_matcher(self, name, matcher):
        """Register a pattern matcher."""
        self.pattern_matchers[name] = matcher

    def process(self, components, context=None):
        """Process components to recognize UI patterns."""
        if context is None:
            context = {}

        # Ensure we have a grid available
        if "grid" not in context:
            raise ValueError("Grid not available in context")

        grid = context["grid"]

        # Apply all registered pattern matchers
        for name, matcher in self.pattern_matchers.items():
            for component in components:
                pattern_matches = matcher.match(component, grid)

                if pattern_matches:
                    # Add pattern matches to component
                    if "pattern_matches" not in component:
                        component["pattern_matches"] = {}

                    component["pattern_matches"][name] = pattern_matches

                    # Apply pattern-specific attributes
                    self._apply_pattern_attributes(component, name, pattern_matches)

        # Store in context for other stages
        context["pattern_recognition_results"] = components

        return components

    def _apply_pattern_attributes(self, component, pattern_name, matches):
        """Apply pattern-specific attributes to a component."""
        if pattern_name == "button":
            component["is_button"] = True

            if "text" in matches:
                component["button_text"] = matches["text"]

        elif pattern_name == "checkbox":
            component["is_checkbox"] = True

            if "state" in matches:
                component["checkbox_state"] = matches["state"]

        elif pattern_name == "radio_button":
            component["is_radio_button"] = True

            if "state" in matches:
                component["radio_state"] = matches["state"]

            if "group" in matches:
                component["radio_group"] = matches["group"]

        elif pattern_name == "text_field":
            component["is_text_field"] = True

            if "text" in matches:
                component["field_text"] = matches["text"]

            if "placeholder" in matches:
                component["placeholder_text"] = matches["placeholder"]

        elif pattern_name == "dropdown":
            component["is_dropdown"] = True

            if "text" in matches:
                component["dropdown_text"] = matches["text"]

            if "state" in matches:
                component["dropdown_state"] = matches["state"]

        elif pattern_name == "window":
            component["is_window"] = True

            if "title" in matches:
                component["window_title"] = matches["title"]

        # Add more pattern-specific attributes for other UI element types
