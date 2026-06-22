"""
Date: 2026-06-22
Built a convex hull finder using the gift wrapping algorithm because I wanted to understand how computational geometry actually works under the hood.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I always thought convex hulls were magic, but the gift wrapping metaphor
makes it click: start at the leftmost point, then keep "wrapping" counterclockwise
until you get back to the start. It's O(nh) where h is hull size, so not the
fastest for huge datasets, but it's elegant and easy to understand.
"""

from typing import List, Tuple
import math


Point = Tuple[float, float]


def orientation(p: Point, q: Point, r: Point) -> int:
    """
    Determine the orientation of ordered triplet (p, q, r).
    
    Returns:
        0 -> p, q, r are colinear
        1 -> Clockwise
        2 -> Counterclockwise
    
    The idea: compute the cross product of vectors (q-p) and (r-q).
    If positive, we turned left (counterclockwise). If negative, we turned right.
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    
    if abs(val) < 1e-9:  # Handle floating point precision
        return 0
    return 1 if val > 0 else 2


def distance_squared(p1: Point, p2: Point) -> float:
    """
    Euclidean distance squared between two points.
    We use squared distance to avoid sqrt() since we only need comparisons.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def gift_wrapping_convex_hull(points: List[Point]) -> List[Point]:
    """
    Compute convex hull using the Gift Wrapping (Jarvis March) algorithm.
    
    Args:
        points: List of (x, y) coordinate tuples
    
    Returns:
        List of points forming the convex hull in counterclockwise order
    
    The algorithm:
    1. Start at the leftmost point (guaranteed to be on the hull)
    2. Keep the current point and find the most counterclockwise point
    3. That becomes our next hull point
    4. Repeat until we wrap back to the start
    """
    n = len(points)
    if n < 3:
        # Can't form a hull with fewer than 3 points
        return points.copy()
    
    # Find the leftmost point (our starting point)
    leftmost_idx = 0
    for i in range(1, n):
        if points[i][0] < points[leftmost_idx][0]:
            leftmost_idx = i
        elif points[i][0] == points[leftmost_idx][0]:
            # If x-coords are equal, pick the one with smaller y
            if points[i][1] < points[leftmost_idx][1]:
                leftmost_idx = i
    
    hull = []
    current = leftmost_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counterclockwise point from points[current]
        next_point = (current + 1) % n
        
        for i in range(n):
            if i == current:
                continue
            
            # Check if point i is more counterclockwise than next_point
            orient = orientation(points[current], points[i], points[next_point])
            
            if orient == 2:
                # i is more counterclockwise
                next_point = i
            elif orient == 0:
                # Colinear points - choose the farthest one
                # This ensures we don't include interior colinear points
                if distance_squared(points[current], points[i]) > \
                   distance_squared(points[current], points[next_point]):
                    next_point = i
        
        current = next_point
        
        # If we've wrapped back to the start, we're done
        if current == leftmost_idx:
            break
    
    return hull


def calculate_hull_area(hull: List[Point]) -> float:
    """
    Calculate the area of a polygon defined by hull points using the shoelace formula.
    
    Just a bonus function because once you have the hull, calculating area is trivial.
    """
    if len(hull) < 3:
        return 0.0
    
    area = 0.0
    n = len(hull)
    for i in range(n):
        j = (i + 1) % n
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    
    return abs(area) / 2.0


def print_visualization(points: List[Point], hull: List[Point]) -> None:
    """
    Print a simple ASCII visualization of points and hull.
    Not fancy, but helps you see what's happening.
    """
    # Find bounds
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add some padding
    padding = 2
    width = 60
    height = 20
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def map_to_grid(p: Point) -> Tuple[int, int]:
        # Map point to grid coordinates
        if max_x - min_x == 0:
            gx = width // 2
        else:
            gx = int((p[0] - min_x) / (max_x - min_x) * (width - 2 * padding)) + padding
        
        if max_y - min_y == 0:
            gy = height // 2
        else:
            gy = int((p[1] - min_y) / (max_y - min_y) * (height - 2 * padding)) + padding
        
        return (min(height - 1, max(0, gy)), min(width - 1, max(0, gx)))
    
    # Mark all points
    for point in points:
        y, x = map_to_grid(point)
        grid[height - 1 - y][x] = '·'
    
    # Mark hull points
    hull_set = set(hull)
    for point in hull:
        y, x = map_to_grid(point)
        grid[height - 1 - y][x] = '*'
    
    print("\n".join("".join(row) for row in grid))


if __name__ == "__main__":
    # Test with a simple set of points
    print("=== Convex Hull Demo ===\n")
    
    # Create some test points - a mix of interior and exterior points
    test_points = [
        (0, 0), (1, 1), (2, 2), (3, 1), (4, 0),
        (3, -1), (1, -1), (1.5, 0.5), (2.5, 0.5),
        (0, 3), (4, 3), (2, 4)
    ]
    
    print(f"Input points ({len(test_points)} total):")
    for i, p in enumerate(test_points):
        print(f"  {i}: {p}")
    
    hull = gift_wrapping_convex_hull(test_points)
    
    print(f"\nConvex hull ({len(hull)} points):")
    for i, p in enumerate(hull):
        print(f"  {i}: {p}")
    
    area = calculate_hull_area(hull)
    print(f"\nHull area: {area:.2f}")
    
    print("\nVisualization (* = hull point, · = interior point):")
    print_visualization(test_points, hull)
    
    # Another test with points on a circle
    print("\n\n=== Circle Test ===\n")
    circle_points = []
    for i in range(12):
        angle = 2 * math.pi * i / 12
        x = 5 + 3 * math.cos(angle)
        y = 5 + 3 * math.sin(angle)
        circle_points.append((x, y))
    
    # Add some interior points
    circle_points.extend([(5, 5), (6, 5), (5, 6)])
    
    circle_hull = gift_wrapping_convex_hull(circle_points)
    print(f"Circle with {len(circle_points)} points -> hull has {len(circle_hull)} points")
    print(f"Hull area: {calculate_hull_area(circle_hull):.2f}")
    
    print("\nVisualization:")
    print_visualization(circle_points, circle_hull)