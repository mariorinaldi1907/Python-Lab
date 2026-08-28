"""
Date: 2026-08-28
Built a Bellman-Ford implementation because I needed something that works with negative edge weights and tells me when there's a negative cycle.
"""

#!/usr/bin/env python3
"""
Bellman-Ford algorithm for finding shortest paths in weighted graphs.
Unlike Dijkstra, this handles negative edge weights and detects negative cycles.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    """
    Weighted directed graph representation using adjacency list.
    Supports negative weights, which is why I'm using Bellman-Ford.
    """
    
    def __init__(self):
        self.edges: List[Tuple[str, str, float]] = []
        self.vertices: set = set()
    
    def add_edge(self, u: str, v: str, weight: float):
        """Add a directed edge from u to v with given weight."""
        self.edges.append((u, v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def bellman_ford(self, source: str) -> Tuple[Optional[Dict[str, float]], Optional[Dict[str, str]]]:
        """
        Run Bellman-Ford algorithm from source vertex.
        
        Returns:
            (distances, predecessors) if no negative cycle exists
            (None, None) if a negative cycle is detected
        
        The algorithm relaxes all edges V-1 times, then checks once more
        to detect negative cycles. That extra check is the key insight here.
        """
        # Initialize distances to infinity except source
        distances = {vertex: float('inf') for vertex in self.vertices}
        distances[source] = 0
        
        # Track predecessors for path reconstruction
        predecessors = {vertex: None for vertex in self.vertices}
        
        # Relax all edges |V| - 1 times
        # Each iteration guarantees shortest paths of length at most i edges
        for _ in range(len(self.vertices) - 1):
            updated = False
            for u, v, weight in self.edges:
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
                    updated = True
            
            # Early termination if no updates in this iteration
            if not updated:
                break
        
        # Check for negative cycles
        # If we can still relax an edge, there's a negative cycle
        for u, v, weight in self.edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                return None, None  # Negative cycle detected
        
        return distances, predecessors
    
    def reconstruct_path(self, predecessors: Dict[str, str], target: str) -> List[str]:
        """
        Reconstruct the shortest path to target using predecessor map.
        Returns the path as a list of vertices from source to target.
        """
        if predecessors[target] is None and target != list(predecessors.keys())[0]:
            return []  # No path exists
        
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return list(reversed(path))


def demo_basic_graph():
    """Simple example with positive and negative weights."""
    print("=" * 60)
    print("Demo 1: Basic graph with negative weights")
    print("=" * 60)
    
    g = Graph()
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 2)
    g.add_edge('B', 'C', -3)  # Negative weight here
    g.add_edge('C', 'D', 2)
    g.add_edge('D', 'B', 1)
    g.add_edge('B', 'E', 4)
    g.add_edge('D', 'E', 1)
    
    source = 'A'
    distances, predecessors = g.bellman_ford(source)
    
    if distances is None:
        print("Negative cycle detected!")
    else:
        print(f"Shortest distances from {source}:")
        for vertex in sorted(distances.keys()):
            dist = distances[vertex]
            if dist == float('inf'):
                print(f"  {source} -> {vertex}: unreachable")
            else:
                path = g.reconstruct_path(predecessors, vertex)
                print(f"  {source} -> {vertex}: {dist:.1f} (path: {' -> '.join(path)})")


def demo_negative_cycle():
    """Example with a negative cycle to show detection works."""
    print("\n" + "=" * 60)
    print("Demo 2: Graph with negative cycle")
    print("=" * 60)
    
    g = Graph()
    g.add_edge('X', 'Y', 1)
    g.add_edge('Y', 'Z', -2)
    g.add_edge('Z', 'X', -1)  # This creates a negative cycle: X -> Y -> Z -> X
    g.add_edge('X', 'W', 5)
    
    source = 'X'
    distances, predecessors = g.bellman_ford(source)
    
    if distances is None:
        print("✓ Negative cycle detected (as expected)!")
        print("The cycle X -> Y -> Z -> X has total weight: 1 + (-2) + (-1) = -2")
    else:
        print("No negative cycle found")


def demo_disconnected():
    """Example showing behavior with unreachable vertices."""
    print("\n" + "=" * 60)
    print("Demo 3: Graph with unreachable vertices")
    print("=" * 60)
    
    g = Graph()
    g.add_edge('A', 'B', 3)
    g.add_edge('B', 'C', 1)
    g.add_edge('D', 'E', 2)  # Disconnected component
    
    source = 'A'
    distances, predecessors = g.bellman_ford(source)
    
    if distances:
        print(f"Shortest distances from {source}:")
        for vertex in sorted(distances.keys()):
            dist = distances[vertex]
            if dist == float('inf'):
                print(f"  {source} -> {vertex}: unreachable")
            else:
                print(f"  {source} -> {vertex}: {dist:.1f}")


if __name__ == "__main__":
    # Run all demos to show different scenarios
    demo_basic_graph()
    demo_negative_cycle()
    demo_disconnected()