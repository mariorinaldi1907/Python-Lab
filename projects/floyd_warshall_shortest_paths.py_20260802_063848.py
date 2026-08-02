"""
Date: 2026-08-02
Built Floyd-Warshall all-pairs shortest path finder because I wanted to understand how it handles negative weights better than running Dijkstra n times.
"""

"""
Floyd-Warshall All-Pairs Shortest Path Algorithm

I wanted a clean implementation that not only finds distances but also
reconstructs the actual paths. This is useful when you need shortest paths
between ALL pairs of vertices, especially when negative edge weights are involved.
"""

from typing import List, Tuple, Optional, Dict
import sys


class FloydWarshall:
    """
    Computes all-pairs shortest paths using the Floyd-Warshall algorithm.
    
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
        # Distance matrix - start with infinity everywhere
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        # Next vertex matrix for path reconstruction
        self.next = [[None] * num_vertices for _ in range(num_vertices)]
        
        # Distance from vertex to itself is 0
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
        self.next[u][v] = v  # Direct edge means next hop is the destination
    
    def compute_shortest_paths(self) -> bool:
        """
        Run Floyd-Warshall algorithm to compute all shortest paths.
        
        The core insight: for each intermediate vertex k, check if going
        through k gives a shorter path from i to j than the current best.
        
        Returns:
            True if no negative cycles detected, False otherwise
        """
        # Try using each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # If we can improve the path from i to j by going through k
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next[i][j] = self.next[i][k]  # Path goes through k
        
        # Check for negative cycles (diagonal should still be 0)
        for i in range(self.n):
            if self.dist[i][i] < 0:
                return False
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """
        Get the shortest distance from u to v.
        
        Returns:
            Shortest distance, or infinity if no path exists
        """
        return self.dist[u][v]
    
    def reconstruct_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the shortest path from u to v.
        
        This is why we maintain the 'next' matrix - it lets us walk
        back through the path without storing the entire path for each pair.
        
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
            current = self.next[current][v]
            if current is None:
                return None
            path.append(current)
        
        return path
    
    def get_distance_matrix(self) -> List[List[float]]:
        """Return the complete distance matrix."""
        return [row[:] for row in self.dist]


def print_distance_matrix(fw: FloydWarshall, vertex_names: List[str] = None):
    """
    Pretty print the distance matrix.
    
    Args:
        fw: FloydWarshall instance
        vertex_names: Optional names for vertices (defaults to numbers)
    """
    n = fw.n
    if vertex_names is None:
        vertex_names = [str(i) for i in range(n)]
    
    # Header
    print("\nDistance Matrix:")
    print("     ", end="")
    for name in vertex_names:
        print(f"{name:>6}", end="")
    print()
    
    # Rows
    for i in range(n):
        print(f"{vertex_names[i]:>4} ", end="")
        for j in range(n):
            dist = fw.dist[i][j]
            if dist == float('inf'):
                print(f"{'∞':>6}", end="")
            else:
                print(f"{dist:>6.1f}", end="")
        print()


if __name__ == "__main__":
    # Demo with a small graph that has negative edges
    # This represents a network where some routes have "costs" or "rewards"
    print("Floyd-Warshall Shortest Paths Demo")
    print("=" * 50)
    
    # Create a graph with 5 vertices
    vertex_names = ["A", "B", "C", "D", "E"]
    fw = FloydWarshall(5)
    
    # Add edges (some negative to show the algorithm handles them)
    edges = [
        (0, 1, 3),    # A -> B: 3
        (0, 3, 7),    # A -> D: 7
        (1, 2, 1),    # B -> C: 1
        (1, 3, 2),    # B -> D: 2
        (2, 4, -2),   # C -> E: -2 (negative edge!)
        (3, 2, 4),    # D -> C: 4
        (3, 4, 1),    # D -> E: 1
        (4, 0, 2),    # E -> A: 2
    ]
    
    print("\nAdding edges:")
    for u, v, w in edges:
        fw.add_edge(u, v, w)
        print(f"  {vertex_names[u]} -> {vertex_names[v]}: {w}")
    
    # Compute shortest paths
    print("\nComputing all-pairs shortest paths...")
    has_no_neg_cycle = fw.compute_shortest_paths()
    
    if not has_no_neg_cycle:
        print("WARNING: Negative cycle detected!")
    else:
        print("✓ No negative cycles found")
    
    # Print distance matrix
    print_distance_matrix(fw, vertex_names)
    
    # Show some example paths
    print("\nExample shortest paths:")
    test_pairs = [(0, 4), (1, 0), (0, 2), (3, 1)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.reconstruct_path(u, v)
        
        if path:
            path_str = " -> ".join(vertex_names[i] for i in path)
            print(f"  {vertex_names[u]} to {vertex_names[v]}: "
                  f"distance = {dist:.1f}, path = {path_str}")
        else:
            print(f"  {vertex_names[u]} to {vertex_names[v]}: No path exists")