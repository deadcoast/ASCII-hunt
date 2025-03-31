"""This is a widget that displays a grid of characters.
It is used to display the ASCII grid of the current file.
"""

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QKeyEvent  # Grouped imports
from PyQt5.QtGui import (
    QFocusEvent,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QWheelEvent,
)
from PyQt5.QtWidgets import QWidget

# Corrected import path
from src.core.drawing_mode import DrawingMode


class ASCIIGridWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:  # Added annotations
        """Initialize the widget.

        Args:
            parent: The optional parent widget.
        """
        super().__init__(parent)
        self.grid_data: list[list[str]] = []  # Added type hint
        self.cell_size = QSize(10, 20)  # Default cell size
        self.cursor_pos = QPoint(0, 0)
        self.selection: tuple[QPoint, QPoint] | None = None  # Added type hint
        self.drawing_mode = DrawingMode.CHARACTER
        self.setup_ui()

    def setup_ui(self) -> None:  # Added annotation
        """Set up the UI for the widget.

        Sets focus policy and enables mouse tracking.
        """
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def set_grid_data(self, data: list[list[str]]) -> None:  # Added annotations
        """Set the grid data and trigger a repaint.

        Args:
            data: A 2D list of strings representing the grid.
        """
        self.grid_data = data
        self.update()

    def cell_at_position(self, pos: QPoint) -> QPoint:  # Added annotations
        """Given a pixel position, return the corresponding cell coordinates.

        Args:
            pos: The position in widget coordinates.

        Returns:
            The grid coordinates (column, row) of the cell.
        """
        x = pos.x() // self.cell_size.width()
        y = pos.y() // self.cell_size.height()
        return QPoint(x, y)

    # Renamed event handlers to snake_case
    def paint_event(self, event: QPaintEvent) -> None:  # Added annotations
        """Handle the paint event for the widget.

        Renders the grid, characters, cursor, selection, and overlays.

        Args:
            event: The paint event.
        """
        painter = QPainter(self)
        # Placeholder calls - Implement drawing logic later
        # self.draw_grid(painter)
        # self.draw_characters(painter)
        # self.draw_cursor(painter)
        # self.draw_selection(painter)
        # self.draw_component_overlays(painter)
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, "Grid Placeholder"
        )  # Simple placeholder

    def key_press_event(self, event: QKeyEvent) -> None:  # Added annotations
        """Handle key press events for editing or navigation.

        Args:
            event: The key press event.
        """
        # Placeholder - Implement editing logic later
        pass

    def mouse_press_event(self, event: QMouseEvent) -> None:  # Added annotations
        """Handle mouse press events based on the current drawing mode.

        Args:
            event: The mouse press event.
        """
        # Placeholder - Implement mode-specific logic later
        pass

    def mouse_release_event(self, event: QMouseEvent) -> None:  # Added annotations
        """Handle mouse release events.

        Args:
            event: The mouse release event.
        """
        # Placeholder
        pass

    def mouse_move_event(self, event: QMouseEvent) -> None:  # Added annotations
        """Handle mouse move events, e.g., for selection or dragging.

        Args:
            event: The mouse move event.
        """
        # Placeholder
        pass

    def wheel_event(self, event: QWheelEvent) -> None:  # Added annotations
        """Handle wheel events, e.g., for zooming.

        Args:
            event: The wheel event.
        """
        # Placeholder
        pass

    def resize_event(self, event: QResizeEvent) -> None:  # Added annotations
        """Handle resize events.

        Args:
            event: The resize event.
        """
        # Placeholder - May need to recalculate layout or cell size
        super().resizeEvent(event)  # Call base implementation if needed

    def focus_in_event(self, event: QFocusEvent) -> None:  # Added annotations
        """Handle focus in events.

        Args:
            event: The focus in event.
        """
        # Placeholder - Maybe change cursor appearance
        super().focusInEvent(event)  # Call base implementation if needed

    # Placeholder methods for actual drawing logic (to be implemented)
    def draw_grid(self, painter: QPainter) -> None:
        pass

    def draw_characters(self, painter: QPainter) -> None:
        pass

    def draw_cursor(self, painter: QPainter) -> None:
        pass

    def draw_selection(self, painter: QPainter) -> None:
        pass

    def draw_component_overlays(self, painter: QPainter) -> None:
        pass
