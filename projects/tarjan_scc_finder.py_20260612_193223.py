"""
Date: 2026-06-12
Built Tarjan's SCC algorithm from scratch to explore how a single DFS pass can identify all strongly connected components in a directed graph using low-link values.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I always found it fascinating that you can find all SCCs in just one DFS pass.
The key insight is tracking both the discovery time and the lowest reachable ancestor
(the "low-link" value) for each node as you traverse.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds strongly connected components using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: Dictionary mapping node -> list of neighbors (adjacency list)
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
        Main entry point - finds all SCCs in the graph.
        
        Returns:
            List of lists, where each inner list is an SCC (set of nodes)
        """
        # Some nodes might not be in the adjacency list as keys if they have no outgoing edges
        all_nodes = set(self.graph.keys())
        for neighbors in self.graph.values():
            all_nodes.update(neighbors)
        
        # Run DFS from each unvisited node
        for node in all_nodes:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that does the heavy lifting.
        
        The algorithm maintains a stack of nodes in the current DFS path.
        When we find that a node's low-link equals its index, we've found the root
        of an SCC and can pop everything above it from the stack.
        """
        # Set the depth index for this node
        self.index[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Consider successors of node
        if node in self.graph:
            for successor in self.graph[node]:
                if successor not in self.index:
                    # Successor has not yet been visited; recurse on it
                    self._strongconnect(successor)
                    self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[successor])
                elif successor in self.on_stack:
                    # Successor is in stack and hence in the current SCC
                    # This is a back edge in the DFS tree
                    self.lowlinks[node] = min(self.lowlinks[node], self.index[successor])
        
        # If node is a root node, pop the stack and create an SCC
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                successor = self.stack.pop()
                self.on_stack.remove(successor)
                scc.append(successor)
                if successor == node:
                    break
            self.sccs.append(scc)


def build_sample_graph():
    """
    Creates a directed graph with some interesting SCC structure.
    
    The graph looks like this:
    0 -> 1 -> 2 -> 0 (forms one SCC)
    2 -> 3 -> 4 -> 3 (3-4 form an SCC)
    4 -> 5 (5 is alone)
    1 -> 6 -> 7 -> 6 (6-7 form an SCC)
    
    So we expect 4 SCCs: [0,1,2], [3,4], [5], [6,7]
    """
    graph = {
        0: [1],
        1: [2, 6],
        2: [0, 3],
        3: [4],
        4: [3, 5],
        5: [],
        6: [7],
        7: [6],
    }
    return graph


def print_sccs(sccs):
    """Pretty print the SCCs in a readable format."""
    print(f"Found {len(sccs)} strongly connected components:\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent output
        scc_sorted = sorted(scc)
        if len(scc) == 1:
            print(f"  SCC #{i}: {scc_sorted[0]} (singleton)")
        else:
            print(f"  SCC #{i}: {scc_sorted} (size {len(scc)})")


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Build and display the test graph
    graph = build_sample_graph()
    print("Input graph (adjacency list):")
    for node in sorted(graph.keys()):
        neighbors = graph[node]
        if neighbors:
            print(f"  {node} -> {neighbors}")
        else:
            print(f"  {node} -> (no outgoing edges)")
    print()
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print_sccs(sccs)
    print("\nNote: The order of SCCs depends on DFS traversal order,")
    print("but within each SCC all nodes can reach each other!")