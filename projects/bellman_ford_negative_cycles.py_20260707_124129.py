"""
Date: 2026-07-07
Built a Bellman-Ford shortest path finder that detects negative cycles since I kept running into graph problems where Dijkstra choked on negative edge weights.
"""

#!/usr/bin/env python3
"""
Bellman-Ford algorithm implementation with negative cycle detection.

I wrote this because I was working on some routing problems where edge weights
could be negative (think cost savings or discounts), and Dijkstra just doesn't
handle that. Bellman-Ford relaxes all edges V-1 times, then checks once more
to detect negative cycles.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set


class Graph:
    """
    Directed weighted graph using adjacency list representation.
    
    I'm storing edges as (src, dest, weight) tuples internally since
    Bellman-Ford needs to iterate over all edges repeatedly anyway.
    """
    
    def __init__(self):
        self.edges: List[Tuple[str, str, float]] = []
        self.vertices: Set[str] = set()
    
    def add_edge(self, src: str, dest: str, weight: float):
        """Add a directed edge from src to dest with given weight."""
        self.edges.append((src, dest, weight))
        self.vertices.add(src)
        self.vertices.add(dest)
    
    def bellman_ford(self, start: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]], bool]:
        """
        Run Bellman-Ford algorithm from start vertex.
        
        Returns:
            distances: Dict mapping vertex to shortest distance from start
            predecessors: Dict mapping vertex to its predecessor in shortest path
            has_negative_cycle: Boolean indicating if a negative cycle exists
        
        The algorithm relaxes all edges V-1 times (where V is number of vertices).
        If we can still relax any edge on the Vth iteration, there's a negative cycle.
        """
        if start not in self.vertices:
            raise ValueError(f"Start vertex '{start}' not in graph")
        
        # Initialize distances to infinity except start
        distances = {v: float('inf') for v in self.vertices}
        distances[start] = 0
        
        # Track predecessors to reconstruct paths later
        predecessors = {v: None for v in self.vertices}
        
        # Relax all edges V-1 times
        # This is the core of Bellman-Ford - we give every edge a chance to
        # improve the distance to every vertex
        for _ in range(len(self.vertices) - 1):
            for src, dest, weight in self.edges:
                if distances[src] != float('inf') and distances[src] + weight < distances[dest]:
                    distances[dest] = distances[src] + weight
                    predecessors[dest] = src
        
        # Check for negative cycles
        # If we can still improve any distance, there's a negative cycle
        has_negative_cycle = False
        for src, dest, weight in self.edges:
            if distances[src] != float('inf') and distances[src] + weight < distances[dest]:
                has_negative_cycle = True
                break
        
        return distances, predecessors, has_negative_cycle
    
    def get_path(self, predecessors: Dict[str, Optional[str]], start: str, end: str) -> Optional[List[str]]:
        """
        Reconstruct the shortest path from start to end using predecessor map.
        
        Returns None if no path exists (end is unreachable from start).
        """
        if end not in self.vertices or start not in self.vertices:
            return None
        
        # Walk backwards from end to start
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            if current == start:
                return path[::-1]  # Reverse to get start -> end
            current = predecessors[current]
        
        # If we got here, end is not reachable from start
        return None


def main():
    """
    Demo with a few test cases to show the algorithm working.
    """
    # Test case 1: Simple graph with positive and negative weights
    print("=== Test 1: Basic graph with negative edge ===")
    g1 = Graph()
    g1.add_edge('A', 'B', 4)
    g1.add_edge('A', 'C', 2)
    g1.add_edge('B', 'C', -3)  # Negative edge, but no negative cycle
    g1.add_edge('C', 'D', 2)
    g1.add_edge('B', 'D', 4)
    
    distances, predecessors, has_cycle = g1.bellman_ford('A')
    
    print(f"Negative cycle detected: {has_cycle}")
    print("\nShortest distances from A:")
    for vertex in sorted(distances.keys()):
        dist = distances[vertex]
        print(f"  {vertex}: {dist if dist != float('inf') else '∞'}")
    
    print("\nShortest path from A to D:")
    path = g1.get_path(predecessors, 'A', 'D')
    if path:
        print(f"  {' -> '.join(path)} (distance: {distances['D']})")
    
    # Test case 2: Graph with a negative cycle
    print("\n\n=== Test 2: Graph with negative cycle ===")
    g2 = Graph()
    g2.add_edge('X', 'Y', 1)
    g2.add_edge('Y', 'Z', -3)
    g2.add_edge('Z', 'X', 1)  # This creates a negative cycle: X->Y->Z->X = -1
    g2.add_edge('X', 'W', 5)
    
    distances, predecessors, has_cycle = g2.bellman_ford('X')
    
    print(f"Negative cycle detected: {has_cycle}")
    print("\nDistances (may be unreliable due to negative cycle):")
    for vertex in sorted(distances.keys()):
        dist = distances[vertex]
        print(f"  {vertex}: {dist if dist != float('inf') else '∞'}")
    
    # Test case 3: Disconnected graph
    print("\n\n=== Test 3: Disconnected vertices ===")
    g3 = Graph()
    g3.add_edge('A', 'B', 1)
    g3.add_edge('C', 'D', 1)  # Separate component
    
    distances, predecessors, has_cycle = g3.bellman_ford('A')
    
    print(f"Negative cycle detected: {has_cycle}")
    print("\nDistances from A:")
    for vertex in sorted(distances.keys()):
        dist = distances[vertex]
        status = dist if dist != float('inf') else 'unreachable'
        print(f"  {vertex}: {status}")


if __name__ == "__main__":
    main()