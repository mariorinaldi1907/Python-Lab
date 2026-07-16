"""
Date: 2026-07-16
Built a topological sort implementation that handles both DAG ordering and cycle detection because I kept needing this for dependency resolution stuff.
"""

#!/usr/bin/env python3
"""
Topological Sort with Cycle Detection

I needed a solid topological sort implementation for working with dependency graphs.
This uses Kahn's algorithm (BFS-based) because it naturally detects cycles and
I find it more intuitive than DFS approaches.

The graph is represented as an adjacency list where edges go from prerequisites
to dependents (A -> B means A must come before B).
"""

from collections import deque, defaultdict
from typing import List, Dict, Set, Tuple, Optional


class TopologicalSorter:
    """
    Performs topological sorting on a directed graph using Kahn's algorithm.
    
    Handles cycle detection automatically - if a cycle exists, the sort fails
    and we can identify which nodes are part of the cycle.
    """
    
    def __init__(self):
        """Initialize an empty graph."""
        self.graph = defaultdict(list)  # adjacency list: node -> [neighbors]
        self.nodes = set()
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        """
        Add a directed edge from from_node to to_node.
        
        This represents a dependency: from_node must come before to_node.
        """
        self.graph[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def _calculate_in_degrees(self) -> Dict[str, int]:
        """
        Calculate in-degree (number of incoming edges) for each node.
        
        This is the core of Kahn's algorithm - we repeatedly remove nodes
        with in-degree 0 (no dependencies).
        """
        in_degree = {node: 0 for node in self.nodes}
        
        for node in self.graph:
            for neighbor in self.graph[node]:
                in_degree[neighbor] += 1
        
        return in_degree
    
    def sort(self) -> Tuple[Optional[List[str]], Optional[Set[str]]]:
        """
        Perform topological sort on the graph.
        
        Returns:
            (sorted_order, None) if successful - sorted_order is a valid topological ordering
            (None, cycle_nodes) if cycle detected - cycle_nodes are nodes involved in cycle(s)
        
        The algorithm works by:
        1. Start with all nodes that have no dependencies (in-degree 0)
        2. Process them one by one, removing their outgoing edges
        3. As edges are removed, more nodes reach in-degree 0
        4. If we process all nodes, we have a valid sort
        5. If nodes remain, they're part of a cycle
        """
        if not self.nodes:
            return ([], None)
        
        in_degree = self._calculate_in_degrees()
        
        # Queue starts with all nodes that have no incoming edges
        queue = deque([node for node in self.nodes if in_degree[node] == 0])
        sorted_order = []
        
        while queue:
            # Process a node with no remaining dependencies
            current = queue.popleft()
            sorted_order.append(current)
            
            # Remove this node's outgoing edges by decrementing in-degrees
            for neighbor in self.graph[current]:
                in_degree[neighbor] -= 1
                
                # If neighbor now has no dependencies, add it to queue
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we processed all nodes, we have a valid topological sort
        if len(sorted_order) == len(self.nodes):
            return (sorted_order, None)
        
        # Otherwise, remaining nodes are part of cycle(s)
        cycle_nodes = {node for node in self.nodes if in_degree[node] > 0}
        return (None, cycle_nodes)
    
    def print_graph(self) -> None:
        """Pretty print the graph structure for debugging."""
        print("Graph structure:")
        for node in sorted(self.nodes):
            neighbors = self.graph.get(node, [])
            if neighbors:
                print(f"  {node} -> {', '.join(sorted(neighbors))}")
            else:
                print(f"  {node} -> (no outgoing edges)")


def build_course_prerequisites() -> TopologicalSorter:
    """
    Example: university course prerequisites.
    
    This models a realistic scenario where some courses depend on others.
    """
    sorter = TopologicalSorter()
    
    # Basic courses have no prerequisites (not explicitly added, but included as from_nodes)
    sorter.add_edge("Intro_CS", "Data_Structures")
    sorter.add_edge("Intro_CS", "Algorithms")
    sorter.add_edge("Data_Structures", "Algorithms")
    sorter.add_edge("Data_Structures", "Databases")
    sorter.add_edge("Algorithms", "Machine_Learning")
    sorter.add_edge("Algorithms", "Compilers")
    sorter.add_edge("Math_101", "Machine_Learning")
    sorter.add_edge("Math_101", "Computer_Graphics")
    sorter.add_edge("Data_Structures", "Operating_Systems")
    
    return sorter


def build_cyclic_graph() -> TopologicalSorter:
    """
    Example with a cycle to demonstrate cycle detection.
    
    A -> B -> C -> A forms a cycle (impossible to order).
    """
    sorter = TopologicalSorter()
    
    sorter.add_edge("A", "B")
    sorter.add_edge("B", "C")
    sorter.add_edge("C", "A")  # Creates the cycle
    sorter.add_edge("D", "B")  # D is fine, but depends on cycle
    
    return sorter


if __name__ == "__main__":
    print("=" * 60)
    print("TOPOLOGICAL SORT DEMO - Course Prerequisites")
    print("=" * 60)
    
    # Test case 1: Valid DAG (Directed Acyclic Graph)
    print("\n1. Valid course dependency graph:")
    course_sorter = build_course_prerequisites()
    course_sorter.print_graph()
    
    sorted_courses, cycle = course_sorter.sort()
    
    if sorted_courses:
        print("\n✓ Valid topological ordering found!")
        print("  You could take courses in this order:")
        for i, course in enumerate(sorted_courses, 1):
            print(f"    {i}. {course}")
    else:
        print(f"\n✗ Cycle detected! Nodes in cycle: {cycle}")
    
    # Test case 2: Graph with cycle
    print("\n" + "=" * 60)
    print("2. Graph with a cycle:")
    cyclic_sorter = build_cyclic_graph()
    cyclic_sorter.print_graph()
    
    sorted_nodes, cycle = cyclic_sorter.sort()
    
    if sorted_nodes:
        print("\n✓ Valid topological ordering:")
        print(f"  {' -> '.join(sorted_nodes)}")
    else:
        print(f"\n✗ Cycle detected! Cannot create topological ordering.")
        print(f"  Nodes involved in cycle(s): {', '.join(sorted(cycle))}")
        print("  (These nodes have circular dependencies)")