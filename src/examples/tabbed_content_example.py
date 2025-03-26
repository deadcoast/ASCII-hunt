"""Example usage of TabbedContent widget."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Label

from src.widgets.tabbed_content import TabbedContent, TabPane


class TabbedContentExample(App):
    """A simple app demonstrating TabbedContent usage."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Example 1: Using TabPane children
        with TabbedContent():
            with TabPane("Tab 1", id="tab1"):
                yield Label("Content for Tab 1")
            with TabPane("Tab 2", id="tab2"):
                yield Label("Content for Tab 2")
            with TabPane("Tab 3", id="tab3"):
                yield Container(
                    Label("Multiple"),
                    Label("widgets"),
                    Label("in"),
                    Label("Tab 3"),
                )

        # Example 2: Using title arguments
        yield TabbedContent(
            "First",
            "Second",
            "Third",
            initial="tab-2",  # Start with second tab active
        )


if __name__ == "__main__":
    app = TabbedContentExample()
    app.run()
