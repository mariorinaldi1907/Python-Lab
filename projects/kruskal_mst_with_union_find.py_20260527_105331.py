"""
Date: 2026-05-27
Built Kruskal's algorithm for finding minimum spanning trees using a union-find data structure with path compression and union by rank.
"""

#!/usr/bin/env python3
"""
Kruskal's Minimum Spanning Tree Algorithm
Uses union-find (disjoint set union) to efficiently detect cycles.
"""


class UnionFind:
    """
    Union-Find data structure with path compression and union by rank.
    
    I always liked how elegant this structure is — basically lets you
    group elements into disjoint sets and check connectivity super fast.
    """
    
    def __init__(self, n):
        """
        Initialize n disjoint sets (0 to n-1).
        
        Args:
            n: Number of elements
        """
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        """
        Find the root of the set containing x, with path compression.
        
        Path compression flattens the tree as we traverse up, making
        future finds way faster. It's one of those "free optimizations"
        that's too good to pass up.
        
        Args:
            x: Element to find
            
        Returns:
            Root of the set containing x
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]
    
    def union(self, x, y):
        """
        Merge the sets containing x and y.
        
        Uses union by rank to keep the tree shallow. Always attach
        the smaller tree under the larger one.
        
        Args:
            x: Element in first set
            y: Element in second set
            
        Returns:
            True if sets were merged, False if already in same set
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # already in the same set
        
        # union by rank: attach smaller tree under larger
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        
        return True


def kruskal_mst(num_vertices, edges):
    """
    Find minimum spanning tree using Kruskal's algorithm.
    
    The idea: sort all edges by weight, then greedily add them unless
    they'd create a cycle. Union-find makes cycle detection O(α(n)),
    which is effectively constant time.
    
    Args:
        num_vertices: Number of vertices (0-indexed)
        edges: List of (weight, u, v) tuples
        
    Returns:
        Tuple of (mst_edges, total_weight) where mst_edges is a list
        of (u, v, weight) tuples in the MST
    """
    # Sort edges by weight (that's the greedy part)
    sorted_edges = sorted(edges)
    
    uf = UnionFind(num_vertices)
    mst_edges = []
    total_weight = 0
    
    for weight, u, v in sorted_edges:
        # Try to add this edge — only works if it doesn't create a cycle
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # MST has exactly n-1 edges, so we can early exit
            if len(mst_edges) == num_vertices - 1:
                break
    
    return mst_edges, total_weight


def print_graph(num_vertices, edges):
    """Pretty print the graph for debugging."""
    print(f"Graph with {num_vertices} vertices:")
    for weight, u, v in sorted(edges):
        print(f"  {u} --[{weight}]-- {v}")


def print_mst(mst_edges, total_weight):
    """Pretty print the MST result."""
    print(f"\nMinimum Spanning Tree (total weight: {total_weight}):")
    for u, v, weight in mst_edges:
        print(f"  {u} --[{weight}]-- {v}")


if __name__ == "__main__":
    # Example graph from CLRS (classic algorithms textbook)
    # Using a connected graph so we actually get a spanning tree
    num_vertices = 9
    edges = [
        (4, 0, 1),
        (8, 0, 7),
        (11, 1, 7),
        (8, 1, 2),
        (7, 2, 3),
        (4, 2, 5),
        (2, 2, 8),
        (9, 3, 4),
        (14, 3, 5),
        (10, 4, 5),
        (2, 5, 6),
        (1, 6, 7),
        (6, 6, 8),
        (7, 7, 8),
    ]
    
    print("=" * 50)
    print("Kruskal's MST Demo")
    print("=" * 50)
    
    print_graph(num_vertices, edges)
    
    mst_edges, total_weight = kruskal_mst(num_vertices, edges)
    
    print_mst(mst_edges, total_weight)
    
    # Sanity check: MST should have n-1 edges
    print(f"\nVerification: MST has {len(mst_edges)} edges")
    print(f"Expected: {num_vertices - 1} edges")
    
    if len(mst_edges) == num_vertices - 1:
        print("✓ Correct number of edges!")
    else:
        print("✗ Something went wrong — graph might be disconnected")