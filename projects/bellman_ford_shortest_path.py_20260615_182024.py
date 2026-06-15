"""
Date: 2026-06-15
Built Bellman-Ford algorithm because I wanted something that handles negative edge weights unlike Dijkstra — detects negative cycles too.
"""

#!/usr/bin/env python3
"""
Bellman-Ford shortest path algorithm with negative cycle detection.

I chose Bellman-Ford over Dijkstra because I wanted to handle graphs with
negative edge weights. This comes up in financial arbitrage detection and
some network routing scenarios where "cost" can be negative.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    """
    Directed weighted graph represented as an adjacency list.
    
    I'm using defaultdict here so I don't have to manually initialize
    empty lists for each vertex when adding edges.
    """
    
    def __init__(self):
        self.edges: List[Tuple[str, str, float]] = []
        self.vertices: set = set()
    
    def add_edge(self, u: str, v: str, weight: float):
        """Add a directed edge from u to v with given weight."""
        self.edges.append((u, v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def bellman_ford(self, source: str) -> Tuple[Optional[Dict[str, float]], Optional[Dict[str, Optional[str]]]]:
        """
        Compute shortest paths from source to all vertices using Bellman-Ford.
        
        Returns (distances, predecessors) where:
        - distances[v] is the shortest distance from source to v
        - predecessors[v] is the previous vertex on the shortest path to v
        
        Returns (None, None) if a negative cycle is detected, since shortest
        paths aren't well-defined in that case.
        
        Time complexity: O(V * E) which is why I only use this when I need
        to handle negative weights. For positive weights, Dijkstra is faster.
        """
        if source not in self.vertices:
            raise ValueError(f"Source vertex '{source}' not in graph")
        
        # Initialize distances to infinity except source
        distances = {v: float('inf') for v in self.vertices}
        distances[source] = 0
        
        # Track predecessors to reconstruct paths
        predecessors = {v: None for v in self.vertices}
        
        # Relax all edges |V| - 1 times
        # Why |V| - 1? Because the longest simple path has |V| - 1 edges
        for _ in range(len(self.vertices) - 1):
            for u, v, weight in self.edges:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
        
        # Check for negative cycles
        # If we can still relax any edge, there's a negative cycle
        for u, v, weight in self.edges:
            if distances[u] + weight < distances[v]:
                return None, None  # Negative cycle detected
        
        return distances, predecessors
    
    def reconstruct_path(self, predecessors: Dict[str, Optional[str]], target: str) -> List[str]:
        """
        Reconstruct the shortest path to target using the predecessors dict.
        
        I walk backwards from target to source, then reverse. Could also
        use a deque and appendleft but this is simpler for small paths.
        """
        if predecessors[target] is None and target not in [pred for pred in predecessors.values() if pred is not None]:
            # Target is not the source and has no predecessor = unreachable
            return []
        
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return path[::-1]


def create_sample_graph() -> Graph:
    """
    Create a sample graph with some negative edges to demonstrate Bellman-Ford.
    
    This is a small network where some routes have "negative cost" (maybe
    representing profit or time savings). I made sure there's no negative
    cycle so the algorithm returns valid results.
    """
    g = Graph()
    
    # Sample network with negative weights
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 2)
    g.add_edge('B', 'C', -3)  # Negative edge: going through B saves cost
    g.add_edge('B', 'D', 2)
    g.add_edge('B', 'E', 3)
    g.add_edge('C', 'D', 4)
    g.add_edge('C', 'E', 5)
    g.add_edge('D', 'E', -1)  # Another negative edge
    g.add_edge('E', 'D', 1)
    
    return g


def create_negative_cycle_graph() -> Graph:
    """
    Create a graph with a negative cycle to test detection.
    
    The cycle B -> C -> D -> B has total weight -1, so you could loop
    forever reducing the path cost. Bellman-Ford should catch this.
    """
    g = Graph()
    
    g.add_edge('A', 'B', 1)
    g.add_edge('B', 'C', 2)
    g.add_edge('C', 'D', -4)  # This creates a negative cycle
    g.add_edge('D', 'B', 1)   # B -> C -> D -> B = 2 + (-4) + 1 = -1
    
    return g


if __name__ == "__main__":
    print("=== Bellman-Ford Shortest Path Demo ===\n")
    
    # Test 1: Normal graph with negative edges (but no negative cycle)
    print("Test 1: Graph with negative edges")
    print("-" * 40)
    g1 = create_sample_graph()
    source = 'A'
    
    distances, predecessors = g1.bellman_ford(source)
    
    if distances is None:
        print("Negative cycle detected!")
    else:
        print(f"Shortest distances from '{source}':")
        for vertex in sorted(distances.keys()):
            dist = distances[vertex]
            path = g1.reconstruct_path(predecessors, vertex)
            path_str = " -> ".join(path) if path else "unreachable"
            print(f"  {vertex}: {dist:6.1f}  (path: {path_str})")
    
    print()
    
    # Test 2: Graph with negative cycle
    print("Test 2: Graph with negative cycle")
    print("-" * 40)
    g2 = create_negative_cycle_graph()
    
    distances, predecessors = g2.bellman_ford('A')
    
    if distances is None:
        print("Negative cycle detected! Shortest paths are not well-defined.")
        print("(You could keep looping and reducing the cost indefinitely)")
    else:
        print(f"Shortest distances from 'A':")
        for vertex in sorted(distances.keys()):
            print(f"  {vertex}: {distances[vertex]:.1f}")