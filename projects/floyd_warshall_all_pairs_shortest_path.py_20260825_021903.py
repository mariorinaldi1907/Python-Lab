"""
Date: 2026-08-25
Built Floyd-Warshall to compute shortest paths between all node pairs — needed this for a graph analysis side project and wanted cycle detection too.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall algorithm for finding shortest paths between all pairs of nodes.

I implemented this because I was working on analyzing some dependency graphs
and needed to compute distances between all nodes efficiently. Floyd-Warshall
is perfect when you need the full distance matrix and your graph isn't huge.
"""

import sys
from typing import List, Tuple, Optional, Dict


class FloydWarshall:
    """
    Computes all-pairs shortest paths using the Floyd-Warshall algorithm.
    
    Works with weighted directed graphs, handles negative weights, and can
    detect negative cycles. Time complexity is O(V^3) which isn't amazing
    for sparse graphs, but it's dead simple to implement and works great
    for dense graphs or when you actually need all pairs.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph with a given number of vertices.
        
        Args:
            num_vertices: Number of nodes in the graph
        """
        self.n = num_vertices
        # Start with infinity for all pairs except diagonal (self-loops = 0)
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        self.next_vertex = [[None] * num_vertices for _ in range(num_vertices)]
        
        # Distance from a node to itself is 0
        for i in range(num_vertices):
            self.dist[i][i] = 0
    
    def add_edge(self, u: int, v: int, weight: float):
        """
        Add a directed edge from u to v with given weight.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        self.dist[u][v] = weight
        self.next_vertex[u][v] = v  # For path reconstruction
    
    def compute_shortest_paths(self) -> bool:
        """
        Run Floyd-Warshall to compute all shortest paths.
        
        The core algorithm: for each intermediate vertex k, check if routing
        through k gives a shorter path between any pair (i, j). This is why
        it's O(V^3) — three nested loops over all vertices.
        
        Returns:
            True if no negative cycles detected, False otherwise
        """
        n = self.n
        
        # The main Floyd-Warshall triple loop
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # If going i -> k -> j is shorter than current i -> j
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next_vertex[i][j] = self.next_vertex[i][k]
        
        # Check for negative cycles — if we can improve distance to self
        for i in range(n):
            if self.dist[i][i] < 0:
                return False
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """
        Get the shortest distance from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            Shortest distance, or float('inf') if no path exists
        """
        return self.dist[u][v]
    
    def reconstruct_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the actual shortest path from u to v.
        
        This is why we maintain the next_vertex matrix — it lets us
        trace back the path without storing all paths explicitly.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            List of vertices forming the path, or None if no path exists
        """
        if self.dist[u][v] == float('inf'):
            return None
        
        path = [u]
        current = u
        
        while current != v:
            current = self.next_vertex[current][v]
            if current is None:
                return None
            path.append(current)
        
        return path
    
    def print_distance_matrix(self, vertex_names: Optional[Dict[int, str]] = None):
        """
        Pretty print the distance matrix.
        
        Args:
            vertex_names: Optional mapping from vertex indices to names
        """
        n = self.n
        names = vertex_names if vertex_names else {i: str(i) for i in range(n)}
        
        print("\nDistance Matrix:")
        print("     ", end="")
        for j in range(n):
            print(f"{names[j]:>6}", end="")
        print()
        
        for i in range(n):
            print(f"{names[i]:>4}:", end="")
            for j in range(n):
                val = self.dist[i][j]
                if val == float('inf'):
                    print("   inf", end="")
                else:
                    print(f"{val:6.1f}", end="")
            print()


if __name__ == "__main__":
    # Demo with a small graph representing city distances
    # I wanted to test both positive/negative weights and path reconstruction
    
    print("=== Floyd-Warshall All-Pairs Shortest Path Demo ===\n")
    
    # Create a graph with 5 cities
    cities = {0: "NYC", 1: "BOS", 2: "DC", 3: "MIA", 4: "CHI"}
    fw = FloydWarshall(5)
    
    # Add some edges (distances in arbitrary units)
    # NYC -> BOS: 215, NYC -> DC: 225, etc.
    edges = [
        (0, 1, 215),  # NYC to Boston
        (0, 2, 225),  # NYC to DC
        (1, 0, 215),  # Boston to NYC (symmetric)
        (1, 4, 980),  # Boston to Chicago
        (2, 3, 1050), # DC to Miami
        (3, 2, 1050), # Miami to DC
        (4, 0, 790),  # Chicago to NYC
        (4, 1, 980),  # Chicago to Boston
    ]
    
    for u, v, w in edges:
        fw.add_edge(u, v, w)
    
    # Compute all shortest paths
    no_negative_cycles = fw.compute_shortest_paths()
    
    if not no_negative_cycles:
        print("ERROR: Negative cycle detected!")
        sys.exit(1)
    
    # Print the complete distance matrix
    fw.print_distance_matrix(cities)
    
    # Show a few example paths
    print("\n=== Example Shortest Paths ===")
    test_pairs = [(0, 3), (1, 3), (4, 2)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.reconstruct_path(u, v)
        
        if path:
            path_str = " -> ".join(cities[node] for node in path)
            print(f"\n{cities[u]} to {cities[v]}:")
            print(f"  Distance: {dist:.1f}")
            print(f"  Path: {path_str}")
        else:
            print(f"\n{cities[u]} to {cities[v]}: No path exists")
    
    print("\n✓ Floyd-Warshall completed successfully!")
```