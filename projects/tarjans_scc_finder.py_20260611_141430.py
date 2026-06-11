"""
Date: 2026-06-11
Built Tarjan's SCC algorithm because I needed to understand cyclic dependencies in a project graph — way cooler than I expected.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I wanted to understand how circular dependencies form in complex systems, so I built this.
Tarjan's is elegant — uses DFS with low-link values to identify SCCs in linear time.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Find all strongly connected components in a directed graph using Tarjan's algorithm.
    
    An SCC is a maximal set of vertices where every vertex is reachable from every other.
    This is super useful for detecting cycles and analyzing graph structure.
    """
    
    def __init__(self, graph):
        """
        Initialize with an adjacency list representation.
        
        Args:
            graph: dict mapping each node to a list of its outgoing neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}
        self.index = {}
        self.on_stack = set()
        self.sccs = []
    
    def strongconnect(self, node):
        """
        Recursive DFS that builds SCCs using the low-link heuristic.
        
        The low-link value tracks the smallest index reachable from this node.
        When a node's index equals its low-link, we've found an SCC root.
        """
        # Set the depth index for this node
        self.index[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Explore neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self.strongconnect(neighbor)
                # Update low-link after returning from recursion
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on the stack, meaning it's in the current SCC
                # Update low-link to reflect this back-edge
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this node is a root node (low-link equals index), pop the SCC off the stack
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            list of lists, where each inner list is an SCC (set of nodes)
        """
        # Run DFS from every unvisited node
        for node in self.graph:
            if node not in self.index:
                self.strongconnect(node)
        
        # Also need to check nodes that are only mentioned as neighbors
        all_nodes = set(self.graph.keys())
        for neighbors in self.graph.values():
            all_nodes.update(neighbors)
        
        for node in all_nodes:
            if node not in self.index:
                self.strongconnect(node)
        
        return self.sccs


def build_example_graph():
    """
    Create a directed graph with some interesting SCCs.
    
    This graph has:
    - A 3-node cycle (0, 1, 2)
    - A 2-node cycle (3, 4)
    - A single strongly connected component (5)
    - Some connections between components
    """
    graph = defaultdict(list)
    
    # First SCC: 0 -> 1 -> 2 -> 0 (cycle)
    graph[0] = [1]
    graph[1] = [2]
    graph[2] = [0]
    
    # Second SCC: 3 <-> 4 (mutual connection)
    graph[3] = [4]
    graph[4] = [3]
    
    # Third SCC: just node 5 by itself
    graph[5] = []
    
    # Connect the SCCs (these edges don't create larger SCCs)
    graph[2].append(3)  # Bridge from first SCC to second
    graph[4].append(5)  # Bridge from second SCC to third
    
    # Add another isolated cycle
    graph[6] = [7]
    graph[7] = [8]
    graph[8] = [6]
    
    return dict(graph)


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Build a test graph
    graph = build_example_graph()
    
    print("Graph structure (adjacency list):")
    for node in sorted(graph.keys()):
        print(f"  {node} -> {graph[node]}")
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected components:")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display (SCCs themselves are unordered sets)
        sorted_scc = sorted(scc)
        if len(scc) > 1:
            print(f"  SCC {i}: {sorted_scc} (contains a cycle!)")
        else:
            print(f"  SCC {i}: {sorted_scc}")
    
    print("\n=== Why this matters ===")
    print("SCCs help identify:")
    print("  - Circular dependencies in software")
    print("  - Communities in social networks")
    print("  - Deadlock potential in concurrent systems")
    print("  - Strongly related web pages (used in early Google)")