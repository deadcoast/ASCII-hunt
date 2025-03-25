"""Spatial Analysis Module."""

from typing import Any


class SpatialIndex:
    def __init__(self, grid_width: int, grid_height: int, cell_size: int = 5):
        """
        Initialize a new SpatialIndex.

        This constructor creates a new SpatialIndex instance with a specified size
        and cell size.

        Parameters
        ----------
        grid_width : int
            The width of the spatial index in pixels.
        grid_height : int
            The height of the spatial index in pixels.
        cell_size : int, optional
            The size of the grid cells in pixels. Defaults to 5.

        Notes
        -----
        The spatial index is represented as a 2D array of sets, where each set
        contains the IDs of the components that overlap a particular cell.
        """
        self.grid_width = int(grid_width)
        self.grid_height = int(grid_height)
        self.cell_size = int(cell_size)

        # Calculate grid dimensions for spatial index
        self.index_width = (self.grid_width + self.cell_size - 1) // self.cell_size
        self.index_height = (self.grid_height + self.cell_size - 1) // self.cell_size

        # Initialize spatial grid
        self.spatial_grid: list[list[set[str]]] = [
            [set() for _ in range(self.index_width)] for _ in range(self.index_height)
        ]

    def add_component(self, component: Any) -> None:
        """Add a component to the spatial index."""
        # Get component bounds
        if "bounding_box" not in component.properties:
            return

        bounds = component.properties["bounding_box"]
        x1, y1, x2, y2 = map(int, bounds)  # Ensure all bounds are integers

        # Calculate grid cells that the component overlaps
        cell_x1 = max(0, x1 // self.cell_size)
        cell_y1 = max(0, y1 // self.cell_size)
        cell_x2 = min(self.index_width - 1, x2 // self.cell_size)
        cell_y2 = min(self.index_height - 1, y2 // self.cell_size)

        # Add component to all overlapping cells
        for cy in range(int(cell_y1), int(cell_y2 + 1)):
            for cx in range(int(cell_x1), int(cell_x2 + 1)):
                self.spatial_grid[cy][cx].add(component.id)

    def query_point(self, x: int | float, y: int | float) -> set[str]:
        """Query components at a specific point."""
        x, y = int(x), int(y)
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return set()

        cell_x = x // self.cell_size
        cell_y = y // self.cell_size

        return self.spatial_grid[cell_y][cell_x].copy()

    def query_region(
        self, x1: int | float, y1: int | float, x2: int | float, y2: int | float
    ) -> set[str]:
        """Query components that overlap with the specified region."""
        # Convert inputs to integers and ensure bounds are within grid
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        x1 = max(0, min(x1, self.grid_width - 1))
        y1 = max(0, min(y1, self.grid_height - 1))
        x2 = max(0, min(x2, self.grid_width - 1))
        y2 = max(0, min(y2, self.grid_height - 1))

        # Calculate grid cells that the region overlaps
        cell_x1 = x1 // self.cell_size
        cell_y1 = y1 // self.cell_size
        cell_x2 = min(self.index_width - 1, x2 // self.cell_size)
        cell_y2 = min(self.index_height - 1, y2 // self.cell_size)

        # Collect components from all overlapping cells
        result: set[str] = set()
        for cy in range(int(cell_y1), int(cell_y2 + 1)):
            for cx in range(int(cell_x1), int(cell_x2 + 1)):
                result.update(self.spatial_grid[cy][cx])

        return result

    def rebuild(self, components: list[Any]) -> None:
        """Rebuild the spatial index with the provided components."""
        # Clear the spatial grid
        self.spatial_grid = [
            [set() for _ in range(self.index_width)] for _ in range(self.index_height)
        ]

        # Add all components
        for component in components:
            self.add_component(component)
