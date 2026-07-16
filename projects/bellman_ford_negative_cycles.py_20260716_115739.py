"""
Date: 2026-07-16
Built a Bellman-Ford implementation that not only finds shortest paths but also detects and extracts negative cycles when they exist.
"""

"""
Bellman-Ford algorithm with negative cycle detection.

I wanted to implement something beyond basic Dijkstra since I've been reading
about arbitrage detection in currency exchange graphs. Bellman-Ford handles
negative weights and can actually tell you *where* the negative cycle is,
which is pretty useful for debugging graph problems.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    """
    Directed weighted graph using adjacency list representation.
    
    I went with a simple adjacency list since it's memory efficient for
    sparse graphs, which is what you usually see in practice.
    """
    
    def __init__(self):
        self.edges = []  # List of (source, dest, weight) tuples
        self.vertices = set()
    
    def add_edge(self, u: int, v: int, weight: float):
        """Add a directed edge from u to v with given weight."""
        self.edges.append((u, v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def bellman_ford(self, source: int) -> Tuple[Optional[Dict[int, float]], Optional[List[int]]]:
        """
        Run Bellman-Ford from source vertex.
        
        Returns:
            - (distances, None) if no negative cycle exists
            - (None, cycle_path) if a negative cycle is detected
        
        The key insight: after |V|-1 iterations, all shortest paths are found.
        If we can still relax edges on iteration |V|, there's a negative cycle.
        """
        if source not in self.vertices:
            raise ValueError(f"Source vertex {source} not in graph")
        
        # Initialize distances - using float('inf') for unreachable vertices
        distances = {v: float('inf') for v in self.vertices}
        distances[source] = 0
        predecessor = {v: None for v in self.vertices}
        
        # Standard Bellman-Ford: relax all edges |V|-1 times
        num_vertices = len(self.vertices)
        for i in range(num_vertices - 1):
            updated = False
            for u, v, weight in self.edges:
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessor[v] = u
                    updated = True
            
            # Small optimization: if nothing changed, we're done early
            if not updated:
                break
        
        # Check for negative cycles on the |V|th iteration
        # If we can still relax, there's definitely a negative cycle
        negative_cycle_vertex = None
        for u, v, weight in self.edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                negative_cycle_vertex = v
                predecessor[v] = u
                break
        
        if negative_cycle_vertex is not None:
            # Extract the actual cycle path - this is the interesting part
            cycle = self._extract_negative_cycle(predecessor, negative_cycle_vertex)
            return None, cycle
        
        return distances, None
    
    def _extract_negative_cycle(self, predecessor: Dict[int, Optional[int]], 
                                start_vertex: int) -> List[int]:
        """
        Walk backward through predecessors to find the cycle.
        
        Since we know start_vertex is part of a negative cycle, we need to
        walk back |V| steps to guarantee we're inside the cycle, then
        trace it properly.
        """
        # Move back |V| steps to ensure we're in the cycle
        current = start_vertex
        for _ in range(len(predecessor)):
            current = predecessor[current]
        
        # Now extract the cycle by walking until we return to current
        cycle = []
        cycle_start = current
        while True:
            cycle.append(current)
            current = predecessor[current]
            if current == cycle_start:
                cycle.append(current)
                break
        
        cycle.reverse()  # We built it backward
        return cycle


def demo_basic_shortest_path():
    """Simple example with no negative cycles."""
    print("=" * 60)
    print("Demo 1: Basic shortest path (no negative cycles)")
    print("=" * 60)
    
    g = Graph()
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, -3)  # Negative edge, but no cycle
    g.add_edge(2, 3, 2)
    g.add_edge(1, 3, 3)
    
    distances, cycle = g.bellman_ford(0)
    
    if cycle is None:
        print("\nShortest distances from vertex 0:")
        for vertex in sorted(distances.keys()):
            dist = distances[vertex]
            print(f"  Vertex {vertex}: {dist}")
    else:
        print(f"\nNegative cycle detected: {cycle}")


def demo_negative_cycle():
    """Example that contains a negative weight cycle."""
    print("\n" + "=" * 60)
    print("Demo 2: Graph with negative cycle")
    print("=" * 60)
    
    # Creating a cycle: 0 -> 1 -> 2 -> 0 with total weight -1
    g = Graph()
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, -3)
    g.add_edge(2, 0, 1)
    g.add_edge(2, 3, 2)
    
    distances, cycle = g.bellman_ford(0)
    
    if cycle is None:
        print("\nNo negative cycle found.")
        print("Shortest distances from vertex 0:")
        for vertex in sorted(distances.keys()):
            print(f"  Vertex {vertex}: {distances[vertex]}")
    else:
        print(f"\nNegative cycle detected: {' -> '.join(map(str, cycle))}")
        print("(No valid shortest paths exist when negative cycles are reachable)")


if __name__ == "__main__":
    # Running both demos to show the algorithm working in different scenarios
    demo_basic_shortest_path()
    demo_negative_cycle()
    
    print("\n" + "=" * 60)
    print("Why Bellman-Ford over Dijkstra?")
    print("=" * 60)
    print("- Handles negative edge weights")
    print("- Detects negative cycles")
    print("- Great for currency arbitrage detection")
    print("- Time: O(VE) vs Dijkstra's O(E log V)")