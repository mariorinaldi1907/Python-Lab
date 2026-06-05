"""
Date: 2026-06-05
Built a convex hull finder using the gift wrapping (Jarvis march) algorithm — seemed like a fun way to brush up on computational geometry basics.
"""

#!/usr/bin/env python3
"""
Convex hull implementation using the gift wrapping algorithm (Jarvis march).
I chose this over Graham scan because it's more intuitive to visualize,
even though it's slower for large point sets. For my use cases (small sets),
the O(nh) complexity is totally fine.
"""

import math
from typing import List, Tuple


def orientation(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> int:
    """
    Calculate the orientation of the ordered triplet (p, q, r).
    
    Returns:
        0 if collinear
        1 if clockwise
        2 if counterclockwise
    
    This uses the cross product to determine which way the angle turns.
    Positive cross product = left turn (CCW), negative = right turn (CW).
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    
    if abs(val) < 1e-10:  # floating point tolerance
        return 0
    return 1 if val > 0 else 2


def distance_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate squared Euclidean distance between two points.
    Using squared distance to avoid sqrt for performance reasons.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find the convex hull of a set of 2D points using gift wrapping algorithm.
    
    The idea: start from the leftmost point, then keep "wrapping" by finding
    the most counterclockwise point from the current one. It's like wrapping
    a string around nails on a board.
    
    Args:
        points: List of (x, y) tuples
        
    Returns:
        List of points forming the convex hull in counterclockwise order
    """
    n = len(points)
    if n < 3:
        return points.copy()  # need at least 3 points for a hull
    
    # Find the leftmost point (guaranteed to be on the hull)
    leftmost = min(range(n), key=lambda i: (points[i][0], points[i][1]))
    
    hull = []
    current = leftmost
    
    while True:
        hull.append(points[current])
        
        # Find the most counterclockwise point from points[current]
        next_point = (current + 1) % n
        
        for i in range(n):
            # If i is more counterclockwise than current next_point, update next_point
            orient = orientation(points[current], points[i], points[next_point])
            
            if orient == 2:  # i is more counterclockwise
                next_point = i
            elif orient == 0:  # collinear - pick the farther one
                if distance_squared(points[current], points[i]) > \
                   distance_squared(points[current], points[next_point]):
                    next_point = i
        
        current = next_point
        
        # We've wrapped around back to the start
        if current == leftmost:
            break
    
    return hull


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Cast a ray from the point to infinity (horizontal ray to the right)
    and count intersections with polygon edges. Odd = inside, even = outside.
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        # Check if ray crosses this edge
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside


def ascii_plot(points: List[Tuple[float, float]], hull: List[Tuple[float, float]], 
               width: int = 60, height: int = 20) -> str:
    """
    Create a simple ASCII visualization of points and their convex hull.
    Not pretty, but gets the job done for debugging in the terminal.
    """
    if not points:
        return ""
    
    # Find bounds
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Add padding
    range_x = max_x - min_x or 1
    range_y = max_y - min_y or 1
    min_x -= range_x * 0.1
    max_x += range_x * 0.1
    min_y -= range_y * 0.1
    max_y += range_y * 0.1
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def to_grid(x: float, y: float) -> Tuple[int, int]:
        gx = int((x - min_x) / (max_x - min_x) * (width - 1))
        gy = int((y - min_y) / (max_y - min_y) * (height - 1))
        return gx, height - 1 - gy  # flip y axis
    
    # Draw hull edges
    hull_set = set(hull)
    for i in range(len(hull)):
        x1, y1 = to_grid(*hull[i])
        x2, y2 = to_grid(*hull[(i + 1) % len(hull)])
        
        # Simple line drawing - not perfect but good enough
        steps = max(abs(x2 - x1), abs(y2 - y1)) + 1
        for step in range(steps):
            t = step / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = '*'
    
    # Draw points
    for point in points:
        x, y = to_grid(*point)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = 'H' if point in hull_set else 'o'
    
    return '\n'.join(''.join(row) for row in grid)


if __name__ == "__main__":
    # Demo with some random-ish points that form an interesting shape
    test_points = [
        (0, 3), (1, 1), (2, 2), (4, 4), (0, 0), (1, 2), (3, 1), (3, 3),
        (2, 1), (1, 3), (4, 1), (5, 2), (4, 3), (2, 4), (1, 4)
    ]
    
    print("Finding convex hull of", len(test_points), "points...")
    print()
    
    hull = convex_hull(test_points)
    
    print("Convex hull vertices (in order):")
    for i, point in enumerate(hull):
        print(f"  {i + 1}. {point}")
    
    print(f"\nHull has {len(hull)} vertices")
    print()
    
    # Test point-in-polygon
    test_point = (2.5, 2.5)
    inside = point_in_polygon(test_point, hull)
    print(f"Point {test_point} is {'INSIDE' if inside else 'OUTSIDE'} the hull")
    
    print("\nASCII visualization (H=hull vertex, o=interior point, *=hull edge):")
    print()
    print(ascii_plot(test_points, hull))