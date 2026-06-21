"""
Date: 2026-06-21
Built a convex hull finder using Graham's scan algorithm because I needed to visualize point sets and their boundaries for a mapping side project.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I wanted to compute convex hulls for some geographic coordinate clustering work,
so I implemented Graham's scan. It's O(n log n) which is optimal, and handles
edge cases like collinear points nicely.
"""

import math
from typing import List, Tuple


Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns positive if counter-clockwise turn, negative if clockwise,
    zero if collinear. This is the core geometric primitive for the scan.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    Using squared distance to avoid sqrt() - we only need it for comparisons
    when sorting points at the same angle from the pivot.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle(pivot: Point, point: Point) -> float:
    """
    Calculate polar angle from pivot to point.
    
    atan2 gives us the angle in radians from the positive x-axis.
    This is used to sort points in counter-clockwise order around the pivot.
    """
    return math.atan2(point[1] - pivot[1], point[0] - pivot[0])


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull of a set of 2D points using Graham's scan.
    
    The algorithm:
    1. Find the bottom-most point (or left-most if tied) as pivot
    2. Sort all other points by polar angle with respect to pivot
    3. Process points in order, maintaining a stack of hull vertices
    4. Use cross product to check if we make a left turn (keep) or right turn (pop)
    
    Returns the vertices of the convex hull in counter-clockwise order.
    """
    if len(points) < 3:
        # Convex hull needs at least 3 points
        return sorted(points)
    
    # Find the pivot: lowest y-coordinate, leftmost if tied
    # This point is guaranteed to be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle from pivot
    # If two points have the same angle (collinear), keep the farther one
    sorted_points = sorted(
        [p for p in points if p != pivot],
        key=lambda p: (polar_angle(pivot, p), distance_squared(pivot, p))
    )
    
    # Remove collinear points except the farthest at each angle
    # This handles the edge case where multiple points lie on the same ray from pivot
    filtered = []
    for i, point in enumerate(sorted_points):
        # Keep the last point at each angle (the farthest one)
        if i == len(sorted_points) - 1 or \
           polar_angle(pivot, point) != polar_angle(pivot, sorted_points[i + 1]):
            filtered.append(point)
    
    # Initialize hull with pivot and first two points
    hull = [pivot]
    
    for point in filtered:
        # Pop points from hull while we make a right turn (or go straight)
        # We want only left (counter-clockwise) turns
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    I added this to verify the hull makes sense - useful for sanity checking.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_hull(points: List[Point], hull: List[Point]) -> None:
    """
    Pretty print the results with some basic stats.
    """
    print(f"Input: {len(points)} points")
    print(f"Convex hull: {len(hull)} vertices")
    print(f"Hull area: {hull_area(hull):.2f}")
    print("\nHull vertices (counter-clockwise):")
    for i, point in enumerate(hull):
        print(f"  {i + 1}. ({point[0]:.2f}, {point[1]:.2f})")


if __name__ == "__main__":
    # Test case 1: Simple square with interior points
    print("=== Test 1: Square with interior points ===")
    test_points_1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners of square
        (2, 2), (1, 1), (3, 3)            # interior points (shouldn't be in hull)
    ]
    hull_1 = graham_scan(test_points_1)
    print_hull(test_points_1, hull_1)
    
    print("\n" + "="*50 + "\n")
    
    # Test case 2: Random-ish points (simulating real data)
    print("=== Test 2: Scattered points ===")
    test_points_2 = [
        (1.5, 2.3), (4.2, 1.1), (3.8, 4.9),
        (0.5, 3.2), (2.1, 0.8), (5.0, 3.5),
        (1.8, 4.2), (3.3, 2.7), (0.9, 1.5)
    ]
    hull_2 = graham_scan(test_points_2)
    print_hull(test_points_2, hull_2)
    
    print("\n" + "="*50 + "\n")
    
    # Test case 3: Collinear points (edge case I wanted to make sure works)
    print("=== Test 3: Collinear points on a line ===")
    test_points_3 = [
        (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
        (1, 0), (2, 1)  # slightly off the line
    ]
    hull_3 = graham_scan(test_points_3)
    print_hull(test_points_3, hull_3)