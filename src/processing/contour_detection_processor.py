import numpy as np


class ContourDetectionProcessor:
    def __init__(self):
        pass

    def process(self, components, context=None):
        """Process components to detect precise contours."""
        if context is None:
            context = {}

        # Ensure we have a grid available
        if "grid" not in context:
            raise ValueError("Grid not available in context")

        grid = context["grid"]

        # Process each component
        for component in components:
            # Create a binary mask for this component
            mask = self._create_component_mask(component, grid)

            # Detect contours in the mask
            contours = self._detect_contours(mask)

            # Add contours to component
            component["contours"] = contours

            # Refine bounding box based on contours
            if contours:
                refined_box = self._refine_bounding_box(contours)
                component["refined_bounding_box"] = refined_box

        # Store in context for other stages
        context["contour_detection_results"] = components

        return components

    def _create_component_mask(self, component, grid):
        """Create a binary mask for a component."""
        # Get bounding box
        min_x, min_y, max_x, max_y = component["bounding_box"]

        # Create mask
        mask = np.zeros((max_y - min_y + 3, max_x - min_x + 3), dtype=np.uint8)

        # Fill mask with boundary points
        for x, y in component["boundary_points"]:
            mask[y - min_y + 1, x - min_x + 1] = 255

        return mask

    def _detect_contours(self, mask):
        """Detect contours in a binary mask using OpenCV."""
        try:
            import cv2

            # Apply morphological operations to clean up the mask
            kernel = np.ones((2, 2), np.uint8)
            mask_processed = cv2.dilate(mask, kernel, iterations=1)

            # Find contours
            contours, hierarchy = cv2.findContours(
                mask_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Convert contours to a serializable format
            serializable_contours = []
            for contour in contours:
                points = []
                for point in contour:
                    x, y = point[0]
                    points.append((int(x), int(y)))
                serializable_contours.append(points)

            return serializable_contours
        except ImportError:
            # Fall back to simpler method if OpenCV not available
            return self._detect_contours_simple(mask)

    def _detect_contours_simple(self, mask):
        """Simplified contour detection without OpenCV."""
        height, width = mask.shape
        visited = np.zeros_like(mask, dtype=bool)
        contours = []

        # Scan for boundary points
        for y in range(height):
            for x in range(width):
                if mask[y, x] > 0 and not visited[y, x]:
                    # Start of a new contour
                    contour = []
                    current_x, current_y = x, y
                    direction = 0  # 0: right, 1: down, 2: left, 3: up

                    # Trace the contour
                    for _ in range(width * height):  # Safety limit
                        contour.append((current_x, current_y))
                        visited[current_y, current_x] = True

                        # Try to turn right first (relative to current direction)
                        turned = False
                        for _ in range(4):  # Try all directions
                            new_direction = (direction - 1) % 4
                            dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][new_direction]
                            new_x, new_y = current_x + dx, current_y + dy

                            if (
                                0 <= new_x < width
                                and 0 <= new_y < height
                                and mask[new_y, new_x] > 0
                                and not visited[new_y, new_x]
                            ):
                                current_x, current_y = new_x, new_y
                                direction = new_direction
                                turned = True
                                break

                            direction = (direction + 1) % 4

                        if not turned:
                            break

                        # Check if we've returned to start
                        if current_x == x and current_y == y:
                            break

                    if len(contour) > 2:
                        contours.append(contour)

        return contours

    def _refine_bounding_box(self, contours):
        """Refine the bounding box based on contours."""
        if not contours:
            return None

        # Flatten all contours
        all_points = [point for contour in contours for point in contour]

        # Find min/max coordinates
        x_coords = [x for x, y in all_points]
        y_coords = [y for x, y in all_points]

        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)

        return (min_x, min_y, max_x, max_y)
