"""
Date: 2026-06-11
Built a convex hull finder using the gift wrapping method because I wanted to visualize point sets and their boundaries without pulling in numpy.
"""

"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I chose gift wrapping over Graham scan because it's more intuitive to visualize
and performs better when the hull has fewer points than the total set.
Time complexity is O(nh) where n is total points and h is hull size.
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
    Calculate the orientation of the ordered triplet (p, q, r).
    
    Returns:
        0 if collinear
        1 if clockwise
        2 if counterclockwise
    
    This uses the cross product to determine which direction we turn
    when going from p->q->r. It's the core of the gift wrapping logic.
    """
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    
    if abs(val) < 1e-9:  # floating point tolerance for collinearity
        return 0
    return 1 if val > 0 else 2


def distance_squared(p: Point, q: Point) -> float:
    """Calculate squared Euclidean distance between two points."""
    return (p.x - q.x) ** 2 + (p.y - q.y) ** 2


def convex_hull(points: List[Point]) -> List[Point]:
    """
    Find the convex hull of a set of 2D points using gift wrapping algorithm.
    
    The algorithm starts from the leftmost point and wraps around the point set
    by repeatedly finding the most counterclockwise point from the current hull point.
    
    Args:
        points: List of Point objects
    
    Returns:
        List of Point objects representing the convex hull in counterclockwise order
    """
    n = len(points)
    
    # Need at least 3 points to form a hull
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (starting point for gift wrapping)
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
            
            # If next_point is current, or candidate is more counterclockwise
            if next_point == current:
                next_point = candidate
            else:
                orient = orientation(current, next_point, candidate)
                
                if orient == 2:  # candidate is more counterclockwise
                    next_point = candidate
                elif orient == 0:  # collinear - pick the farther one
                    if distance_squared(current, candidate) > distance_squared(current, next_point):
                        next_point = candidate
        
        current = next_point
        
        # We've wrapped around back to the start
        if current == leftmost:
            break
    
    return hull


def polygon_area(hull: List[Point]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    I added this to verify the hull makes sense - bigger area usually means
    we captured more of the point cloud correctly.
    """
    n = len(hull)
    if n < 3:
        return 0.0
    
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += hull[i].x * hull[j].y
        area -= hull[j].x * hull[i].y
    
    return abs(area) / 2.0


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Casts a ray from the point to infinity and counts intersections.
    Odd number of intersections = inside, even = outside.
    """
    n = len(polygon)
    inside = False
    
    p1 = polygon[0]
    for i in range(1, n + 1):
        p2 = polygon[i % n]
        
        if point.y > min(p1.y, p2.y):
            if point.y <= max(p1.y, p2.y):
                if point.x <= max(p1.x, p2.x):
                    if p1.y != p2.y:
                        x_intersection = (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
                        if p1.x == p2.x or point.x <= x_intersection:
                            inside = not inside
        p1 = p2
    
    return inside


if __name__ == "__main__":
    print("=== Convex Hull Demo ===\n")
    
    # Create a test point cloud - some random-ish points
    test_points = [
        Point(0, 3),
        Point(1, 1),
        Point(2, 2),
        Point(4, 4),
        Point(0, 0),
        Point(1, 2),
        Point(3, 1),
        Point(3, 3),
        Point(2, 0),
        Point(4, 0),
    ]
    
    print(f"Input: {len(test_points)} points")
    for p in test_points:
        print(f"  {p}")
    
    hull = convex_hull(test_points)
    
    print(f"\nConvex Hull: {len(hull)} vertices")
    for p in hull:
        print(f"  {p}")
    
    area = polygon_area(hull)
    print(f"\nHull area: {area:.2f} square units")
    
    # Test point-in-polygon with a point inside and outside
    test_inside = Point(2, 1.5)
    test_outside = Point(5, 5)
    
    print(f"\nPoint-in-polygon tests:")
    print(f"  {test_inside} inside hull? {point_in_polygon(test_inside, hull)}")
    print(f"  {test_outside} inside hull? {point_in_polygon(test_outside, hull)}")