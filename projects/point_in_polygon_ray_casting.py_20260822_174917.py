"""
Date: 2026-08-22
Built a point-in-polygon detector using ray casting because I needed to check if coordinates fall inside arbitrary shapes without pulling in shapely or numpy.
"""

#!/usr/bin/env python3
"""
Point-in-Polygon Detection using Ray Casting Algorithm

I needed a simple way to check if points are inside polygons for a personal mapping
project. Ray casting is elegant: shoot a ray from the point to infinity and count
how many polygon edges it crosses. Odd = inside, even = outside.
"""

from typing import List, Tuple
import random


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
    
    Uses ray casting to determine if points are inside the polygon.
    The algorithm shoots a horizontal ray from the test point to infinity
    and counts edge intersections.
    """
    
    def __init__(self, vertices: List[Tuple[float, float]]):
        """
        Initialize a polygon with vertices.
        
        Args:
            vertices: List of (x, y) tuples defining the polygon boundary.
                     Should form a closed shape (last connects to first).
        """
        if len(vertices) < 3:
            raise ValueError("Polygon needs at least 3 vertices")
        
        self.vertices = [Point(x, y) for x, y in vertices]
        self.num_vertices = len(self.vertices)
    
    def contains_point(self, test_point: Tuple[float, float]) -> bool:
        """
        Check if a point is inside the polygon using ray casting.
        
        The ray casting algorithm works by extending a ray from the test point
        to infinity (I use horizontal right direction) and counting how many
        times it crosses polygon edges. Odd crossings = inside, even = outside.
        
        Args:
            test_point: (x, y) tuple of the point to test
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        px, py = test_point
        inside = False
        
        # Check each edge of the polygon
        j = self.num_vertices - 1  # Start with last vertex
        
        for i in range(self.num_vertices):
            xi, yi = self.vertices[i].x, self.vertices[i].y
            xj, yj = self.vertices[j].x, self.vertices[j].y
            
            # Check if the horizontal ray from (px, py) crosses the edge (i, j)
            # This is the tricky part: we need to check if the ray intersects
            # the edge, accounting for edge cases where the ray passes through
            # a vertex or is collinear with an edge
            
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            
            j = i
        
        return inside
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate the axis-aligned bounding box of the polygon.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        return (min(xs), min(ys), max(xs), max(ys))
    
    def area(self) -> float:
        """
        Calculate polygon area using the shoelace formula.
        
        This is a bonus method I added because once you have vertices,
        computing area is straightforward and useful.
        """
        area_sum = 0.0
        j = self.num_vertices - 1
        
        for i in range(self.num_vertices):
            area_sum += (self.vertices[j].x + self.vertices[i].x) * \
                       (self.vertices[j].y - self.vertices[i].y)
            j = i
        
        return abs(area_sum / 2.0)


def generate_test_points(bbox: Tuple[float, float, float, float], 
                        count: int) -> List[Tuple[float, float]]:
    """
    Generate random test points within a bounding box.
    
    Args:
        bbox: (min_x, min_y, max_x, max_y) bounding box
        count: Number of points to generate
        
    Returns:
        List of (x, y) tuples
    """
    min_x, min_y, max_x, max_y = bbox
    points = []
    
    for _ in range(count):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        points.append((x, y))
    
    return points


if __name__ == "__main__":
    # Demo with a simple star polygon - good test because it's concave
    print("=== Point-in-Polygon Ray Casting Demo ===\n")
    
    # Create a 5-pointed star centered roughly at origin
    star_vertices = [
        (0, 10),      # top point
        (2, 3),       # inner right
        (9, 3),       # outer right
        (4, -2),      # inner bottom right
        (6, -9),      # bottom right point
        (0, -5),      # inner bottom
        (-6, -9),     # bottom left point
        (-4, -2),     # inner bottom left
        (-9, 3),      # outer left
        (-2, 3),      # inner left
    ]
    
    star = Polygon(star_vertices)
    print(f"Created star polygon with {len(star_vertices)} vertices")
    print(f"Star area: {star.area():.2f} square units")
    
    bbox = star.get_bounding_box()
    print(f"Bounding box: ({bbox[0]:.1f}, {bbox[1]:.1f}) to ({bbox[2]:.1f}, {bbox[3]:.1f})\n")
    
    # Test some specific points
    test_cases = [
        (0, 0, "center"),
        (0, 8, "near top point"),
        (7, 2, "outer right area"),
        (0, -7, "bottom spike"),
        (-10, -10, "far outside"),
    ]
    
    print("Testing specific points:")
    for x, y, description in test_cases:
        inside = star.contains_point((x, y))
        status = "INSIDE" if inside else "OUTSIDE"
        print(f"  ({x:4}, {y:4}) [{description:20s}] -> {status}")
    
    # Generate random points and classify them
    print("\nRandom point classification:")
    random.seed(42)  # Reproducible results
    test_points = generate_test_points(bbox, 20)
    
    inside_count = 0
    for point in test_points:
        if star.contains_point(point):
            inside_count += 1
    
    print(f"  Generated 20 random points in bounding box")
    print(f"  {inside_count} points inside star, {20 - inside_count} outside")
    print(f"  Fill ratio: {inside_count / 20 * 100:.1f}%")