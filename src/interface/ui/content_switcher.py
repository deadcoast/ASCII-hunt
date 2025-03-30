from PyQt5.QtWidgets import QStackedWidget, QWidget


class ContentSwitcher(QStackedWidget):
    """A widget that manages switchable content using a stacked widget."""

    def __init__(self, parent: QWidget | None = None):
        """Initialize the content switcher.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.content_map: dict[str, QWidget] = {}

    def add_content(self, name: str, widget: QWidget) -> None:
        """Add a new content widget.

        Args:
            name: Unique name for the content
            widget: Widget to add
        """
        if name not in self.content_map:
            self.content_map[name] = widget
            self.addWidget(widget)

    def remove_content(self, name: str) -> None:
        """Remove a content widget.

        Args:
            name: Name of content to remove
        """
        if name in self.content_map:
            widget = self.content_map[name]
            self.removeWidget(widget)
            del self.content_map[name]

    def switch_to(self, name: str) -> bool:
        """Switch to the specified content.

        Args:
            name: Name of content to switch to

        Returns:
            True if switch was successful, False if content not found
        """
        if name in self.content_map:
            widget = self.content_map[name]
            self.setCurrentWidget(widget)
            return True
        return False

    def get_current_name(self) -> str | None:
        """Get the name of the currently displayed content.

        Returns:
            Name of current content, or None if no content
        """
        current = self.currentWidget()
        return next(
            (name for name, widget in self.content_map.items() if widget == current),
            None,
        )

    def clear(self) -> None:
        """Remove all content widgets."""
        for name in list(self.content_map.keys()):
            self.remove_content(name)
