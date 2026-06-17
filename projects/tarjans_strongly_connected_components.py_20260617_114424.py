"""
Date: 2026-06-17
Built Tarjan's algorithm to find strongly connected components in directed graphs — wanted something more elegant than Kosaraju's two-pass approach.
"""

"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I've always found SCCs fascinating — they show up everywhere from compiler optimization
to social network analysis. Tarjan's approach is beautiful because it finds all SCCs
in a single DFS pass, which feels almost magical when you first see it work.

The key insight is using a "low-link" value to track the smallest node reachable
in the current SCC being explored. When low[node] == disc[node], we've found the
root of an SCC and can pop everything above it on the stack.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    Time complexity: O(V + E) where V is vertices and E is edges.
    Space complexity: O(V) for the recursion stack and auxiliary data structures.
    """
    
    def __init__(self, vertices):
        """
        Initialize the graph with a given number of vertices.
        
        Args:
            vertices: Number of vertices in the graph (0-indexed)
        """
        self.V = vertices
        self.graph = defaultdict(list)
        
    def add_edge(self, u, v):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def _dfs(self, node, disc, low, stack, on_stack, time, sccs):
        """
        Recursive DFS helper that does the heavy lifting for Tarjan's algorithm.
        
        This is where the magic happens. We track discovery time and the lowest
        reachable ancestor (low-link value) for each node. When we find that
        low[node] == disc[node], we know we've hit an SCC root.
        
        Args:
            node: Current node being explored
            disc: Discovery times for each node
            low: Low-link values (smallest reachable node)
            stack: Stack of nodes in current DFS path
            on_stack: Set tracking which nodes are currently on the stack
            time: Current discovery time (passed as list to maintain reference)
            sccs: List to collect all SCCs found
        """
        # Initialize discovery time and low value
        disc[node] = low[node] = time[0]
        time[0] += 1
        stack.append(node)
        on_stack.add(node)
        
        # Explore all neighbors
        for neighbor in self.graph[node]:
            if disc[neighbor] == -1:
                # Neighbor not visited yet, recurse
                self._dfs(neighbor, disc, low, stack, on_stack, time, sccs)
                # After returning, update low[node] based on the subtree
                low[node] = min(low[node], low[neighbor])
            elif neighbor in on_stack:
                # Neighbor is on stack, meaning it's in the current SCC
                # Update low[node] to the discovery time of the neighbor
                low[node] = min(low[node], disc[neighbor])
        
        # If low[node] == disc[node], then node is the root of an SCC
        # Time to pop everything that belongs to this component
        if low[node] == disc[node]:
            scc = []
            while True:
                popped = stack.pop()
                on_stack.remove(popped)
                scc.append(popped)
                if popped == node:
                    break
            sccs.append(scc)
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            A list of SCCs, where each SCC is a list of vertices.
        """
        # Initialize data structures
        disc = [-1] * self.V  # Discovery times, -1 means unvisited
        low = [-1] * self.V   # Low-link values
        stack = []
        on_stack = set()
        time = [0]  # Using list to maintain reference across recursive calls
        sccs = []
        
        # Call DFS for each unvisited node
        # This handles disconnected graphs gracefully
        for node in range(self.V):
            if disc[node] == -1:
                self._dfs(node, disc, low, stack, on_stack, time, sccs)
        
        return sccs


def visualize_graph(graph_obj):
    """
    Print a simple visualization of the graph's adjacency list.
    
    Args:
        graph_obj: TarjanSCC instance to visualize
    """
    print("\nGraph structure (adjacency list):")
    for node in range(graph_obj.V):
        neighbors = graph_obj.graph[node]
        if neighbors:
            print(f"  {node} -> {neighbors}")
        else:
            print(f"  {node} -> []")


if __name__ == "__main__":
    # Demo with a classic example that has multiple SCCs
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Create a graph with 8 vertices
    # This graph has some interesting structure with multiple SCCs
    g = TarjanSCC(8)
    
    # Building a graph that looks like this:
    #   0 → 1 → 2
    #   ↑   ↓   ↓
    #   └── 3 ← ┘
    # 
    # Plus a separate component:
    #   4 ⇄ 5 → 6 → 7
    #           ↑   ↓
    #           └───┘
    
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),  # First SCC: 0-1-2-3 form a cycle
        (1, 3),  # Extra edge within the SCC
        (4, 5),
        (5, 4),  # Second SCC: 4-5 form a cycle
        (5, 6),
        (6, 7),
        (7, 6),  # Third SCC: 6-7 form a cycle
    ]
    
    for u, v in edges:
        g.add_edge(u, v)
    
    visualize_graph(g)
    
    # Find and display SCCs
    sccs = g.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        print(f"  SCC {i}: {scc}")
    
    # Verify the algorithm with a simpler acyclic case
    print("\n" + "="*50)
    print("\nBonus: Testing with a simple DAG (should have all singleton SCCs):\n")
    
    dag = TarjanSCC(4)
    dag.add_edge(0, 1)
    dag.add_edge(0, 2)
    dag.add_edge(1, 3)
    dag.add_edge(2, 3)
    
    visualize_graph(dag)
    dag_sccs = dag.find_sccs()
    
    print(f"\nFound {len(dag_sccs)} SCC(s) in DAG:")
    for i, scc in enumerate(dag_sccs, 1):
        print(f"  SCC {i}: {scc}")
    
    print("\n✓ As expected, DAGs have only singleton SCCs!")