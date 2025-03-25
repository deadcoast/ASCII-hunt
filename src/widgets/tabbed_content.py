"""TabbedContent Widget Module.

A widget that combines Tabs and ContentSwitcher to create a tabbed interface.
"""

from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ContentSwitcher, Tabs

from .content_switcher import ContentSwitcher
from .tabs import Tabs


class TabPane(Widget):
    """A container for tab content."""

    def __init__(self, title: str, *, id: str | None = None) -> None:
        """Initialize a TabPane.

        Args:
            title: The title to display in the tab
            id: Optional ID for the tab pane
        """
        super().__init__(id=id)
        self.title = title


class TabbedContent(Widget):
    """A widget that combines tabs with content switching."""

    active = reactive("")

    class Cleared(Message):
        """Posted when the content is cleared."""

    class TabActivated(Message):
        """Posted when a tab is activated.

        Attributes:
            tab_id: The ID of the activated tab
        """

        def __init__(self, tab_id: str) -> None:
            """Initialize the message.

            Args:
                tab_id: The ID of the activated tab
            """
            super().__init__()
            self.tab_id = tab_id

    def __init__(
        self,
        *titles: str,
        initial: str | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize TabbedContent.

        Args:
            *titles: Optional tab titles (if not using TabPane)
            initial: ID of initially active tab
            name: Optional name for the widget
            id: Optional ID for the widget
        """
        super().__init__(name=name, id=id)
        self._titles = titles
        self._initial = initial
        self._tabs: Tabs | None = None
        self._content: ContentSwitcher | None = None

    def compose(self) -> list[Widget]:
        """Compose the widget's content.

        Returns:
            List of child widgets
        """
        # Create tabs from either titles or TabPane children
        tabs = []
        if self._titles:
            # Using titles provided in constructor
            for i, title in enumerate(self._titles, 1):
                tabs.append((f"tab-{i}", title))
        else:
            # Using TabPane children
            for child in self.children:
                if isinstance(child, TabPane):
                    tab_id = child.id or f"tab-{len(tabs) + 1}"
                    tabs.append((tab_id, child.title))

        # Create the tabs widget
        self._tabs = Tabs(*[title for _, title in tabs])
        for tab, (tab_id, _) in zip(self._tabs.children, tabs, strict=False):
            tab.id = f"--content-tab-{tab_id}"

        # Create the content switcher
        self._content = ContentSwitcher()

        # Set initial active tab
        if self._initial:
            self.active = self._initial
        elif tabs:
            self.active = tabs[0][0]

        return [self._tabs, self._content]

    def watch_active(self, value: str) -> None:
        """React to changes in the active tab.

        Args:
            value: The ID of the newly active tab
        """
        if self._tabs and self._content:
            # Update tabs
            tab_id = f"--content-tab-{value}"
            self._tabs.active = tab_id

            # Update content
            self._content.current = value

            # Post message
            self.post_message(self.TabActivated(value))

    def clear(self) -> None:
        """Clear all content."""
        if self._tabs:
            self._tabs.clear()
        if self._content:
            self._content.clear()
        self.post_message(self.Cleared())
