"""
Date: 2026-07-25
Built a convex hull calculator using Graham's scan algorithm to find the smallest convex polygon containing a set of 2D points.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham Scan Algorithm

I needed a way to find the outer boundary of a set of points for a project
involving spatial data visualization. Graham scan is elegant because it sorts
points by polar angle and then does a single sweep to build the hull.
"""

import math
from typing import List, Tuple


Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive result means counter-clockwise turn, negative means clockwise.
    This is the core of determining whether we're making a left or right turn
    when traversing points, which is how we know if a point should be on the hull.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """Calculate squared Euclidean distance between two points."""
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle(origin: Point, point: Point) -> float:
    """
    Calculate the polar angle from origin to point.
    
    Using atan2 because it handles all quadrants correctly and we don't
    have to worry about division by zero or special cases.
    """
    return math.atan2(point[1] - origin[1], point[0] - origin[0])


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Find the convex hull of a set of 2D points using Graham's scan algorithm.
    
    The algorithm:
    1. Find the bottommost point (or leftmost if tied) as the pivot
    2. Sort all other points by polar angle relative to the pivot
    3. Process points in order, maintaining only left turns (counter-clockwise)
    
    Returns the convex hull as a list of points in counter-clockwise order.
    """
    if len(points) < 3:
        # Need at least 3 points to form a polygon
        return points.copy()
    
    # Find the starting point - lowest y-coordinate, leftmost if tied
    # This guarantees it's on the hull and gives us a good reference point
    start = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to start point
    # If two points have the same angle, closer one comes first
    sorted_points = sorted(
        [p for p in points if p != start],
        key=lambda p: (polar_angle(start, p), distance_squared(start, p))
    )
    
    # Initialize hull with the starting point and first sorted point
    hull = [start, sorted_points[0]]
    
    # Process each point in sorted order
    for point in sorted_points[1:]:
        # Remove points from hull while we make a non-left turn
        # This is the key insight: we only keep points that maintain convexity
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def convex_hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    Threw this in because once you have the hull, you often want to know
    how much area it covers.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def point_in_convex_hull(point: Point, hull: List[Point]) -> bool:
    """
    Check if a point is inside a convex hull.
    
    For a convex polygon, a point is inside if it's on the same side
    (left side in our case, since hull is counter-clockwise) of all edges.
    """
    if len(hull) < 3:
        return False
    
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        # If point is on the right side of any edge, it's outside
        if cross_product(hull[i], hull[j], point) < 0:
            return False
    
    return True


def visualize_hull(points: List[Point], hull: List[Point]) -> None:
    """
    Print a simple ASCII visualization of points and hull.
    
    Not fancy, but helps when debugging or demonstrating the algorithm.
    """
    if not points:
        return
    
    # Find bounds for the grid
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add some padding
    padding = 2
    min_x -= padding
    max_x += padding
    min_y -= padding
    max_y += padding
    
    # Create grid (limit size for readability)
    width = min(60, int(max_x - min_x + 1))
    height = min(30, int(max_y - min_y + 1))
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Mark regular points
    for px, py in points:
        gx = int((px - min_x) / (max_x - min_x) * (width - 1))
        gy = int((py - min_y) / (max_y - min_y) * (height - 1))
        if 0 <= gx < width and 0 <= gy < height:
            grid[height - 1 - gy][gx] = '·'
    
    # Mark hull points
    for px, py in hull:
        gx = int((px - min_x) / (max_x - min_x) * (width - 1))
        gy = int((py - min_y) / (max_y - min_y) * (height - 1))
        if 0 <= gx < width and 0 <= gy < height:
            grid[height - 1 - gy][gx] = '*'
    
    print('\n'.join(''.join(row) for row in grid))


if __name__ == "__main__":
    # Demo with a set of random-ish points that form an interesting hull
    test_points = [
        (0, 0), (1, 1), (2, 2), (3, 1), (4, 0),
        (3, -1), (2, -2), (1, -1), (2, 0), (2, 1),
        (1.5, 0.5), (2.5, 0.5), (2, -0.5), (0.5, 0.5)
    ]
    
    print("Computing convex hull for", len(test_points), "points...")
    print()
    
    hull = graham_scan(test_points)
    
    print("Convex hull vertices (counter-clockwise):")
    for i, point in enumerate(hull):
        print(f"  {i + 1}. ({point[0]}, {point[1]})")
    
    print()
    area = convex_hull_area(hull)
    print(f"Hull area: {area:.2f} square units")
    
    print()
    print("Visualization (* = hull vertex, · = interior point):")
    visualize_hull(test_points, hull)
    
    # Test point inclusion
    print()
    test_point = (2, 0.5)
    inside = point_in_convex_hull(test_point, hull)
    print(f"Is point {test_point} inside the hull? {inside}")
    
    outside_point = (5, 5)
    inside = point_in_convex_hull(outside_point, hull)
    print(f"Is point {outside_point} inside the hull? {inside}")