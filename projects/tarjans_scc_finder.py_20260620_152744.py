"""
Date: 2026-06-20
Built Tarjan's SCC algorithm from scratch to detect cycles and component structure in directed graphs — uses DFS with low-link values.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.
I always found this algorithm fascinating because it does everything in a single DFS pass.
The 'low-link' value idea is clever: it tracks the smallest node index reachable from a subtree.
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
        Initialize the algorithm with a graph represented as an adjacency list.
        
        Args:
            graph: dict mapping node -> list of neighbors (directed edges)
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # lowest index reachable from this node
        self.index = {}     # discovery index for each node
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Main entry point. Returns all strongly connected components.
        
        Returns:
            List of lists, where each inner list is one SCC
        """
        # Need to check all nodes since graph might be disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that does the heavy lifting.
        
        The key insight: we track both discovery time (index) and the lowest
        index reachable (lowlink). When they're equal, we've found an SCC root.
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
                # Neighbor hasn't been visited yet, recurse on it
                self._strongconnect(neighbor)
                # After returning, update lowlink based on what we learned
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on the stack, meaning it's part of current SCC
                # Update lowlink to point to the earlier node
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If lowlink equals index, this node is an SCC root
        # Pop everything up to and including this node from stack
        if self.lowlinks[node] == self.index[node]:
            component = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                component.append(w)
                if w == node:
                    break
            self.sccs.append(component)


def build_sample_graph():
    """
    Create a sample directed graph with some interesting structure.
    
    This graph has multiple SCCs and some cycles to demonstrate the algorithm.
    
    Visual representation:
        0 → 1 → 2
        ↑       ↓
        └───────┘
        
        3 → 4 ⇄ 5
        
        6 → 7 → 8
            ↓
            9
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],      # cycle: 0-1-2-0
        3: [4],
        4: [5],
        5: [4],      # cycle: 4-5-4
        6: [7],
        7: [8, 9],
        8: [],
        9: []
    }
    return graph


def detect_cycles(sccs):
    """
    Determine which SCCs represent actual cycles (more than one node).
    
    Args:
        sccs: List of strongly connected components
        
    Returns:
        List of SCCs that form cycles
    """
    # A cycle exists if an SCC has more than one node
    # (or a single node with a self-loop, but we'll keep it simple)
    return [scc for scc in sccs if len(scc) > 1]


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Build a test graph
    graph = build_sample_graph()
    
    print("Graph structure (adjacency list):")
    for node in sorted(graph.keys()):
        neighbors = graph[node]
        print(f"  {node} → {neighbors if neighbors else '(no outgoing edges)'}")
    
    print("\nFinding strongly connected components...")
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent output
        scc_sorted = sorted(scc)
        size = len(scc)
        is_cycle = "CYCLE" if size > 1 else "single node"
        print(f"  SCC #{i}: {scc_sorted} ({size} node(s)) - {is_cycle}")
    
    # Detect cycles specifically
    cycles = detect_cycles(sccs)
    print(f"\nCycles detected: {len(cycles)}")
    for cycle in cycles:
        print(f"  → {sorted(cycle)}")
    
    # Another example: a simple chain with no cycles
    print("\n" + "="*50)
    print("\nTesting on a directed acyclic graph (DAG):")
    dag = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': []
    }
    
    print("DAG structure:")
    for node in sorted(dag.keys()):
        print(f"  {node} → {dag[node]}")
    
    tarjan_dag = TarjanSCC(dag)
    sccs_dag = tarjan_dag.find_sccs()
    
    print(f"\nSCCs in DAG: {len(sccs_dag)} (should all be single nodes)")
    for scc in sccs_dag:
        print(f"  {scc}")
    
    print("\n✓ All tests complete!")