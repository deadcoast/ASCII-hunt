from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QWidget


class Tabs(QTabWidget):
    """A widget that manages tabs with content."""

    tab_changed = pyqtSignal(str)  # Signal emitted when active tab changes

    def __init__(self, parent: QWidget | None = None):
        """Initialize the tabs widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.tab_map: dict[str, QWidget] = {}
        self.currentChanged.connect(self._on_tab_changed)

    def add_tab(self, name: str, widget: QWidget, title: str) -> None:
        """Add a new tab.

        Args:
            name: Unique name for the tab
            widget: Widget to show in the tab
            title: Display title for the tab
        """
        if name not in self.tab_map:
            self.tab_map[name] = widget
            self.addTab(widget, title)

    def remove_tab(self, name: str) -> None:
        """Remove a tab.

        Args:
            name: Name of tab to remove
        """
        if name in self.tab_map:
            widget = self.tab_map[name]
            index = self.indexOf(widget)
            if index >= 0:
                self.removeTab(index)
            del self.tab_map[name]

    def switch_to(self, name: str) -> bool:
        """Switch to the specified tab.

        Args:
            name: Name of tab to switch to

        Returns:
            True if switch was successful, False if tab not found
        """
        if name in self.tab_map:
            widget = self.tab_map[name]
            index = self.indexOf(widget)
            if index >= 0:
                self.setCurrentIndex(index)
                return True
        return False

    def get_current_name(self) -> str | None:
        """Get the name of the currently active tab.

        Returns:
            Name of current tab, or None if no tabs
        """
        current = self.currentWidget()
        for name, widget in self.tab_map.items():
            if widget == current:
                return name
        return None

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change events.

        Args:
            index: Index of the newly selected tab
        """
        if index >= 0:
            widget = self.widget(index)
            for name, tab_widget in self.tab_map.items():
                if widget == tab_widget:
                    self.tab_changed.emit(name)
                    break

    def clear(self) -> None:
        """Remove all tabs."""
        super().clear()
        self.tab_map.clear()
