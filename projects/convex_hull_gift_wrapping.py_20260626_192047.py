"""
Date: 2026-06-26
Built a convex hull finder using the gift wrapping algorithm because I wanted to visualize point clouds and their boundaries without any external dependencies.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping Algorithm (Jarvis March)
---------------------------------------------------------
Finds the convex hull of a set of 2D points. I chose gift wrapping because
it's intuitive and efficient for small hulls (O(nh) where h is hull size).
"""

from typing import List, Tuple
import math


def orientation(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> float:
    """
    Calculate the orientation of ordered triplet (p, q, r).
    
    Returns:
        > 0 if counter-clockwise
        < 0 if clockwise
        = 0 if collinear
    
    This uses the cross product to determine which direction we turn
    when going from p->q->r. Super useful for checking if a point
    lies to the left or right of a line segment.
    """
    return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])


def distance_squared(p: Tuple[float, float], q: Tuple[float, float]) -> float:
    """Calculate squared Euclidean distance between two points."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Compute the convex hull using the Gift Wrapping algorithm.
    
    Args:
        points: List of (x, y) tuples
    
    Returns:
        List of points forming the convex hull in counter-clockwise order
    
    The idea is to start from the leftmost point and keep "wrapping"
    around the point set, always choosing the most counter-clockwise
    point as the next hull vertex. Like wrapping a string around nails.
    """
    n = len(points)
    
    # Edge cases
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (or bottommost if tie) as our starting point
    # This is guaranteed to be on the hull
    start_idx = 0
    for i in range(1, n):
        if points[i][0] < points[start_idx][0]:
            start_idx = i
        elif points[i][0] == points[start_idx][0] and points[i][1] < points[start_idx][1]:
            start_idx = i
    
    hull = []
    current = start_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counter-clockwise point from current
        next_point = 0
        for i in range(n):
            if i == current:
                continue
            
            # If next_point is the same as current, or i is more counter-clockwise
            if next_point == current:
                next_point = i
            else:
                cross = orientation(points[current], points[next_point], points[i])
                
                # i is more counter-clockwise
                if cross > 0:
                    next_point = i
                # Collinear case: choose the farthest point to avoid interior points
                elif cross == 0:
                    if distance_squared(points[current], points[i]) > distance_squared(points[current], points[next_point]):
                        next_point = i
        
        current = next_point
        
        # Wrapped back to start
        if current == start_idx:
            break
    
    return hull


def polygon_area(points: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    I added this to verify the hull is correct — the hull should
    have the maximum area possible for the given point set.
    """
    if len(points) < 3:
        return 0.0
    
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    
    return abs(area) / 2.0


def visualize_hull(points: List[Tuple[float, float]], hull: List[Tuple[float, float]]):
    """
    Print a simple ASCII visualization of points and hull.
    
    Not fancy, but helps me quickly see if the hull looks reasonable
    without firing up matplotlib.
    """
    if not points:
        return
    
    # Find bounds
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Create grid (40x20 characters)
    width, height = 60, 20
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def to_grid(x, y):
        """Map real coordinates to grid coordinates."""
        if max_x == min_x:
            gx = width // 2
        else:
            gx = int((x - min_x) / (max_x - min_x) * (width - 1))
        
        if max_y == min_y:
            gy = height // 2
        else:
            gy = int((y - min_y) / (max_y - min_y) * (height - 1))
        
        return gx, height - 1 - gy  # Flip y for display
    
    # Plot all points
    for px, py in points:
        gx, gy = to_grid(px, py)
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = '·'
    
    # Plot hull points
    hull_set = set(hull)
    for px, py in hull:
        gx, gy = to_grid(px, py)
        if 0 <= gx < width and 0 <= gy < height:
            grid[gy][gx] = 'H'
    
    print("\nVisualization (H = hull vertex, · = interior point):")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")


if __name__ == "__main__":
    # Test case 1: Simple square with some interior points
    print("=== Test 1: Square with interior points ===")
    test_points_1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners
        (2, 2), (1, 1), (3, 3),  # interior
        (2, 1), (3, 2)  # more interior
    ]
    
    hull_1 = convex_hull(test_points_1)
    print(f"Input: {len(test_points_1)} points")
    print(f"Hull: {hull_1}")
    print(f"Hull size: {len(hull_1)} vertices")
    print(f"Hull area: {polygon_area(hull_1):.2f}")
    visualize_hull(test_points_1, hull_1)
    
    # Test case 2: Random-ish scattered points
    print("\n=== Test 2: Scattered points ===")
    test_points_2 = [
        (1, 1), (2, 5), (3, 3), (5, 3), (3, 2),
        (2, 2), (4, 4), (6, 1), (5, 5), (7, 3)
    ]
    
    hull_2 = convex_hull(test_points_2)
    print(f"Input: {len(test_points_2)} points")
    print(f"Hull: {hull_2}")
    print(f"Hull size: {len(hull_2)} vertices")
    print(f"Hull area: {polygon_area(hull_2):.2f}")
    visualize_hull(test_points_2, hull_2)
    
    # Test case 3: Collinear points (edge case)
    print("\n=== Test 3: Collinear points ===")
    test_points_3 = [(i, 2*i) for i in range(6)]
    hull_3 = convex_hull(test_points_3)
    print(f"Input: {test_points_3}")
    print(f"Hull: {hull_3}")
    print(f"Expected: Only endpoints for collinear points")