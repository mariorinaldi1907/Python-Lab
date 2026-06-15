"""
Date: 2026-06-15
Built Floyd-Warshall algorithm to find shortest paths between all vertex pairs — wanted something that could handle negative weights unlike Dijkstra.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall All-Pairs Shortest Path Algorithm

I needed an algorithm that could find shortest paths between ALL pairs of vertices
in one go, and also handle negative edge weights. Floyd-Warshall is perfect for this.
It's a dynamic programming approach that's super elegant — just three nested loops.

Time: O(V^3), Space: O(V^2)
"""

from typing import List, Dict, Tuple, Optional


class FloydWarshall:
    """
    Computes shortest paths between all pairs of vertices using Floyd-Warshall.
    
    This implementation also tracks the actual paths, not just distances.
    I use a 'next' matrix to reconstruct paths efficiently.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the algorithm with a given number of vertices.
        
        Args:
            num_vertices: Number of vertices in the graph (0-indexed)
        """
        self.n = num_vertices
        # Using float('inf') for unreachable pairs initially
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        # Next matrix helps us reconstruct the actual path
        self.next = [[None] * num_vertices for _ in range(num_vertices)]
        
        # Distance from a vertex to itself is always 0
        for i in range(num_vertices):
            self.dist[i][i] = 0
    
    def add_edge(self, u: int, v: int, weight: float) -> None:
        """
        Add a directed edge to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        self.dist[u][v] = weight
        self.next[u][v] = v  # Direct edge means next step from u to v is v itself
    
    def compute(self) -> bool:
        """
        Run the Floyd-Warshall algorithm.
        
        The core idea: for each intermediate vertex k, check if going through k
        gives a shorter path from i to j than the current best path.
        
        Returns:
            True if no negative cycles detected, False otherwise
        """
        # The magic: try each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # If going through k is better, update distance and path
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next[i][j] = self.next[i][k]  # Path goes through k
        
        # Check for negative cycles: if we can still improve distance to self
        for i in range(self.n):
            if self.dist[i][i] < 0:
                return False  # Negative cycle detected
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """
        Get the shortest distance from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            Shortest distance, or inf if unreachable
        """
        return self.dist[u][v]
    
    def get_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the actual shortest path from u to v.
        
        This is why we keep the 'next' matrix — makes reconstruction O(V) worst case.
        
        Args:
            u: Source vertex
            v: Destination vertex
            
        Returns:
            List of vertices in the path, or None if no path exists
        """
        if self.dist[u][v] == float('inf'):
            return None  # No path exists
        
        path = [u]
        while u != v:
            u = self.next[u][v]
            if u is None:
                return None  # Path broken (shouldn't happen if dist is finite)
            path.append(u)
        
        return path
    
    def print_distance_matrix(self) -> None:
        """Pretty print the distance matrix for debugging."""
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


def demo_graph():
    """
    Demo with a small weighted directed graph.
    
    I'm using a 5-vertex graph with some negative edges to show
    that Floyd-Warshall handles them fine (unlike Dijkstra).
    """
    print("=" * 60)
    print("Floyd-Warshall All-Pairs Shortest Path Demo")
    print("=" * 60)
    
    # Create a graph with 5 vertices (0-4)
    fw = FloydWarshall(5)
    
    # Add edges: (from, to, weight)
    # I deliberately included a negative edge (1->2) to show it works
    edges = [
        (0, 1, 3),
        (0, 2, 8),
        (0, 4, -4),
        (1, 3, 1),
        (1, 4, 7),
        (2, 1, 4),
        (3, 0, 2),
        (3, 2, -5),  # Negative edge
        (4, 3, 6),
    ]
    
    print("\nAdding edges:")
    for u, v, w in edges:
        fw.add_edge(u, v, w)
        print(f"  {u} -> {v} (weight: {w})")
    
    # Run the algorithm
    print("\nRunning Floyd-Warshall...")
    no_negative_cycle = fw.compute()
    
    if not no_negative_cycle:
        print("ERROR: Negative cycle detected!")
        return
    
    print("Success! No negative cycles found.")
    
    # Show the distance matrix
    fw.print_distance_matrix()
    
    # Show some specific paths
    print("\n" + "=" * 60)
    print("Sample Shortest Paths:")
    print("=" * 60)
    
    test_pairs = [(0, 2), (0, 3), (2, 4), (1, 0)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.get_path(u, v)
        
        if path:
            path_str = " -> ".join(map(str, path))
            print(f"\n{u} to {v}:")
            print(f"  Distance: {dist}")
            print(f"  Path: {path_str}")
        else:
            print(f"\n{u} to {v}: No path exists")


if __name__ == "__main__":
    demo_graph()