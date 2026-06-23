"""
Date: 2026-06-23
Built a convex hull finder using the gift wrapping algorithm because I wanted to visualize point clouds and their boundaries without any external dependencies.
"""

#!/usr/bin/env python3
"""
Convex Hull using Gift Wrapping (Jarvis March) Algorithm

I implemented this because I was working on some clustering visualization
and needed to draw boundaries around point groups. Gift wrapping is slower
than Graham scan for large datasets (O(nh) vs O(n log n)), but it's more
intuitive and works great for small-to-medium point sets.
"""

from typing import List, Tuple
import math


def cross_product(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Calculate the cross product of vectors OA and OB.
    
    Returns positive if counter-clockwise turn, negative if clockwise,
    zero if collinear. This is the core geometric primitive for convex hull.
    
    Args:
        o: Origin point
        a: First point
        b: Second point
    
    Returns:
        Cross product value
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate squared Euclidean distance between two points.
    
    Using squared distance to avoid sqrt for performance — we only
    need relative distances for the gift wrapping algorithm.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Compute the convex hull using the gift wrapping algorithm.
    
    The idea: start from the leftmost point, then repeatedly find the point
    that makes the smallest counter-clockwise angle with the current edge.
    It's like wrapping a string around the points from outside.
    
    Args:
        points: List of (x, y) tuples
    
    Returns:
        List of points forming the convex hull in counter-clockwise order
    """
    if len(points) < 3:
        return points
    
    # Remove duplicates while preserving order-ish (convert to set then back)
    # Actually, let me do this properly to keep original order benefits
    unique_points = []
    seen = set()
    for p in points:
        if p not in seen:
            unique_points.append(p)
            seen.add(p)
    
    points = unique_points
    
    if len(points) < 3:
        return points
    
    # Find the leftmost point (smallest x, break ties with smallest y)
    start = min(points, key=lambda p: (p[0], p[1]))
    
    hull = []
    current = start
    
    while True:
        hull.append(current)
        next_point = points[0]
        
        # Find the most counter-clockwise point from current
        for candidate in points:
            if candidate == current:
                continue
            
            if next_point == current:
                next_point = candidate
                continue
            
            # Check the turn direction
            cp = cross_product(current, next_point, candidate)
            
            if cp > 0:
                # Candidate is more counter-clockwise
                next_point = candidate
            elif cp == 0:
                # Collinear — pick the farther one to avoid intermediate points
                if distance_squared(current, candidate) > distance_squared(current, next_point):
                    next_point = candidate
        
        current = next_point
        
        # Wrapped back to start
        if current == start:
            break
    
    return hull


def polygon_area(vertices: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    This is a nice side effect of having the convex hull — you can
    immediately compute its area.
    
    Args:
        vertices: List of (x, y) tuples in order (clockwise or counter-clockwise)
    
    Returns:
        Area of the polygon
    """
    if len(vertices) < 3:
        return 0.0
    
    area = 0.0
    for i in range(len(vertices)):
        j = (i + 1) % len(vertices)
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    
    return abs(area) / 2.0


def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Cast a ray from the point to infinity and count edge crossings.
    Odd crossings = inside, even = outside.
    
    Args:
        point: (x, y) tuple to test
        polygon: List of vertices forming a closed polygon
    
    Returns:
        True if point is inside or on the boundary
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        # Check if point is on the edge
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside


if __name__ == "__main__":
    # Test with a classic dataset: points forming a rough circle with some interior points
    test_points = [
        (0, 3), (1, 1), (2, 2), (4, 4), (0, 0), (1, 2), (3, 1), (3, 3),
        (2, 1), (4, 2), (2, 3), (3, 2), (1, 3), (4, 0), (0, 2)
    ]
    
    print("=" * 50)
    print("Convex Hull Calculator (Gift Wrapping Algorithm)")
    print("=" * 50)
    print(f"\nInput points: {len(test_points)} total")
    for i, p in enumerate(test_points):
        print(f"  {i+1:2d}. {p}")
    
    # Compute convex hull
    hull = convex_hull(test_points)
    
    print(f"\nConvex Hull: {len(hull)} vertices")
    for i, vertex in enumerate(hull):
        print(f"  {i+1}. {vertex}")
    
    # Calculate area
    area = polygon_area(hull)
    print(f"\nHull Area: {area:.2f} square units")
    
    # Test point containment
    print("\nPoint-in-Polygon Tests:")
    test_cases = [(2, 2), (5, 5), (0, 0), (1.5, 1.5)]
    for test_point in test_cases:
        is_inside = point_in_polygon(test_point, hull)
        status = "INSIDE" if is_inside else "OUTSIDE"
        print(f"  {test_point} is {status} the convex hull")
    
    print("\n" + "=" * 50)