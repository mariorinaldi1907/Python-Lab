"""
Date: 2026-08-22
Built a convex hull finder using the gift wrapping algorithm because I wanted to visualize point clouds and needed something intuitive to debug.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping (Jarvis March)
I chose this algorithm because it's conceptually simple and easy to visualize.
Works in O(nh) time where n is points and h is hull vertices.
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
        """Check equality with small epsilon for floating point comparison."""
        if not isinstance(other, Point):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
    
    def __hash__(self):
        return hash((round(self.x, 10), round(self.y, 10)))


def orientation(p: Point, q: Point, r: Point) -> int:
    """
    Find orientation of ordered triplet (p, q, r).
    Returns:
        0 if collinear
        1 if clockwise
        2 if counterclockwise
    
    This is the heart of the algorithm — we use the cross product to determine
    which way we're turning when going from p->q->r.
    """
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    
    if abs(val) < 1e-9:  # collinear case with epsilon for floating point
        return 0
    return 1 if val > 0 else 2


def distance_squared(p: Point, q: Point) -> float:
    """Calculate squared distance between two points (avoids sqrt for speed)."""
    return (p.x - q.x) ** 2 + (p.y - q.y) ** 2


def convex_hull_gift_wrap(points: List[Point]) -> List[Point]:
    """
    Compute convex hull using gift wrapping (Jarvis march).
    
    The idea: start from leftmost point, then keep wrapping counterclockwise
    by always picking the most counterclockwise point from current point.
    
    Returns hull points in counterclockwise order.
    """
    n = len(points)
    if n < 3:
        return points.copy()  # hull is just the points themselves
    
    # Find the leftmost point (guaranteed to be on hull)
    leftmost_idx = 0
    for i in range(1, n):
        if points[i].x < points[leftmost_idx].x:
            leftmost_idx = i
        elif points[i].x == points[leftmost_idx].x:
            # if same x, pick lower y to handle vertical edge case
            if points[i].y < points[leftmost_idx].y:
                leftmost_idx = i
    
    hull = []
    current = leftmost_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counterclockwise point from current
        next_point = (current + 1) % n
        
        for i in range(n):
            if i == current:
                continue
            
            orient = orientation(points[current], points[next_point], points[i])
            
            # If i is more counterclockwise than next_point, update next_point
            if orient == 2:
                next_point = i
            # If collinear, pick the farthest one (handles collinear points on hull edge)
            elif orient == 0:
                if distance_squared(points[current], points[i]) > distance_squared(points[current], points[next_point]):
                    next_point = i
        
        current = next_point
        
        # We've wrapped around to start
        if current == leftmost_idx:
            break
    
    return hull


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Cast a horizontal ray from the point to infinity and count intersections.
    Odd number of intersections = inside, even = outside.
    """
    if len(polygon) < 3:
        return False
    
    count = 0
    n = len(polygon)
    
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        
        # Check if ray intersects with edge p1-p2
        if ((p1.y > point.y) != (p2.y > point.y)) and \
           (point.x < (p2.x - p1.x) * (point.y - p1.y) / (p2.y - p1.y) + p1.x):
            count += 1
    
    return count % 2 == 1


def polygon_area(polygon: List[Point]) -> float:
    """
    Calculate area of polygon using shoelace formula.
    Works for any simple polygon (non-self-intersecting).
    """
    if len(polygon) < 3:
        return 0.0
    
    area = 0.0
    n = len(polygon)
    
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i].x * polygon[j].y
        area -= polygon[j].x * polygon[i].y
    
    return abs(area) / 2.0


if __name__ == "__main__":
    # Demo with some test points - I'm creating a shape that looks interesting
    test_points = [
        Point(0, 0),
        Point(1, 1),
        Point(2, 2),      # collinear with above, should be handled
        Point(2, 0),
        Point(3, 1),
        Point(4, 3),
        Point(2, 4),
        Point(0, 3),
        Point(1.5, 1.5),  # interior point
        Point(2.5, 2),    # interior point
    ]
    
    print("Computing convex hull using gift wrapping algorithm")
    print(f"Input: {len(test_points)} points")
    print()
    
    hull = convex_hull_gift_wrap(test_points)
    
    print(f"Convex hull has {len(hull)} vertices:")
    for i, p in enumerate(hull):
        print(f"  {i+1}. ({p.x}, {p.y})")
    print()
    
    area = polygon_area(hull)
    print(f"Hull area: {area:.2f} square units")
    print()
    
    # Test point-in-polygon on some points
    test_inside = [
        Point(1.5, 1.5),
        Point(2.5, 2),
        Point(5, 5),      # definitely outside
        Point(0, 0),      # on hull vertex
    ]
    
    print("Testing point-in-polygon:")
    for p in test_inside:
        inside = point_in_polygon(p, hull)
        status = "inside" if inside else "outside"
        print(f"  Point ({p.x}, {p.y}) is {status} the hull")