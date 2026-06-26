"""
Date: 2026-06-26
Built Tarjan's algorithm to find all strongly connected components in a directed graph — uses DFS with low-link values and a stack.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I've always found SCCs fascinating because they reveal the "core structure" of a graph.
This implementation uses a single DFS pass with low-link values to identify all SCCs efficiently.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal subset of vertices where every vertex
    is reachable from every other vertex in that subset.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: Dictionary mapping each vertex to a list of its outgoing neighbors.
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}
        self.index = {}
        self.on_stack = set()
        self.sccs = []
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of lists, where each inner list is a strongly connected component.
        """
        # We need to check all nodes because the graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS helper that does the heavy lifting.
        
        The key insight: lowlink[v] tracks the smallest index reachable from v.
        When lowlink[v] == index[v], we've found the root of an SCC.
        """
        # Assign the smallest unused index to this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Explore neighbors
        for neighbor in self.graph.get(vertex, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse on it
                self._strongconnect(neighbor)
                # After returning, update our lowlink with the neighbor's lowlink
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC (still on stack)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[neighbor])
        
        # If this is a root node of an SCC, pop the stack to collect all vertices in this SCC
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def build_sample_graph():
    """
    Create a sample directed graph with multiple SCCs for testing.
    
    The graph looks like this:
        0 -> 1 -> 2 -> 0  (forms SCC {0, 1, 2})
        2 -> 3
        3 -> 4
        4 -> 5 -> 3       (forms SCC {3, 4, 5})
        6 -> 7 -> 6       (forms SCC {6, 7})
        7 -> 8            (8 is alone)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [5],
        5: [3],
        6: [7],
        7: [6, 8],
        8: [],
    }
    return graph


def print_graph_structure(graph):
    """Pretty print the graph structure."""
    print("Graph structure:")
    for vertex in sorted(graph.keys()):
        neighbors = graph[vertex]
        if neighbors:
            print(f"  {vertex} -> {neighbors}")
        else:
            print(f"  {vertex} -> (no outgoing edges)")
    print()


if __name__ == "__main__":
    # Build and display the test graph
    graph = build_sample_graph()
    print("=" * 60)
    print("Tarjan's Algorithm - Strongly Connected Components Finder")
    print("=" * 60)
    print()
    
    print_graph_structure(graph)
    
    # Run Tarjan's algorithm
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    # Display results
    print(f"Found {len(sccs)} strongly connected component(s):")
    print()
    
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display
        scc_sorted = sorted(scc)
        print(f"  SCC #{i}: {scc_sorted}")
        
        # Show why it's strongly connected (just for the demo)
        if len(scc_sorted) > 1:
            print(f"    → All vertices in {scc_sorted} are mutually reachable")
        else:
            print(f"    → Singleton component (no cycles involving other nodes)")
        print()
    
    # Quick verification: total vertices should equal sum of SCC sizes
    total_in_sccs = sum(len(scc) for scc in sccs)
    print(f"Verification: {total_in_sccs} total vertices in SCCs = {len(graph)} graph vertices ✓")