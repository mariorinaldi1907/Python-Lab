"""
Date: 2026-08-28
Built a ray casting algorithm to check if points lie inside arbitrary polygons — handles convex, concave, and even self-intersecting shapes.
"""

#!/usr/bin/env python3
"""
Point-in-polygon checker using the ray casting algorithm.

I needed this for a project where I was working with geographic boundaries,
and didn't want to pull in heavy dependencies. The ray casting method is
elegant: cast a ray from the point to infinity and count intersections with
polygon edges. Odd = inside, even = outside.
"""

from typing import List, Tuple


class Polygon:
    """Represents a polygon defined by a list of vertices."""
    
    def __init__(self, vertices: List[Tuple[float, float]]):
        """
        Initialize a polygon with vertices.
        
        Args:
            vertices: List of (x, y) tuples defining the polygon vertices.
                     Should be in order (clockwise or counter-clockwise).
        """
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices")
        self.vertices = vertices
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """
        Check if a point is inside the polygon using ray casting.
        
        The algorithm casts a horizontal ray from the point to the right
        and counts how many times it intersects with polygon edges.
        Odd count = inside, even count = outside.
        
        Args:
            point: (x, y) tuple representing the point to check
            
        Returns:
            True if point is inside the polygon, False otherwise
        """
        x, y = point
        n = len(self.vertices)
        inside = False
        
        # Check intersections with each edge
        p1x, p1y = self.vertices[0]
        for i in range(1, n + 1):
            p2x, p2y = self.vertices[i % n]
            
            # Check if the ray intersects this edge
            # The ray goes horizontally to the right from our point
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        # Calculate the x-intersection of the ray with this edge
                        # This is where the horizontal line at height y crosses the edge
                        if p1y != p2y:
                            x_intersection = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        
                        # If edge is vertical or point is to the left of intersection
                        if p1x == p2x or x <= x_intersection:
                            inside = not inside
            
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate the axis-aligned bounding box of the polygon.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        return (min(xs), min(ys), max(xs), max(ys))
    
    def area(self) -> float:
        """
        Calculate the area of the polygon using the shoelace formula.
        
        Returns:
            The area of the polygon (always positive)
        """
        n = len(self.vertices)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i][0] * self.vertices[j][1]
            area -= self.vertices[j][0] * self.vertices[i][1]
        
        return abs(area) / 2.0


def generate_test_grid(bbox: Tuple[float, float, float, float], 
                       resolution: int = 10) -> List[Tuple[float, float]]:
    """
    Generate a grid of test points within a bounding box.
    
    Args:
        bbox: (min_x, min_y, max_x, max_y) bounding box
        resolution: Number of points per dimension
        
    Returns:
        List of (x, y) points forming a grid
    """
    min_x, min_y, max_x, max_y = bbox
    points = []
    
    for i in range(resolution):
        for j in range(resolution):
            x = min_x + (max_x - min_x) * i / (resolution - 1)
            y = min_y + (max_y - min_y) * j / (resolution - 1)
            points.append((x, y))
    
    return points


def visualize_polygon_ascii(polygon: Polygon, width: int = 40, height: int = 20):
    """
    Create a simple ASCII visualization of the polygon and which points are inside.
    
    This is just for fun — wanted a way to visually verify the algorithm works
    without needing matplotlib or anything fancy.
    
    Args:
        polygon: The polygon to visualize
        width: Width of the ASCII canvas
        height: Height of the ASCII canvas
    """
    bbox = polygon.get_bounding_box()
    min_x, min_y, max_x, max_y = bbox
    
    # Add some padding
    padding = 0.1
    x_range = max_x - min_x
    y_range = max_y - min_y
    min_x -= x_range * padding
    max_x += x_range * padding
    min_y -= y_range * padding
    max_y += y_range * padding
    
    # Create canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Fill in points
    for row in range(height):
        for col in range(width):
            x = min_x + (max_x - min_x) * col / (width - 1)
            y = max_y - (max_y - min_y) * row / (height - 1)  # Flip y-axis for display
            
            if polygon.contains_point((x, y)):
                canvas[row][col] = '█'
            else:
                canvas[row][col] = '·'
    
    # Print the canvas
    for row in canvas:
        print(''.join(row))


if __name__ == "__main__":
    print("Point-in-Polygon Checker Demo\n" + "="*50 + "\n")
    
    # Test 1: Simple square
    print("Test 1: Square polygon")
    square = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)])
    print(f"Area: {square.area()}")
    print(f"Point (2, 2) inside? {square.contains_point((2, 2))}")
    print(f"Point (5, 5) inside? {square.contains_point((5, 5))}")
    print("\nVisualization:")
    visualize_polygon_ascii(square, width=30, height=15)
    
    # Test 2: Concave polygon (L-shape)
    print("\n" + "="*50)
    print("Test 2: L-shaped (concave) polygon")
    l_shape = Polygon([(0, 0), (3, 0), (3, 2), (1, 2), (1, 3), (0, 3)])
    print(f"Area: {l_shape.area()}")
    print(f"Point (0.5, 0.5) inside? {l_shape.contains_point((0.5, 0.5))}")
    print(f"Point (2, 2.5) inside? {l_shape.contains_point((2, 2.5))}")
    print("\nVisualization:")
    visualize_polygon_ascii(l_shape, width=30, height=15)
    
    # Test 3: Triangle
    print("\n" + "="*50)
    print("Test 3: Triangle")
    triangle = Polygon([(1, 1), (5, 1), (3, 4)])
    print(f"Area: {triangle.area()}")
    print(f"Point (3, 2) inside? {triangle.contains_point((3, 2))}")
    print(f"Point (1, 3) inside? {triangle.contains_point((1, 3))}")
    print("\nVisualization:")
    visualize_polygon_ascii(triangle, width=30, height=15)