"""
Date: 2026-08-07
Built a convex hull calculator using Graham's scan algorithm to find the smallest convex polygon containing a set of 2D points.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I needed this for a game physics project where I was detecting collisions
between arbitrary shapes. Graham's scan is elegant and O(n log n), which
beats the brute force O(n^3) approaches.

The idea: sort points by polar angle from a pivot (the lowest point),
then walk around the hull, rejecting points that would create a right turn.
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
    
    This is the heart of the algorithm - we use it to decide
    whether to keep or discard points as we build the hull.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared distance between two points (faster than actual distance)."""
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(pivot: Point, point: Point) -> Tuple[float, float]:
    """
    Return a key for sorting points by polar angle relative to pivot.
    
    I use atan2 here because it handles all quadrants correctly.
    The second element (distance) breaks ties for collinear points -
    we want the farthest one when multiple points lie on the same ray.
    """
    dx = point[0] - pivot[0]
    dy = point[1] - pivot[1]
    angle = math.atan2(dy, dx)
    return (angle, -distance_squared(pivot, point))  # Negative for farthest first


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull of a set of 2D points using Graham's scan.
    
    Returns points in counter-clockwise order starting from the bottom-most point.
    If there are fewer than 3 points, returns all points (can't form a hull).
    """
    n = len(points)
    
    if n < 3:
        return points.copy()
    
    # Find the pivot: lowest point, leftmost if there's a tie
    # This is guaranteed to be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort all other points by polar angle relative to pivot
    other_points = [p for p in points if p != pivot]
    sorted_points = sorted(other_points, key=lambda p: polar_angle_key(pivot, p))
    
    # Initialize the hull with pivot and first two points
    hull = [pivot, sorted_points[0], sorted_points[1]]
    
    # Process remaining points
    for point in sorted_points[2:]:
        # Remove points from hull while we would make a clockwise turn
        # This is the key insight: we only keep left turns (counter-clockwise)
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    Added this because once you have a hull, you often want to know its area.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_hull(hull: List[Point]) -> None:
    """Pretty-print the convex hull vertices."""
    print(f"Convex Hull ({len(hull)} vertices):")
    for i, point in enumerate(hull):
        print(f"  {i + 1}. ({point[0]:.2f}, {point[1]:.2f})")
    print(f"Area: {hull_area(hull):.2f}")


if __name__ == "__main__":
    print("Graham Scan Convex Hull Calculator\n")
    
    # Test case 1: Simple square with some internal points
    print("=== Test 1: Square with internal points ===")
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # Square corners
        (2, 2), (1, 1), (3, 3),           # Internal points
        (2, 1), (3, 2)                    # More internal points
    ]
    hull1 = graham_scan(points1)
    print_hull(hull1)
    print()
    
    # Test case 2: Random-ish scattered points
    print("=== Test 2: Scattered points ===")
    points2 = [
        (1, 1), (2, 5), (3, 3), (5, 3),
        (3, 2), (2, 2), (4, 4), (1, 4),
        (4, 1), (5, 5)
    ]
    hull2 = graham_scan(points2)
    print_hull(hull2)
    print()
    
    # Test case 3: Collinear points (edge case I always check)
    print("=== Test 3: Points on a line ===")
    points3 = [(i, i) for i in range(5)]
    hull3 = graham_scan(points3)
    print_hull(hull3)
    print()
    
    # Test case 4: Triangle (already convex)
    print("=== Test 4: Triangle ===")
    points4 = [(0, 0), (5, 0), (2.5, 4)]
    hull4 = graham_scan(points4)
    print_hull(hull4)
    print()
    
    # Visual representation for the first test case
    print("=== Visual for Test 1 ===")
    print("Original points (. = internal, * = hull vertex):")
    hull_set = set(hull1)
    for y in range(5, -1, -1):
        for x in range(5):
            point = (x, y)
            if point in hull_set:
                print("* ", end="")
            elif point in points1:
                print(". ", end="")
            else:
                print("  ", end="")
        print()