"""
Date: 2026-07-28
Built Tarjan's SCC algorithm because I needed to analyze dependency cycles in a config graph — works in one DFS pass which is pretty neat.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I implemented this after realizing that doing two DFS passes (Kosaraju's) felt wasteful.
Tarjan's does it in one pass using a stack and some clever bookkeeping with "lowlink" values.
The lowlink represents the smallest index reachable from a node's subtree.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Find all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: dict mapping node -> list of neighbors (adjacency list)
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
            List of SCCs, where each SCC is a list of nodes.
        """
        # Need to check all nodes in case graph is disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that builds SCCs.
        
        The tricky part: we maintain a stack of nodes in the current path.
        When we find a node whose lowlink equals its index, we've found
        the root of an SCC and can pop everything above it off the stack.
        """
        # Set the depth index for this node
        self.index[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Check all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self._strongconnect(neighbor)
                # After returning, update lowlink based on what we found
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC (still on stack)
                # This is a back edge, so update lowlink
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this is a root node (lowlink equals index), pop the SCC off the stack
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)


def build_graph_from_edges(edges):
    """
    Convert a list of directed edges into an adjacency list.
    
    Args:
        edges: List of (from_node, to_node) tuples
    
    Returns:
        Adjacency list as a defaultdict
    """
    graph = defaultdict(list)
    nodes = set()
    
    for src, dst in edges:
        graph[src].append(dst)
        nodes.add(src)
        nodes.add(dst)
    
    # Make sure isolated nodes are in the graph too
    for node in nodes:
        if node not in graph:
            graph[node] = []
    
    return dict(graph)


def visualize_graph(graph):
    """Print a human-readable representation of the graph."""
    print("Graph structure:")
    for node in sorted(graph.keys()):
        neighbors = graph[node]
        if neighbors:
            print(f"  {node} -> {', '.join(map(str, neighbors))}")
        else:
            print(f"  {node} -> (no outgoing edges)")
    print()


if __name__ == "__main__":
    # Example 1: Classic SCC example from textbooks
    # This creates a graph with two clear SCCs: {0,1,2} and {3,4}
    print("=" * 60)
    print("Example 1: Textbook case with two SCCs")
    print("=" * 60)
    
    edges1 = [
        (0, 1),
        (1, 2),
        (2, 0),  # Cycle: 0->1->2->0
        (1, 3),
        (3, 4),
        (4, 3),  # Cycle: 3->4->3
    ]
    
    graph1 = build_graph_from_edges(edges1)
    visualize_graph(graph1)
    
    finder1 = TarjanSCC(graph1)
    sccs1 = finder1.find_sccs()
    
    print(f"Found {len(sccs1)} strongly connected components:")
    for i, scc in enumerate(sccs1, 1):
        print(f"  SCC {i}: {{{', '.join(map(str, sorted(scc)))}}}")
    
    print("\n")
    
    # Example 2: More complex graph with single-node SCCs
    print("=" * 60)
    print("Example 2: Mixed graph with various SCC sizes")
    print("=" * 60)
    
    edges2 = [
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'A'),  # SCC: A, B, C
        ('C', 'D'),
        ('D', 'E'),  # D and E are separate SCCs (no cycles)
        ('B', 'F'),
        ('F', 'G'),
        ('G', 'F'),  # SCC: F, G
    ]
    
    graph2 = build_graph_from_edges(edges2)
    visualize_graph(graph2)
    
    finder2 = TarjanSCC(graph2)
    sccs2 = finder2.find_sccs()
    
    print(f"Found {len(sccs2)} strongly connected components:")
    for i, scc in enumerate(sccs2, 1):
        print(f"  SCC {i}: {{{', '.join(sorted(scc))}}}")
    
    print("\n")
    
    # Example 3: Disconnected graph
    print("=" * 60)
    print("Example 3: Disconnected components")
    print("=" * 60)
    
    edges3 = [
        (1, 2),
        (2, 1),
        (5, 6),
        (6, 7),
        (7, 5),
    ]
    
    graph3 = build_graph_from_edges(edges3)
    visualize_graph(graph3)
    
    finder3 = TarjanSCC(graph3)
    sccs3 = finder3.find_sccs()
    
    print(f"Found {len(sccs3)} strongly connected components:")
    for i, scc in enumerate(sccs3, 1):
        print(f"  SCC {i}: {{{', '.join(map(str, sorted(scc)))}}}")
```