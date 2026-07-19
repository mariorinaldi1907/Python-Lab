"""
Date: 2026-07-19
Built a convex hull calculator using Graham's scan algorithm — it finds the smallest convex polygon enclosing a set of 2D points.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I needed this for a little game prototype where I was experimenting with collision
detection. Graham's scan is elegant: sort by polar angle, then walk the perimeter
removing concave turns. Runs in O(n log n) time which is optimal.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns positive if counter-clockwise turn, negative if clockwise,
    zero if collinear. This is the key to detecting which way we're turning.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    I use squared distance to avoid the sqrt() call since we only need
    relative comparisons for sorting.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(pivot: Point):
    """
    Returns a sorting key function for polar angle sorting around a pivot point.
    
    Points are sorted by angle first, then by distance if angles are equal.
    I use atan2 here because it handles all quadrants correctly.
    """
    def key(point: Point) -> Tuple[float, float]:
        angle = math.atan2(point[1] - pivot[1], point[0] - pivot[0])
        dist = distance_squared(pivot, point)
        return (angle, dist)
    return key


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull of a set of 2D points using Graham's scan.
    
    The algorithm:
    1. Find the bottom-most point (or left-most if tie) as the pivot
    2. Sort all other points by polar angle around the pivot
    3. Walk through sorted points, maintaining a stack of hull vertices
    4. For each point, pop vertices that would create a clockwise turn
    
    Returns vertices of the convex hull in counter-clockwise order.
    """
    if len(points) < 3:
        return points.copy()  # Need at least 3 points for a hull
    
    # Find the pivot: lowest y-coordinate, leftmost if tie
    # This point is guaranteed to be on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to pivot
    # Remove the pivot from the list first, we'll add it back at the start
    sorted_points = sorted([p for p in points if p != pivot], 
                          key=polar_angle_key(pivot))
    
    # Initialize hull with pivot and first two sorted points
    hull = [pivot]
    
    for point in sorted_points:
        # Pop points from hull while we would make a clockwise turn
        # (or go straight, since we want strictly convex hull)
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    I added this because it's a nice sanity check — the area should always
    be positive for a properly computed hull.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_hull(points: List[Point], hull: List[Point]):
    """
    Pretty-print the input points and resulting hull for debugging.
    """
    print(f"Input points ({len(points)} total):")
    for i, p in enumerate(points):
        marker = " *" if p in hull else ""
        print(f"  {i}: ({p[0]:6.2f}, {p[1]:6.2f}){marker}")
    
    print(f"\nConvex hull ({len(hull)} vertices):")
    for i, p in enumerate(hull):
        print(f"  {i}: ({p[0]:6.2f}, {p[1]:6.2f})")
    
    print(f"\nHull area: {hull_area(hull):.2f}")


if __name__ == "__main__":
    # Demo 1: Simple square with some interior points
    print("=" * 60)
    print("Demo 1: Square with interior points")
    print("=" * 60)
    
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # Square corners
        (2, 2), (1, 1), (3, 3),          # Interior points
        (2, 1), (1, 3)                   # More interior points
    ]
    
    hull1 = graham_scan(points1)
    print_hull(points1, hull1)
    
    # Demo 2: Random-ish scattered points forming a rough circle
    print("\n" + "=" * 60)
    print("Demo 2: Scattered points")
    print("=" * 60)
    
    points2 = [
        (1, 2), (2, 5), (3, 1), (4, 4), (5, 2),
        (6, 6), (7, 3), (3, 7), (2, 2), (5, 5),
        (4, 2), (3, 4)
    ]
    
    hull2 = graham_scan(points2)
    print_hull(points2, hull2)
    
    # Demo 3: Edge case - collinear points
    print("\n" + "=" * 60)
    print("Demo 3: Collinear points on a line")
    print("=" * 60)
    
    points3 = [(i, i) for i in range(5)]  # Diagonal line
    hull3 = graham_scan(points3)
    print_hull(points3, hull3)
    print("(Note: Collinear points reduce to just the endpoints)")