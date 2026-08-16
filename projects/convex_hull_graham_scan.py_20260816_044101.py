"""
Date: 2026-08-16
Built a convex hull finder using Graham scan because I wanted to visualize the smallest boundary around point clouds without any heavy dependencies.
"""

"""
Convex Hull using Graham Scan Algorithm

I needed a way to find the convex hull of a set of 2D points without pulling in
scipy or shapely. Graham scan is elegant and runs in O(n log n) time, which is
optimal for convex hull algorithms in the comparison model.

The idea: start from the lowest point, sort everything else by polar angle,
then walk counterclockwise while keeping only left turns.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def cross_product(o: Point, a: Point, b: Point) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive means counterclockwise turn, negative means clockwise,
    zero means collinear. This is the heart of the algorithm — we use
    it to decide whether to keep or discard points.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    We don't need the actual distance, just relative ordering,
    so skipping the sqrt saves computation.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def polar_angle_key(origin: Point, point: Point) -> Tuple[float, float]:
    """
    Generate a sort key based on polar angle from origin.
    
    Returns (angle, distance_squared) so that if two points have the same
    angle, we prefer the closer one. Using atan2 here because it handles
    all quadrants correctly.
    """
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    angle = math.atan2(dy, dx)
    dist_sq = dx * dx + dy * dy
    return (angle, dist_sq)


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull of a set of 2D points using Graham scan.
    
    Returns the vertices of the convex hull in counterclockwise order.
    Edge case: if there are fewer than 3 points, just return them all
    since there's no meaningful hull.
    """
    if len(points) < 3:
        return points[:]
    
    # Find the starting point: lowest y-coordinate, leftmost if tie
    # This is guaranteed to be on the hull
    start = min(points, key=lambda p: (p[1], p[0]))
    
    # Sort all other points by polar angle with respect to start point
    # I'm filtering out the start point itself here
    sorted_points = sorted(
        [p for p in points if p != start],
        key=lambda p: polar_angle_key(start, p)
    )
    
    # Initialize the hull with the start point and first sorted point
    hull = [start]
    
    for point in sorted_points:
        # Remove points from hull while we would make a clockwise turn
        # We want to keep only left turns (counterclockwise)
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    
    return hull


def hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a polygon defined by hull points.
    
    Using the shoelace formula because it's simple and works for any
    simple polygon. Useful for verifying the hull makes sense.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_hull_visualization(points: List[Point], hull: List[Point]) -> None:
    """
    Print a simple ASCII visualization of points and their hull.
    
    Not fancy, but helps verify the algorithm is working correctly
    when you run it. I'm scaling everything to fit in a 40x20 grid.
    """
    if not points:
        print("No points to visualize")
        return
    
    # Find bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Add padding
    padding = 0.1
    range_x = max_x - min_x if max_x != min_x else 1
    range_y = max_y - min_y if max_y != min_y else 1
    
    width, height = 40, 20
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    hull_set = set(hull)
    
    for point in points:
        # Map to grid coordinates
        x = int((point[0] - min_x) / range_x * (width - 1))
        y = int((point[1] - min_y) / range_y * (height - 1))
        y = height - 1 - y  # Flip y-axis for display
        
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '#' if point in hull_set else '.'
    
    print("\nVisualization (# = hull vertex, . = interior point):")
    for row in grid:
        print(''.join(row))


if __name__ == "__main__":
    # Test with a classic case: points forming a rough circle with some interior points
    test_points = [
        (0, 0), (1, 1), (2, 0), (2, 2), (0, 2),  # Outer square
        (1, 0.5), (0.5, 1), (1.5, 1),            # Some interior points
        (3, 1), (1, 3), (-1, 1), (1, -1)         # Extension points
    ]
    
    print("Computing convex hull for {} points...".format(len(test_points)))
    print("\nInput points:")
    for i, p in enumerate(test_points):
        print(f"  {i}: {p}")
    
    hull = graham_scan(test_points)
    
    print(f"\nConvex hull has {len(hull)} vertices:")
    for i, vertex in enumerate(hull):
        print(f"  {i}: {vertex}")
    
    area = hull_area(hull)
    print(f"\nHull area: {area:.2f}")
    
    print_hull_visualization(test_points, hull)
    
    # Another test: collinear points (edge case)
    print("\n" + "="*50)
    print("Testing edge case: collinear points")
    collinear = [(0, 0), (1, 1), (2, 2), (3, 3)]
    hull_collinear = graham_scan(collinear)
    print(f"Hull of collinear points: {hull_collinear}")