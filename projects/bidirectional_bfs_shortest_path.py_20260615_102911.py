"""
Date: 2026-06-15
Built a bidirectional BFS algorithm that searches from both ends simultaneously, cutting search space dramatically for finding shortest paths in unweighted graphs.
"""

#!/usr/bin/env python3
"""
Bidirectional BFS for finding shortest paths in unweighted graphs.

I wanted to implement this after reading about how it's used in things like
Six Degrees of Kevin Bacon. The idea is simple: start BFS from both the source
and target simultaneously, and stop when they meet in the middle. This can be
way faster than regular BFS because the search space grows exponentially with
depth, so two smaller searches beat one big one.
"""

from collections import deque
from typing import Dict, List, Set, Optional, Tuple


class BidirectionalBFS:
    """
    Bidirectional BFS implementation for shortest path finding.
    
    Works on unweighted, undirected graphs. The bidirectional approach can
    reduce the search space significantly compared to standard BFS, especially
    when the graph has high branching factor.
    """
    
    def __init__(self, graph: Dict[str, List[str]]):
        """
        Initialize with an adjacency list representation of the graph.
        
        Args:
            graph: Dictionary mapping each node to a list of its neighbors
        """
        self.graph = graph
    
    def find_shortest_path(self, start: str, goal: str) -> Optional[List[str]]:
        """
        Find shortest path between start and goal using bidirectional BFS.
        
        The algorithm maintains two frontiers (one from each end) and alternates
        expanding them. When a node is found in both visited sets, we've found
        the meeting point and can reconstruct the path.
        
        Args:
            start: Starting node
            goal: Target node
            
        Returns:
            List of nodes representing the path, or None if no path exists
        """
        if start == goal:
            return [start]
        
        if start not in self.graph or goal not in self.graph:
            return None
        
        # Forward search: from start toward goal
        forward_queue = deque([start])
        forward_visited = {start: None}  # maps node to its parent
        
        # Backward search: from goal toward start
        backward_queue = deque([goal])
        backward_visited = {goal: None}
        
        # Keep searching until we find intersection or exhaust possibilities
        while forward_queue and backward_queue:
            # Expand from the smaller frontier to keep things balanced
            # This heuristic helps when one direction has more branching
            if len(forward_queue) <= len(backward_queue):
                meeting_point = self._expand_frontier(
                    forward_queue, forward_visited, backward_visited
                )
                if meeting_point:
                    return self._reconstruct_path(
                        meeting_point, forward_visited, backward_visited
                    )
            else:
                meeting_point = self._expand_frontier(
                    backward_queue, backward_visited, forward_visited
                )
                if meeting_point:
                    return self._reconstruct_path(
                        meeting_point, forward_visited, backward_visited
                    )
        
        # No path exists
        return None
    
    def _expand_frontier(
        self, 
        queue: deque, 
        visited: Dict[str, Optional[str]], 
        other_visited: Dict[str, Optional[str]]
    ) -> Optional[str]:
        """
        Expand one level of BFS from the current frontier.
        
        This processes all nodes at the current depth level. I'm doing it
        level-by-level instead of node-by-node to ensure we find the shortest
        path and detect intersections properly.
        
        Args:
            queue: Current frontier to expand
            visited: Visited set for this direction
            other_visited: Visited set for the opposite direction
            
        Returns:
            Meeting point node if frontiers intersect, None otherwise
        """
        # Process all nodes at current level
        level_size = len(queue)
        
        for _ in range(level_size):
            current = queue.popleft()
            
            # Check all neighbors
            for neighbor in self.graph.get(current, []):
                # Skip if already visited in this direction
                if neighbor in visited:
                    continue
                
                # Mark as visited and track parent
                visited[neighbor] = current
                queue.append(neighbor)
                
                # Check if we've intersected with the other search
                if neighbor in other_visited:
                    return neighbor
        
        return None
    
    def _reconstruct_path(
        self,
        meeting_point: str,
        forward_visited: Dict[str, Optional[str]],
        backward_visited: Dict[str, Optional[str]]
    ) -> List[str]:
        """
        Reconstruct the full path once the two searches meet.
        
        We trace back from the meeting point to the start (using forward_visited),
        then from the meeting point to the goal (using backward_visited), and
        stitch them together.
        
        Args:
            meeting_point: Node where the two searches intersected
            forward_visited: Parent map from forward search
            backward_visited: Parent map from backward search
            
        Returns:
            Complete path from start to goal
        """
        # Build path from start to meeting point
        path_start = []
        node = meeting_point
        while node is not None:
            path_start.append(node)
            node = forward_visited[node]
        path_start.reverse()
        
        # Build path from meeting point to goal
        path_end = []
        node = backward_visited[meeting_point]  # Start with meeting point's parent
        while node is not None:
            path_end.append(node)
            node = backward_visited[node]
        
        # Combine both halves
        return path_start + path_end


if __name__ == "__main__":
    # Build a social network-style graph for testing
    # This represents friendships in a small network
    social_network = {
        "Alice": ["Bob", "Carol", "Diana"],
        "Bob": ["Alice", "Eve"],
        "Carol": ["Alice", "Frank"],
        "Diana": ["Alice", "George"],
        "Eve": ["Bob", "Helen"],
        "Frank": ["Carol", "Ian"],
        "George": ["Diana"],
        "Helen": ["Eve", "Ian"],
        "Ian": ["Frank", "Helen"]
    }
    
    print("Social Network Graph - Finding shortest paths\n")
    
    bfs = BidirectionalBFS(social_network)
    
    # Test several paths
    test_cases = [
        ("Alice", "Ian"),
        ("Alice", "Helen"),
        ("George", "Eve"),
        ("Alice", "Alice"),  # Same node
        ("Bob", "Frank"),
    ]
    
    for start, goal in test_cases:
        path = bfs.find_shortest_path(start, goal)
        if path:
            print(f"{start} → {goal}:")
            print(f"  Path: {' → '.join(path)}")
            print(f"  Distance: {len(path) - 1} connections\n")
        else:
            print(f"{start} → {goal}: No path exists\n")