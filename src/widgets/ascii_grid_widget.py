   class ASCIIGridWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.grid_data = []
           self.cell_size = QSize(10, 20)  # Default cell size
           self.cursor_pos = QPoint(0, 0)
           self.selection = None
           self.drawing_mode = DrawingMode.CHARACTER
           self.setup_ui()

       def setup_ui(self):
           self.setFocusPolicy(Qt.StrongFocus)
           self.setMouseTracking(True)

       def set_grid_data(self, data):
           self.grid_data = data
           self.update()

       def cell_at_position(self, pos):
           x = pos.x() // self.cell_size.width()
           y = pos.y() // self.cell_size.height()
           return QPoint(x, y)

       def paintEvent(self, event):
           painter = QPainter(self)
           self.draw_grid(painter)
           self.draw_characters(painter)
           self.draw_cursor(painter)
           self.draw_selection(painter)
           self.draw_component_overlays(painter)

       def keyPressEvent(self, event):
           # Handle keyboard input for editing
           pass

       def mousePressEvent(self, event):
           # Handle mouse input based on current drawing mode
           pass