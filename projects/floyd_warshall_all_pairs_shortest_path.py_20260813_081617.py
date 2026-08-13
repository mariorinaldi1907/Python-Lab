"""
Date: 2026-08-13
Built Floyd-Warshall to find shortest paths between all vertex pairs — wanted to compare it against running Dijkstra repeatedly for a research problem.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall Algorithm for All-Pairs Shortest Paths

I needed this for analyzing fully-connected graphs where I wanted distances
between every pair of nodes. Floyd-Warshall is simpler than running Dijkstra
V times, especially for dense graphs.

Time: O(V^3), Space: O(V^2)
"""

from typing import Dict, List, Tuple, Optional


class FloydWarshall:
    """
    Computes shortest paths between all pairs of vertices in a weighted graph.
    
    Handles negative edge weights but detects negative cycles.
    """
    
    def __init__(self, vertices: List[int]):
        """
        Initialize the algorithm with a list of vertex identifiers.
        
        Args:
            vertices: List of vertex IDs (can be any integers)
        """
        self.vertices = sorted(vertices)
        self.n = len(self.vertices)
        # Map vertex ID to index for internal matrix representation
        self.vertex_to_idx = {v: i for i, v in enumerate(self.vertices)}
        
        # Distance matrix: dist[i][j] = shortest distance from vertex i to j
        self.dist = [[float('inf')] * self.n for _ in range(self.n)]
        
        # Next matrix: next[i][j] = next vertex on shortest path from i to j
        # This allows us to reconstruct paths, not just compute distances
        self.next = [[None] * self.n for _ in range(self.n)]
        
        # Distance from any vertex to itself is 0
        for i in range(self.n):
            self.dist[i][i] = 0
            self.next[i][i] = i
    
    def add_edge(self, u: int, v: int, weight: float):
        """
        Add a directed edge to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        i = self.vertex_to_idx[u]
        j = self.vertex_to_idx[v]
        self.dist[i][j] = weight
        self.next[i][j] = j
    
    def compute(self) -> bool:
        """
        Run the Floyd-Warshall algorithm.
        
        The core insight: for each intermediate vertex k, check if routing
        through k gives a shorter path between any pair (i, j).
        
        Returns:
            True if no negative cycles detected, False otherwise
        """
        # Try each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # If going i -> k -> j is shorter than current i -> j
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        # Path from i to j now goes through same next vertex
                        # as path from i to k
                        self.next[i][j] = self.next[i][k]
        
        # Check for negative cycles (diagonal becomes negative)
        for i in range(self.n):
            if self.dist[i][i] < 0:
                return False
        
        return True
    
    def get_distance(self, u: int, v: int) -> float:
        """
        Get the shortest distance from vertex u to vertex v.
        
        Returns:
            Shortest distance, or float('inf') if no path exists
        """
        i = self.vertex_to_idx[u]
        j = self.vertex_to_idx[v]
        return self.dist[i][j]
    
    def get_path(self, u: int, v: int) -> Optional[List[int]]:
        """
        Reconstruct the shortest path from u to v.
        
        This is why I maintain the next matrix — being able to show
        the actual path is way more useful than just the distance.
        
        Returns:
            List of vertices forming the shortest path, or None if no path
        """
        i = self.vertex_to_idx[u]
        j = self.vertex_to_idx[v]
        
        if self.dist[i][j] == float('inf'):
            return None
        
        path = []
        current = i
        
        while current != j:
            path.append(self.vertices[current])
            current = self.next[current][j]
            if current is None:
                return None
        
        path.append(self.vertices[j])
        return path
    
    def print_distance_matrix(self):
        """Pretty-print the distance matrix for debugging."""
        print("\nDistance Matrix:")
        print("     ", end="")
        for v in self.vertices:
            print(f"{v:5}", end=" ")
        print()
        
        for i, u in enumerate(self.vertices):
            print(f"{u:3}: ", end="")
            for j in range(self.n):
                val = self.dist[i][j]
                if val == float('inf'):
                    print("  inf", end=" ")
                else:
                    print(f"{val:5.1f}", end=" ")
            print()


if __name__ == "__main__":
    # Demo on a small graph with some interesting paths
    # Graph from CLRS textbook, slightly modified
    print("=== Floyd-Warshall All-Pairs Shortest Paths ===\n")
    
    vertices = [1, 2, 3, 4, 5]
    fw = FloydWarshall(vertices)
    
    # Building a graph where shortest paths aren't always direct edges
    edges = [
        (1, 2, 3),
        (1, 3, 8),
        (1, 5, -4),
        (2, 4, 1),
        (2, 5, 7),
        (3, 2, 4),
        (4, 1, 2),
        (4, 3, -5),
        (5, 4, 6),
    ]
    
    print("Adding edges:")
    for u, v, w in edges:
        fw.add_edge(u, v, w)
        print(f"  {u} -> {v} (weight: {w})")
    
    print("\nRunning Floyd-Warshall...")
    has_no_negative_cycle = fw.compute()
    
    if not has_no_negative_cycle:
        print("WARNING: Negative cycle detected!")
    else:
        print("No negative cycles found.")
    
    fw.print_distance_matrix()
    
    # Show some interesting paths
    print("\n=== Sample Shortest Paths ===")
    test_pairs = [(1, 3), (1, 4), (3, 5), (2, 1)]
    
    for u, v in test_pairs:
        dist = fw.get_distance(u, v)
        path = fw.get_path(u, v)
        
        if path:
            path_str = " -> ".join(map(str, path))
            print(f"{u} to {v}: distance = {dist:5.1f}, path = {path_str}")
        else:
            print(f"{u} to {v}: no path exists")