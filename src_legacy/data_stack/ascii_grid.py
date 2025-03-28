import numpy as np


class ASCIIGrid:
    def __init__(self, data=None, width=0, height=0):
        """Initialize a new ASCIIGrid instance.

        Parameters
        ----------
        data : str or numpy.ndarray, optional
            Existing data to initialize the grid from. If None, an empty grid of size
            (width, height) is created.
        width : int, optional
            Width of the grid if data is None.
        height : int, optional
            Height of the grid if data is None.

        """
        if data is not None:
            # Initialize from existing data
            if isinstance(data, str):
                # Parse string into grid
                lines = data.splitlines()
                self.height = len(lines)
                self.width = max(len(line) for line in lines) if self.height > 0 else 0
                self._grid = np.zeros((self.height, self.width), dtype=np.str_)

                for y, line in enumerate(lines):
                    for x, char in enumerate(line):
                        self._grid[y, x] = char
            elif isinstance(data, np.ndarray):
                # Use NumPy array directly
                self._grid = data
                self.height, self.width = data.shape
        else:
            # Create empty grid of specified size
            self._grid = np.full((height, width), " ", dtype=np.str_)
            self.height = height
            self.width = width

        # Create views for efficient processing
        self._char_mapping = None
        self._line_indices = None
        self._boundary_mask = None

    def get_char(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y, x]
        return None

    def set_char(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y, x] = char

            # Invalidate cached views
            self._char_mapping = None
            self._line_indices = None
            self._boundary_mask = None

    def get_row(self, y):
        if 0 <= y < self.height:
            return self._grid[y, :]
        return None

    def get_column(self, x):
        if 0 <= x < self.width:
            return self._grid[:, x]
        return None

    def get_region(self, x1, y1, x2, y2):
        x1 = max(0, min(x1, self.width - 1))
        y1 = max(0, min(y1, self.height - 1))
        x2 = max(0, min(x2, self.width - 1))
        y2 = max(0, min(y2, self.height - 1))

        if x1 <= x2 and y1 <= y2:
            return self._grid[y1 : y2 + 1, x1 : x2 + 1]
        return None

    def get_boundary_mask(self):
        """Get a mask indicating boundary characters."""
        if self._boundary_mask is None:
            # Create boundary character set
            boundary_chars = set("┌┐└┘│─┬┴├┤┼╔╗╚╝║═╦╩╠╣╬┏┓┗┛┃━┳┻┣┫╋╭╮╰╯")

            # Create mask using vectorized operations
            char_array = np.array(list(boundary_chars))
            self._boundary_mask = np.isin(self._grid, char_array)

        return self._boundary_mask

    def get_character_density_map(self):
        """Get a map of character densities for content analysis."""
        # Non-whitespace density
        density = np.zeros((self.height, self.width))

        # Use sliding window to calculate local density
        window_size = 3
        for y in range(self.height):
            for x in range(self.width):
                # Calculate window boundaries
                x1 = max(0, x - window_size // 2)
                x2 = min(self.width - 1, x + window_size // 2)
                y1 = max(0, y - window_size // 2)
                y2 = min(self.height - 1, y + window_size // 2)

                # Calculate density in window
                window = self._grid[y1 : y2 + 1, x1 : x2 + 1]
                count = np.sum(window != " ")
                total = window.size

                density[y, x] = count / total if total > 0 else 0

        return density

    def to_numpy(self):
        """Get the NumPy array representation of the grid."""
        return self._grid.copy()

    def to_string(self):
        """Convert grid to a string representation."""
        lines = []
        for y in range(self.height):
            line = "".join(self._grid[y, :])
            lines.append(line)
        return "\n".join(lines)
