"""
Date: 2026-06-09
Built a convex hull calculator using Graham's scan algorithm because I needed something fast and elegant for finding the boundary of point clouds.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I've always found Graham's scan beautiful - it's one of those algorithms
that just *works* elegantly. The idea is simple: sort points by polar angle
from a pivot, then walk around keeping only left turns.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive = counter-clockwise turn
    Negative = clockwise turn
    Zero = collinear
    
    This is the heart of the algorithm - we use it to decide which
    points to keep as we build the hull.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared distance between two points (faster than actual distance)."""
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle(pivot: Point, point: Point) -> float:
    """
    Calculate polar angle from pivot to point.
    
    Using atan2 here because it handles all quadrants correctly.
    """
    return math.atan2(point[1] - pivot[1], point[0] - pivot[0])


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Find the convex hull of a set of 2D points using Graham's scan.
    
    Args:
        points: List of (x, y) tuples
        
    Returns:
        List of points forming the convex hull in counter-clockwise order
        
    The algorithm:
    1. Find the lowest point (our pivot)
    2. Sort all other points by polar angle from pivot
    3. Process points, keeping only those that make left turns
    """
    if len(points) < 3:
        return points.copy()
    
    # Find the pivot - the point with lowest y-coordinate (leftmost if tied)
    # This point is guaranteed to be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle, with distance as tiebreaker
    # Remove the pivot from the list first
    other_points = [p for p in points if p != pivot]
    sorted_points = sorted(
        other_points,
        key=lambda p: (polar_angle(pivot, p), distance_squared(pivot, p))
    )
    
    # Build the hull using a stack approach
    # Start with pivot and first sorted point
    hull = [pivot, sorted_points[0]]
    
    for point in sorted_points[1:]:
        # Pop points that would create a right turn
        # We only want left turns (counter-clockwise) on our hull
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area enclosed by the convex hull using the shoelace formula.
    
    This is just a nice bonus feature - once you have the hull,
    calculating area is straightforward.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def point_inside_hull(point: Point, hull: List[Point]) -> bool:
    """
    Check if a point is inside the convex hull.
    
    For a convex polygon, a point is inside if it's on the same side
    of all edges. We check this using cross products.
    """
    if len(hull) < 3:
        return False
    
    # All cross products should have the same sign
    sign = None
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        cp = cross_product(hull[i], hull[j], point)
        
        if abs(cp) < 1e-10:  # On edge
            continue
            
        if sign is None:
            sign = cp > 0
        elif (cp > 0) != sign:
            return False
    
    return True


if __name__ == "__main__":
    # Demo with a scattered point cloud
    print("=== Convex Hull Demo ===\n")
    
    # Create some test points - imagine scattered data from a sensor or something
    test_points = [
        (0, 0), (1, 1), (2, 2), (2, 0), (2, 4),
        (0, 2), (1, 4), (3, 1), (3, 3), (4, 4),
        (1.5, 2.5), (2.5, 1.5)  # These are inside the hull
    ]
    
    print(f"Input: {len(test_points)} points")
    for p in test_points:
        print(f"  {p}")
    
    # Calculate the convex hull
    hull = graham_scan(test_points)
    
    print(f"\nConvex Hull: {len(hull)} vertices")
    for p in hull:
        print(f"  {p}")
    
    # Calculate and display area
    area = hull_area(hull)
    print(f"\nHull Area: {area:.2f} square units")
    
    # Test point containment
    print("\n=== Point Containment Tests ===")
    test_inside = [
        ((1.5, 2.5), "inside"),
        ((2.5, 1.5), "inside"),
        ((0, 0), "on hull"),
        ((5, 5), "outside"),
        ((-1, -1), "outside")
    ]
    
    for point, expected in test_inside:
        inside = point_inside_hull(point, hull)
        status = "INSIDE" if inside else "OUTSIDE"
        print(f"  Point {point}: {status} (expected: {expected})")
    
    print("\n=== Edge Case: Triangle ===")
    triangle = [(0, 0), (4, 0), (2, 3)]
    tri_hull = graham_scan(triangle)
    print(f"Triangle hull: {tri_hull}")
    print(f"Triangle area: {hull_area(tri_hull):.2f}")