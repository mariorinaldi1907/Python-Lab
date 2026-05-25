"""
Generated: 2026-05-25T04:29:06.942285
Description: A complete implementation of the Bellman-Ford algorithm that finds shortest paths from a source vertex and detects negative weight cycles, demonstrating its advantage over Dijkstra's algorithm.
"""

#!/usr/bin/env python3
"""
Bellman-Ford Shortest Path Algorithm Implementation

This module implements the Bellman-Ford algorithm for finding shortest paths
from a single source vertex to all other vertices in a weighted directed graph.
Unlike Dijkstra's algorithm, Bellman-Ford can handle negative edge weights and
detect negative weight cycles.
"""

from typing import Dict, List, Tuple, Optional
import sys


class Graph:
    """
    A directed weighted graph represented using an adjacency list.
    
    Attributes:
        vertices: Set of all vertices in the graph
        edges: List of tuples (source, destination, weight)
    """
    
    def __init__(self):
        """Initialize an empty graph."""
        self.vertices = set()
        self.edges = []
    
    def add_edge(self, source: int, destination: int, weight: float) -> None:
        """
        Add a directed edge to the graph.
        
        Args:
            source: Starting vertex of the edge
            destination: Ending vertex of the edge
            weight: Weight/cost of the edge
        """
        self.vertices.add(source)
        self.vertices.add(destination)
        self.edges.append((source, destination, weight))
    
    def bellman_ford(self, source: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]], bool]:
        """
        Compute shortest paths from source vertex using Bellman-Ford algorithm.
        
        The algorithm relaxes all edges |V|-1 times, then checks for negative cycles.
        Time complexity: O(V*E), Space complexity: O(V)
        
        Args:
            source: The starting vertex for shortest path computation
            
        Returns:
            A tuple containing:
            - distances: Dictionary mapping vertices to their shortest distance from source
            - predecessors: Dictionary mapping vertices to their predecessor in shortest path
            - has_negative_cycle: Boolean indicating if a negative cycle exists
        """
        # Initialize distances to infinity and predecessors to None
        distances = {vertex: float('inf') for vertex in self.vertices}
        predecessors = {vertex: None for vertex in self.vertices}
        distances[source] = 0
        
        # Relax all edges |V| - 1 times
        num_vertices = len(self.vertices)
        for _ in range(num_vertices - 1):
            for u, v, weight in self.edges:
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
        
        # Check for negative weight cycles
        has_negative_cycle = False
        for u, v, weight in self.edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                has_negative_cycle = True
                break
        
        return distances, predecessors, has_negative_cycle
    
    def get_path(self, predecessors: Dict[int, Optional[int]], 
                 source: int, destination: int) -> Optional[List[int]]:
        """
        Reconstruct the shortest path from source to destination.
        
        Args:
            predecessors: Dictionary of predecessors from bellman_ford
            source: Starting vertex
            destination: Ending vertex
            
        Returns:
            List of vertices forming the path, or None if no path exists
        """
        if predecessors[destination] is None and destination != source:
            return None
        
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        path.reverse()
        return path if path[0] == source else None


def print_shortest_paths(graph: Graph, source: int) -> None:
    """
    Run Bellman-Ford algorithm and print results in a readable format.
    
    Args:
        graph: The graph to analyze
        source: The source vertex for shortest paths
    """
    print(f"Running Bellman-Ford algorithm from source vertex {source}")
    print("=" * 60)
    
    distances, predecessors, has_negative_cycle = graph.bellman_ford(source)
    
    if has_negative_cycle:
        print("⚠️  WARNING: Negative weight cycle detected!")
        print("Shortest paths are not well-defined in this graph.")
        return
    
    print("\nShortest distances from source:")
    for vertex in sorted(distances.keys()):
        dist = distances[vertex]
        if dist == float('inf'):
            print(f"  Vertex {vertex}: UNREACHABLE")
        else:
            print(f"  Vertex {vertex}: {dist}")
    
    print("\nShortest paths:")
    for vertex in sorted(graph.vertices):
        if vertex != source:
            path = graph.get_path(predecessors, source, vertex)
            if path:
                path_str = " -> ".join(map(str, path))
                print(f"  {source} to {vertex}: {path_str} (cost: {distances[vertex]})")
            else:
                print(f"  {source} to {vertex}: NO PATH")


if __name__ == "__main__":
    # Demo 1: Graph with negative edges (but no negative cycle)
    print("DEMO 1: Graph with negative edges")
    print("-" * 60)
    graph1 = Graph()
    graph1.add_edge(0, 1, 4)
    graph1.add_edge(0, 2, 5)
    graph1.add_edge(1, 2, -3)
    graph1.add_edge(1, 3, 6)
    graph1.add_edge(2, 3, 2)
    graph1.add_edge(2, 4, 3)
    graph1.add_edge(3, 4, -2)
    
    print_shortest_paths(graph1, 0)
    
    # Demo 2: Graph with negative cycle
    print("\n\nDEMO 2: Graph with negative weight cycle")
    print("-" * 60)
    graph2 = Graph()
    graph2.add_edge(0, 1, 1)
    graph2.add_edge(1, 2, -1)
    graph2.add_edge(2, 3, -1)
    graph2.add_edge(3, 1, -1)  # Creates negative cycle: 1 -> 2 -> 3 -> 1
    
    print_shortest_paths(graph2, 0)
    
    # Demo 3: Larger graph with mixed weights
    print("\n\nDEMO 3: Larger graph with mixed edge weights")
    print("-" * 60)
    graph3 = Graph()
    edges = [
        (0, 1, 6), (0, 2, 7),
        (1, 2, 8), (1, 3, -4), (1, 4, 5),
        (2, 3, 9), (2, 4, -3),
        (3, 4, 7), (3, 5, 2),
        (4, 5, 3)
    ]
    for src, dst, wt in edges:
        graph3.add_edge(src, dst, wt)
    
    print_shortest_paths(graph3, 0)
```