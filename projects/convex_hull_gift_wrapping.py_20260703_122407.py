"""
Date: 2026-07-03
Built a convex hull calculator using the gift wrapping algorithm because I wanted to understand how it walks the perimeter step by step.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I chose gift wrapping because it's intuitive - you literally "wrap" the points
like wrapping a gift. Time complexity is O(nh) where h is the number of hull points,
which beats other algorithms when the hull is small relative to total points.
"""

import math
from typing import List, Tuple

Point = Tuple[float, float]


def orientation(p: Point, q: Point, r: Point) -> float:
    """
    Calculate the orientation of the ordered triplet (p, q, r).
    
    Returns:
        > 0: counter-clockwise turn
        < 0: clockwise turn
        = 0: collinear
    
    Uses cross product: (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    """
    return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])


def distance_squared(p: Point, q: Point) -> float:
    """Calculate squared Euclidean distance between two points."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def gift_wrapping_convex_hull(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull using the gift wrapping algorithm.
    
    The idea: start from the leftmost point, then keep picking the most
    counter-clockwise point until we wrap back around to the start.
    
    Args:
        points: List of (x, y) coordinate tuples
        
    Returns:
        List of points on the convex hull in counter-clockwise order
    """
    n = len(points)
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (guaranteed to be on hull)
    leftmost_idx = min(range(n), key=lambda i: (points[i][0], points[i][1]))
    
    hull = []
    current = leftmost_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counter-clockwise point from points[current]
        # Start by assuming the next point is the candidate
        next_point = (current + 1) % n
        
        for candidate in range(n):
            if candidate == current:
                continue
                
            # Check if candidate is more counter-clockwise than next_point
            cross = orientation(points[current], points[next_point], points[candidate])
            
            if cross > 0:
                # candidate is more counter-clockwise
                next_point = candidate
            elif cross == 0:
                # Collinear - pick the farther one (to handle edge cases cleanly)
                if distance_squared(points[current], points[candidate]) > \
                   distance_squared(points[current], points[next_point]):
                    next_point = candidate
        
        current = next_point
        
        # We've wrapped around to the starting point
        if current == leftmost_idx:
            break
    
    return hull


def compute_hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    Fun fact: I learned this formula years ago and it still feels like magic.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def ascii_visualize(points: List[Point], hull: List[Point], width: int = 60, height: int = 20):
    """
    Create a simple ASCII visualization of the points and convex hull.
    
    Not fancy, but good enough to see what's happening at a glance.
    """
    if not points:
        return
    
    # Find bounds
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Add padding
    margin = 0.1
    range_x = max_x - min_x
    range_y = max_y - min_y
    min_x -= range_x * margin
    max_x += range_x * margin
    min_y -= range_y * margin
    max_y += range_y * margin
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def to_grid(p: Point) -> Tuple[int, int]:
        """Convert point to grid coordinates."""
        x = int((p[0] - min_x) / (max_x - min_x) * (width - 1))
        y = int((p[1] - min_y) / (max_y - min_y) * (height - 1))
        return (x, height - 1 - y)  # Flip y-axis for display
    
    # Draw all points
    for point in points:
        gx, gy = to_grid(point)
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = '·'
    
    # Draw hull points
    hull_set = set(hull)
    for point in points:
        if point in hull_set:
            gx, gy = to_grid(point)
            if 0 <= gx < width and 0 <= gy < height:
                grid[gy][gx] = '*'
    
    # Print the grid
    print('┌' + '─' * width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * width + '┘')


if __name__ == "__main__":
    # Test with some random-ish points that form an interesting shape
    test_points = [
        (0, 0), (1, 1), (2, 2), (3, 1), (4, 0),
        (3, -1), (2, 0), (1, -1), (2, 1),
        (1.5, 0.5), (2.5, 0.5), (2, -0.5)
    ]
    
    print("Computing Convex Hull using Gift Wrapping Algorithm")
    print("=" * 60)
    print(f"\nInput: {len(test_points)} points")
    
    hull = gift_wrapping_convex_hull(test_points)
    
    print(f"Hull contains {len(hull)} vertices:")
    for i, point in enumerate(hull):
        print(f"  {i}: {point}")
    
    area = compute_hull_area(hull)
    print(f"\nHull area: {area:.2f}")
    
    print("\nVisualization (* = hull vertex, · = interior point):")
    ascii_visualize(test_points, hull)
    
    # Edge case: test with collinear points
    print("\n" + "=" * 60)
    print("Edge case: collinear points")
    collinear_points = [(i, 2*i) for i in range(5)]
    hull2 = gift_wrapping_convex_hull(collinear_points)
    print(f"Input: {collinear_points}")
    print(f"Hull: {hull2}")