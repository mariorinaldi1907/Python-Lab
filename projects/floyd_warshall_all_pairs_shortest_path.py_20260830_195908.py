"""
Date: 2026-08-30
Built Floyd-Warshall from scratch to find shortest paths between all vertex pairs — threw in actual path reconstruction since that's the useful part anyway.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall algorithm for all-pairs shortest paths.

I wanted to implement this because it's such an elegant dynamic programming
solution. The triple nested loop looks scary O(n³) but for dense graphs or
when you need ALL shortest paths, it's actually perfect.
"""

from typing import List, Tuple, Optional, Dict
import sys


class FloydWarshall:
    """
    All-pairs shortest path using Floyd-Warshall algorithm.
    
    This handles negative edges (but not negative cycles), and I added
    path reconstruction because just knowing distances isn't always enough.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize with number of vertices.
        
        Args:
            num_vertices: Total number of vertices in the graph
        """
        self.n = num_vertices
        # Start with infinity everywhere except diagonal
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        # Next matrix for path reconstruction - initially no intermediate vertices
        self.next_vertex = [[None] * num_vertices for _ in range(num_vertices)]
        
        # Distance from vertex to itself is 0
        for i in range(num_vertices):
            self.dist[i][i] = 0
            self.next_vertex[i][i] = i
    
    def add_edge(self, u: int, v: int, weight: float):
        """
        Add a directed edge to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        self.dist[u][v] = weight
        self.next_vertex[u][v] = v
    
    def compute_shortest_paths(self) -> bool:
        """
        Run Floyd-Warshall algorithm to find all shortest paths.
        
        The core idea: for each vertex k, check if going through k
        gives a shorter path between any pair (i, j).
        
        Returns:
            True if successful, False if negative cycle detected
        """
        # Classic Floyd-Warshall triple loop
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # Can we improve dist[i][j] by going through k?
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        # Path from i to j now goes through same intermediate as i to k
                        self.next_vertex[i][j] = self.next_vertex[i][k]
        
        # Check for negative cycles (diagonal becomes negative)
        for i in range(self.n):
            if self.dist[i][i] < 0:
                return False
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """Get shortest distance from u to v."""
        return self.dist[u][v]
    
    def reconstruct_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the actual shortest path from u to v.
        
        This is why I kept the next_vertex matrix - otherwise we'd only
        have distances with no idea how to actually get there.
        
        Args:
            u: Start vertex
            v: End vertex
            
        Returns:
            List of vertices in the path, or None if no path exists
        """
        if self.dist[u][v] == float('inf'):
            return None
        
        path = []
        current = u
        
        # Follow the next pointers until we reach destination
        while current != v:
            path.append(current)
            current = self.next_vertex[current][v]
            if current is None:
                return None
        
        path.append(v)
        return path
    
    def print_distance_matrix(self):
        """Print the complete distance matrix (useful for debugging)."""
        print("\nDistance Matrix:")
        print("     ", end="")
        for j in range(self.n):
            print(f"{j:6}", end="")
        print()
        
        for i in range(self.n):
            print(f"{i:3}: ", end="")
            for j in range(self.n):
                if self.dist[i][j] == float('inf'):
                    print("   INF", end="")
                else:
                    print(f"{self.dist[i][j]:6.1f}", end="")
            print()


def demo_graph_example():
    """
    Demo with a small graph to show Floyd-Warshall in action.
    
    Using a graph with 5 vertices and some weighted edges including
    a negative edge to show the algorithm handles it fine.
    """
    print("Floyd-Warshall All-Pairs Shortest Path Demo")
    print("=" * 50)
    
    # Create a directed graph with 5 vertices
    fw = FloydWarshall(5)
    
    # Add edges: (from, to, weight)
    edges = [
        (0, 1, 3),
        (0, 2, 8),
        (0, 4, -4),
        (1, 3, 1),
        (1, 4, 7),
        (2, 1, 4),
        (3, 0, 2),
        (3, 2, -5),
        (4, 3, 6),
    ]
    
    print("\nAdding edges:")
    for u, v, w in edges:
        fw.add_edge(u, v, w)
        print(f"  {u} → {v} (weight: {w})")
    
    # Run the algorithm
    print("\nRunning Floyd-Warshall algorithm...")
    if not fw.compute_shortest_paths():
        print("ERROR: Negative cycle detected!")
        return
    
    print("✓ Algorithm completed successfully")
    
    # Show the complete distance matrix
    fw.print_distance_matrix()
    
    # Demonstrate path reconstruction for a few interesting pairs
    print("\nExample Shortest Paths:")
    test_pairs = [(0, 2), (0, 3), (1, 2), (2, 4)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.reconstruct_path(u, v)
        
        if path:
            path_str = " → ".join(map(str, path))
            print(f"  {u} to {v}: distance = {dist:5.1f}, path = {path_str}")
        else:
            print(f"  {u} to {v}: No path exists")


if __name__ == "__main__":
    demo_graph_example()