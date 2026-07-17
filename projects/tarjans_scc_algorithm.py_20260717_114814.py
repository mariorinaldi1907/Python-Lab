"""
Date: 2026-07-17
Built Tarjan's SCC algorithm because I wanted to understand how cycle detection works in directed graphs at a deeper level.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I implemented this because I was curious about how tools like dependency analyzers
detect circular dependencies. Tarjan's approach is elegant — it uses a single DFS
pass with a stack to identify SCCs, which are maximal subgraphs where every vertex
can reach every other vertex.
"""

from collections import defaultdict
from typing import List, Set, Dict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    The algorithm maintains a stack of vertices and assigns each vertex a discovery time
    (index) and a low-link value. The low-link tracks the smallest index reachable from
    the vertex. When we finish exploring a vertex and its low-link equals its index,
    we've found the root of an SCC.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph with a given number of vertices.
        
        Args:
            num_vertices: Total number of vertices (labeled 0 to num_vertices-1)
        """
        self.num_vertices = num_vertices
        self.graph = defaultdict(list)  # adjacency list
        
    def add_edge(self, u: int, v: int):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def find_sccs(self) -> List[List[int]]:
        """
        Find all strongly connected components in the graph.
        
        Returns:
            A list of SCCs, where each SCC is a list of vertex IDs
        """
        # Initialize tracking structures
        self.index_counter = 0
        self.stack = []
        self.on_stack = set()
        self.indices = {}  # discovery time for each vertex
        self.low_links = {}  # lowest index reachable from this vertex
        self.sccs = []
        
        # Run DFS from every unvisited vertex
        # This handles disconnected components in the graph
        for vertex in range(self.num_vertices):
            if vertex not in self.indices:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, v: int):
        """
        Recursive DFS helper that actually implements Tarjan's algorithm.
        
        This is where the magic happens: we explore the graph depth-first,
        maintaining the stack and updating low-links as we backtrack.
        
        Args:
            v: Current vertex being explored
        """
        # Set the depth index for v to the smallest unused index
        self.indices[v] = self.index_counter
        self.low_links[v] = self.index_counter
        self.index_counter += 1
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Explore all neighbors
        for neighbor in self.graph[v]:
            if neighbor not in self.indices:
                # Neighbor hasn't been visited yet, recurse on it
                self._strongconnect(neighbor)
                # Update low-link after returning from recursion
                # This propagates the lowest reachable index back up the call stack
                self.low_links[v] = min(self.low_links[v], self.low_links[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on the stack, meaning it's in the current SCC
                # Update v's low-link to the neighbor's index (not low-link!)
                self.low_links[v] = min(self.low_links[v], self.indices[neighbor])
        
        # If v is a root node (low-link == index), pop the stack to create an SCC
        if self.low_links[v] == self.indices[v]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            self.sccs.append(scc)


def print_graph_info(graph: TarjanSCC, edges: List[tuple]):
    """
    Pretty print the graph structure and edges.
    
    Args:
        graph: The TarjanSCC graph instance
        edges: List of (source, dest) tuples representing edges
    """
    print(f"Graph with {graph.num_vertices} vertices:")
    for u, v in edges:
        print(f"  {u} → {v}")
    print()


if __name__ == "__main__":
    # Demo 1: Classic example with multiple SCCs
    print("=" * 60)
    print("Demo 1: Graph with three distinct SCCs")
    print("=" * 60)
    
    g1 = TarjanSCC(8)
    edges1 = [
        (0, 1), (1, 2), (2, 0),  # First SCC: cycle between 0, 1, 2
        (1, 3), (3, 4), (4, 5), (5, 3),  # Second SCC: cycle between 3, 4, 5
        (5, 6), (6, 7), (7, 6)  # Third SCC: cycle between 6, 7
    ]
    
    for u, v in edges1:
        g1.add_edge(u, v)
    
    print_graph_info(g1, edges1)
    sccs1 = g1.find_sccs()
    
    print(f"Found {len(sccs1)} strongly connected components:")
    for i, scc in enumerate(sccs1, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    
    print("\n")
    
    # Demo 2: A graph representing a circular dependency scenario
    print("=" * 60)
    print("Demo 2: Simulating circular dependencies in modules")
    print("=" * 60)
    
    # Imagine modules where A imports B, B imports C, C imports A (circular!)
    # and D imports E, E imports D (another circular dependency)
    modules = {
        0: "ModuleA", 1: "ModuleB", 2: "ModuleC",
        3: "ModuleD", 4: "ModuleE", 5: "ModuleF"
    }
    
    g2 = TarjanSCC(6)
    edges2 = [
        (0, 1),  # A imports B
        (1, 2),  # B imports C
        (2, 0),  # C imports A (cycle!)
        (3, 4),  # D imports E
        (4, 3),  # E imports D (another cycle!)
        (2, 5),  # C imports F
        (5, 3)   # F imports D
    ]
    
    for u, v in edges2:
        g2.add_edge(u, v)
    
    print("Module dependency graph:")
    for u, v in edges2:
        print(f"  {modules[u]} imports {modules[v]}")
    print()
    
    sccs2 = g2.find_sccs()
    
    print(f"Found {len(sccs2)} strongly connected components:")
    for i, scc in enumerate(sccs2, 1):
        module_names = [modules[v] for v in sorted(scc)]
        if len(scc) > 1:
            print(f"  SCC {i}: {module_names} ⚠️  CIRCULAR DEPENDENCY!")
        else:
            print(f"  SCC {i}: {module_names}")