"""
Date: 2026-07-08
Built a convex hull finder using the gift wrapping algorithm because I wanted to visualize how Jarvis march works in 2D space.
"""

"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I wanted a clean implementation of convex hull that doesn't rely on scipy
or any fancy libraries. The gift wrapping approach is intuitive - you start
from the leftmost point and keep "wrapping" counterclockwise until you get back.
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
        """Check equality with a small epsilon for floating point comparison."""
        if not isinstance(other, Point):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
    
    def __hash__(self):
        return hash((round(self.x, 10), round(self.y, 10)))


def orientation(p: Point, q: Point, r: Point) -> int:
    """
    Determine the orientation of the ordered triplet (p, q, r).
    
    Returns:
        0 if p, q, r are collinear
        1 if clockwise
        2 if counterclockwise
    
    This uses the cross product approach - if the cross product is positive,
    we're turning left (counterclockwise), if negative, turning right (clockwise).
    """
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    
    if abs(val) < 1e-10:  # Using epsilon for floating point comparison
        return 0
    return 1 if val > 0 else 2


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared distance between two points (avoiding sqrt for performance)."""
    return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2


def gift_wrapping_convex_hull(points: List[Point]) -> List[Point]:
    """
    Find the convex hull using the gift wrapping (Jarvis march) algorithm.
    
    The idea is simple: start from the leftmost point, then keep finding the
    next point that makes the smallest left turn. It's O(nh) where h is the
    number of hull points, so great for small hulls.
    
    Args:
        points: List of Point objects
        
    Returns:
        List of Points forming the convex hull in counterclockwise order
    """
    n = len(points)
    
    # Edge cases - need at least 3 points for a hull
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (break ties with lowest y)
    leftmost_idx = 0
    for i in range(1, n):
        if points[i].x < points[leftmost_idx].x:
            leftmost_idx = i
        elif points[i].x == points[leftmost_idx].x and points[i].y < points[leftmost_idx].y:
            leftmost_idx = i
    
    hull = []
    current = leftmost_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counterclockwise point from points[current]
        next_point = (current + 1) % n
        
        for i in range(n):
            if i == current:
                continue
            
            orient = orientation(points[current], points[next_point], points[i])
            
            # If i is more counterclockwise than next_point, update next_point
            if orient == 2:
                next_point = i
            # If collinear, pick the farthest one (to handle collinear points properly)
            elif orient == 0:
                if distance_squared(points[current], points[i]) > \
                   distance_squared(points[current], points[next_point]):
                    next_point = i
        
        current = next_point
        
        # We've wrapped around back to the starting point
        if current == leftmost_idx:
            break
    
    return hull


def point_in_convex_polygon(point: Point, hull: List[Point]) -> bool:
    """
    Check if a point is inside a convex polygon.
    
    For convex polygons, a point is inside if it's on the same side of all edges.
    I check this by ensuring the point is always to the left (counterclockwise)
    of each edge when traversing the hull.
    """
    if len(hull) < 3:
        return False
    
    # Check orientation with respect to each edge
    for i in range(len(hull)):
        next_i = (i + 1) % len(hull)
        if orientation(hull[i], hull[next_i], point) == 1:  # Clockwise = outside
            return False
    
    return True


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    This is a neat trick I learned - you sum up (x_i * y_{i+1} - x_{i+1} * y_i)
    and divide by 2. Works for any simple polygon.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i].x * hull[j].y
        area -= hull[j].x * hull[i].y
    
    return abs(area) / 2.0


if __name__ == "__main__":
    # Demo with some test points - creating a scattered set
    test_points = [
        Point(0, 3),
        Point(2, 2),
        Point(1, 1),
        Point(2, 1),
        Point(3, 0),
        Point(0, 0),
        Point(3, 3),
        Point(1, 2),  # This one should be interior
        Point(2, 0.5),  # This too
    ]
    
    print("Finding convex hull for these points:")
    for i, p in enumerate(test_points):
        print(f"  {i}: {p}")
    
    hull = gift_wrapping_convex_hull(test_points)
    
    print(f"\nConvex hull has {len(hull)} vertices:")
    for p in hull:
        print(f"  {p}")
    
    area = hull_area(hull)
    print(f"\nHull area: {area:.2f}")
    
    # Test point containment
    test_interior = Point(1.5, 1.5)
    test_exterior = Point(5, 5)
    
    print(f"\nPoint containment tests:")
    print(f"  {test_interior} inside hull: {point_in_convex_polygon(test_interior, hull)}")
    print(f"  {test_exterior} inside hull: {point_in_convex_polygon(test_exterior, hull)}")
    
    # Edge case: collinear points
    print("\n--- Testing with collinear points ---")
    collinear_points = [
        Point(0, 0),
        Point(1, 1),
        Point(2, 2),
        Point(0, 2),
        Point(2, 0),
    ]
    
    collinear_hull = gift_wrapping_convex_hull(collinear_points)
    print(f"Hull with collinear points:")
    for p in collinear_hull:
        print(f"  {p}")