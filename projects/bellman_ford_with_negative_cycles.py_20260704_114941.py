"""
Date: 2026-07-04
Built a Bellman-Ford shortest path finder that explicitly detects and reports negative cycles, which Dijkstra can't handle.
"""

"""
Bellman-Ford algorithm with negative cycle detection.

I wanted to implement this because it's more robust than Dijkstra —
handles negative weights and actually tells you when there's a negative cycle.
Useful for currency arbitrage detection or analyzing costs that can decrease.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    """Directed weighted graph using adjacency list representation."""
    
    def __init__(self):
        """Initialize an empty graph."""
        self.edges = []  # List of (source, dest, weight) tuples
        self.vertices = set()
    
    def add_edge(self, u: str, v: str, weight: float):
        """
        Add a directed edge from u to v with given weight.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (can be negative)
        """
        self.edges.append((u, v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
    
    def bellman_ford(self, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]], Optional[List[str]]]:
        """
        Find shortest paths from source using Bellman-Ford algorithm.
        
        The key insight here is that we relax edges V-1 times. If we can
        still relax on the Vth iteration, there's a negative cycle.
        
        Args:
            source: Starting vertex
            
        Returns:
            Tuple of (distances, predecessors, negative_cycle_path)
            - distances: Dict mapping vertex to shortest distance from source
            - predecessors: Dict for reconstructing paths
            - negative_cycle_path: List of vertices in cycle, or None if no cycle
        """
        # Initialize distances to infinity, except source
        distances = {v: float('inf') for v in self.vertices}
        distances[source] = 0
        
        # Track predecessors for path reconstruction
        predecessors = {v: None for v in self.vertices}
        
        # Relax edges V-1 times
        # Why V-1? Because the longest simple path has at most V-1 edges
        for _ in range(len(self.vertices) - 1):
            for u, v, weight in self.edges:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
        
        # Check for negative cycles by doing one more relaxation
        # If we can still improve, there's a negative cycle
        negative_cycle_vertex = None
        for u, v, weight in self.edges:
            if distances[u] + weight < distances[v]:
                negative_cycle_vertex = v
                predecessors[v] = u
                break
        
        negative_cycle = None
        if negative_cycle_vertex:
            negative_cycle = self._extract_negative_cycle(predecessors, negative_cycle_vertex)
        
        return distances, predecessors, negative_cycle
    
    def _extract_negative_cycle(self, predecessors: Dict[str, Optional[str]], 
                                start_vertex: str) -> List[str]:
        """
        Extract the actual negative cycle from the predecessor chain.
        
        We need to walk back V steps to ensure we're in the cycle,
        then trace back until we see the vertex again.
        """
        # Walk back V steps to ensure we're definitely in the cycle
        current = start_vertex
        for _ in range(len(self.vertices)):
            current = predecessors[current]
        
        # Now trace the cycle
        cycle = []
        first_vertex = current
        while True:
            cycle.append(current)
            current = predecessors[current]
            if current == first_vertex:
                cycle.append(current)
                break
        
        cycle.reverse()
        return cycle
    
    def get_path(self, predecessors: Dict[str, Optional[str]], 
                 source: str, target: str) -> Optional[List[str]]:
        """
        Reconstruct path from source to target using predecessor chain.
        
        Args:
            predecessors: Dict of vertex -> predecessor
            source: Starting vertex
            target: Ending vertex
            
        Returns:
            List of vertices forming path, or None if no path exists
        """
        if predecessors[target] is None and target != source:
            return None
        
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        path.reverse()
        return path


if __name__ == "__main__":
    print("=== Bellman-Ford Shortest Path Demo ===\n")
    
    # Example 1: Normal graph with negative weights (but no negative cycle)
    print("Example 1: Graph with negative edges (no cycle)")
    g1 = Graph()
    g1.add_edge("A", "B", 4)
    g1.add_edge("A", "C", 2)
    g1.add_edge("B", "C", -3)  # Negative edge
    g1.add_edge("C", "D", 2)
    g1.add_edge("D", "B", 1)
    
    distances, predecessors, neg_cycle = g1.bellman_ford("A")
    
    if neg_cycle:
        print(f"Negative cycle detected: {' -> '.join(neg_cycle)}")
    else:
        print("No negative cycle found")
        for vertex in sorted(distances.keys()):
            path = g1.get_path(predecessors, "A", vertex)
            print(f"  A -> {vertex}: distance = {distances[vertex]}, path = {' -> '.join(path)}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Graph WITH a negative cycle
    print("Example 2: Graph with negative cycle (arbitrage opportunity!)")
    g2 = Graph()
    g2.add_edge("A", "B", 1)
    g2.add_edge("B", "C", -3)
    g2.add_edge("C", "A", 1)  # Cycle A->B->C->A has total weight -1
    g2.add_edge("A", "D", 5)
    
    distances, predecessors, neg_cycle = g2.bellman_ford("A")
    
    if neg_cycle:
        print(f"Negative cycle detected: {' -> '.join(neg_cycle)}")
        print("(In currency trading, this would be an arbitrage opportunity)")
    else:
        print("No negative cycle found")
    
    print("\n" + "="*50 + "\n")
    print("Done! Bellman-Ford is slower than Dijkstra (O(VE) vs O((V+E)logV))")
    print("but it handles negative weights and detects negative cycles.")