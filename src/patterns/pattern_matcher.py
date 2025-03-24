class PatternMatcher:
    def __init__(self, pattern_registry):
        self.pattern_registry = pattern_registry

    def match_component(self, grid, component, context=None):
        """Match a component against registered patterns."""
        if context is None:
            context = {}

        # Get all component patterns
        component_patterns = self.pattern_registry.get_all_component_patterns()

        # Try to match the component with each pattern
        matches = []

        for component_type, pattern in component_patterns.items():
            match_result = self._match_component_pattern(
                grid, component, pattern, context
            )

            if match_result["match"]:
                matches.append(
                    {
                        "component_type": component_type,
                        "confidence": match_result["confidence"],
                        "properties": match_result["properties"],
                    }
                )

        # Sort matches by confidence
        matches.sort(key=lambda m: m["confidence"], reverse=True)

        return matches

    def _match_component_pattern(self, grid, component, pattern, context):
        """Match a component against a specific pattern."""
        result = {"match": False, "confidence": 0.0, "properties": {}}

        # Extract pattern rules
        rules = pattern.get("rules", [])

        if not rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each rule
        for rule in rules:
            rule_type = rule.get("command")

            if rule_type == "tag":
                # Match tag rules
                tag_match = self._match_tag_rule(grid, component, rule, context)

                if tag_match["match"]:
                    total_confidence += tag_match["confidence"]
                    matched_rules += 1

                    # Add properties
                    result["properties"].update(tag_match["properties"])

            elif rule_type == "pluck":
                # Match pluck rules
                pluck_match = self._match_pluck_rule(grid, component, rule, context)

                if pluck_match["match"]:
                    total_confidence += pluck_match["confidence"]
                    matched_rules += 1

                    # Add properties
                    result["properties"].update(pluck_match["properties"])

            # Add more rule types as needed

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            result["match"] = result["confidence"] > 0.5  # Threshold for matching

        return result

    def _match_tag_rule(self, grid, component, rule, context):
        """Match a tag rule against a component."""
        result = {"match": False, "confidence": 0.0, "properties": {}}

        # Get tag name and rules
        tag_name = rule.get("tag_name")
        tag_rules = rule.get("rules", [])

        if not tag_name or not tag_rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each tag rule
        for tag_rule in tag_rules:
            # Process tag rule
            # This will depend on the specific tag rule format
            # For example, checking if a component has a specific character pattern

            # For illustration, let's say we're looking for a specific character
            if isinstance(tag_rule, list) and len(tag_rule) > 0:
                char_to_find = tag_rule[0]

                # Check if the component contains the character
                content = component.get("content", [])
                found = False

                for line in content:
                    if char_to_find in line:
                        found = True
                        break

                if found:
                    total_confidence += 1.0
                    matched_rules += 1

                    # Add property
                    result["properties"][f"has_{tag_name}"] = True

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            result["match"] = result["confidence"] > 0.5  # Threshold for matching

        return result

    def _match_pluck_rule(self, grid, component, rule, context):
        """Match a pluck rule against a component."""
        result = {"match": False, "confidence": 0.0, "properties": {}}

        # Get target and rules
        target = rule.get("target")
        pluck_rules = rule.get("rules", [])

        if not target or not pluck_rules:
            return result

        # Initialize confidence
        total_confidence = 0.0
        matched_rules = 0

        # Check each pluck rule
        for pluck_rule in pluck_rules:
            # Process pluck rule
            # This will depend on the specific pluck rule format
            # For example, extracting text from a specific region of the component

            # For illustration, let's say we're extracting text matching a pattern
            if isinstance(pluck_rule, list) and len(pluck_rule) > 0:
                pattern = pluck_rule[0]

                # Check if the component contains text matching the pattern
                content = component.get("content", [])
                extracted_text = None

                for line in content:
                    import re

                    match = re.search(pattern, line)

                    if match:
                        extracted_text = match.group(0)
                        break

                if extracted_text:
                    total_confidence += 1.0
                    matched_rules += 1

                    # Add property
                    result["properties"][target] = extracted_text

        # Calculate overall confidence
        if matched_rules > 0:
            result["confidence"] = total_confidence / matched_rules
            result["match"] = result["confidence"] > 0.5  # Threshold for matching

        return result

    def match_relationships(self, grid, components, context=None):
        """Match relationships between components."""
        if context is None:
            context = {}

        # Get all relationship patterns
        relationship_patterns = self.pattern_registry.get_all_relationship_patterns()

        # Try to match relationships
        relationships = []

        for relationship_type, pattern in relationship_patterns.items():
            relationship_matches = self._match_relationship_pattern(
                grid, components, pattern, context
            )
            relationships.extend(relationship_matches)

        return relationships

    def _match_relationship_pattern(self, grid, components, pattern, context):
        """Match a relationship pattern between components."""
        # Extract pattern rules
        rules = pattern.get("rules", [])

        if not rules:
            return []

        # Initialize relationships
        relationships = []

        # Check each rule
        for rule in rules:
            rule_type = rule.get("command")

            if rule_type == "tag":
                # Match tag rules for relationships
                tag_relationships = self._match_relationship_tag_rule(
                    grid, components, rule, context
                )
                relationships.extend(tag_relationships)

            # Add more rule types as needed

        return relationships

    def _match_relationship_tag_rule(self, grid, components, rule, context):
        """Match a tag rule for relationships between components."""
        # Get tag name and rules
        tag_name = rule.get("tag_name")
        tag_rules = rule.get("rules", [])

        if not tag_name or not tag_rules:
            return []

        # Initialize relationships
        relationships = []

        # Implement relationship matching logic
        # This will depend on the specific tag rule format
        # For example, checking for containing relationships based on bounding boxes

        return relationships
