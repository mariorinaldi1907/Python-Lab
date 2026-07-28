"""
Date: 2026-07-28
Built a topological sorting algorithm that detects cycles in directed graphs — useful for task scheduling and dependency resolution problems I keep running into.
"""

#!/usr/bin/env python3
"""
Topological Sort Implementation with Cycle Detection

I kept needing this for build system stuff and dependency graphs,
so I finally sat down and implemented Kahn's algorithm properly.
It handles cycle detection which is critical — you don't want to
silently fail when someone creates a circular dependency.
"""

from collections import deque, defaultdict
from typing import List, Dict, Set, Tuple, Optional


class Graph:
    """
    Directed graph representation using adjacency lists.
    
    I went with adjacency lists because they're memory-efficient for
    sparse graphs, which is what I usually deal with.
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node: str, to_node: str):
        """Add a directed edge from from_node to to_node."""
        self.adjacency_list[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def get_neighbors(self, node: str) -> List[str]:
        """Get all nodes that this node points to."""
        return self.adjacency_list[node]
    
    def get_all_nodes(self) -> Set[str]:
        """Return all nodes in the graph."""
        return self.nodes.copy()


def compute_indegrees(graph: Graph) -> Dict[str, int]:
    """
    Calculate the in-degree (number of incoming edges) for each node.
    
    This is the key data structure for Kahn's algorithm. Nodes with
    in-degree 0 have no dependencies and can be processed first.
    """
    indegrees = {node: 0 for node in graph.get_all_nodes()}
    
    for node in graph.get_all_nodes():
        for neighbor in graph.get_neighbors(node):
            indegrees[neighbor] += 1
    
    return indegrees


def topological_sort(graph: Graph) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """
    Perform topological sort using Kahn's algorithm.
    
    Returns:
        A tuple of (sorted_order, cycle_nodes):
        - If no cycle exists: (list of nodes in topological order, None)
        - If cycle exists: (None, list of nodes involved in cycle)
    
    The algorithm works by repeatedly removing nodes with no dependencies.
    If we can't remove all nodes, there's a cycle.
    """
    indegrees = compute_indegrees(graph)
    
    # Start with all nodes that have no incoming edges
    # These are the "roots" of our dependency tree
    queue = deque([node for node in graph.get_all_nodes() if indegrees[node] == 0])
    
    sorted_order = []
    
    while queue:
        # Process a node with no remaining dependencies
        current = queue.popleft()
        sorted_order.append(current)
        
        # "Remove" this node by decrementing the in-degree of its neighbors
        for neighbor in graph.get_neighbors(current):
            indegrees[neighbor] -= 1
            
            # If a neighbor now has no dependencies, it's ready to process
            if indegrees[neighbor] == 0:
                queue.append(neighbor)
    
    # If we processed all nodes, we have a valid topological order
    if len(sorted_order) == len(graph.get_all_nodes()):
        return (sorted_order, None)
    
    # Otherwise, there's a cycle — return the nodes still with dependencies
    cycle_nodes = [node for node in graph.get_all_nodes() if indegrees[node] > 0]
    return (None, cycle_nodes)


def find_cycle_path(graph: Graph, nodes_in_cycle: List[str]) -> List[str]:
    """
    Find an actual cycle path for better error messages.
    
    This uses DFS to trace an actual circular path, which is way more
    helpful for debugging than just knowing "there's a cycle somewhere".
    """
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found the cycle — trim path to just the cycle part
                cycle_start_idx = path.index(neighbor)
                path[:] = path[cycle_start_idx:] + [neighbor]
                return True
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    # Start DFS from nodes we know are in a cycle
    for node in nodes_in_cycle:
        if node not in visited:
            if dfs(node):
                return path
    
    return []


if __name__ == "__main__":
    print("=== Topological Sort Demo ===\n")
    
    # Example 1: A valid DAG (course prerequisites)
    print("Example 1: College course prerequisites")
    print("---------------------------------------")
    course_graph = Graph()
    course_graph.add_edge("Intro to CS", "Data Structures")
    course_graph.add_edge("Intro to CS", "Computer Architecture")
    course_graph.add_edge("Data Structures", "Algorithms")
    course_graph.add_edge("Data Structures", "Operating Systems")
    course_graph.add_edge("Computer Architecture", "Operating Systems")
    course_graph.add_edge("Algorithms", "Machine Learning")
    course_graph.add_edge("Operating Systems", "Distributed Systems")
    
    result, cycle = topological_sort(course_graph)
    
    if result:
        print("Valid course order:")
        for i, course in enumerate(result, 1):
            print(f"  {i}. {course}")
    else:
        print(f"ERROR: Cycle detected involving: {cycle}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: A graph with a cycle (build system dependencies)
    print("Example 2: Build dependencies with a cycle")
    print("------------------------------------------")
    build_graph = Graph()
    build_graph.add_edge("main.o", "app")
    build_graph.add_edge("utils.o", "app")
    build_graph.add_edge("app", "test")
    build_graph.add_edge("test", "utils.o")  # Oops, circular dependency!
    build_graph.add_edge("logger.o", "app")
    
    result, cycle = topological_sort(build_graph)
    
    if result:
        print("Valid build order:")
        for i, target in enumerate(result, 1):
            print(f"  {i}. {target}")
    else:
        print(f"ERROR: Cycle detected!")
        print(f"Nodes involved: {cycle}")
        cycle_path = find_cycle_path(build_graph, cycle)
        print(f"Actual cycle path: {' -> '.join(cycle_path)}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Simple task scheduling
    print("Example 3: Morning routine tasks")
    print("--------------------------------")
    routine_graph = Graph()
    routine_graph.add_edge("wake up", "brush teeth")
    routine_graph.add_edge("wake up", "make coffee")
    routine_graph.add_edge("brush teeth", "get dressed")
    routine_graph.add_edge("make coffee", "drink coffee")
    routine_graph.add_edge("get dressed", "leave house")
    routine_graph.add_edge("drink coffee", "leave house")
    
    result, cycle = topological_sort(routine_graph)
    
    if result:
        print("Task order:")
        for i, task in enumerate(result, 1):
            print(f"  {i}. {task}")
    else:
        print(f"ERROR: Cycle detected involving: {cycle}")