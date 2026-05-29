"""
Date: 2026-05-29
Built Tarjan's SCC algorithm from scratch to find cycles in directed graphs — really satisfying to see the stack-based approach work in practice.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I've always found SCCs fascinating — they show up in analyzing dependencies,
finding cycles in state machines, and even in compiler optimization.
This implementation uses the classic depth-first search with a low-link value trick.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    The beauty of this algorithm is that it does everything in a single DFS pass,
    using an auxiliary stack to track the current "potential SCC" being explored.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: dict mapping each node to a list of its outgoing neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # lowest index reachable from this node
        self.index = {}     # discovery time of each node
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of lists, where each inner list is one SCC (set of nodes).
        """
        # Need to visit every node since the graph might be disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that does the actual SCC detection.
        
        The lowlink value tracks the smallest index of any node reachable from
        the current node. When a node's lowlink equals its index, we've found
        the root of an SCC.
        """
        # Set the depth index for this node
        self.index[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Explore all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self._strongconnect(neighbor)
                # After returning, update our lowlink based on what we found
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC, update lowlink
                # This is the key insight — we found a back edge!
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this node is a root of an SCC, pop the stack to extract the component
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)


def build_example_graph():
    """
    Create a sample directed graph with multiple SCCs.
    
    This graph has some interesting structure:
    - A cycle between nodes 0, 1, 2 (one SCC)
    - A cycle between nodes 3, 4 (another SCC)
    - Node 5 points to both SCCs but isn't part of either
    - Node 6 is isolated (its own SCC)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],      # cycle: 0 -> 1 -> 2 -> 0
        3: [4],
        4: [3, 5],   # cycle: 3 -> 4 -> 3
        5: [0, 6],   # 5 connects to the first SCC and node 6
        6: [],       # isolated node
    }
    return graph


def visualize_graph(graph):
    """Print the graph structure in a readable format."""
    print("Graph structure:")
    for node in sorted(graph.keys()):
        neighbors = graph.get(node, [])
        if neighbors:
            print(f"  {node} -> {neighbors}")
        else:
            print(f"  {node} -> (no outgoing edges)")
    print()


def main():
    """
    Demo the SCC finder on an example graph.
    
    I'm printing everything step-by-step so it's easy to verify correctness.
    """
    print("=" * 60)
    print("Tarjan's Strongly Connected Components Algorithm")
    print("=" * 60)
    print()
    
    # Build and display the graph
    graph = build_example_graph()
    visualize_graph(graph)
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    # Display results
    print(f"Found {len(sccs)} strongly connected component(s):")
    print()
    
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display (though SCCs themselves are unordered)
        sorted_scc = sorted(scc)
        print(f"  SCC #{i}: {sorted_scc}")
        
        # Explain what makes this an SCC
        if len(scc) == 1:
            node = scc[0]
            if node in graph.get(node, []):
                print(f"           (self-loop)")
            else:
                print(f"           (isolated or no cycles)")
        else:
            print(f"           (cycle of {len(scc)} nodes)")
    
    print()
    print("=" * 60)
    print("Why this matters:")
    print("  - SCCs help identify circular dependencies")
    print("  - Useful in compiler optimization (loop detection)")
    print("  - Key for analyzing social networks and web graphs")
    print("=" * 60)


if __name__ == "__main__":
    main()