"""
Date: 2026-06-22
Built a convex hull calculator using the gift wrapping (Jarvis march) algorithm because I needed to find boundaries of point clouds for a side project.
"""

"""
Convex Hull using Gift Wrapping Algorithm (Jarvis March)

I chose gift wrapping over Graham scan because it's more intuitive to visualize
and performs better when the hull has few vertices (O(nh) vs O(n log n)).
Plus it was fun to implement the "wrapping" logic.
"""

from typing import List, Tuple
import math


class Point:
    """Represents a 2D point with x and y coordinates."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


def orientation(p: Point, q: Point, r: Point) -> int:
    """
    Calculate the orientation of three points.
    
    Returns:
        0 if collinear
        1 if clockwise
        2 if counterclockwise
    
    This is the core geometric primitive - uses the cross product
    to determine which way we're turning.
    """
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    
    if abs(val) < 1e-10:  # floating point tolerance
        return 0
    return 1 if val > 0 else 2


def distance_squared(p: Point, q: Point) -> float:
    """Calculate squared distance between two points (avoids sqrt for speed)."""
    return (p.x - q.x) ** 2 + (p.y - q.y) ** 2


def convex_hull(points: List[Point]) -> List[Point]:
    """
    Compute convex hull using gift wrapping algorithm.
    
    The idea: start from leftmost point, then keep "wrapping" counterclockwise
    by picking the point that makes the smallest left turn.
    
    Args:
        points: List of Point objects
    
    Returns:
        List of Point objects forming the convex hull in counterclockwise order
    """
    n = len(points)
    
    # Need at least 3 points for a hull
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (our starting point)
    leftmost = min(points, key=lambda p: (p.x, p.y))
    
    hull = []
    current = leftmost
    
    while True:
        hull.append(current)
        
        # Find the most counterclockwise point from current
        next_point = points[0]
        
        for candidate in points[1:]:
            if candidate == current:
                continue
            
            # If next_point is same as current, or candidate is more counterclockwise
            if next_point == current:
                next_point = candidate
                continue
            
            orient = orientation(current, next_point, candidate)
            
            # If candidate is more counterclockwise, use it
            if orient == 2:
                next_point = candidate
            # If collinear, pick the farther one (handles collinear points on hull)
            elif orient == 0:
                if distance_squared(current, candidate) > distance_squared(current, next_point):
                    next_point = candidate
        
        current = next_point
        
        # We've wrapped back to the start
        if current == leftmost:
            break
    
    return hull


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Shoots a ray from the point to infinity and counts intersections.
    Odd = inside, Even = outside. Classic computer graphics trick.
    """
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i].x, polygon[i].y
        xj, yj = polygon[j].x, polygon[j].y
        
        # Check if point is on a horizontal edge (edge case, literally)
        if ((yi > point.y) != (yj > point.y)) and \
           (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside


def polygon_area(polygon: List[Point]) -> float:
    """
    Calculate area of a polygon using the shoelace formula.
    
    I love this formula - it's like magic how it just works.
    """
    n = len(polygon)
    area = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i].x * polygon[j].y
        area -= polygon[j].x * polygon[i].y
    
    return abs(area) / 2.0


if __name__ == "__main__":
    print("=== Convex Hull Demo ===\n")
    
    # Create a point cloud - some inside, some on the boundary
    test_points = [
        Point(0, 3),
        Point(1, 1),
        Point(2, 2),
        Point(4, 4),
        Point(0, 0),
        Point(1, 2),
        Point(3, 1),
        Point(3, 3),
        Point(2, 1),  # interior point
    ]
    
    print(f"Input points ({len(test_points)} total):")
    for p in test_points:
        print(f"  {p}")
    
    print("\nComputing convex hull...")
    hull = convex_hull(test_points)
    
    print(f"\nConvex hull vertices ({len(hull)} points):")
    for p in hull:
        print(f"  {p}")
    
    # Calculate and display the hull area
    area = polygon_area(hull)
    print(f"\nHull area: {area:.2f} square units")
    
    # Test point containment
    print("\n=== Point-in-Polygon Tests ===")
    test_queries = [
        Point(2, 2),    # should be inside
        Point(5, 5),    # should be outside
        Point(0, 0),    # on boundary
    ]
    
    for query in test_queries:
        result = point_in_polygon(query, hull)
        status = "INSIDE" if result else "OUTSIDE"
        print(f"{query} is {status} the hull")