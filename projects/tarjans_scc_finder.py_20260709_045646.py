"""
Date: 2026-07-09
Built Tarjan's SCC algorithm because I wanted to understand how compilers find loops and cycles in control flow graphs.
"""

"""
Tarjan's algorithm for finding strongly connected components in a directed graph.

I wrote this after reading about how compilers optimize code by detecting
strongly connected components in control flow graphs. It's a beautiful
single-pass DFS algorithm that uses the discovery time and low-link values
to identify SCCs on the fly.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Find all strongly connected components in a directed graph using Tarjan's algorithm.
    
    Time complexity: O(V + E)
    Space complexity: O(V)
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: dict mapping vertex -> list of adjacent vertices
        """
        self.graph = graph
        self.discovery_time = {}  # When we first visited each node
        self.low_link = {}  # Lowest discovery time reachable from subtree
        self.on_stack = set()  # Nodes currently on the DFS stack
        self.stack = []  # Explicit stack for tracking current path
        self.time = 0  # Global counter for discovery times
        self.sccs = []  # Result: list of SCCs (each SCC is a list of nodes)
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of vertices
        """
        # We need to run DFS from every unvisited node because the graph
        # might be disconnected or have unreachable components
        for vertex in self.graph:
            if vertex not in self.discovery_time:
                self._dfs(vertex)
        
        return self.sccs
    
    def _dfs(self, v):
        """
        Depth-first search that identifies SCCs on the fly.
        
        The key insight: when we finish exploring a node and its low-link
        value equals its discovery time, that node is the root of an SCC.
        """
        # Initialize discovery time and low-link for this node
        self.discovery_time[v] = self.time
        self.low_link[v] = self.time
        self.time += 1
        
        # Push onto stack — this tracks our current DFS path
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Explore all neighbors
        for neighbor in self.graph.get(v, []):
            if neighbor not in self.discovery_time:
                # Tree edge: neighbor hasn't been visited yet
                self._dfs(neighbor)
                # After returning, update our low-link based on what
                # the subtree could reach
                self.low_link[v] = min(self.low_link[v], self.low_link[neighbor])
            elif neighbor in self.on_stack:
                # Back edge: neighbor is an ancestor in current DFS tree
                # This means there's a cycle, update low-link
                self.low_link[v] = min(self.low_link[v], self.discovery_time[neighbor])
        
        # If v is a root node of an SCC, pop the SCC off the stack
        if self.low_link[v] == self.discovery_time[v]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == v:
                    break
            self.sccs.append(scc)


def build_sample_graph():
    """
    Build a sample directed graph with multiple SCCs.
    
    This graph has 3 strongly connected components:
    - {0, 1, 2} form a cycle
    - {3} is alone
    - {4, 5, 6} form another cycle
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],  # Cycle: 0 -> 1 -> 2 -> 0
        3: [0, 4],  # 3 connects to other SCCs but isn't part of any cycle
        4: [5],
        5: [6],
        6: [4],  # Cycle: 4 -> 5 -> 6 -> 4
    }
    return graph


def visualize_graph(graph):
    """Print the graph structure in a readable format."""
    print("Graph structure:")
    for vertex in sorted(graph.keys()):
        neighbors = graph.get(vertex, [])
        if neighbors:
            print(f"  {vertex} -> {neighbors}")
        else:
            print(f"  {vertex} -> (no outgoing edges)")
    print()


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components Algorithm ===\n")
    
    # Build and display the graph
    graph = build_sample_graph()
    visualize_graph(graph)
    
    # Find SCCs
    finder = TarjanSCC(graph)
    sccs = finder.find_sccs()
    
    # Display results
    print(f"Found {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display (Tarjan's returns them in reverse
        # topological order, which is cool but makes demo output inconsistent)
        scc_sorted = sorted(scc)
        print(f"SCC #{i}: {scc_sorted}")
        
        # Show why it's strongly connected
        if len(scc) > 1:
            print(f"  → These nodes form a cycle")
        else:
            print(f"  → Singleton component (no cycles involving this node)")
    
    print("\n=== Testing with a simple cycle ===\n")
    simple_cycle = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A'],
    }
    visualize_graph(simple_cycle)
    
    finder2 = TarjanSCC(simple_cycle)
    sccs2 = finder2.find_sccs()
    print(f"SCCs: {sccs2}")
    print("\nAll nodes in one component — the whole graph is one big cycle!")