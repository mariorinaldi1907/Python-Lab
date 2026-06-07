"""
Date: 2026-06-07
Built an A* pathfinding algorithm to find optimal routes on a 2D grid — wanted to see how the heuristic guides the search compared to plain Dijkstra.
"""

"""
A* Pathfinding Algorithm Implementation
Finds the shortest path on a 2D grid using Manhattan distance as heuristic.
"""

import heapq
from typing import List, Tuple, Set, Optional


class Node:
    """Represents a node in the A* search space."""
    
    def __init__(self, position: Tuple[int, int], g_cost: float = float('inf'), 
                 h_cost: float = 0, parent: Optional['Node'] = None):
        """
        Initialize a node for A* pathfinding.
        
        Args:
            position: (row, col) coordinates on the grid
            g_cost: cost from start to this node
            h_cost: estimated cost from this node to goal (heuristic)
            parent: previous node in the path
        """
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = parent
    
    @property
    def f_cost(self) -> float:
        """Total estimated cost (g + h)."""
        return self.g_cost + self.h_cost
    
    def __lt__(self, other: 'Node') -> bool:
        """Compare nodes by f_cost for priority queue."""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other: 'Node') -> bool:
        """Nodes are equal if they're at the same position."""
        return self.position == other.position
    
    def __hash__(self) -> int:
        """Hash by position so we can use nodes in sets/dicts."""
        return hash(self.position)


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two positions.
    This is admissible for grid-based movement (no diagonals).
    
    Args:
        pos1: first position (row, col)
        pos2: second position (row, col)
    
    Returns:
        Manhattan distance as integer
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_neighbors(position: Tuple[int, int], grid: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Get valid neighboring positions (up, down, left, right).
    
    Args:
        position: current (row, col)
        grid: 2D grid where 0 = walkable, 1 = obstacle
    
    Returns:
        List of valid neighbor positions
    """
    rows, cols = len(grid), len(grid[0])
    row, col = position
    neighbors = []
    
    # Check all 4 cardinal directions
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        
        # Make sure we're in bounds and not hitting an obstacle
        if (0 <= new_row < rows and 
            0 <= new_col < cols and 
            grid[new_row][new_col] == 0):
            neighbors.append((new_row, new_col))
    
    return neighbors


def a_star(grid: List[List[int]], start: Tuple[int, int], 
           goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    Find shortest path using A* algorithm.
    
    Args:
        grid: 2D grid where 0 = walkable, 1 = obstacle
        start: starting position (row, col)
        goal: goal position (row, col)
    
    Returns:
        List of positions from start to goal, or None if no path exists
    """
    # Priority queue for nodes to explore, ordered by f_cost
    open_set = []
    start_node = Node(start, g_cost=0, h_cost=manhattan_distance(start, goal))
    heapq.heappush(open_set, start_node)
    
    # Track nodes we've already evaluated
    closed_set: Set[Tuple[int, int]] = set()
    
    # Map position to node for quick lookups
    position_to_node = {start: start_node}
    
    while open_set:
        current = heapq.heappop(open_set)
        
        # Found the goal! Reconstruct path
        if current.position == goal:
            path = []
            while current:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Reverse to get start -> goal
        
        closed_set.add(current.position)
        
        # Check all neighbors
        for neighbor_pos in get_neighbors(current.position, grid):
            if neighbor_pos in closed_set:
                continue
            
            # Cost to reach this neighbor through current node
            tentative_g = current.g_cost + 1  # assuming uniform cost of 1
            
            # Get or create neighbor node
            if neighbor_pos in position_to_node:
                neighbor = position_to_node[neighbor_pos]
                if tentative_g >= neighbor.g_cost:
                    continue  # Not a better path
            else:
                neighbor = Node(neighbor_pos, h_cost=manhattan_distance(neighbor_pos, goal))
                position_to_node[neighbor_pos] = neighbor
            
            # Update neighbor with better path
            neighbor.g_cost = tentative_g
            neighbor.parent = current
            heapq.heappush(open_set, neighbor)
    
    return None  # No path found


def visualize_path(grid: List[List[int]], path: Optional[List[Tuple[int, int]]],
                   start: Tuple[int, int], goal: Tuple[int, int]) -> None:
    """
    Print the grid with the path marked.
    
    Args:
        grid: original grid
        path: computed path or None
        start: start position
        goal: goal position
    """
    if path is None:
        print("No path found!")
        return
    
    # Create a copy to mark the path
    display = [row[:] for row in grid]
    path_set = set(path)
    
    for r in range(len(display)):
        for c in range(len(display[0])):
            pos = (r, c)
            if pos == start:
                print('S', end=' ')
            elif pos == goal:
                print('G', end=' ')
            elif pos in path_set:
                print('*', end=' ')
            elif display[r][c] == 1:
                print('#', end=' ')
            else:
                print('.', end=' ')
        print()
    
    print(f"\nPath length: {len(path)} steps")


if __name__ == "__main__":
    # Create a test grid with some obstacles
    test_grid = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    
    start_pos = (0, 0)
    goal_pos = (6, 6)
    
    print("Finding path from top-left to bottom-right:")
    print("S = Start, G = Goal, * = Path, # = Obstacle, . = Empty\n")
    
    path = a_star(test_grid, start_pos, goal_pos)
    visualize_path(test_grid, path, start_pos, goal_pos)