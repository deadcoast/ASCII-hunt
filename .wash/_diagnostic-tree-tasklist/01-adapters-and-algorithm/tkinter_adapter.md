# Tkinter Adapter

- Implements an adapter pattern for Tkinter GUI framework
- Key class: `TkinterAdapter` providing an interface for GUI operations
- Core functionality:
  - Initializes a Tkinter canvas and frame
  - Manages drawing modes through an enum system (DrawingMode)
  - Handles mouse events with coordinate translation
  - Provides grid rendering and update functionality
  - Includes methods for cell drawing and grid size management
- Factory function: `create_tkinter_adapter()` for creating adapter instances
- Well-structured with clear type hints and docstrings
- Dependencies:
  - Tkinter standard library components
  - Custom drawing mode enum from `..enums.drawing_mode`
- Default configuration:
  - Grid size: 80x24 characters
  - Cell size: 20 pixels
