"""
Date: 2026-07-31
Built a convex hull finder using the gift wrapping (Jarvis march) algorithm because I needed something visual and intuitive to understand how convex hulls actually work.
"""

"""
Convex Hull using Gift Wrapping Algorithm (Jarvis March)

I wanted to understand convex hulls beyond just theory, so I implemented
the gift wrapping algorithm. It's not the fastest (O(nh) where h is hull size),
but it's super intuitive — you literally "wrap" around the points.
"""

from typing import List, Tuple
import random


def cross_product(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Calculate cross product of vectors OA and OB.
    
    Positive means counter-clockwise turn, negative means clockwise,
    zero means collinear. This is the core of determining if we're
    wrapping left or right around the point cloud.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def distance_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Squared Euclidean distance between two points.
    
    Using squared distance to avoid sqrt() — we only need relative
    ordering anyway for tie-breaking collinear points.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def gift_wrapping_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Compute convex hull using the gift wrapping algorithm.
    
    The idea: start from the leftmost point (guaranteed on hull), then
    keep picking the "most counterclockwise" point relative to current
    direction until we wrap back to start.
    
    Returns points in counter-clockwise order starting from leftmost point.
    """
    n = len(points)
    if n < 3:
        return points  # Hull is the points themselves
    
    # Remove duplicates — they mess with the algorithm
    points = list(set(points))
    n = len(points)
    
    if n < 3:
        return points
    
    # Find the leftmost point (lowest x, ties broken by lowest y)
    # This point is guaranteed to be on the convex hull
    leftmost = min(points, key=lambda p: (p[0], p[1]))
    
    hull = []
    current = leftmost
    
    while True:
        hull.append(current)
        
        # Find the most counterclockwise point relative to current
        # Start by assuming the next point is the first one that isn't current
        next_point = points[0]
        if next_point == current:
            next_point = points[1] if n > 1 else points[0]
        
        for candidate in points:
            if candidate == current:
                continue
            
            # Check if candidate is more counterclockwise than next_point
            cp = cross_product(current, next_point, candidate)
            
            if cp > 0:
                # Candidate is more counterclockwise, it's our new leader
                next_point = candidate
            elif cp == 0:
                # Collinear points! Pick the farthest one to avoid
                # adding interior points on hull edges
                if distance_squared(current, candidate) > distance_squared(current, next_point):
                    next_point = candidate
        
        current = next_point
        
        # We've wrapped around back to start
        if current == leftmost:
            break
    
    return hull


def print_hull_visualization(points: List[Tuple[float, float]], hull: List[Tuple[float, float]]):
    """
    Print a simple ASCII visualization of points and hull.
    
    Not pretty, but good enough to see what's happening. I scale
    everything to fit in a small grid.
    """
    if not points:
        return
    
    # Find bounds and scale to 40x20 grid
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    width, height = 60, 20
    
    def scale(p: Tuple[float, float]) -> Tuple[int, int]:
        if max_x - min_x == 0:
            sx = width // 2
        else:
            sx = int((p[0] - min_x) / (max_x - min_x) * (width - 1))
        
        if max_y - min_y == 0:
            sy = height // 2
        else:
            sy = int((p[1] - min_y) / (max_y - min_y) * (height - 1))
        
        return sx, height - 1 - sy  # Flip y for screen coordinates
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Mark all points
    for p in points:
        x, y = scale(p)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '·'
    
    # Mark hull points
    hull_set = set(hull)
    for p in hull:
        x, y = scale(p)
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = 'H'
    
    print("\n".join("".join(row) for row in grid))
    print(f"\nPoints: {len(points)} | Hull vertices: {len(hull)}")


if __name__ == "__main__":
    # Demo 1: Random points in a square
    print("=" * 60)
    print("Demo 1: Random points scattered in a square")
    print("=" * 60)
    
    random.seed(42)  # Reproducible results
    random_points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(30)]
    
    hull = gift_wrapping_convex_hull(random_points)
    
    print_hull_visualization(random_points, hull)
    print("\nHull vertices (counter-clockwise):")
    for i, point in enumerate(hull):
        print(f"  {i+1}. ({point[0]:.2f}, {point[1]:.2f})")
    
    # Demo 2: Points forming a specific shape (star-ish)
    print("\n" + "=" * 60)
    print("Demo 2: Points in a circular-ish pattern with some interior")
    print("=" * 60)
    
    import math
    circle_points = []
    for i in range(12):
        angle = 2 * math.pi * i / 12
        circle_points.append((50 + 40 * math.cos(angle), 50 + 40 * math.sin(angle)))
    
    # Add some interior points
    circle_points.extend([(50, 50), (55, 55), (45, 50), (50, 45)])
    
    hull2 = gift_wrapping_convex_hull(circle_points)
    
    print_hull_visualization(circle_points, hull2)
    print("\nHull vertices (counter-clockwise):")
    for i, point in enumerate(hull2):
        print(f"  {i+1}. ({point[0]:.2f}, {point[1]:.2f})")
    
    # Demo 3: Edge case — collinear points
    print("\n" + "=" * 60)
    print("Demo 3: Collinear points (should form a line segment)")
    print("=" * 60)
    
    collinear = [(i * 10.0, i * 5.0) for i in range(8)]
    hull3 = gift_wrapping_convex_hull(collinear)
    
    print(f"Input points: {collinear}")
    print(f"Hull: {hull3}")
    print("(Only endpoints should be in hull for perfectly collinear points)")