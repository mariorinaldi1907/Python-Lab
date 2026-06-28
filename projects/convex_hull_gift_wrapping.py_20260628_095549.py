"""
Date: 2026-06-28
Built a convex hull finder using the gift wrapping algorithm because I wanted to visualize point sets and understand how jarvis march actually works in practice.
"""

"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I wrote this because I was curious about how to find the convex hull of a set of 
2D points. Gift wrapping is O(nh) where n is the number of points and h is the 
number of hull vertices, which makes it efficient when the hull is small.

The algorithm works by starting at the leftmost point and "wrapping" counterclockwise
around the point set, always choosing the most counterclockwise point as the next
hull vertex.
"""

from typing import List, Tuple
import math


def cross_product(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns:
        Positive if counterclockwise turn, negative if clockwise, zero if collinear.
    
    I use this to determine the orientation of three points, which is the core
    of deciding which point is "more counterclockwise" from our current position.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate squared distance between two points.
    
    I avoid sqrt here for performance since we only need relative distances
    when breaking ties between collinear points.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def gift_wrapping(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find convex hull using gift wrapping algorithm.
    
    Args:
        points: List of (x, y) tuples representing 2D points
        
    Returns:
        List of points forming the convex hull in counterclockwise order
        
    The algorithm:
    1. Start at the leftmost point (guaranteed to be on hull)
    2. For each hull point, find the most counterclockwise point
    3. Continue until we wrap back to the start
    
    I handle collinear points by choosing the farthest one, which ensures
    we don't miss any hull vertices.
    """
    n = len(points)
    
    # Edge cases - need at least 3 points for a proper hull
    if n < 3:
        return points.copy()
    
    # Find the leftmost point (guaranteed to be on the convex hull)
    # If there's a tie, take the one with smallest y coordinate
    leftmost = min(points, key=lambda p: (p[0], p[1]))
    
    hull = []
    current = leftmost
    
    while True:
        hull.append(current)
        next_point = points[0]
        
        # Find the most counterclockwise point from current
        for candidate in points:
            if candidate == current:
                continue
                
            # Calculate orientation
            cp = cross_product(current, next_point, candidate)
            
            if next_point == current or cp > 0:
                # candidate is more counterclockwise
                next_point = candidate
            elif cp == 0:
                # Collinear case - choose the farthest point
                # This ensures we don't create a hull that "cuts corners"
                if distance_squared(current, candidate) > distance_squared(current, next_point):
                    next_point = candidate
        
        current = next_point
        
        # We've wrapped around back to the start
        if current == leftmost:
            break
    
    return hull


def calculate_hull_area(hull: List[Tuple[float, float]]) -> float:
    """
    Calculate area of convex hull using the shoelace formula.
    
    I added this because it's useful to know the area enclosed by the hull,
    and the shoelace formula is elegant and efficient.
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


def calculate_hull_perimeter(hull: List[Tuple[float, float]]) -> float:
    """
    Calculate perimeter of convex hull.
    
    Simple but useful metric - just sum the distances between consecutive vertices.
    """
    if len(hull) < 2:
        return 0.0
    
    perimeter = 0.0
    n = len(hull)
    
    for i in range(n):
        j = (i + 1) % n
        perimeter += math.sqrt(distance_squared(hull[i], hull[j]))
    
    return perimeter


def visualize_hull(points: List[Tuple[float, float]], hull: List[Tuple[float, float]]):
    """
    Print a simple ASCII visualization of the points and hull.
    
    This is pretty basic but helps verify the algorithm is working correctly.
    I scale everything to fit in a 40x20 character grid.
    """
    if not points:
        return
    
    # Find bounds
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    width = 40
    height = 20
    
    # Scale points to fit grid
    def scale(p):
        x = int((p[0] - min_x) / (max_x - min_x + 1e-9) * (width - 1))
        y = int((p[1] - min_y) / (max_y - min_y + 1e-9) * (height - 1))
        return (x, height - 1 - y)  # Flip y for display
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    hull_set = set(hull)
    
    # Mark all points
    for p in points:
        sx, sy = scale(p)
        if p in hull_set:
            grid[sy][sx] = 'H'  # Hull vertex
        else:
            grid[sy][sx] = '.'  # Interior point
    
    # Print grid
    print('┌' + '─' * width + '┐')
    for row in grid:
        print('│' + ''.join(row) + '│')
    print('└' + '─' * width + '┘')


if __name__ == "__main__":
    # Demo with a few different test cases
    
    print("=== Convex Hull Demo ===\n")
    
    # Test 1: Simple square with interior points
    print("Test 1: Square with interior points")
    points1 = [
        (0, 0), (4, 0), (4, 4), (0, 4),  # corners
        (2, 2), (1, 1), (3, 3), (2, 1)   # interior
    ]
    hull1 = gift_wrapping(points1)
    print(f"Points: {len(points1)}")
    print(f"Hull vertices: {hull1}")
    print(f"Hull size: {len(hull1)} vertices")
    print(f"Area: {calculate_hull_area(hull1):.2f}")
    print(f"Perimeter: {calculate_hull_perimeter(hull1):.2f}")
    visualize_hull(points1, hull1)
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Random-ish scattered points
    print("Test 2: Scattered points")
    points2 = [
        (1, 1), (2, 5), (3, 3), (5, 2), (4, 7),
        (6, 4), (8, 6), (7, 2), (9, 3), (3, 6),
        (5, 5), (4, 3)
    ]
    hull2 = gift_wrapping(points2)
    print(f"Points: {len(points2)}")
    print(f"Hull vertices: {hull2}")
    print(f"Hull size: {len(hull2)} vertices")
    print(f"Area: {calculate_hull_area(hull2):.2f}")
    print(f"Perimeter: {calculate_hull_perimeter(hull2):.2f}")
    visualize_hull(points2, hull2)
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Collinear points (edge case)
    print("Test 3: Points with collinear segments")
    points3 = [
        (0, 0), (1, 1), (2, 2), (3, 3),  # diagonal line
        (3, 0), (0, 3), (1.5, 1.5)       # complete the triangle
    ]
    hull3 = gift_wrapping(points3)
    print(f"Points: {len(points3)}")
    print(f"Hull vertices: {hull3}")
    print(f"Hull size: {len(hull3)} vertices")
    print(f"Area: {calculate_hull_area(hull3):.2f}")