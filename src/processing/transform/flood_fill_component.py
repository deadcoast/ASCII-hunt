"""Flood Fill Component Module."""

import numpy as np


def flood_fill_component(grid, start_x, start_y, boundary_chars):
    """Implements the mathematical flood fill algorithm using NumPy operations.

    Parameters
    ----------
    grid : 2D numpy array of characters
        The grid to search for connected components.
    start_x : int
        The x-coordinate of the point to start the search from.
    start_y : int
        The y-coordinate of the point to start the search from.
    boundary_chars : set of characters
        The set of characters that mark the boundary of a component.

    Returns:
    -------
    component : dict
        A dictionary containing information about the connected component
        found, including the interior points, boundary points, bounding box,
        width, and height. If no component is found, None is returned.
    """
    height, width = grid.shape
    visited = np.zeros((height, width), dtype=bool)

    # Initialize for vectorized operations
    interior = {(start_x, start_y)}
    boundary = set()
    queue = [(start_x, start_y)]
    visited[start_y, start_x] = True

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while queue:
        x, y = queue.pop(0)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny, nx] in boundary_chars:
                    boundary.add((nx, ny))
                elif not visited[ny, nx]:
                    visited[ny, nx] = True
                    interior.add((nx, ny))
                    queue.append((nx, ny))

    # Calculate component properties using NumPy operations
    if boundary:
        boundary_array = np.array(list(boundary))
        min_x, min_y = boundary_array.min(axis=0)
        max_x, max_y = boundary_array.max(axis=0)

        return {
            "interior": interior,
            "boundary": boundary,
            "bounding_box": (min_x, min_y, max_x, max_y),
            "width": max_x - min_x + 1,
            "height": max_y - min_y + 1,
        }

    return None
