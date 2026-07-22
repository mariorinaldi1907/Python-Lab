"""
Date: 2026-07-22
Built Tarjan's SCC algorithm because I wanted to understand how compilers detect cycles in dependency graphs — pure recursive DFS approach with discovery time tracking.
"""

"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I chose this algorithm because it's elegant — single DFS pass, no need for transposing
the graph like Kosaraju's. Uses discovery time and low-link values to identify SCCs.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, vertices):
        """
        Initialize the graph structure.
        
        Args:
            vertices: Number of vertices in the graph (0-indexed)
        """
        self.vertices = vertices
        self.graph = defaultdict(list)
        
        # Core Tarjan data structures
        self.time = 0  # Global timer for discovery times
        self.disc = [-1] * vertices  # Discovery time of each vertex
        self.low = [-1] * vertices   # Earliest discovered vertex reachable
        self.on_stack = [False] * vertices  # Track which vertices are on the stack
        self.stack = []
        self.sccs = []  # Store all found SCCs
    
    def add_edge(self, u, v):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def _dfs(self, u):
        """
        Recursive DFS that does the heavy lifting for Tarjan's algorithm.
        
        The key insight: when we finish exploring a vertex and its low-link value
        equals its discovery time, we've found the root of an SCC.
        
        Args:
            u: Current vertex being explored
        """
        # Initialize discovery time and low-link value
        self.disc[u] = self.time
        self.low[u] = self.time
        self.time += 1
        
        self.stack.append(u)
        self.on_stack[u] = True
        
        # Explore all neighbors
        for v in self.graph[u]:
            if self.disc[v] == -1:
                # Haven't visited this neighbor yet
                self._dfs(v)
                # After returning, update low-link based on what the subtree found
                self.low[u] = min(self.low[u], self.low[v])
            elif self.on_stack[v]:
                # Found a back edge to a vertex still being processed
                # This means v is an ancestor in the current DFS tree
                self.low[u] = min(self.low[u], self.disc[v])
        
        # If u is the root of an SCC, pop the stack to collect all vertices in this SCC
        if self.low[u] == self.disc[u]:
            scc = []
            while True:
                v = self.stack.pop()
                self.on_stack[v] = False
                scc.append(v)
                if v == u:
                    break
            self.sccs.append(scc)
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of vertex indices
        """
        # Run DFS from every unvisited vertex
        # This handles disconnected graphs
        for i in range(self.vertices):
            if self.disc[i] == -1:
                self._dfs(i)
        
        return self.sccs


def demo_tarjan():
    """
    Demonstrate Tarjan's algorithm with a graph that has multiple SCCs.
    
    The graph looks like this:
    0 → 1 → 2
    ↑   ↓   ↓
    ← 3 ← 4
    
    5 → 6 (separate component)
    ↓   ↑
    → 7 ←
    """
    print("=" * 60)
    print("Tarjan's SCC Finder Demo")
    print("=" * 60)
    
    # Create a graph with 8 vertices
    g = TarjanSCC(8)
    
    # First component: vertices 0-4 form a cycle
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 4)
    g.add_edge(4, 3)
    g.add_edge(3, 0)
    g.add_edge(1, 3)  # Additional edge
    
    # Second component: vertices 5-7 form a triangle
    g.add_edge(5, 6)
    g.add_edge(6, 7)
    g.add_edge(7, 5)
    
    print("\nGraph edges:")
    for u in sorted(g.graph.keys()):
        for v in g.graph[u]:
            print(f"  {u} → {v}")
    
    # Find all SCCs
    sccs = g.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected component(s):\n")
    for idx, scc in enumerate(sccs, 1):
        print(f"  SCC {idx}: {sorted(scc)}")
    
    # Demonstrate with a DAG (no cycles except self-loops)
    print("\n" + "=" * 60)
    print("Testing with a DAG (should have all singleton SCCs)")
    print("=" * 60)
    
    dag = TarjanSCC(4)
    dag.add_edge(0, 1)
    dag.add_edge(0, 2)
    dag.add_edge(1, 3)
    dag.add_edge(2, 3)
    
    print("\nDAG edges:")
    for u in sorted(dag.graph.keys()):
        for v in dag.graph[u]:
            print(f"  {u} → {v}")
    
    dag_sccs = dag.find_sccs()
    print(f"\nFound {len(dag_sccs)} SCC(s) (each vertex is its own component):")
    for idx, scc in enumerate(dag_sccs, 1):
        print(f"  SCC {idx}: {scc}")


if __name__ == "__main__":
    demo_tarjan()