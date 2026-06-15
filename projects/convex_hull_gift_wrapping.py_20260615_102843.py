"""
Date: 2026-06-15
Built a convex hull solver using the gift wrapping (Jarvis march) algorithm because I wanted something intuitive to visualize point clouds.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping Algorithm (Jarvis March)

I picked gift wrapping over Graham scan because it's easier to visualize
mentally — you literally "wrap" the points like wrapping a gift. Plus it's
O(nh) which is better than O(n log n) when h (hull points) is small.
"""

from typing import List, Tuple
import math


def cross_product(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Positive = counter-clockwise turn
    Negative = clockwise turn
    Zero = collinear
    
    I use this to determine which direction we're turning when going from
    point o -> a -> b. It's the z-component of the 3D cross product.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Squared Euclidean distance between two points.
    
    We use squared distance to avoid sqrt() calls — we only need relative
    comparisons anyway.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def gift_wrapping_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Compute convex hull using gift wrapping (Jarvis march) algorithm.
    
    The idea: start from the leftmost point (guaranteed to be on hull),
    then keep "wrapping" by finding the most counter-clockwise point
    relative to the current edge. Repeat until we come back to start.
    
    Time complexity: O(nh) where n is total points, h is hull points
    Space complexity: O(h) for storing the hull
    """
    if len(points) < 3:
        return points
    
    # Find the leftmost point (guaranteed to be on convex hull)
    start = min(points, key=lambda p: (p[0], p[1]))
    
    hull = []
    current = start
    
    while True:
        hull.append(current)
        next_point = points[0]
        
        # Find the most counter-clockwise point relative to current
        for candidate in points:
            if candidate == current:
                continue
            
            # If next_point is current, or candidate is more counter-clockwise
            if next_point == current:
                next_point = candidate
            else:
                cross = cross_product(current, next_point, candidate)
                
                # candidate is more counter-clockwise
                if cross > 0:
                    next_point = candidate
                # Collinear case: pick the farthest one
                elif cross == 0 and distance_squared(current, candidate) > distance_squared(current, next_point):
                    next_point = candidate
        
        current = next_point
        
        # Wrapped back to start
        if current == start:
            break
    
    return hull


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Cast a ray from the point to infinity (we use horizontal ray to the right)
    and count intersections with polygon edges. Odd = inside, even = outside.
    
    This is a bonus utility function since we already have the hull.
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


def visualize_points_ascii(points: List[Tuple[float, float]], hull: List[Tuple[float, float]], width: int = 60, height: int = 20):
    """
    ASCII art visualization of points and their convex hull.
    
    I added this because text output is way more satisfying than just
    printing coordinates. Scales all points to fit in the grid.
    """
    if not points:
        return
    
    # Find bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Scale points to grid
    def scale(p):
        if max_x == min_x:
            sx = width // 2
        else:
            sx = int((p[0] - min_x) / (max_x - min_x) * (width - 1))
        
        if max_y == min_y:
            sy = height // 2
        else:
            sy = int((p[1] - min_y) / (max_y - min_y) * (height - 1))
        
        return sx, height - 1 - sy  # Flip y for display
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Mark all points
    for p in points:
        sx, sy = scale(p)
        grid[sy][sx] = '·'
    
    # Mark hull points (overwrite with capitals)
    hull_set = set(hull)
    for p in hull:
        sx, sy = scale(p)
        grid[sy][sx] = 'H'
    
    # Print grid
    print('┌' + '─' * width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * width + '┘')


if __name__ == "__main__":
    # Test case 1: Simple square with some interior points
    print("Test 1: Square with interior points")
    points = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # Square corners
        (2, 2), (1, 1), (3, 3), (2, 1)    # Interior points
    ]
    
    hull = gift_wrapping_convex_hull(points)
    print(f"Input points: {len(points)}")
    print(f"Hull points: {len(hull)}")
    print(f"Hull vertices: {hull}")
    visualize_points_ascii(points, hull)
    
    # Test if interior point is detected correctly
    test_point = (2, 2)
    inside = point_in_polygon(test_point, hull)
    print(f"\nPoint {test_point} inside hull: {inside}")
    
    print("\n" + "="*60 + "\n")
    
    # Test case 2: Random-ish points that form interesting shape
    print("Test 2: Scattered points")
    import random
    random.seed(42)  # Reproducible results
    
    scattered = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(20)]
    
    hull2 = gift_wrapping_convex_hull(scattered)
    print(f"Input points: {len(scattered)}")
    print(f"Hull points: {len(hull2)}")
    print(f"Hull vertices: {hull2}")
    visualize_points_ascii(scattered, hull2)
    
    # Show some point-in-polygon tests
    print(f"\nPoint (5, 5) inside hull: {point_in_polygon((5, 5), hull2)}")
    print(f"Point (0, 0) inside hull: {point_in_polygon((0, 0), hull2)}")
    print(f"Point (100, 100) inside hull: {point_in_polygon((100, 100), hull2)}")