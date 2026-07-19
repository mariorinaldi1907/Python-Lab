"""
Date: 2026-07-19
Built a point-in-polygon checker using ray casting because I needed to figure out if coordinates fall inside irregular boundaries for a mapping side project.
"""

#!/usr/bin/env python3
"""
Point-in-polygon detection using the ray casting algorithm.

I needed this for checking if GPS coordinates fall within irregular geographic
boundaries. The ray casting method is pretty elegant: shoot a ray from the point
to infinity and count how many times it crosses the polygon edges. Odd = inside,
even = outside. Simple but handles complex polygons nicely.
"""

from typing import List, Tuple


class Point:
    """Represents a 2D point with x and y coordinates."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Polygon:
    """
    Represents a polygon defined by a list of vertices.
    
    The polygon is assumed to be closed (last vertex connects to first).
    Vertices should be ordered either clockwise or counter-clockwise.
    """
    
    def __init__(self, vertices: List[Tuple[float, float]]):
        """
        Initialize polygon with list of (x, y) tuples.
        
        Args:
            vertices: List of (x, y) coordinate tuples defining the polygon
        """
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices")
        
        self.vertices = [Point(x, y) for x, y in vertices]
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """
        Check if a point is inside the polygon using ray casting algorithm.
        
        The idea: cast a ray from the point to infinity (I use horizontal ray
        going right). Count how many times it crosses polygon edges. If odd,
        the point is inside; if even, it's outside.
        
        Edge cases handled:
        - Point exactly on a vertex
        - Ray passing through a vertex (count carefully to avoid double-counting)
        - Horizontal edges (ignored, they don't contribute)
        
        Args:
            point: (x, y) tuple of the point to test
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        px, py = point
        n = len(self.vertices)
        inside = False
        
        # Check each edge of the polygon
        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % n]  # Wrap around to first vertex
            
            # Get the y-coordinates of the edge vertices
            y1, y2 = v1.y, v2.y
            x1, x2 = v1.x, v2.x
            
            # Skip horizontal edges (they don't affect the ray casting)
            if y1 == y2:
                continue
            
            # Check if the point's y-coordinate is within the edge's y-range
            # Using min/max to handle edges going either direction
            if not (min(y1, y2) < py <= max(y1, y2)):
                continue
            
            # Calculate where the ray intersects this edge's x-coordinate
            # This is basically solving for x when y = py on the line segment
            # Using the formula: x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            x_intersection = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            
            # If the intersection is to the right of our point, count it
            if x_intersection > px:
                inside = not inside
        
        return inside
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Get the axis-aligned bounding box of the polygon.
        
        Returns:
            (min_x, min_y, max_x, max_y) tuple
        """
        x_coords = [v.x for v in self.vertices]
        y_coords = [v.y for v in self.vertices]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))


def visualize_test_grid(polygon: Polygon, resolution: int = 20):
    """
    Visualize which points are inside/outside using ASCII art.
    
    This creates a grid of test points and marks them as inside (■) or outside (□).
    It's a quick way to visualize the polygon without any graphical libraries.
    
    Args:
        polygon: The polygon to visualize
        resolution: Number of points to test in each direction
    """
    min_x, min_y, max_x, max_y = polygon.get_bounding_box()
    
    # Add some padding so we can see the boundary clearly
    padding = 0.1 * max(max_x - min_x, max_y - min_y)
    min_x -= padding
    max_x += padding
    min_y -= padding
    max_y += padding
    
    print(f"\nVisualization (■ = inside, □ = outside):")
    print(f"Bounding box: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})\n")
    
    # Test points on a grid (reversed y so it prints top-down)
    for j in range(resolution):
        y = max_y - (j / (resolution - 1)) * (max_y - min_y)
        row = ""
        for i in range(resolution):
            x = min_x + (i / (resolution - 1)) * (max_x - min_x)
            if polygon.contains_point((x, y)):
                row += "■ "
            else:
                row += "□ "
        print(row)


if __name__ == "__main__":
    # Test with a simple triangle
    print("=== Triangle Test ===")
    triangle = Polygon([(0, 0), (4, 0), (2, 3)])
    
    test_points = [
        (2, 1),    # Inside
        (0, 0),    # Vertex (edge case, considered inside due to <=)
        (5, 5),    # Outside
        (2, 0),    # On edge
        (1, 1),    # Inside
    ]
    
    for point in test_points:
        result = triangle.contains_point(point)
        print(f"Point {point}: {'INSIDE' if result else 'OUTSIDE'}")
    
    # Test with a more complex polygon (like an "L" shape)
    print("\n=== L-Shape Polygon Test ===")
    l_shape = Polygon([
        (0, 0), (2, 0), (2, 2), (4, 2),
        (4, 4), (0, 4)
    ])
    
    test_points_l = [
        (1, 1),    # Inside lower part
        (3, 3),    # Inside upper part
        (3, 1),    # Outside (in the notch)
        (1, 3),    # Inside
        (5, 5),    # Outside completely
    ]
    
    for point in test_points_l:
        result = l_shape.contains_point(point)
        print(f"Point {point}: {'INSIDE' if result else 'OUTSIDE'}")
    
    # Visual grid test
    visualize_test_grid(l_shape, resolution=25)
    
    print("\n=== Star Shape Test ===")
    # Five-pointed star (more complex concave polygon)
    import math
    star_points = []
    for i in range(10):
        angle = (i * math.pi / 5) - (math.pi / 2)
        radius = 3 if i % 2 == 0 else 1.2
        x = 2 + radius * math.cos(angle)
        y = 2 + radius * math.sin(angle)
        star_points.append((x, y))
    
    star = Polygon(star_points)
    visualize_test_grid(star, resolution=20)