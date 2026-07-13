"""
Date: 2026-07-13
Built Floyd-Warshall to compute shortest paths between all node pairs — useful when I need the full distance matrix and not just single-source paths.
"""

"""
Floyd-Warshall Algorithm Implementation

Computes shortest paths between all pairs of vertices in a weighted graph.
Works with negative edge weights (but not negative cycles).
Time complexity: O(V^3), Space: O(V^2)

I chose this over running Dijkstra V times because:
1. It's simpler when you need the full distance matrix
2. Handles negative weights (unlike Dijkstra without modifications)
3. The path reconstruction is elegant with the successor matrix
"""

from typing import List, Tuple, Optional, Dict


def floyd_warshall(num_vertices: int, edges: List[Tuple[int, int, float]]) -> Tuple[List[List[float]], List[List[Optional[int]]]]:
    """
    Compute shortest paths between all pairs of vertices using Floyd-Warshall.
    
    Args:
        num_vertices: Number of vertices in the graph (vertices labeled 0 to num_vertices-1)
        edges: List of tuples (from_vertex, to_vertex, weight)
    
    Returns:
        Tuple of (distance_matrix, next_matrix):
            - distance_matrix[i][j] = shortest distance from i to j (inf if no path)
            - next_matrix[i][j] = next vertex on shortest path from i to j (None if no path)
    """
    INF = float('inf')
    
    # Initialize distance matrix with infinities
    dist = [[INF] * num_vertices for _ in range(num_vertices)]
    
    # Distance from a vertex to itself is 0
    for i in range(num_vertices):
        dist[i][i] = 0
    
    # Initialize next matrix for path reconstruction
    # next[i][j] tells us the next vertex to visit when going from i to j
    next_vertex = [[None] * num_vertices for _ in range(num_vertices)]
    
    # Fill in the direct edges
    for u, v, weight in edges:
        dist[u][v] = weight
        next_vertex[u][v] = v
    
    # Core Floyd-Warshall: try using each vertex k as an intermediate point
    # The order matters — k must be the outermost loop
    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                # If going through k is shorter, update
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_vertex[i][j] = next_vertex[i][k]  # Path from i to j goes through k
    
    return dist, next_vertex


def reconstruct_path(start: int, end: int, next_matrix: List[List[Optional[int]]]) -> Optional[List[int]]:
    """
    Reconstruct the shortest path from start to end using the next matrix.
    
    Args:
        start: Starting vertex
        end: Ending vertex
        next_matrix: Next matrix from floyd_warshall
    
    Returns:
        List of vertices forming the path, or None if no path exists
    """
    if next_matrix[start][end] is None:
        return None
    
    path = [start]
    current = start
    
    # Follow the next pointers until we reach the destination
    while current != end:
        current = next_matrix[current][end]
        path.append(current)
    
    return path


def has_negative_cycle(dist_matrix: List[List[float]]) -> bool:
    """
    Check if the graph has a negative cycle by examining the diagonal.
    
    A negative value on the diagonal means there's a negative cycle
    (a vertex has negative distance to itself).
    
    Args:
        dist_matrix: Distance matrix from floyd_warshall
    
    Returns:
        True if negative cycle exists, False otherwise
    """
    for i in range(len(dist_matrix)):
        if dist_matrix[i][i] < 0:
            return True
    return False


def print_distance_matrix(dist: List[List[float]], labels: Optional[List[str]] = None):
    """Pretty print the distance matrix."""
    n = len(dist)
    if labels is None:
        labels = [str(i) for i in range(n)]
    
    # Header
    print("\nDistance Matrix:")
    print("     ", end="")
    for label in labels:
        print(f"{label:>6}", end="")
    print()
    
    # Rows
    for i, label in enumerate(labels):
        print(f"{label:>4} ", end="")
        for j in range(n):
            val = dist[i][j]
            if val == float('inf'):
                print(f"{'∞':>6}", end="")
            else:
                print(f"{val:>6.1f}", end="")
        print()


if __name__ == "__main__":
    # Demo graph: a small road network between cities
    # Cities: 0=SF, 1=LA, 2=Vegas, 3=Phoenix, 4=Denver
    
    print("=" * 60)
    print("Floyd-Warshall Algorithm Demo: Southwest US Road Network")
    print("=" * 60)
    
    num_cities = 5
    city_names = ["SF", "LA", "Vegas", "Phoenix", "Denver"]
    
    # Edges: (from, to, distance in hundreds of miles)
    # I'm making these up but they're roughly realistic
    roads = [
        (0, 1, 3.8),    # SF to LA
        (1, 0, 3.8),    # LA to SF (symmetric)
        (1, 2, 2.7),    # LA to Vegas
        (2, 1, 2.7),    # Vegas to LA
        (1, 3, 3.7),    # LA to Phoenix
        (3, 1, 3.7),    # Phoenix to LA
        (2, 3, 2.9),    # Vegas to Phoenix
        (3, 2, 2.9),    # Phoenix to Vegas
        (2, 4, 7.5),    # Vegas to Denver
        (4, 2, 7.5),    # Denver to Vegas
        (3, 4, 6.0),    # Phoenix to Denver
        (4, 3, 6.0),    # Denver to Phoenix
    ]
    
    print(f"\nComputing shortest paths between {num_cities} cities...")
    print(f"Processing {len(roads)} road segments...\n")
    
    # Run Floyd-Warshall
    distances, next_hop = floyd_warshall(num_cities, roads)
    
    # Check for negative cycles (shouldn't happen with distances!)
    if has_negative_cycle(distances):
        print("⚠️  Warning: Negative cycle detected!")
    else:
        print("✓ No negative cycles detected")
    
    # Print the full distance matrix
    print_distance_matrix(distances, city_names)
    
    # Show some example paths
    print("\n" + "=" * 60)
    print("Example Shortest Paths:")
    print("=" * 60)
    
    test_routes = [(0, 3), (0, 4), (1, 4)]  # SF→Phoenix, SF→Denver, LA→Denver
    
    for start, end in test_routes:
        path = reconstruct_path(start, end, next_hop)
        if path:
            path_names = " → ".join(city_names[i] for i in path)
            distance = distances[start][end]
            print(f"\n{city_names[start]} to {city_names[end]}:")
            print(f"  Path: {path_names}")
            print(f"  Total Distance: {distance * 100:.0f} miles")
        else:
            print(f"\n{city_names[start]} to {city_names[end]}: No path exists")
    
    print("\n" + "=" * 60)