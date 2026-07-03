"""
Date: 2026-07-03
Built Floyd-Warshall algorithm to find shortest paths between all node pairs in a weighted graph — includes full path reconstruction which I needed for a side project.
"""

"""
Floyd-Warshall Algorithm Implementation
Computes shortest paths between all pairs of vertices in a weighted graph.
Handles negative edges but detects negative cycles.

I wrote this because I needed to precompute distances between all nodes
in a small graph, and Floyd-Warshall is perfect for dense graphs where
you need the full distance matrix anyway.
"""

from typing import List, Tuple, Optional, Dict
import sys


class FloydWarshall:
    """
    All-pairs shortest path using Floyd-Warshall algorithm.
    
    Time complexity: O(V^3)
    Space complexity: O(V^2)
    Works with negative edges but detects negative cycles.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph with a given number of vertices.
        
        Args:
            num_vertices: Number of vertices in the graph
        """
        self.n = num_vertices
        # Using infinity for unreachable nodes initially
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        # For path reconstruction - stores the next vertex on shortest path
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
        Run Floyd-Warshall algorithm to compute all shortest paths.
        
        The core idea: for each intermediate vertex k, check if going
        through k gives a shorter path between any pair (i, j).
        
        Returns:
            True if successful, False if negative cycle detected
        """
        # The key insight: try each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # If path i->k->j is shorter than current i->j
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        # Path reconstruction: to go from i to j, first go to
                        # wherever you'd go from i to reach k
                        self.next_vertex[i][j] = self.next_vertex[i][k]
        
        # Check for negative cycles - if we can improve distance to ourselves
        # then we have a negative cycle
        for i in range(self.n):
            if self.dist[i][i] < 0:
                return False
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """
        Get shortest distance between vertices u and v.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            Shortest distance, or inf if no path exists
        """
        return self.dist[u][v]
    
    def reconstruct_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the actual shortest path from u to v.
        
        This was the tricky part - you need to follow the next_vertex
        pointers to build the path. I always mess this up on the first try.
        
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
    
    def print_distance_matrix(self):
        """
        Pretty print the distance matrix.
        Useful for debugging and visualizing results.
        """
        print("\nDistance Matrix:")
        print("     ", end="")
        for j in range(self.n):
            print(f"{j:6}", end="")
        print()
        
        for i in range(self.n):
            print(f"{i:3}: ", end="")
            for j in range(self.n):
                val = self.dist[i][j]
                if val == float('inf'):
                    print("   inf", end="")
                else:
                    print(f"{val:6.1f}", end="")
            print()


def demo_basic_graph():
    """
    Demonstrate Floyd-Warshall on a simple weighted graph.
    This is the classic textbook example with 4 vertices.
    """
    print("=" * 60)
    print("Demo: Basic Weighted Graph")
    print("=" * 60)
    
    fw = FloydWarshall(4)
    
    # Building a small graph with some negative edges
    edges = [
        (0, 1, 3),
        (0, 3, 7),
        (1, 0, 8),
        (1, 2, 2),
        (2, 0, 5),
        (2, 3, 1),
        (3, 0, 2),
    ]
    
    print("\nAdding edges:")
    for u, v, w in edges:
        fw.add_edge(u, v, w)
        print(f"  {u} -> {v} (weight: {w})")
    
    if not fw.compute_shortest_paths():
        print("\nNegative cycle detected!")
        return
    
    fw.print_distance_matrix()
    
    # Show some specific paths
    print("\nSample shortest paths:")
    test_pairs = [(0, 2), (1, 3), (3, 2)]
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.reconstruct_path(u, v)
        print(f"  {u} -> {v}: distance = {dist}, path = {path}")


if __name__ == "__main__":
    demo_basic_graph()