from tkinter import Canvas, Event, Frame, Tk
from typing import Any

from src.engine.modeling.drawing_mode import DrawingMode


class TkinterAdapter:
    """Adapter class for Tkinter-specific functionality."""

    def __init__(self, root: Tk | None = None) -> None:
        self.root = root or Tk()
        self.canvas: Canvas | None = None
        self.frame: Frame | None = None
        self.current_mode: DrawingMode = DrawingMode.get_default()
        self.grid_size: tuple[int, int] = (80, 24)  # Default grid size
        self.cell_size: int = 20  # Default cell size in pixels

    def initialize(self) -> None:
        """Initialize the Tkinter interface."""
        self.frame = Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        self.canvas = Canvas(
            self.frame,
            width=self.grid_size[0] * self.cell_size,
            height=self.grid_size[1] * self.cell_size,
        )
        self.canvas.pack(expand=True)

    def set_mode(self, mode: DrawingMode) -> None:
        """Set the current drawing mode."""
        self.current_mode = mode

    def handle_click(self, event: Event) -> dict[str, Any]:
        """Handle mouse click events."""
        if not self.canvas:
            return {}

        x = event.x // self.cell_size
        y = event.y // self.cell_size

        return {"x": x, "y": y, "mode": self.current_mode, "type": event.type}

    def update_grid(self, grid: list[list[str]]) -> None:
        """Update the grid display."""
        if not self.canvas:
            return

        self.canvas.delete("all")
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell.strip():
                    self.draw_cell(x, y, cell)

    def draw_cell(self, x: int, y: int, char: str) -> None:
        """Draw a single cell on the canvas."""
        if not self.canvas:
            return

        x1 = x * self.cell_size
        y1 = y * self.cell_size

        self.canvas.create_text(
            x1 + self.cell_size / 2,
            y1 + self.cell_size / 2,
            text=char,
            font=("Courier", int(self.cell_size * 0.8)),
        )

    def get_grid_size(self) -> tuple[int, int]:
        """Get the current grid size."""
        return self.grid_size

    def set_grid_size(self, width: int, height: int) -> None:
        """Set the grid size."""
        self.grid_size = (width, height)
        if self.canvas:
            self.canvas.config(
                width=width * self.cell_size, height=height * self.cell_size
            )


def create_tkinter_adapter() -> TkinterAdapter:
    """Create and return a new TkinterAdapter instance."""
    return TkinterAdapter()
