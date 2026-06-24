"""
Date: 2026-06-24
Built Tarjan's SCC algorithm because I needed to understand graph cycle structures better and it's way more elegant than Kosaraju's two-pass approach.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I wanted to dig into this after reading about how compilers use SCCs for optimization.
Tarjan's is beautiful because it does everything in one DFS pass with a stack.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize with an adjacency list representation of the graph.
        
        Args:
            graph: dict mapping vertices to lists of adjacent vertices
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
            list of lists, where each inner list is a strongly connected component
        """
        # Run DFS from every unvisited node
        # This handles disconnected graphs automatically
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS helper that does the actual SCC detection.
        
        The key insight: lowlink[v] tracks the smallest index reachable from v.
        When lowlink[v] == index[v], we've found the root of an SCC.
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Consider successors of vertex
        for neighbor in self.graph.get(vertex, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self._strongconnect(neighbor)
                # Update lowlink based on what we learned from the subtree
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC, update lowlink
                # This is where we detect back edges (cycles)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[neighbor])
        
        # If vertex is a root node, pop the stack to get the SCC
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == vertex:
                    break
            self.sccs.append(scc)


def build_example_graph():
    """
    Build a sample directed graph with multiple SCCs.
    
    This creates a graph that looks like:
    0 -> 1 -> 2 -> 0 (one SCC)
    2 -> 3 -> 4 -> 3 (another SCC)
    4 -> 5 (single node SCC)
    
    Returns:
        dict representing the adjacency list
    """
    graph = defaultdict(list)
    
    # First strongly connected component: 0, 1, 2
    graph[0] = [1]
    graph[1] = [2]
    graph[2] = [0, 3]
    
    # Second strongly connected component: 3, 4
    graph[3] = [4]
    graph[4] = [3, 5]
    
    # Single node component: 5
    graph[5] = []
    
    # Add a disconnected component for fun: 6 <-> 7
    graph[6] = [7]
    graph[7] = [6]
    
    return dict(graph)


def visualize_graph(graph, sccs):
    """
    Print a nice representation of the graph and its SCCs.
    
    Args:
        graph: adjacency list representation
        sccs: list of strongly connected components
    """
    print("Graph structure (adjacency list):")
    print("-" * 40)
    for vertex in sorted(graph.keys()):
        neighbors = graph[vertex]
        if neighbors:
            print(f"  {vertex} -> {neighbors}")
        else:
            print(f"  {vertex} -> (no outgoing edges)")
    
    print("\n" + "=" * 40)
    print(f"Found {len(sccs)} strongly connected components:")
    print("=" * 40)
    
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display
        scc_sorted = sorted(scc)
        print(f"  SCC #{i}: {scc_sorted}")
        
        # Show why it's strongly connected (if it has multiple nodes)
        if len(scc) > 1:
            print(f"    └─ These {len(scc)} nodes can all reach each other")


if __name__ == "__main__":
    print("Tarjan's Strongly Connected Components Algorithm")
    print("=" * 50)
    print()
    
    # Build and analyze the example graph
    graph = build_example_graph()
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    visualize_graph(graph, sccs)
    
    print("\n" + "=" * 50)
    print("Why this matters:")
    print("  - SCCs help detect cycles in dependency graphs")
    print("  - Compilers use them for optimization passes")
    print("  - Great for analyzing social networks (mutual connections)")
    print("  - Used in garbage collection algorithms")