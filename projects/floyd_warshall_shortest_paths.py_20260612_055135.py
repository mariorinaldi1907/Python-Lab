"""
Date: 2026-06-12
Built Floyd-Warshall algorithm to find shortest paths between all pairs of vertices — wanted to compare it against running Dijkstra n times for a project.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall Algorithm Implementation

Computes shortest paths between all pairs of vertices in a weighted graph.
Works with negative edge weights (but not negative cycles).
Time complexity: O(V^3), Space complexity: O(V^2)

I needed this for analyzing connectivity in a network graph where I wanted
all-pairs distances rather than running Dijkstra repeatedly.
"""


def floyd_warshall(graph):
    """
    Run Floyd-Warshall algorithm on a graph represented as adjacency matrix.
    
    Args:
        graph: 2D list where graph[i][j] is the weight from vertex i to j.
               Use float('inf') for no direct edge, 0 for self-loops.
    
    Returns:
        dist: 2D list of shortest distances between all pairs
        next_vertex: 2D list for path reconstruction (or None if no path exists)
    """
    n = len(graph)
    
    # Initialize distance matrix as a copy of the input graph
    # We need a deep copy because we'll modify it
    dist = [row[:] for row in graph]
    
    # Initialize next_vertex matrix for path reconstruction
    # next_vertex[i][j] tells us the next vertex to go to from i towards j
    next_vertex = [[None for _ in range(n)] for _ in range(n)]
    
    # Set up initial next_vertex values for direct edges
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                next_vertex[i][j] = j
    
    # Core Floyd-Warshall: try using each vertex k as an intermediate point
    # This is the heart of the algorithm - for each pair (i,j), we check
    # if going through k gives us a shorter path
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # If path i->k->j is shorter than current i->j, update it
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_vertex[i][j] = next_vertex[i][k]
    
    return dist, next_vertex


def reconstruct_path(next_vertex, start, end):
    """
    Reconstruct the shortest path from start to end using next_vertex matrix.
    
    Args:
        next_vertex: The path reconstruction matrix from floyd_warshall
        start: Starting vertex index
        end: Ending vertex index
    
    Returns:
        List of vertex indices forming the path, or None if no path exists
    """
    if next_vertex[start][end] is None:
        return None
    
    path = [start]
    current = start
    
    # Follow the next_vertex pointers until we reach the destination
    while current != end:
        current = next_vertex[current][end]
        path.append(current)
    
    return path


def detect_negative_cycle(dist):
    """
    Check if the graph contains a negative cycle.
    
    A negative cycle exists if any vertex has a negative distance to itself
    after running Floyd-Warshall.
    
    Args:
        dist: Distance matrix from floyd_warshall
    
    Returns:
        True if negative cycle detected, False otherwise
    """
    n = len(dist)
    for i in range(n):
        if dist[i][i] < 0:
            return True
    return False


def print_distance_matrix(dist, vertex_names=None):
    """Pretty print the distance matrix with optional vertex labels."""
    n = len(dist)
    if vertex_names is None:
        vertex_names = [str(i) for i in range(n)]
    
    # Print header
    print("     ", end="")
    for name in vertex_names:
        print(f"{name:>6}", end="")
    print()
    
    # Print each row
    for i in range(n):
        print(f"{vertex_names[i]:>4} ", end="")
        for j in range(n):
            val = dist[i][j]
            if val == float('inf'):
                print("   INF", end="")
            else:
                print(f"{val:6.1f}", end="")
        print()


if __name__ == "__main__":
    # Demo graph: a small network with 5 vertices
    # Using cities as an example because it's more intuitive than abstract nodes
    INF = float('inf')
    
    # Adjacency matrix representation
    # 0=A, 1=B, 2=C, 3=D, 4=E
    graph = [
        [0,   4,   INF, INF, INF],  # A connects to B
        [INF, 0,   3,   INF, 7],    # B connects to C and E
        [INF, INF, 0,   1,   INF],  # C connects to D
        [INF, INF, INF, 0,   2],    # D connects to E
        [INF, INF, 2,   INF, 0],    # E connects back to C (creates alternate paths)
    ]
    
    vertex_names = ['A', 'B', 'C', 'D', 'E']
    
    print("Floyd-Warshall All-Pairs Shortest Path\n")
    print("Input graph (adjacency matrix):")
    print_distance_matrix(graph, vertex_names)
    
    # Run the algorithm
    dist, next_vertex = floyd_warshall(graph)
    
    print("\n" + "="*50)
    print("Shortest distances between all pairs:")
    print_distance_matrix(dist, vertex_names)
    
    # Check for negative cycles
    if detect_negative_cycle(dist):
        print("\n⚠️  Warning: Graph contains a negative cycle!")
    
    # Demo path reconstruction
    print("\n" + "="*50)
    print("Sample path reconstructions:\n")
    
    test_paths = [(0, 4), (0, 3), (1, 4), (4, 3)]
    
    for start, end in test_paths:
        path = reconstruct_path(next_vertex, start, end)
        if path:
            path_str = " -> ".join(vertex_names[v] for v in path)
            distance = dist[start][end]
            print(f"{vertex_names[start]} to {vertex_names[end]}: {path_str} (distance: {distance})")
        else:
            print(f"{vertex_names[start]} to {vertex_names[end]}: No path exists")