"""
Date: 2026-07-10
Built Tarjan's SCC algorithm to decompose directed graphs into strongly connected components — really elegant use of DFS and stack invariants.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components in a directed graph.

I've always been fascinated by how this algorithm uses a single DFS pass to find
all SCCs. The key insight is tracking both discovery time and the lowest reachable
ancestor, which lets us identify when we've completed an SCC.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds strongly connected components using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every
    vertex is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder with a directed graph.
        
        Args:
            graph: Dict mapping each node to a list of its outgoing neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # Lowest index reachable from this node
        self.index = {}     # Discovery time of each node
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of lists, where each inner list is one SCC
        """
        # We need to check all nodes because the graph might be disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that identifies SCCs.
        
        The magic happens here: we track the lowest index reachable from each
        node. When a node's lowlink equals its index, we've found the root of
        an SCC and can pop everything above it from the stack.
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
                # Update lowlink based on what we learned from the subtree
                self.lowlinks[node] = min(self.lowlinks[node], 
                                         self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on stack, meaning it's in the current SCC
                # Update lowlink to reflect this back edge
                self.lowlinks[node] = min(self.lowlinks[node], 
                                         self.index[neighbor])
        
        # If this node is a root node (lowlink == index), pop the SCC off stack
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
    Build a test graph with multiple SCCs for demonstration.
    
    The graph looks like:
        0 -> 1 -> 2 -> 0  (SCC 1: cycle)
        2 -> 3
        3 -> 4 -> 5 -> 3  (SCC 2: cycle)
        6 -> 7 -> 6       (SCC 3: cycle)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [5],
        5: [3],
        6: [7],
        7: [6],
    }
    return graph


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components ===\n")
    
    # Build and analyze the example graph
    graph = build_example_graph()
    
    print("Graph structure:")
    for node, neighbors in sorted(graph.items()):
        print(f"  {node} -> {neighbors}")
    
    print("\nFinding strongly connected components...\n")
    
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"Found {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent output (the algorithm order can vary)
        scc_sorted = sorted(scc)
        print(f"  SCC {i}: {scc_sorted}")
        if len(scc) == 1:
            print(f"         (singleton - no cycles)")
        else:
            print(f"         (cycle detected!)")
    
    # Test with a simple DAG (no cycles)
    print("\n" + "="*50)
    print("\nTesting with a DAG (should have all singletons):")
    dag = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': [],
    }
    
    print("\nDAG structure:")
    for node, neighbors in sorted(dag.items()):
        print(f"  {node} -> {neighbors}")
    
    tarjan_dag = TarjanSCC(dag)
    dag_sccs = tarjan_dag.find_sccs()
    
    print(f"\nFound {len(dag_sccs)} component(s):")
    for scc in dag_sccs:
        print(f"  {sorted(scc)}")