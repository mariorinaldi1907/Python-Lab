"""
Date: 2026-08-04
Built a convex hull finder using Graham scan algorithm — takes 2D points and returns the minimal convex polygon containing them all.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham Scan Algorithm

I wrote this because I was working on some collision detection stuff and needed
a fast way to find the convex hull of a set of points. Graham scan is O(n log n)
which is pretty much optimal for this problem.

The idea is: find the bottom-most point, sort all other points by polar angle,
then walk through them maintaining a "left turn only" property. Any time we'd
make a right turn, we backtrack and remove the previous point.
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
    
    This is the heart of the algorithm - we use it to determine if we're
    making left turns or right turns as we build the hull.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    We use squared distance to avoid sqrt operations - we only need relative
    ordering anyway, not actual distances.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(pivot: Point, point: Point) -> Tuple[float, float]:
    """
    Generate a sort key for polar angle relative to pivot.
    
    Returns (angle, distance) tuple. The angle is computed using atan2,
    and we include distance as a tiebreaker for collinear points (we want
    closer points first).
    """
    dx = point[0] - pivot[0]
    dy = point[1] - pivot[1]
    angle = math.atan2(dy, dx)
    dist = distance_squared(pivot, point)
    return (angle, dist)


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Find the convex hull of a set of 2D points using Graham scan.
    
    Args:
        points: List of (x, y) tuples
        
    Returns:
        List of points forming the convex hull in counter-clockwise order
        
    The algorithm:
    1. Find the point with lowest y-coordinate (our pivot)
    2. Sort all other points by polar angle with respect to pivot
    3. Process points in order, maintaining only "left turns"
    """
    if len(points) < 3:
        return points.copy()  # No hull possible with < 3 points
    
    # Find the bottom-most point (ties broken by leftmost)
    # This will definitely be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to pivot
    sorted_points = sorted(
        [p for p in points if p != pivot],
        key=lambda p: polar_angle_key(pivot, p)
    )
    
    # Initialize hull with pivot and first sorted point
    hull = [pivot]
    
    for point in sorted_points:
        # Remove points that would create a right turn
        # We keep going while we have at least 2 points and the last 3 points
        # (including the new one) make a right turn or are collinear
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    This is just a bonus function I added because once you have the hull,
    computing its area is trivial and often useful.
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
    """Pretty print the input points and resulting hull."""
    print(f"Input: {len(points)} points")
    print(f"Convex hull: {len(hull)} vertices")
    print("\nHull vertices (counter-clockwise):")
    for i, p in enumerate(hull):
        print(f"  {i+1}. ({p[0]:.2f}, {p[1]:.2f})")
    print(f"\nHull area: {hull_area(hull):.2f}")


if __name__ == "__main__":
    # Test case 1: Simple square with interior points
    print("=" * 50)
    print("Test 1: Square with interior points")
    print("=" * 50)
    
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # Square corners
        (2, 2), (1, 1), (3, 3),           # Interior points
        (2, 1), (1, 3)                    # More interior points
    ]
    hull1 = graham_scan(points1)
    print_hull(points1, hull1)
    
    # Test case 2: Points on a circle (should form polygon)
    print("\n" + "=" * 50)
    print("Test 2: Points arranged in a circle")
    print("=" * 50)
    
    import math
    n = 8
    radius = 5.0
    points2 = [
        (radius * math.cos(2 * math.pi * i / n), 
         radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]
    # Add some interior points
    points2.extend([(0, 0), (1, 1), (-1, -1)])
    
    hull2 = graham_scan(points2)
    print_hull(points2, hull2)
    
    # Test case 3: Collinear points
    print("\n" + "=" * 50)
    print("Test 3: Mostly collinear points")
    print("=" * 50)
    
    points3 = [
        (0, 0), (1, 1), (2, 2), (3, 3),  # Diagonal line
        (0, 3), (3, 0)                    # Two points off the line
    ]
    hull3 = graham_scan(points3)
    print_hull(points3, hull3)