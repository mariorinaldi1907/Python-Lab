"""
Date: 2026-06-30
Built Tarjan's SCC algorithm from scratch because I kept running into circular dependency issues in my projects and wanted to really understand how to detect them properly.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I wrote this after dealing with some gnarly circular import issues in a Flask app.
Wanted to understand how dependency analysis actually works under the hood.
Tarjan's algorithm is elegant - single DFS pass, O(V+E) time complexity.
"""

from collections import defaultdict
from typing import List, Set, Dict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    An SCC is a maximal set of vertices where every vertex is reachable from every other.
    Uses DFS with a stack to track the current path and low-link values to identify SCCs.
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
        self.on_stack = set()
        
        # Track discovery time and lowest reachable ancestor
        self.indices = {}
        self.low_link = {}
        
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
        Recursive DFS that does the heavy lifting for Tarjan's algorithm.
        
        This is where the magic happens - we assign indices as we discover nodes,
        track the lowest index reachable (low_link), and pop SCCs off the stack
        when we find a root node (where index == low_link).
        
        Args:
            v: Current vertex being explored
        """
        # Set the depth index for v to the smallest unused index
        self.indices[v] = self.index_counter
        self.low_link[v] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Explore neighbors
        for w in self.graph[v]:
            if w not in self.indices:
                # Successor w has not yet been visited; recurse on it
                self._strongconnect(w)
                self.low_link[v] = min(self.low_link[v], self.low_link[w])
            elif w in self.on_stack:
                # Successor w is on the stack and hence in the current SCC
                # This is the key insight - if we reach something already on stack,
                # it means there's a cycle back to it
                self.low_link[v] = min(self.low_link[v], self.indices[w])
        
        # If v is a root node, pop the stack to get the SCC
        if self.low_link[v] == self.indices[v]:
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
        # Reset state in case we run this multiple times
        self.index_counter = 0
        self.stack = []
        self.on_stack = set()
        self.indices = {}
        self.low_link = {}
        self.sccs = []
        
        # Run DFS from every unvisited vertex
        # This handles disconnected graphs correctly
        for v in range(self.num_vertices):
            if v not in self.indices:
                self._strongconnect(v)
        
        return self.sccs
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains any cycles.
        
        A cycle exists if any SCC has more than one vertex.
        
        Returns:
            True if graph contains at least one cycle
        """
        sccs = self.find_sccs()
        return any(len(scc) > 1 for scc in sccs)


def visualize_sccs(sccs: List[List[int]], vertex_names: Dict[int, str] = None):
    """
    Pretty print the SCCs found.
    
    Args:
        sccs: List of strongly connected components
        vertex_names: Optional mapping from vertex index to readable name
    """
    print(f"\nFound {len(sccs)} strongly connected component(s):\n")
    
    for i, scc in enumerate(sccs, 1):
        if vertex_names:
            named_scc = [vertex_names.get(v, str(v)) for v in scc]
        else:
            named_scc = [str(v) for v in scc]
        
        if len(scc) == 1:
            print(f"  SCC {i}: [{named_scc[0]}] (singleton)")
        else:
            print(f"  SCC {i}: [{', '.join(named_scc)}] (cycle detected!)")


if __name__ == "__main__":
    # Demo 1: Classic example with multiple SCCs
    print("=" * 60)
    print("Demo 1: Graph with multiple strongly connected components")
    print("=" * 60)
    
    graph1 = TarjanSCC(8)
    
    # Building a graph that has a few interesting cycles
    # Visualizing this: 0→1→2→0 (cycle), 3→4→5→3 (cycle), 6→7
    graph1.add_edge(0, 1)
    graph1.add_edge(1, 2)
    graph1.add_edge(2, 0)  # Completes first cycle
    
    graph1.add_edge(3, 4)
    graph1.add_edge(4, 5)
    graph1.add_edge(5, 3)  # Completes second cycle
    
    graph1.add_edge(6, 7)
    
    # Cross-component edges
    graph1.add_edge(2, 3)
    graph1.add_edge(5, 6)
    
    sccs1 = graph1.find_sccs()
    visualize_sccs(sccs1)
    print(f"\nGraph has cycles: {graph1.has_cycle()}")
    
    # Demo 2: Dependency graph example (like imports in code)
    print("\n" + "=" * 60)
    print("Demo 2: Package dependency graph (circular dependency detection)")
    print("=" * 60)
    
    packages = {
        0: "auth",
        1: "database", 
        2: "models",
        3: "api",
        4: "utils",
        5: "config"
    }
    
    graph2 = TarjanSCC(6)
    
    # auth depends on database
    graph2.add_edge(0, 1)
    # database depends on models
    graph2.add_edge(1, 2)
    # models depends on auth (circular dependency!)
    graph2.add_edge(2, 0)
    
    # api depends on auth
    graph2.add_edge(3, 0)
    # utils is standalone
    # config is standalone
    
    sccs2 = graph2.find_sccs()
    visualize_sccs(sccs2, packages)
    print(f"\nCircular dependencies detected: {graph2.has_cycle()}")
    
    print("\n" + "=" * 60)
    print("This is why refactoring is important! 😅")
    print("=" * 60)