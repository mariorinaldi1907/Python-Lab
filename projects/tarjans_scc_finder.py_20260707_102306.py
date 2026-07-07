"""
Date: 2026-07-07
Built Tarjan's algorithm to find strongly connected components in directed graphs — always wanted a clean implementation of this for analyzing dependency cycles.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I've always been fascinated by how this algorithm uses a single DFS pass with
a stack to identify all SCCs. It's way more elegant than running multiple passes.
"""

from collections import defaultdict
from typing import List, Set, Dict


class TarjanSCC:
    """
    Finds strongly connected components using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set. This is super useful for
    finding cycles in dependency graphs, call graphs, etc.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph structure.
        
        Args:
            num_vertices: Total number of vertices in the graph
        """
        self.num_vertices = num_vertices
        self.graph = defaultdict(list)
        
        # These are the core data structures for Tarjan's algorithm
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # Lowest index reachable from this node
        self.index = {}     # Discovery time of each node
        self.on_stack = set()
        self.sccs = []
        
    def add_edge(self, u: int, v: int):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def _strongconnect(self, v: int):
        """
        The recursive heart of Tarjan's algorithm.
        
        This is where the magic happens — we assign each node an index,
        track the lowest reachable index, and pop SCCs off the stack
        when we find a root node (where lowlink == index).
        
        Args:
            v: Current vertex being explored
        """
        # Set the depth index for v
        self.index[v] = self.index_counter
        self.lowlinks[v] = self.index_counter
        self.index_counter += 1
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Explore all neighbors
        for w in self.graph[v]:
            if w not in self.index:
                # Successor w has not yet been visited; recurse on it
                self._strongconnect(w)
                self.lowlinks[v] = min(self.lowlinks[v], self.lowlinks[w])
            elif w in self.on_stack:
                # Successor w is on stack and hence in the current SCC
                # This is a back edge, update lowlink
                self.lowlinks[v] = min(self.lowlinks[v], self.index[w])
        
        # If v is a root node, pop the stack to get the SCC
        if self.lowlinks[v] == self.index[v]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            self.sccs.append(scc)
    
    def find_sccs(self) -> List[List[int]]:
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of vertex indices
        """
        # Reset state in case this is called multiple times
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}
        self.index = {}
        self.on_stack = set()
        self.sccs = []
        
        # Handle disconnected graphs by checking all vertices
        for v in range(self.num_vertices):
            if v not in self.index:
                self._strongconnect(v)
        
        return self.sccs
    
    def print_sccs(self):
        """Pretty print all SCCs with some formatting."""
        print(f"\nFound {len(self.sccs)} strongly connected component(s):\n")
        for i, scc in enumerate(self.sccs, 1):
            # Sort for consistent output
            scc_sorted = sorted(scc)
            if len(scc) == 1:
                print(f"  SCC {i}: [{scc_sorted[0]}] (singleton)")
            else:
                print(f"  SCC {i}: {scc_sorted} (cycle of {len(scc)} nodes)")


if __name__ == "__main__":
    print("=== Tarjan's Algorithm Demo ===")
    print("\nBuilding a directed graph with some interesting cycles...")
    
    # Create a graph with 8 vertices
    # This graph has multiple SCCs including a nice 3-cycle
    tarjan = TarjanSCC(8)
    
    # Add edges to create a few interesting components:
    # - Component 1: A cycle between 0, 1, 2
    tarjan.add_edge(0, 1)
    tarjan.add_edge(1, 2)
    tarjan.add_edge(2, 0)
    
    # - Component 2: A cycle between 3, 4
    tarjan.add_edge(3, 4)
    tarjan.add_edge(4, 3)
    
    # - Bridge edges connecting components
    tarjan.add_edge(2, 3)
    tarjan.add_edge(4, 5)
    
    # - Component 3: Isolated vertex 5 connecting to 6
    tarjan.add_edge(5, 6)
    
    # - Component 4: Self-loop on 6
    tarjan.add_edge(6, 6)
    
    # - Singleton: Vertex 7 is completely isolated
    
    print("\nGraph edges:")
    for node in sorted(tarjan.graph.keys()):
        print(f"  {node} -> {tarjan.graph[node]}")
    
    # Find and print SCCs
    sccs = tarjan.find_sccs()
    tarjan.print_sccs()
    
    print("\n--- Analysis ---")
    print(f"Total vertices: {tarjan.num_vertices}")
    print(f"Total SCCs: {len(sccs)}")
    cycle_sccs = [scc for scc in sccs if len(scc) > 1]
    print(f"SCCs with cycles: {len(cycle_sccs)}")
    
    # This is useful for detecting circular dependencies
    print("\nCircular dependency detection:")
    for scc in cycle_sccs:
        print(f"  Cycle detected: {sorted(scc)}")