"""Spatial Analysis Module."""

from typing import Any


class SpatialIndex:
    def __init__(self, grid_width: int, grid_height: int, cell_size: int = 5):
        """Initialize a new SpatialIndex.

        Parameters
        ----------
        grid_width : int
            The width of the spatial index in pixels.
        grid_height : int
            The height of the spatial index in pixels.
        cell_size : int, optional
            The size of the grid cells in pixels. Defaults to 5.

        Notes:
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
        """Add a component to the spatial index.

        Args:
            component: Component object with bounding box property
        """
        bb = self._get_bounding_box(component)
        if not bb:
            return

        x1, y1, x2, y2 = map(int, bb)  # Ensure all bounds are integers

        # Calculate grid cells that the component overlaps
        cell_x1 = max(0, x1 // self.cell_size)
        cell_y1 = max(0, y1 // self.cell_size)
        cell_x2 = min(self.index_width - 1, x2 // self.cell_size)
        cell_y2 = min(self.index_height - 1, y2 // self.cell_size)

        # Add component to all overlapping cells
        for cy in range(int(cell_y1), int(cell_y2 + 1)):
            for cx in range(int(cell_x1), int(cell_x2 + 1)):
                self.spatial_grid[cy][cx].add(component.id)

    def query_point(self, x: float, y: float) -> set[str]:
        """Query components at a specific point.

        Args:
            x: X coordinate to query
            y: Y coordinate to query

        Returns:
            Set of component IDs at the queried point
        """
        x, y = int(x), int(y)
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return set()

        cell_x = x // self.cell_size
        cell_y = y // self.cell_size

        return self.spatial_grid[cell_y][cell_x].copy()

    def query_region(self, x1: float, y1: float, x2: float, y2: float) -> set[str]:
        """Query components that overlap with the specified region.

        Args:
            x1: Left coordinate of query region
            y1: Top coordinate of query region
            x2: Right coordinate of query region
            y2: Bottom coordinate of query region

        Returns:
            Set of component IDs that might intersect with the region
        """
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
        """Rebuild the spatial index with the provided components.

        Args:
            components: List of components to rebuild the index with
        """
        # Clear the spatial grid
        self.spatial_grid = [
            [set() for _ in range(self.index_width)] for _ in range(self.index_height)
        ]

        # Add all components
        for component in components:
            self.add_component(component)

    def _get_bounding_box(self, component: Any) -> tuple[int, int, int, int] | None:
        """Get the bounding box of a component.

        Args:
            component: Component object with bounding box property

        Returns:
            Tuple of (x1, y1, x2, y2) coordinates or None if no bounding box exists
        """
        if "refined_bounding_box" in component.properties:
            return component.properties["refined_bounding_box"]
        if "bounding_box" in component.properties:
            return component.properties["bounding_box"]
        return None
