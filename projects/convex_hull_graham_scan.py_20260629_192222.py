"""
Date: 2026-06-29
Built a convex hull finder using Graham's scan algorithm to wrap arbitrary 2D point sets with their minimal convex boundary.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham Scan Algorithm

I wrote this because I was working with some coordinate data and wanted
to find the outermost boundary efficiently. Graham scan is elegant —
it sorts points by polar angle and then walks around eliminating concave turns.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive: counter-clockwise turn
    Negative: clockwise turn
    Zero: collinear
    
    This is the heart of the algorithm — we use it to detect which
    direction we're turning as we traverse the hull.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared Euclidean distance between two points."""
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle(origin: Point, point: Point) -> float:
    """
    Calculate polar angle from origin to point.
    
    Returns angle in radians. I use atan2 because it handles all quadrants
    correctly without special cases.
    """
    return math.atan2(point[1] - origin[1], point[0] - origin[0])


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute convex hull using Graham's scan algorithm.
    
    Steps:
    1. Find the point with lowest y-coordinate (our pivot)
    2. Sort all other points by polar angle relative to pivot
    3. Walk through sorted points, keeping only left turns
    
    Time complexity: O(n log n) due to sorting
    Space complexity: O(n) for the hull
    
    Returns points in counter-clockwise order starting from the pivot.
    """
    if len(points) < 3:
        return points.copy()
    
    # Find the pivot point (lowest y, then leftmost if tied)
    # This will definitely be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to pivot
    # If angles are equal, sort by distance (closer first)
    def sort_key(p: Point) -> Tuple[float, float]:
        if p == pivot:
            return (-math.pi, 0)  # Pivot comes first
        angle = polar_angle(pivot, p)
        dist = distance_squared(pivot, p)
        return (angle, dist)
    
    sorted_points = sorted(points, key=sort_key)
    
    # Build the hull
    hull = []
    
    for point in sorted_points:
        # Remove points that would create a clockwise turn
        # We only want counter-clockwise (left) turns on the hull
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate area of convex hull using the shoelace formula.
    
    I added this because once you have the hull, you often want to know
    how much space it covers.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def format_point(p: Point) -> str:
    """Format a point nicely for display."""
    return f"({p[0]:.2f}, {p[1]:.2f})"


if __name__ == "__main__":
    print("=== Convex Hull Demo (Graham Scan) ===\n")
    
    # Test case 1: Simple square with interior point
    print("Test 1: Square with interior point")
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners
        (2, 2)  # interior point (should not be in hull)
    ]
    hull1 = graham_scan(points1)
    print(f"Input points: {len(points1)}")
    print(f"Hull points: {len(hull1)}")
    print(f"Hull vertices: {[format_point(p) for p in hull1]}")
    print(f"Area: {hull_area(hull1):.2f}\n")
    
    # Test case 2: Random-ish scattered points
    print("Test 2: Scattered points")
    points2 = [
        (1, 1), (2, 5), (3, 3), (5, 3), (3, 2),
        (2, 2), (4, 4), (1, 4), (6, 2), (5, 1)
    ]
    hull2 = graham_scan(points2)
    print(f"Input points: {len(points2)}")
    print(f"Hull points: {len(hull2)}")
    print(f"Hull vertices: {[format_point(p) for p in hull2]}")
    print(f"Area: {hull_area(hull2):.2f}\n")
    
    # Test case 3: Collinear points (edge case)
    print("Test 3: Collinear points")
    points3 = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    hull3 = graham_scan(points3)
    print(f"Input points: {len(points3)}")
    print(f"Hull points: {len(hull3)}")
    print(f"Hull vertices: {[format_point(p) for p in hull3]}")
    print(f"Area: {hull_area(hull3):.2f}\n")
    
    # Test case 4: Triangle (minimal hull)
    print("Test 4: Triangle")
    points4 = [(0, 0), (5, 0), (2.5, 4)]
    hull4 = graham_scan(points4)
    print(f"Input points: {len(points4)}")
    print(f"Hull points: {len(hull4)}")
    print(f"Hull vertices: {[format_point(p) for p in hull4]}")
    print(f"Area: {hull_area(hull4):.2f}\n")
    
    print("✓ All tests completed!")