"""
Date: 2026-06-18
Built Floyd-Warshall algorithm to find shortest paths between all vertex pairs — wanted something that could handle negative edges unlike Dijkstra.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall All-Pairs Shortest Path Algorithm

I wanted to implement this after running into a problem where I needed distances
between ALL pairs of nodes. Dijkstra would work but you'd have to run it V times.
Floyd-Warshall does it in one shot with a cleaner O(V³) approach.

Plus it handles negative edge weights, which is pretty cool.
"""

import sys
from typing import List, Tuple, Optional


class FloydWarshall:
    """
    Computes shortest paths between all pairs of vertices in a weighted graph.
    
    Can detect negative cycles and handles negative edge weights (unlike Dijkstra).
    Uses dynamic programming — the key insight is that shortest path from i to j
    either goes through vertex k or it doesn't.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize with number of vertices.
        
        Args:
            num_vertices: Number of nodes in the graph
        """
        self.n = num_vertices
        # Start with infinity everywhere except diagonal (distance to self = 0)
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        self.next_vertex = [[None] * num_vertices for _ in range(num_vertices)]
        
        for i in range(num_vertices):
            self.dist[i][i] = 0
    
    def add_edge(self, u: int, v: int, weight: float):
        """
        Add a directed edge to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        self.dist[u][v] = weight
        # Track next vertex for path reconstruction
        self.next_vertex[u][v] = v
    
    def compute_shortest_paths(self) -> bool:
        """
        Run Floyd-Warshall algorithm to compute all shortest paths.
        
        The triple nested loop is the heart of it — for each intermediate vertex k,
        we check if routing through k gives us a shorter path from i to j.
        
        Returns:
            True if successful, False if negative cycle detected
        """
        # This is the DP magic — try each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # Can we improve i→j by going through k?
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next_vertex[i][j] = self.next_vertex[i][k]
        
        # Check for negative cycles — if we can still improve distance to self, we have a problem
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
        
        This is why we kept the next_vertex matrix — lets us walk the path.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            List of vertices in the path, or None if no path exists
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
    
    def print_distance_matrix(self):
        """Pretty print the distance matrix — useful for debugging."""
        print("\nDistance Matrix:")
        print("     ", end="")
        for j in range(self.n):
            print(f"{j:6}", end="")
        print()
        
        for i in range(self.n):
            print(f"{i:3}:", end="")
            for j in range(self.n):
                if self.dist[i][j] == float('inf'):
                    print("   INF", end="")
                else:
                    print(f"{self.dist[i][j]:6.1f}", end="")
            print()


def demo_basic_graph():
    """Run a basic demo with a simple weighted graph."""
    print("=== Basic Graph Demo ===")
    print("Creating a graph with 4 vertices...")
    
    # Create a small directed graph
    fw = FloydWarshall(4)
    
    # Add some edges with various weights
    fw.add_edge(0, 1, 3)
    fw.add_edge(0, 3, 7)
    fw.add_edge(1, 2, 1)
    fw.add_edge(1, 3, 2)
    fw.add_edge(2, 3, 1)
    fw.add_edge(3, 0, 2)
    
    print("Running Floyd-Warshall algorithm...")
    if not fw.compute_shortest_paths():
        print("ERROR: Negative cycle detected!")
        return
    
    fw.print_distance_matrix()
    
    # Show some specific paths
    print("\nSample shortest paths:")
    test_pairs = [(0, 2), (0, 3), (3, 1)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.reconstruct_path(u, v)
        print(f"  {u} → {v}: distance = {dist}, path = {' → '.join(map(str, path))}")


def demo_negative_cycle():
    """Demo showing negative cycle detection."""
    print("\n=== Negative Cycle Detection Demo ===")
    print("Creating a graph with a negative cycle...")
    
    fw = FloydWarshall(3)
    fw.add_edge(0, 1, 1)
    fw.add_edge(1, 2, -2)
    fw.add_edge(2, 0, -1)  # This creates a negative cycle: 0→1→2→0 = -2
    
    print("Running Floyd-Warshall algorithm...")
    if not fw.compute_shortest_paths():
        print("✓ Negative cycle detected (as expected)!")
    else:
        print("ERROR: Should have detected negative cycle!")


if __name__ == "__main__":
    demo_basic_graph()
    demo_negative_cycle()
    
    print("\n=== Custom Graph Example ===")
    print("Building a road network with 5 cities...")
    
    # Model a simple road network
    cities = FloydWarshall(5)
    cities.add_edge(0, 1, 10)
    cities.add_edge(0, 4, 5)
    cities.add_edge(1, 2, 1)
    cities.add_edge(1, 4, 2)
    cities.add_edge(2, 3, 4)
    cities.add_edge(3, 2, 6)
    cities.add_edge(3, 0, 7)
    cities.add_edge(4, 1, 3)
    cities.add_edge(4, 2, 9)
    cities.add_edge(4, 3, 2)
    
    cities.compute_shortest_paths()
    cities.print_distance_matrix()
    
    print("\nFinding route from city 0 to city 3:")
    path = cities.reconstruct_path(0, 3)
    dist = cities.get_distance(0, 3)
    print(f"  Best route: {' → '.join(map(str, path))}")
    print(f"  Total distance: {dist}")