"""
Date: 2026-08-14
Built a convex hull algorithm using Graham scan because I needed to find boundaries of point clouds for a visualization project I'm tinkering with.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham Scan Algorithm

I wanted a clean implementation of Graham scan for finding convex hulls.
This came up when I was working on some 2D point clustering stuff and needed
to visualize the outer boundary of point sets. Graham scan is elegant because
it sorts points by polar angle and then does a single pass to build the hull.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive means counter-clockwise turn, negative means clockwise,
    zero means collinear. This is the heart of the algorithm - we use
    it to determine if we're making a left turn or right turn.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    I use squared distance to avoid sqrt() calls - we only need it
    for comparing distances, not the actual values.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(pivot: Point, point: Point) -> Tuple[float, float]:
    """
    Generate a sort key based on polar angle from pivot point.
    
    Returns (angle, distance_squared) tuple. The angle is computed using
    atan2 which handles all quadrants correctly. Distance is the tiebreaker
    for collinear points - we want closer points first.
    """
    dx = point[0] - pivot[0]
    dy = point[1] - pivot[1]
    angle = math.atan2(dy, dx)
    dist_sq = dx * dx + dy * dy
    return (angle, dist_sq)


def convex_hull(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull of a set of 2D points using Graham scan.
    
    Returns points of the convex hull in counter-clockwise order.
    Handles edge cases like < 3 points, all collinear, duplicates, etc.
    
    The algorithm:
    1. Find the lowest point (or leftmost if tie) - this is our pivot
    2. Sort all other points by polar angle with respect to pivot
    3. Scan through sorted points, keeping only left turns
    """
    if len(points) < 3:
        return sorted(points)  # Need at least 3 points for a hull
    
    # Remove duplicates - they mess up the polar angle sort
    unique_points = list(set(points))
    if len(unique_points) < 3:
        return sorted(unique_points)
    
    # Find the pivot point: lowest y-coordinate, leftmost if tie
    # This point is guaranteed to be on the hull
    pivot = min(unique_points, key=lambda p: (p[1], p[0]))
    
    # Sort all other points by polar angle from pivot
    other_points = [p for p in unique_points if p != pivot]
    other_points.sort(key=lambda p: polar_angle_key(pivot, p))
    
    # Initialize hull with pivot and first sorted point
    hull = [pivot, other_points[0]]
    
    # Scan through remaining points
    for point in other_points[1:]:
        # Remove points that would create a right turn (clockwise)
        # We only want left turns (counter-clockwise) on the hull
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    Just a bonus utility function - sometimes you want to know the area
    enclosed by the hull. Shoelace formula is super clean for polygons.
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
    Pretty print the input points and resulting hull.
    
    I wanted nice output for debugging and demos.
    """
    print(f"Input: {len(points)} points")
    print(f"Convex Hull: {len(hull)} vertices")
    print(f"Hull Area: {hull_area(hull):.2f}")
    print("\nHull vertices (counter-clockwise):")
    for i, point in enumerate(hull):
        print(f"  {i+1}. ({point[0]:.2f}, {point[1]:.2f})")


if __name__ == "__main__":
    # Test 1: Simple square with an interior point
    print("=" * 50)
    print("Test 1: Square with interior point")
    print("=" * 50)
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # Square corners
        (2, 2)  # Interior point (should not be in hull)
    ]
    hull1 = convex_hull(points1)
    print_hull(points1, hull1)
    
    # Test 2: Random-ish scattered points
    print("\n" + "=" * 50)
    print("Test 2: Scattered points")
    print("=" * 50)
    points2 = [
        (1, 1), (2, 5), (3, 3), (5, 3), (3, 2),
        (2, 2), (4, 4), (1, 4), (5, 1)
    ]
    hull2 = convex_hull(points2)
    print_hull(points2, hull2)
    
    # Test 3: Collinear points (edge case I wanted to handle)
    print("\n" + "=" * 50)
    print("Test 3: Collinear points")
    print("=" * 50)
    points3 = [(i, i) for i in range(5)]  # Points on line y = x
    hull3 = convex_hull(points3)
    print_hull(points3, hull3)
    
    # Test 4: Triangle (minimal hull)
    print("\n" + "=" * 50)
    print("Test 4: Simple triangle")
    print("=" * 50)
    points4 = [(0, 0), (3, 0), (1.5, 3)]
    hull4 = convex_hull(points4)
    print_hull(points4, hull4)