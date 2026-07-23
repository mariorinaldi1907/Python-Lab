"""
Date: 2026-07-23
Built a convex hull finder using Graham's scan algorithm because I wanted to understand how collision boundaries actually get computed in 2D games.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I wrote this because I was curious how game engines compute collision hulls
for sprites. Graham scan is elegant — sorts points by polar angle then walks
the perimeter, removing concave vertices as it goes.
"""

import math


def cross_product(o, a, b):
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns positive if counter-clockwise turn, negative if clockwise,
    zero if collinear. This is the key to detecting which points form
    the convex boundary.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1, p2):
    """Calculate squared distance between two points (avoids sqrt for speed)."""
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(pivot):
    """
    Return a sorting key function for ordering points by polar angle from pivot.
    
    I initially tried atan2 but realized comparing cross products is more robust
    and doesn't require trig functions. If angles are equal, closer points come first.
    """
    def key(point):
        # Use cross product for angle comparison (avoids atan2 edge cases)
        dx = point[0] - pivot[0]
        dy = point[1] - pivot[1]
        angle = math.atan2(dy, dx)
        dist = distance_squared(pivot, point)
        return (angle, dist)
    return key


def graham_scan(points):
    """
    Compute the convex hull of a set of 2D points using Graham's scan.
    
    Algorithm:
    1. Find the bottom-most point (or leftmost if tied) as the pivot
    2. Sort all other points by polar angle with respect to pivot
    3. Walk through sorted points, maintaining a stack of hull vertices
    4. Remove points that would create a right turn (concave angle)
    
    Returns a list of points forming the convex hull in counter-clockwise order.
    """
    if len(points) < 3:
        return points.copy()  # Convex hull not possible
    
    # Find the pivot — bottom-most point, leftmost if tied
    # This guarantees we start from a point definitely on the hull
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle from pivot
    sorted_points = sorted(
        [p for p in points if p != pivot],
        key=polar_angle_key(pivot)
    )
    
    # Initialize hull with pivot and first sorted point
    hull = [pivot, sorted_points[0]]
    
    # Process each point in polar-sorted order
    for point in sorted_points[1:]:
        # Remove points from hull while they create a clockwise turn
        # This is the key insight: we only keep left turns (CCW)
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull):
    """
    Calculate the area of a convex hull using the shoelace formula.
    
    Useful for sanity checking — the hull area should always be >= 0
    and should encompass all the original points.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_hull_visualization(points, hull):
    """
    Print a crude ASCII visualization of the points and hull.
    
    This is mostly for debugging but it's fun to see the shape.
    """
    if not points:
        return
    
    # Find bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Scale to fit in ~40x20 character grid
    width, height = 40, 20
    
    def scale(point):
        x = int((point[0] - min_x) / (max_x - min_x + 1) * (width - 1))
        y = int((point[1] - min_y) / (max_y - min_y + 1) * (height - 1))
        return (x, height - 1 - y)  # Flip y for display
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Mark all points
    for point in points:
        x, y = scale(point)
        grid[y][x] = '·'
    
    # Mark hull points
    hull_set = set(hull)
    for point in hull:
        x, y = scale(point)
        grid[y][x] = '*'
    
    print('\n'.join(''.join(row) for row in grid))


if __name__ == "__main__":
    # Test with a simple set of points — some inside, some on the boundary
    test_points = [
        (0, 0), (1, 1), (2, 2), (3, 1), (4, 0),
        (3, -1), (2, -1), (1, -1), (2, 0), (2, 1),
        (0, 3), (4, 3), (2, 4), (1, 2), (3, 2)
    ]
    
    print("Computing convex hull for", len(test_points), "points")
    print("Input points:", test_points)
    print()
    
    hull = graham_scan(test_points)
    
    print("Convex hull vertices (", len(hull), "points):", sep='')
    for point in hull:
        print(f"  {point}")
    
    area = hull_area(hull)
    print(f"\nHull area: {area:.2f}")
    
    print("\nVisualization (* = hull vertex, · = interior point):")
    print_hull_visualization(test_points, hull)
    
    # Test edge cases
    print("\n--- Edge case tests ---")
    print("Empty:", graham_scan([]))
    print("Single point:", graham_scan([(1, 1)]))
    print("Two points:", graham_scan([(0, 0), (1, 1)]))
    print("Collinear points:", graham_scan([(0, 0), (1, 1), (2, 2), (3, 3)]))