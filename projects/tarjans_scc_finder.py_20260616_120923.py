"""
Date: 2026-06-16
Built Tarjan's SCC algorithm from scratch to detect cycles and component structure in directed graphs — uses a single DFS pass with low-link values.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.
This is one of those elegant algorithms that blew my mind in college — single DFS pass,
no need for the two-pass Kosaraju approach. Uses a stack and "low-link" values to 
identify SCCs on the fly.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Implements Tarjan's algorithm to find all strongly connected components.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set. Great for analyzing dependency
    graphs, finding cycles, or understanding network structure.
    """
    
    def __init__(self, graph):
        """
        Initialize with an adjacency list representation.
        
        Args:
            graph: dict mapping node -> list of neighbor nodes
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
        Main entry point — finds all SCCs in the graph.
        
        Returns:
            List of lists, where each inner list is a strongly connected component.
        """
        # Run DFS from every unvisited node
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that does the heavy lifting.
        
        The key insight: we track the "low-link" value for each node, which represents
        the smallest index reachable from that node. When a node's low-link equals its
        index, we've found the root of an SCC.
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
                # Neighbor hasn't been visited yet — recurse
                self._strongconnect(neighbor)
                # After returning, update our low-link based on the neighbor's
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on the stack, meaning it's part of the current SCC being explored
                # Update low-link to the neighbor's index (earlier in DFS)
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this node is a root of an SCC (low-link equals its own index)
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)


def detect_cycles(graph):
    """
    Uses Tarjan's to detect if a directed graph has cycles.
    
    If any SCC has more than one node, or a single node with a self-loop,
    then the graph contains a cycle.
    """
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    for scc in sccs:
        if len(scc) > 1:
            return True
        # Check for self-loop
        node = scc[0]
        if node in graph.get(node, []):
            return True
    
    return False


def build_condensation_graph(graph, sccs):
    """
    Build the "condensation graph" where each SCC becomes a single node.
    
    This is useful for understanding the high-level structure — the condensation
    is always a DAG (directed acyclic graph), even if the original had cycles.
    """
    # Map each node to its SCC index
    node_to_scc = {}
    for idx, scc in enumerate(sccs):
        for node in scc:
            node_to_scc[node] = idx
    
    # Build edges between SCCs
    condensation = defaultdict(set)
    for node in graph:
        scc_idx = node_to_scc[node]
        for neighbor in graph.get(node, []):
            neighbor_scc = node_to_scc[neighbor]
            if scc_idx != neighbor_scc:
                condensation[scc_idx].add(neighbor_scc)
    
    return {k: list(v) for k, v in condensation.items()}


if __name__ == "__main__":
    # Example 1: A graph with multiple SCCs and cycles
    print("=== Example 1: Classic SCC test case ===")
    graph1 = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [5, 7],
        5: [6],
        6: [4],
        7: []
    }
    
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    print(f"Graph 1 nodes: {list(graph1.keys())}")
    print(f"Strongly Connected Components: {sccs1}")
    print(f"Has cycles: {detect_cycles(graph1)}")
    
    condensation1 = build_condensation_graph(graph1, sccs1)
    print(f"Condensation graph (SCC relationships): {condensation1}")
    print()
    
    # Example 2: A simple cycle
    print("=== Example 2: Simple cycle ===")
    graph2 = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A']
    }
    
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    print(f"Graph 2: {graph2}")
    print(f"SCCs: {sccs2}")
    print(f"Has cycles: {detect_cycles(graph2)}")
    print()
    
    # Example 3: DAG (no cycles)
    print("=== Example 3: Directed Acyclic Graph ===")
    graph3 = {
        'start': ['a', 'b'],
        'a': ['c'],
        'b': ['c'],
        'c': ['end'],
        'end': []
    }
    
    tarjan3 = TarjanSCC(graph3)
    sccs3 = tarjan3.find_sccs()
    print(f"Graph 3 (DAG): {graph3}")
    print(f"SCCs: {sccs3}")
    print(f"Has cycles: {detect_cycles(graph3)}")