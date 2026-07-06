"""
Date: 2026-07-06
Built a convex hull finder using Graham's scan algorithm because I needed to visualize point clusters and find their boundaries.
"""

#!/usr/bin/env python3
"""
Convex Hull using Graham's Scan Algorithm

I wrote this because I was working with some scattered coordinate data
and wanted to find the boundary polygon. Graham's scan is elegant and
runs in O(n log n) time, which is optimal for convex hull problems.
"""

import math
from typing import List, Tuple


class Point:
    """Represents a 2D point with x and y coordinates."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


def polar_angle(p0: Point, p1: Point) -> float:
    """
    Calculate the polar angle from p0 to p1.
    
    Returns the angle in radians. I use atan2 because it handles
    all quadrants correctly without special cases.
    """
    return math.atan2(p1.y - p0.y, p1.x - p0.x)


def distance_squared(p0: Point, p1: Point) -> float:
    """
    Calculate squared Euclidean distance between two points.
    
    I skip the sqrt since we only need this for comparison — saves
    a bit of computation and avoids floating point precision issues.
    """
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    return dx * dx + dy * dy


def cross_product(p0: Point, p1: Point, p2: Point) -> float:
    """
    Calculate the cross product of vectors (p0->p1) and (p0->p2).
    
    Returns:
        > 0 if p2 is to the left of line p0->p1 (counterclockwise)
        < 0 if p2 is to the right (clockwise)
        = 0 if points are collinear
    
    This is the heart of the algorithm — determining which direction
    we're turning as we traverse the hull.
    """
    return (p1.x - p0.x) * (p2.y - p0.y) - (p1.y - p0.y) * (p2.x - p0.x)


def graham_scan(points: List[Point]) -> List[Point]:
    """
    Compute the convex hull using Graham's scan algorithm.
    
    Args:
        points: List of Point objects
    
    Returns:
        List of Points forming the convex hull in counterclockwise order
    
    The algorithm:
    1. Find the lowest point (our pivot)
    2. Sort all other points by polar angle from pivot
    3. Scan through sorted points, keeping only left turns
    """
    if len(points) < 3:
        return points
    
    # Find the point with the lowest y-coordinate (and leftmost if tied)
    # This will be our pivot point — guaranteed to be on the hull
    pivot = min(points, key=lambda p: (p.y, p.x))
    
    # Sort points by polar angle with respect to pivot
    # If two points have the same angle (collinear), keep the farther one
    def sort_key(p):
        if p == pivot:
            return -math.pi, 0  # Pivot comes first
        angle = polar_angle(pivot, p)
        dist = distance_squared(pivot, p)
        return angle, dist
    
    sorted_points = sorted(points, key=sort_key)
    
    # Build the hull using a stack
    # We maintain the invariant that stack always contains valid hull points
    hull = [sorted_points[0], sorted_points[1]]
    
    for i in range(2, len(sorted_points)):
        current = sorted_points[i]
        
        # Pop points from hull while we make a right turn
        # We only want left turns (counterclockwise) on our hull
        while len(hull) > 1:
            cross = cross_product(hull[-2], hull[-1], current)
            if cross <= 0:  # Right turn or collinear — pop it
                hull.pop()
            else:
                break
        
        hull.append(current)
    
    return hull


def visualize_hull(points: List[Point], hull: List[Point]):
    """
    Print a simple ASCII visualization of points and hull.
    
    Not fancy, but good enough to see what's happening. I scale everything
    to fit in a 40x20 character grid.
    """
    if not points:
        return
    
    # Find bounds
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)
    
    width, height = 60, 25
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Scale and plot function
    def scale(p):
        if max_x - min_x == 0:
            sx = width // 2
        else:
            sx = int((p.x - min_x) / (max_x - min_x) * (width - 1))
        
        if max_y - min_y == 0:
            sy = height // 2
        else:
            sy = int((p.y - min_y) / (max_y - min_y) * (height - 1))
        
        return sx, height - 1 - sy  # Flip y for screen coordinates
    
    # Plot all points
    for p in points:
        x, y = scale(p)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '.'
    
    # Plot hull points
    hull_set = set((p.x, p.y) for p in hull)
    for p in points:
        if (p.x, p.y) in hull_set:
            x, y = scale(p)
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = '*'
    
    # Print grid
    print('=' * width)
    for row in grid:
        print(''.join(row))
    print('=' * width)


if __name__ == "__main__":
    # Demo with some interesting point configurations
    print("Convex Hull Demo using Graham's Scan\n")
    
    # Test case 1: Random-ish scattered points
    test_points = [
        Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 1),
        Point(4, 3), Point(3, 4), Point(1, 3), Point(0, 2),
        Point(2, 1), Point(1.5, 2), Point(2.5, 2.5)
    ]
    
    print(f"Input: {len(test_points)} points")
    hull = graham_scan(test_points)
    print(f"Convex hull has {len(hull)} vertices:\n")
    for i, p in enumerate(hull):
        print(f"  {i+1}. ({p.x}, {p.y})")
    
    print("\nVisualization (* = hull vertex, . = interior point):")
    visualize_hull(test_points, hull)
    
    # Test case 2: Square with interior point
    print("\n" + "="*60)
    print("Test case 2: Square with center point\n")
    square_points = [
        Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4), Point(2, 2)
    ]
    
    hull2 = graham_scan(square_points)
    print(f"Hull vertices: {len(hull2)}")
    for p in hull2:
        print(f"  ({p.x}, {p.y})")