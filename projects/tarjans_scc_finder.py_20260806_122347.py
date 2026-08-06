"""
Date: 2026-08-06
Built Tarjan's SCC algorithm because I wanted to understand how dependency cycles get detected in real build systems.
"""

"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I implemented this after reading about how package managers detect circular dependencies.
The algorithm is beautifully elegant — it does a single DFS pass and uses a stack to track
potential SCCs. The "low-link" value is what makes it work: it tracks the smallest index
reachable from each node, which lets us identify when we've completed an SCC.
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
        Initialize with a graph represented as an adjacency list.
        
        Args:
            graph: dict mapping each node to a list of its outgoing neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # lowest index reachable from this node
        self.index = {}  # discovery time of each node
        self.on_stack = {}  # track which nodes are currently on the stack
        self.sccs = []  # will hold all the strongly connected components
        
    def find_sccs(self):
        """
        Find all SCCs in the graph.
        
        Returns:
            list of lists, where each inner list is one SCC
        """
        # Need to check all nodes since graph might be disconnected
        for node in self.graph:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, node):
        """
        Recursive DFS that identifies SCCs.
        
        This is the heart of Tarjan's algorithm. We assign each node an index (discovery time)
        and a lowlink value (smallest index reachable). When we finish exploring a node and
        its lowlink equals its index, we've found the root of an SCC.
        """
        # Set the depth index for this node
        self.index[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        self.on_stack[node] = True
        self.stack.append(node)
        
        # Check all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet; recurse
                self._strongconnect(neighbor)
                # After returning, update our lowlink based on what the neighbor found
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif self.on_stack[neighbor]:
                # Neighbor is on stack, so it's in the current SCC being formed
                # Update lowlink to the neighbor's index (not lowlink, which is key!)
                self.lowlinks[node] = min(self.lowlinks[node], self.index[neighbor])
        
        # If this is a root node of an SCC, pop the SCC off the stack
        if self.lowlinks[node] == self.index[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack[w] = False
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)


def build_example_graph():
    """
    Create a directed graph with several SCCs for demonstration.
    
    This graph has 3 SCCs:
    - {0, 1, 2} form a cycle
    - {3, 4} form a cycle
    - {5} is alone (self-loop makes it an SCC of size 1)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],  # cycle: 0 -> 1 -> 2 -> 0
        3: [4],
        4: [3, 5],  # cycle: 3 -> 4 -> 3, plus edge to 5
        5: [5],  # self-loop
    }
    return graph


def visualize_graph(graph):
    """Print the graph in a readable format."""
    print("Graph structure:")
    for node in sorted(graph.keys()):
        neighbors = graph[node]
        if neighbors:
            print(f"  {node} -> {neighbors}")
        else:
            print(f"  {node} -> []")
    print()


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components Algorithm ===\n")
    
    # Build and display the example graph
    graph = build_example_graph()
    visualize_graph(graph)
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    # Display results
    print(f"Found {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display (Tarjan's order can vary)
        scc_sorted = sorted(scc)
        print(f"SCC #{i}: {scc_sorted}")
        
        # Explain what makes it an SCC
        if len(scc) == 1:
            node = scc[0]
            if node in graph[node]:
                print(f"  → Single node with self-loop")
            else:
                print(f"  → Single node (trivial SCC)")
        else:
            print(f"  → {len(scc)} nodes forming a cycle")
    
    print("\n" + "="*60)
    print("Why this matters: build systems use this to detect circular")
    print("dependencies, and it's also used in compiler optimization for")
    print("finding mutually recursive functions.")