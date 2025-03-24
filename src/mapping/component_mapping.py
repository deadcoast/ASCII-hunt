class Mapping:
    def __init__(self, component_mappings):
        self.component_mappings = component_mappings

    def apply(self, component, context=None):
        """Apply the mapping to a component and generate code."""
        if context is None:
            context = {}

        component_type = component.type

        if component_type not in self.component_mappings:
            raise ValueError(f"No mapping defined for component type: {component_type}")

        mapping = self.component_mappings[component_type]
        return mapping.apply(component, context)


class ComponentMapping:
    def __init__(self, component_type, property_mappings, template, children_mappings):
        self.component_type = component_type
        self.property_mappings = property_mappings
        self.template = template
        self.children_mappings = children_mappings

    def apply(self, component, parent_context=None):
        """Apply the mapping to a component and generate code."""
        # Create context for expression evaluation
        context = {"component": component, "parent": parent_context}

        # Evaluate property mappings
        properties = {}
        for prop_name, prop_expr in self.property_mappings.items():
            properties[prop_name] = prop_expr(context)

        # Process template
        if self.template:
            template_engine = TemplateEngine()
            code = template_engine.render(
                self.template, {"component": component, "properties": properties}
            )
        else:
            code = None

        # Process children if any
        children_code = []

        for i, child in enumerate(component.children):
            child_context = dict(context)
            child_context["index"] = i

            child_type = child.type

            if child_type in self.children_mappings:
                child_mapping_expr = self.children_mappings[child_type]
                child_mapping = child_mapping_expr(child_context)

                if child_mapping:
                    child_code = child_mapping.apply(child, context)
                    children_code.append(child_code)

        # Combine code from this component and its children
        if code and children_code:
            # Insert children at placeholder or append
            if "{children}" in code:
                final_code = code.replace("{children}", "\n".join(children_code))
            else:
                final_code = code + "\n" + "\n".join(children_code)
        elif code:
            final_code = code
        elif children_code:
            final_code = "\n".join(children_code)
        else:
            final_code = ""

        return final_code
