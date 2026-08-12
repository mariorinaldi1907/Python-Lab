"""
Date: 2026-08-12
Built Tarjan's SCC algorithm because I wanted to detect circular dependencies in directed graphs without multiple DFS passes.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I chose this over Kosaraju's because it only needs one DFS pass, which felt cleaner.
Works great for detecting cycles and understanding graph structure.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, num_vertices):
        """
        Initialize the SCC finder.
        
        Args:
            num_vertices: Total number of vertices in the graph (0-indexed)
        """
        self.num_vertices = num_vertices
        self.graph = defaultdict(list)
        
    def add_edge(self, u, v):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def find_sccs(self):
        """
        Find all strongly connected components using Tarjan's algorithm.
        
        Uses a single DFS with low-link values to identify SCCs in O(V + E) time.
        The algorithm maintains a stack of vertices in the current path and assigns
        each vertex a discovery time and low-link value.
        
        Returns:
            List of SCCs, where each SCC is a list of vertex indices
        """
        # Discovery time counter - when we first visit each vertex
        self.time = 0
        
        # Track discovery time for each vertex
        self.disc = [-1] * self.num_vertices
        
        # Low-link value: smallest discovery time reachable from this vertex
        self.low = [-1] * self.num_vertices
        
        # Stack to keep track of vertices in current SCC candidate
        self.stack = []
        
        # Track which vertices are currently on the stack
        self.on_stack = [False] * self.num_vertices
        
        # Store the resulting SCCs
        self.sccs = []
        
        # Run DFS from each unvisited vertex (handles disconnected graphs)
        for vertex in range(self.num_vertices):
            if self.disc[vertex] == -1:
                self._dfs(vertex)
        
        return self.sccs
    
    def _dfs(self, u):
        """
        Recursive DFS helper for Tarjan's algorithm.
        
        Args:
            u: Current vertex being explored
        """
        # Assign discovery time and initial low-link value
        self.disc[u] = self.time
        self.low[u] = self.time
        self.time += 1
        
        # Push to stack and mark as on stack
        self.stack.append(u)
        self.on_stack[u] = True
        
        # Explore all neighbors
        for v in self.graph[u]:
            if self.disc[v] == -1:
                # If v hasn't been visited, recurse on it
                self._dfs(v)
                # After returning, update low-link value
                # This propagates the lowest reachable vertex back up
                self.low[u] = min(self.low[u], self.low[v])
            elif self.on_stack[v]:
                # If v is on the stack, it's part of the current SCC candidate
                # Update low-link to v's discovery time
                self.low[u] = min(self.low[u], self.disc[v])
        
        # If u is a root node (low[u] == disc[u]), pop the SCC from stack
        if self.low[u] == self.disc[u]:
            scc = []
            while True:
                v = self.stack.pop()
                self.on_stack[v] = False
                scc.append(v)
                if v == u:
                    break
            self.sccs.append(scc)


def print_graph_info(graph, sccs):
    """
    Pretty print the graph structure and its SCCs.
    
    Args:
        graph: TarjanSCC instance
        sccs: List of strongly connected components
    """
    print("Graph edges:")
    for u in range(graph.num_vertices):
        if graph.graph[u]:
            print(f"  {u} -> {graph.graph[u]}")
    
    print(f"\nFound {len(sccs)} strongly connected component(s):")
    for i, scc in enumerate(sccs, 1):
        print(f"  SCC {i}: {sorted(scc)}")
        if len(scc) > 1:
            print(f"    ^ This is a cycle!")


if __name__ == "__main__":
    # Test case 1: Classic example with multiple SCCs
    print("=" * 60)
    print("Test 1: Graph with multiple SCCs and a cycle")
    print("=" * 60)
    
    g1 = TarjanSCC(8)
    # Creating a graph structure:
    # 0 -> 1 -> 2 -> 0 (cycle forming one SCC)
    # 2 -> 3 -> 4
    # 4 -> 5 -> 3 (another cycle: 3-4-5)
    # 1 -> 6 -> 7
    g1.add_edge(0, 1)
    g1.add_edge(1, 2)
    g1.add_edge(2, 0)
    g1.add_edge(2, 3)
    g1.add_edge(3, 4)
    g1.add_edge(4, 5)
    g1.add_edge(5, 3)
    g1.add_edge(1, 6)
    g1.add_edge(6, 7)
    
    sccs1 = g1.find_sccs()
    print_graph_info(g1, sccs1)
    
    # Test case 2: Simple DAG (no cycles, each vertex is its own SCC)
    print("\n" + "=" * 60)
    print("Test 2: Directed Acyclic Graph (DAG)")
    print("=" * 60)
    
    g2 = TarjanSCC(5)
    g2.add_edge(0, 1)
    g2.add_edge(0, 2)
    g2.add_edge(1, 3)
    g2.add_edge(2, 3)
    g2.add_edge(3, 4)
    
    sccs2 = g2.find_sccs()
    print_graph_info(g2, sccs2)
    
    # Test case 3: Single large SCC (everything connected)
    print("\n" + "=" * 60)
    print("Test 3: Fully connected cycle")
    print("=" * 60)
    
    g3 = TarjanSCC(4)
    g3.add_edge(0, 1)
    g3.add_edge(1, 2)
    g3.add_edge(2, 3)
    g3.add_edge(3, 0)
    
    sccs3 = g3.find_sccs()
    print_graph_info(g3, sccs3)