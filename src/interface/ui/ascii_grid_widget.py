"""This is a widget that displays a grid of characters.
It is used to display the ASCII grid of the current file.
"""

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

from src.engine.drawing_mode import DrawingMode


class ASCIIGridWidget(QWidget):
    def __init__(self, parent=None):
        """Initialize the widget.

        :param parent: The parent of the widget.
        :type parent: QWidget
        """
        super().__init__(parent)
        self.grid_data = []
        self.cell_size = QSize(10, 20)  # Default cell size
        self.cursor_pos = QPoint(0, 0)
        self.selection = None
        self.drawing_mode = DrawingMode.CHARACTER
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the widget.

        This method sets the focus policy to Qt.StrongFocus, which means that the widget will
        receive focus when it is clicked. It also sets mouse tracking, which means that the widget
        will receive mouse move events even if no mouse buttons are pressed.
        """
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def set_grid_data(self, data):
        self.grid_data = data
        self.update()

    def cell_at_position(self, pos):
        """Given a position in the widget, return the corresponding cell coordinates.

        :param pos: The position in the widget.
        :type pos: QPoint
        :return: The coordinates of the cell that the position is in.
        :rtype: QPoint
        """
        x = pos.x() // self.cell_size.width()
        y = pos.y() // self.cell_size.height()
        return QPoint(x, y)

    def paintEvent(self, event):
        """Handle the paint event for the widget.

        :param event: The paint event.
        :type event: QPaintEvent

        This method is responsible for rendering the visual representation of the widget. It
        initializes a QPainter object and delegates the drawing tasks to specific methods for
        rendering the grid, characters, cursor, selection, and any component overlays.
        """
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_characters(painter)
        self.draw_cursor(painter)
        self.draw_selection(painter)
        self.draw_component_overlays(painter)

    def keyPressEvent(self, event):
        # Handle keyboard input for editing
        """Handle key press events for the widget.

        This method is responsible for handling all key press events for the widget. It
        should be overridden by subclasses to handle specific key presses.

        :param event: The key press event.
        :type event: QKeyEvent
        """

    def mousePressEvent(self, event):
        # Handle mouse input based on current drawing mode
        """Handle mouse press events for the widget.

        This method is responsible for handling all mouse press events for the widget. It
        should be overridden by subclasses to handle specific mouse presses.

        :param event: The mouse press event.
        :type event: QMouseEvent
        """

    def mouseReleaseEvent(self, event):
        # Handle mouse release events
        """Handle mouse release events for the widget.

        This method is responsible for handling all mouse release events for the widget. It
        should be overridden by subclasses to handle specific mouse releases.

        :param event: The mouse release event.
        :type event: QMouseEvent
        """

    def mouseMoveEvent(self, event):
        # Handle mouse move events
        """Handle mouse move events for the widget.

        This method is responsible for handling all mouse move events for the widget. It
        should be overridden by subclasses to handle specific mouse moves.

        :param event: The mouse move event.
        :type event: QMouseEvent
        """

    def wheelEvent(self, event):
        # Handle wheel events
        """Handle wheel events for the widget.

        This method is responsible for handling all wheel events for the widget. It
        should be overridden by subclasses to handle specific wheel events.

        :param event: The wheel event.
        :type event: QWheelEvent
        """

    def resizeEvent(self, event):
        # Handle resize events
        """Handle resize events for the widget.

        This method is responsible for handling all resize events for the widget. It
        should be overridden by subclasses to handle specific resize events.

        :param event: The resize event.
        :type event: QResizeEvent
        """

    def focusInEvent(self, event):
        # Handle focus in events
        """Handle focus in events for the widget.

        This method is responsible for handling all focus in events for the widget. It
        should be overridden by subclasses to handle specific focus in events.

        :param event: The focus in event.
        :type event: QFocusEvent

        Returns None
        """
