"""
Date: 2026-08-24
Built a convex hull finder using the gift wrapping algorithm because I wanted to understand how computational geometry works without heavy dependencies.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

This implementation finds the convex hull of a set of 2D points.
I chose gift wrapping because it's intuitive - you literally "wrap" the points
like wrapping a gift with string, always turning left as much as possible.
"""

import math
from typing import List, Tuple


Point = Tuple[float, float]


def orientation(p: Point, q: Point, r: Point) -> float:
    """
    Calculate the orientation of ordered triplet (p, q, r).
    
    Returns:
        Positive value: counter-clockwise turn
        Negative value: clockwise turn
        Zero: collinear points
    
    This is the cross product of vectors (q-p) and (r-q).
    I use this to determine which direction we're turning.
    """
    return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])


def distance_squared(p: Point, q: Point) -> float:
    """
    Euclidean distance squared between two points.
    
    Avoiding sqrt for performance since we only need relative distances.
    """
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def convex_hull_gift_wrap(points: List[Point]) -> List[Point]:
    """
    Find convex hull using gift wrapping (Jarvis march) algorithm.
    
    Time complexity: O(nh) where n is number of points and h is hull size.
    For most practical cases this is fine, though Graham scan would be O(n log n).
    
    Args:
        points: List of (x, y) tuples
        
    Returns:
        List of points forming the convex hull in counter-clockwise order
    """
    n = len(points)
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (guaranteed to be on hull)
    # In case of tie, pick the one with smallest y
    leftmost_idx = min(range(n), key=lambda i: (points[i][0], points[i][1]))
    
    hull = []
    current = leftmost_idx
    
    while True:
        hull.append(points[current])
        
        # Find the most counter-clockwise point from current
        # Start by assuming next point is the candidate
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
                # Collinear - pick the farther one to avoid intermediate points
                if distance_squared(points[current], points[candidate]) > \
                   distance_squared(points[current], points[next_point]):
                    next_point = candidate
        
        current = next_point
        
        # We've wrapped around back to the start
        if current == leftmost_idx:
            break
    
    return hull


def visualize_hull(points: List[Point], hull: List[Point], width: int = 60, height: int = 20):
    """
    Create a simple ASCII visualization of the convex hull.
    
    This is just for fun - helps me see if the algorithm is working correctly.
    """
    if not points:
        return
    
    # Find bounds
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add padding
    padding = 0.1
    x_range = max_x - min_x
    y_range = max_y - min_y
    min_x -= x_range * padding
    max_x += x_range * padding
    min_y -= y_range * padding
    max_y += y_range * padding
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    def scale(point: Point) -> Tuple[int, int]:
        """Scale point to grid coordinates."""
        x = int((point[0] - min_x) / (max_x - min_x) * (width - 1))
        y = int((point[1] - min_y) / (max_y - min_y) * (height - 1))
        return x, height - 1 - y  # Flip y for display
    
    # Draw all points
    for point in points:
        x, y = scale(point)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '·'
    
    # Draw hull points
    hull_set = set(hull)
    for point in points:
        if point in hull_set:
            x, y = scale(point)
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = '*'
    
    # Draw hull edges
    for i in range(len(hull)):
        p1 = hull[i]
        p2 = hull[(i + 1) % len(hull)]
        x1, y1 = scale(p1)
        x2, y2 = scale(p2)
        
        # Simple line drawing (not perfect but good enough)
        steps = max(abs(x2 - x1), abs(y2 - y1)) + 1
        for step in range(steps):
            t = step / max(steps - 1, 1)
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < width and 0 <= y < height:
                if grid[y][x] == ' ':
                    grid[y][x] = '#'
    
    # Print grid
    print('┌' + '─' * width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * width + '┘')


if __name__ == "__main__":
    # Demo with some interesting point sets
    
    print("=== Convex Hull Demo using Gift Wrapping ===\n")
    
    # Test case 1: Square with points inside
    print("Test 1: Square with interior points")
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners
        (2, 2), (1, 1), (3, 2), (2, 3)    # interior
    ]
    hull1 = convex_hull_gift_wrap(points1)
    print(f"Points: {len(points1)}, Hull vertices: {len(hull1)}")
    print(f"Hull: {hull1}\n")
    visualize_hull(points1, hull1)
    
    # Test case 2: Random-ish scattered points
    print("\nTest 2: Scattered points")
    points2 = [
        (1, 1), (2, 5), (3, 3), (5, 3), (3, 2),
        (2, 2), (4, 4), (1, 4), (5, 1), (4, 1)
    ]
    hull2 = convex_hull_gift_wrap(points2)
    print(f"Points: {len(points2)}, Hull vertices: {len(hull2)}")
    print(f"Hull: {hull2}\n")
    visualize_hull(points2, hull2)
    
    # Test case 3: Circle-ish pattern
    print("\nTest 3: Roughly circular distribution")
    points3 = []
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x = 5 + 4 * math.cos(rad)
        y = 5 + 4 * math.sin(rad)
        points3.append((x, y))
    # Add some interior points
    points3.extend([(5, 5), (6, 5), (5, 6), (4, 5)])
    
    hull3 = convex_hull_gift_wrap(points3)
    print(f"Points: {len(points3)}, Hull vertices: {len(hull3)}")
    print(f"Hull: {[f'({p[0]:.1f}, {p[1]:.1f})' for p in hull3]}\n")
    visualize_hull(points3, hull3)