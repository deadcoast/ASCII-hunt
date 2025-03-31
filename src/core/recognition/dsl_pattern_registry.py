"""Pattern Registry Module for HUNT DSL."""

from collections.abc import Callable
from typing import Any


class PatternRegistry:
    """Registry for pattern definitions and matchers used in HUNT DSL."""

    def __init__(self) -> None:
        """Initialize a new PatternRegistry."""
        self.patterns: dict[str, dict[str, Any]] = {}
        self.pattern_matchers: dict[str, Callable] = {}
        self.tag_index: dict[str, set[str]] = {}

    def register_pattern(
        self,
        pattern_id: str,
        pattern_definition: dict[str, Any],
        tags: list[str] | None = None,
    ) -> None:
        """Register a pattern with the registry.

        Args:
            pattern_id: Unique identifier for the pattern
            pattern_definition: Definition of the pattern
            tags: Optional list of tags to categorize the pattern
        """
        if pattern_id in self.patterns:
            error_message = f"Pattern with ID '{pattern_id}' already exists"
            raise ValueError(error_message)

        self.patterns[pattern_id] = pattern_definition

        # Index the pattern by tags
        if tags:
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = set()
                self.tag_index[tag].add(pattern_id)

    def register_matcher(self, pattern_id: str, matcher_function: Callable) -> None:
        """Register a matcher function for a pattern.

        Args:
            pattern_id: ID of the pattern to register the matcher for
            matcher_function: Function that implements the pattern matching logic
        """
        if pattern_id not in self.patterns:
            error_message = (
                f"Cannot register matcher for unknown pattern '{pattern_id}'"
            )
            raise ValueError(error_message)

        self.pattern_matchers[pattern_id] = matcher_function

    def get_pattern(self, pattern_id: str) -> dict[str, Any]:
        """Get a pattern by its ID.

        Args:
            pattern_id: ID of the pattern to retrieve

        Returns:
            The pattern definition

        Raises:
            KeyError: If pattern is not found
        """
        if pattern_id not in self.patterns:
            error_message = f"Pattern '{pattern_id}' not found"
            raise KeyError(error_message)

        return self.patterns[pattern_id]

    def get_matcher(self, pattern_id: str) -> Callable:
        """Get the matcher function for a pattern.

        Args:
            pattern_id: ID of the pattern to get the matcher for

        Returns:
            The matcher function

        Raises:
            KeyError: If matcher is not found
        """
        if pattern_id not in self.pattern_matchers:
            error_message = f"Matcher for pattern '{pattern_id}' not found"
            raise KeyError(error_message)

        return self.pattern_matchers[pattern_id]

    def find_patterns_by_tag(self, tag: str) -> set[str]:
        """Find patterns by tag.

        Args:
            tag: Tag to search for

        Returns:
            Set of pattern IDs with the given tag
        """
        return self.tag_index.get(tag, set())

    def match(self, pattern_id: str, content: dict[str, Any]) -> dict[str, Any] | None:
        """Apply a pattern matcher to content.

        Args:
            pattern_id: ID of the pattern to apply
            content: Content to match against

        Returns:
            Match result if successful, None otherwise
        """
        if pattern_id not in self.pattern_matchers:
            error_message = f"Matcher for pattern '{pattern_id}' not found"
            raise KeyError(error_message)

        return self.pattern_matchers[pattern_id](content)
