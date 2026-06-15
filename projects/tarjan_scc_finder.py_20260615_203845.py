"""
Date: 2026-06-15
Built Tarjan's SCC algorithm from scratch because I finally wanted to understand how it identifies cycles in directed graphs using a single DFS pass.
"""

"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I've always found this algorithm elegant — it uses just one DFS traversal with a stack
to identify all SCCs. The key insight is tracking both discovery time and the lowest
reachable ancestor, which lets us detect when we've completed an SCC.
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
            List of lists, where each inner list is one SCC containing node IDs
        """
        # Need to check all nodes because graph might be disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that identifies SCCs.
        
        The algorithm maintains two key values per node:
        - index: when we first discovered this node (never changes)
        - lowlink: lowest index reachable from this node (updates during DFS)
        
        When lowlink[v] == index[v], we've found the root of an SCC.
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
                # Neighbor hasn't been visited yet, recurse on it
                self._strongconnect(neighbor)
                # After returning, update our lowlink if neighbor found a lower ancestor
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in current SCC (on stack), update lowlink
                # This is the key to detecting cycles
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this node is a root of an SCC, pop the SCC off the stack
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
    
    The graph looks like this:
    0 -> 1 -> 2 -> 0  (one SCC: triangle)
    2 -> 3
    3 -> 4 -> 5 -> 3  (another SCC: triangle)
    5 -> 6
    6 -> 7 -> 8 -> 6  (third SCC: triangle)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [5],
        5: [3, 6],
        6: [7],
        7: [8],
        8: [6],
    }
    return graph


def visualize_graph(graph):
    """Pretty print the graph structure."""
    print("Graph structure:")
    for node in sorted(graph.keys()):
        neighbors = graph.get(node, [])
        if neighbors:
            print(f"  {node} -> {neighbors}")
        else:
            print(f"  {node} -> []")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Tarjan's Algorithm - Strongly Connected Components")
    print("=" * 60)
    print()
    
    # Build and display the example graph
    graph = build_example_graph()
    visualize_graph(graph)
    
    # Find all SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"Found {len(sccs)} strongly connected components:")
    print()
    
    # Display each SCC
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display (Tarjan's doesn't guarantee order)
        scc_sorted = sorted(scc)
        print(f"SCC {i}: {scc_sorted}")
        
        # Show why it's strongly connected
        if len(scc_sorted) > 1:
            print(f"  -> Forms a cycle: ", end="")
            print(" <-> ".join(map(str, scc_sorted)))
        else:
            print(f"  -> Single node (no outgoing edges to cycle)")
        print()
    
    # Another example: simple cycle
    print("-" * 60)
    print("Testing with a simple 4-node cycle:")
    simple_graph = {
        'A': ['B'],
        'B': ['C'],
        'C': ['D'],
        'D': ['A'],
    }
    visualize_graph(simple_graph)
    
    tarjan2 = TarjanSCC(simple_graph)
    sccs2 = tarjan2.find_sccs()
    print(f"Result: {sccs2[0]} forms one SCC (all nodes reachable from each other)")