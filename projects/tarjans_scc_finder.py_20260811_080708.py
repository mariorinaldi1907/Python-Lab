"""
Date: 2026-08-11
Built Tarjan's SCC algorithm from scratch because I wanted to understand how compilers detect circular dependencies in module imports.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components in a directed graph.
I implemented this to better understand how dependency cycles get detected in build systems.
Uses a single DFS pass with a stack to track the components - pretty elegant approach.
"""

from collections import defaultdict
from typing import List, Set, Dict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in that set.
    """
    
    def __init__(self, num_vertices: int):
        """
        Initialize the graph structure.
        
        Args:
            num_vertices: Number of vertices in the graph (0-indexed)
        """
        self.num_vertices = num_vertices
        self.graph = defaultdict(list)
        
        # Tarjan's algorithm state
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}
        self.index = {}
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
        Recursive DFS helper that does the actual SCC detection.
        
        The lowlink value tracks the smallest index reachable from v.
        When lowlink[v] == index[v], we've found the root of an SCC.
        
        Args:
            v: Current vertex being explored
        """
        # Set the depth index for v to the smallest unused index
        self.index[v] = self.index_counter
        self.lowlinks[v] = self.index_counter
        self.index_counter += 1
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Consider successors of v
        for w in self.graph[v]:
            if w not in self.index:
                # Successor w has not yet been visited; recurse on it
                self._strongconnect(w)
                self.lowlinks[v] = min(self.lowlinks[v], self.lowlinks[w])
            elif w in self.on_stack:
                # Successor w is in stack and hence in the current SCC
                # This is a back edge, so we update lowlink
                self.lowlinks[v] = min(self.lowlinks[v], self.index[w])
        
        # If v is a root node, pop the stack and create an SCC
        if self.lowlinks[v] == self.index[v]:
            component = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                component.append(w)
                if w == v:
                    break
            self.sccs.append(component)
    
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
        
        # Call the recursive helper for all vertices
        # This handles disconnected components too
        for v in range(self.num_vertices):
            if v not in self.index:
                self._strongconnect(v)
        
        return self.sccs
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains any cycles.
        
        A graph has cycles if any SCC contains more than one vertex,
        or if a single vertex has a self-loop.
        
        Returns:
            True if the graph contains at least one cycle
        """
        sccs = self.find_sccs()
        for component in sccs:
            if len(component) > 1:
                return True
            # Check for self-loop
            if len(component) == 1:
                v = component[0]
                if v in self.graph[v]:
                    return True
        return False


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components Algorithm ===\n")
    
    # Example 1: Classic SCC example with multiple components
    print("Example 1: Graph with multiple SCCs")
    print("Vertices: 0-7")
    print("Edges: 0→1, 1→2, 2→0, 1→3, 3→4, 4→5, 5→3, 6→5, 6→7, 7→6")
    print()
    
    graph1 = TarjanSCC(8)
    edges1 = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]
    for u, v in edges1:
        graph1.add_edge(u, v)
    
    sccs1 = graph1.find_sccs()
    print(f"Found {len(sccs1)} strongly connected components:")
    for i, scc in enumerate(sccs1, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    print(f"Has cycles: {graph1.has_cycle()}")
    print()
    
    # Example 2: DAG (no cycles except for isolated vertices)
    print("Example 2: Directed Acyclic Graph (DAG)")
    print("Vertices: 0-4")
    print("Edges: 0→1, 0→2, 1→3, 2→3, 3→4")
    print()
    
    graph2 = TarjanSCC(5)
    edges2 = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    for u, v in edges2:
        graph2.add_edge(u, v)
    
    sccs2 = graph2.find_sccs()
    print(f"Found {len(sccs2)} strongly connected components:")
    for i, scc in enumerate(sccs2, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    print(f"Has cycles: {graph2.has_cycle()}")
    print()
    
    # Example 3: Single large cycle
    print("Example 3: One big cycle")
    print("Vertices: 0-4")
    print("Edges: 0→1→2→3→4→0")
    print()
    
    graph3 = TarjanSCC(5)
    edges3 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    for u, v in edges3:
        graph3.add_edge(u, v)
    
    sccs3 = graph3.find_sccs()
    print(f"Found {len(sccs3)} strongly connected components:")
    for i, scc in enumerate(sccs3, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    print(f"Has cycles: {graph3.has_cycle()}")
```