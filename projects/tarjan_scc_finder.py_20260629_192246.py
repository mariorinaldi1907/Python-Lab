"""
Date: 2026-06-29
Built Tarjan's SCC algorithm from scratch to finally wrap my head around how it uses DFS and a stack to find cycles in directed graphs.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I've always found this algorithm fascinating because it does everything in a single DFS pass.
The trick is using two values per node: discovery time and the lowest reachable ancestor.
When those two values are equal, you've found the root of an SCC.
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
            graph: dict mapping each node to a list of its outgoing neighbors
        """
        self.graph = graph
        self.index_counter = 0  # Tracks discovery order
        self.stack = []
        self.on_stack = set()
        
        # These track the DFS state for each node
        self.indices = {}  # Discovery time of each node
        self.lowlinks = {}  # Lowest index reachable from this node
        
        self.sccs = []  # Will store the final list of SCCs
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of nodes
        """
        # Need to check all nodes because the graph might be disconnected
        for node in self.graph:
            if node not in self.indices:
                self._strong_connect(node)
        
        return self.sccs
    
    def _strong_connect(self, node):
        """
        Recursive DFS that does the heavy lifting.
        
        The key insight: we track the lowest index reachable from each node.
        When a node's lowlink equals its index, it's the root of an SCC.
        """
        # Set the depth index for this node
        self.indices[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Explore all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.indices:
                # Neighbor hasn't been visited yet, recurse on it
                self._strong_connect(neighbor)
                # After recursion, update our lowlink based on what we found
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC, update lowlink
                # This is the back edge case that creates the cycle
                self.lowlinks[node] = min(self.lowlinks[node], self.indices[neighbor])
        
        # If this node is a root of an SCC, pop the SCC off the stack
        if self.lowlinks[node] == self.indices[node]:
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
    Creates a test graph with some interesting SCC structure.
    
    This graph has 3 SCCs:
    - {0, 1, 2} form a cycle
    - {3, 4} form a cycle  
    - {5} is alone
    - {6, 7} form a cycle
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],      # First SCC: 0->1->2->0
        3: [4],
        4: [3, 5],   # Second SCC: 3->4->3, with edge to 5
        5: [6],      # Third SCC: just 5 (no incoming edges from its outgoing)
        6: [7],
        7: [6],      # Fourth SCC: 6->7->6
    }
    return graph


def visualize_graph(graph):
    """Print the graph structure in a readable format."""
    print("Graph structure (node -> neighbors):")
    for node in sorted(graph.keys()):
        neighbors = graph.get(node, [])
        print(f"  {node} -> {neighbors}")
    print()


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Build and display the test graph
    graph = build_example_graph()
    visualize_graph(graph)
    
    # Find all SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"Found {len(sccs)} strongly connected components:\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent output (Tarjan's order can vary)
        scc_sorted = sorted(scc)
        print(f"  SCC {i}: {scc_sorted}")
    
    print("\n" + "="*50)
    print("Testing with a simple cycle:")
    print("="*50 + "\n")
    
    # Another test case: simple triangle
    simple_graph = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A'],
        'D': ['E'],  # Disconnected component
        'E': []
    }
    
    visualize_graph(simple_graph)
    
    tarjan2 = TarjanSCC(simple_graph)
    sccs2 = tarjan2.find_sccs()
    
    print(f"Found {len(sccs2)} strongly connected components:\n")
    for i, scc in enumerate(sccs2, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    
    print("\n✓ Algorithm completed successfully!")