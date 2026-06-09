"""
Date: 2026-06-09
Built a convex hull finder using Graham's scan algorithm to see how sorting by polar angle makes the whole thing elegant.
"""

"""
Convex Hull using Graham Scan Algorithm

I wanted to understand how Graham scan actually works under the hood.
The key insight is sorting points by polar angle from a pivot point,
then using a stack to maintain the convex property as we traverse.
"""

import math


def cross_product(o, a, b):
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns:
        > 0 if counter-clockwise turn
        < 0 if clockwise turn
        = 0 if collinear
    
    This is the heart of the algorithm — determines if we turn left or right.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1, p2):
    """
    Calculate squared Euclidean distance between two points.
    
    Using squared distance to avoid sqrt() since we only need comparison.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle(pivot, point):
    """
    Calculate polar angle from pivot to point.
    
    Returns tuple (angle, distance) for sorting.
    We include distance as tiebreaker for collinear points.
    """
    dx = point[0] - pivot[0]
    dy = point[1] - pivot[1]
    angle = math.atan2(dy, dx)
    dist = distance_squared(pivot, point)
    return (angle, dist)


def graham_scan(points):
    """
    Find convex hull of points using Graham scan algorithm.
    
    Args:
        points: List of (x, y) tuples
    
    Returns:
        List of points forming the convex hull in counter-clockwise order
    
    The algorithm:
    1. Find the bottommost point (or leftmost if tie) as pivot
    2. Sort all other points by polar angle from pivot
    3. Use a stack, pushing points and popping when we make a right turn
    """
    if len(points) < 3:
        # Need at least 3 points for a hull
        return points
    
    # Find the starting point (lowest y-coordinate, leftmost if tie)
    pivot = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort points by polar angle with respect to pivot
    # Remove the pivot from the list first
    other_points = [p for p in points if p != pivot]
    sorted_points = sorted(other_points, key=lambda p: polar_angle(pivot, p))
    
    # Initialize hull with pivot and first two sorted points
    hull = [pivot]
    
    for point in sorted_points:
        # Pop points from hull while we would make a clockwise turn
        # We want to maintain counter-clockwise (left) turns only
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull):
    """
    Calculate area of a polygon using the shoelace formula.
    
    Just a bonus utility to verify our hull makes sense.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def plot_points_ascii(points, hull):
    """
    Create a simple ASCII visualization of points and hull.
    
    Not fancy but helps visualize what's happening without matplotlib.
    """
    if not points:
        return
    
    # Find bounds
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Create grid (scale to ~40 chars wide)
    width = 50
    height = 20
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Map point coordinates to grid
    def map_to_grid(x, y):
        gx = int((x - min_x) / (max_x - min_x + 1) * (width - 1))
        gy = int((y - min_y) / (max_y - min_y + 1) * (height - 1))
        return gx, height - 1 - gy  # Flip y for display
    
    # Mark all points
    for p in points:
        gx, gy = map_to_grid(p[0], p[1])
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = '·'
    
    # Mark hull points
    for p in hull:
        gx, gy = map_to_grid(p[0], p[1])
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = '*'
    
    # Print grid
    print('\n'.join(''.join(row) for row in grid))


if __name__ == "__main__":
    print("=== Convex Hull Demo using Graham Scan ===\n")
    
    # Test case 1: Simple square with interior points
    print("Test 1: Square with interior points")
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners
        (2, 2), (1, 1), (3, 3), (2, 3)   # interior
    ]
    hull1 = graham_scan(points1)
    print(f"Input points: {len(points1)}")
    print(f"Hull vertices: {hull1}")
    print(f"Hull area: {hull_area(hull1):.2f}")
    plot_points_ascii(points1, hull1)
    
    print("\n" + "="*50 + "\n")
    
    # Test case 2: Random-ish scattered points
    print("Test 2: Scattered points")
    points2 = [
        (1, 3), (5, 8), (8, 3), (3, 1), (7, 7),
        (4, 4), (6, 2), (2, 6), (9, 5), (3, 7)
    ]
    hull2 = graham_scan(points2)
    print(f"Input points: {len(points2)}")
    print(f"Hull vertices: {hull2}")
    print(f"Hull area: {hull_area(hull2):.2f}")
    plot_points_ascii(points2, hull2)
    
    print("\n" + "="*50 + "\n")
    
    # Test case 3: Collinear points (edge case)
    print("Test 3: Mostly collinear points")
    points3 = [(i, i) for i in range(5)] + [(2, 5), (5, 2)]
    hull3 = graham_scan(points3)
    print(f"Input points: {len(points3)}")
    print(f"Hull vertices: {hull3}")
    print(f"Hull area: {hull_area(hull3):.2f}")