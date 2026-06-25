"""
Date: 2026-06-25
Built Floyd-Warshall to compute shortest paths between all node pairs in a weighted graph — handles negative edges and detects negative cycles too.
"""

#!/usr/bin/env python3
"""
Floyd-Warshall All-Pairs Shortest Path Algorithm

I wanted a solid implementation that not only finds distances but also
reconstructs the actual paths. Floyd-Warshall is great for dense graphs
and when you need all pairs at once — O(V³) but super clean to implement.
"""

from typing import List, Tuple, Optional, Dict


class FloydWarshall:
    """
    Floyd-Warshall algorithm for finding shortest paths between all pairs of vertices.
    
    Handles negative edge weights and detects negative cycles.
    Uses dynamic programming to iteratively improve path estimates.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph with a given number of vertices.
        
        Args:
            num_vertices: Number of nodes in the graph
        """
        self.n = num_vertices
        # Start with infinity for all distances except self-loops
        self.dist = [[float('inf')] * num_vertices for _ in range(num_vertices)]
        # next[i][j] stores the next vertex on the shortest path from i to j
        self.next = [[None] * num_vertices for _ in range(num_vertices)]
        
        # Distance from a vertex to itself is 0
        for i in range(num_vertices):
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
        self.dist[u][v] = weight
        self.next[u][v] = v
    
    def run(self) -> Tuple[List[List[float]], bool]:
        """
        Execute the Floyd-Warshall algorithm.
        
        The core idea: for each intermediate vertex k, check if going through k
        gives a shorter path between any pair (i, j). This is the DP magic.
        
        Returns:
            Tuple of (distance_matrix, has_negative_cycle)
        """
        # Try using each vertex as an intermediate point
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    # If path i->k->j is shorter than current i->j, update it
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next[i][j] = self.next[i][k]
        
        # Check for negative cycles (diagonal becomes negative)
        has_negative_cycle = any(self.dist[i][i] < 0 for i in range(self.n))
        
        return self.dist, has_negative_cycle
    
    def get_path(self, start: int, end: int) -> Optional[List[int]]:
        """
        Reconstruct the shortest path between two vertices.
        
        Args:
            start: Starting vertex
            end: Ending vertex
            
        Returns:
            List of vertices in the path, or None if no path exists
        """
        if self.dist[start][end] == float('inf'):
            return None
        
        path = []
        current = start
        
        # Follow the next pointers to reconstruct the path
        while current != end:
            path.append(current)
            current = self.next[current][end]
            # Safety check to avoid infinite loops
            if current is None:
                return None
        
        path.append(end)
        return path
    
    def print_distance_matrix(self):
        """Print the distance matrix in a readable format."""
        print("\nAll-Pairs Shortest Distances:")
        print("    ", end="")
        for j in range(self.n):
            print(f"{j:6}", end=" ")
        print()
        
        for i in range(self.n):
            print(f"{i:2}: ", end="")
            for j in range(self.n):
                val = self.dist[i][j]
                if val == float('inf'):
                    print("   INF", end=" ")
                else:
                    print(f"{val:6.1f}", end=" ")
            print()


def demo_basic_graph():
    """Demo with a simple weighted graph showing basic functionality."""
    print("=" * 60)
    print("Demo 1: Basic Weighted Graph")
    print("=" * 60)
    
    # Create a graph with 4 vertices
    # Graph structure:
    #   0 --5--> 1
    #   |        |
    #   2        3
    #   |        |
    #   +--1--> 2 --2--> 3
    fw = FloydWarshall(4)
    fw.add_edge(0, 1, 5)
    fw.add_edge(0, 2, 2)
    fw.add_edge(1, 3, 3)
    fw.add_edge(2, 3, 2)
    
    dist, has_neg_cycle = fw.run()
    
    fw.print_distance_matrix()
    print(f"\nNegative cycle detected: {has_neg_cycle}")
    
    # Show some paths
    print("\nSample Paths:")
    for start, end in [(0, 3), (0, 1), (2, 1)]:
        path = fw.get_path(start, end)
        if path:
            print(f"  {start} → {end}: {' → '.join(map(str, path))} (cost: {dist[start][end]})")
        else:
            print(f"  {start} → {end}: No path exists")


def demo_negative_edges():
    """Demo showing handling of negative edge weights."""
    print("\n" + "=" * 60)
    print("Demo 2: Graph with Negative Edges")
    print("=" * 60)
    
    fw = FloydWarshall(3)
    fw.add_edge(0, 1, 4)
    fw.add_edge(1, 2, 3)
    fw.add_edge(2, 0, -10)  # Negative edge creates a better path
    
    dist, has_neg_cycle = fw.run()
    
    fw.print_distance_matrix()
    print(f"\nNegative cycle detected: {has_neg_cycle}")
    
    path = fw.get_path(1, 0)
    if path:
        print(f"\nPath 1 → 0: {' → '.join(map(str, path))} (cost: {dist[1][0]})")


if __name__ == "__main__":
    print("\n🚀 Floyd-Warshall All-Pairs Shortest Path")
    print("Personal implementation by Mario\n")
    
    demo_basic_graph()
    demo_negative_edges()
    
    print("\n✨ All demos completed successfully!")