"""
Date: 2026-08-24
Simulated forest fires spreading through a grid where trees grow, burn, and leave empty spaces — uses simple probabilistic rules and runs in the terminal.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton where trees grow, catch fire, and burn out.
Each cell can be: empty, tree, or burning.
Rules are simple probability-based transitions.
"""

import random
import time
from typing import List, Tuple


class ForestFireSimulation:
    """
    Simulates forest fire dynamics on a 2D grid.
    
    Each cell has three possible states:
    - EMPTY (0): No tree, can grow one
    - TREE (1): Healthy tree, can catch fire
    - FIRE (2): Burning tree, will become empty next step
    """
    
    EMPTY = 0
    TREE = 1
    FIRE = 2
    
    def __init__(self, width: int, height: int, tree_prob: float = 0.5, 
                 grow_prob: float = 0.01, lightning_prob: float = 0.0001):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_prob: Initial probability of a cell having a tree
            grow_prob: Probability empty cell grows a tree each step
            lightning_prob: Probability a tree spontaneously catches fire
        """
        self.width = width
        self.height = height
        self.grow_prob = grow_prob
        self.lightning_prob = lightning_prob
        
        # Initialize grid with random trees
        self.grid = [[self.TREE if random.random() < tree_prob else self.EMPTY
                      for _ in range(width)] for _ in range(height)]
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get valid neighbor coordinates (4-directional: up, down, left, right).
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            List of (row, col) tuples for valid neighbors
        """
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors.append((nr, nc))
        return neighbors
    
    def step(self):
        """
        Execute one simulation step using forest fire rules.
        
        Rules:
        1. Burning trees become empty
        2. Trees catch fire if any neighbor is burning
        3. Trees can spontaneously catch fire (lightning)
        4. Empty cells can grow new trees
        """
        new_grid = [[self.EMPTY for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        for row in range(self.height):
            for col in range(self.width):
                current = self.grid[row][col]
                
                if current == self.FIRE:
                    # Burning trees become empty
                    new_grid[row][col] = self.EMPTY
                
                elif current == self.TREE:
                    # Check if neighbors are on fire
                    neighbors_on_fire = any(
                        self.grid[nr][nc] == self.FIRE 
                        for nr, nc in self.get_neighbors(row, col)
                    )
                    
                    if neighbors_on_fire:
                        new_grid[row][col] = self.FIRE
                    elif random.random() < self.lightning_prob:
                        # Lightning strike!
                        new_grid[row][col] = self.FIRE
                    else:
                        new_grid[row][col] = self.TREE
                
                else:  # EMPTY
                    # Empty cells can grow trees
                    if random.random() < self.grow_prob:
                        new_grid[row][col] = self.TREE
                    else:
                        new_grid[row][col] = self.EMPTY
        
        self.grid = new_grid
    
    def count_states(self) -> Tuple[int, int, int]:
        """
        Count cells in each state.
        
        Returns:
            Tuple of (empty_count, tree_count, fire_count)
        """
        empty = sum(row.count(self.EMPTY) for row in self.grid)
        tree = sum(row.count(self.TREE) for row in self.grid)
        fire = sum(row.count(self.FIRE) for row in self.grid)
        return empty, tree, fire
    
    def display(self):
        """Print the current grid state to terminal."""
        symbols = {self.EMPTY: ' ', self.TREE: '🌲', self.FIRE: '🔥'}
        print('\n' + '─' * (self.width * 2 + 2))
        for row in self.grid:
            print('│' + ''.join(symbols[cell] for cell in row) + '│')
        print('─' * (self.width * 2 + 2))
        
        empty, tree, fire = self.count_states()
        total = self.width * self.height
        print(f"Empty: {empty}/{total} | Trees: {tree}/{total} | Fire: {fire}/{total}")


def run_simulation(steps: int = 50, width: int = 30, height: int = 20, 
                   delay: float = 0.2):
    """
    Run the forest fire simulation for a given number of steps.
    
    Args:
        steps: Number of simulation steps to run
        width: Grid width
        height: Grid height
        delay: Seconds to pause between frames (for visualization)
    """
    # Start with moderate tree coverage, slow growth, occasional lightning
    sim = ForestFireSimulation(
        width=width, 
        height=height,
        tree_prob=0.6,
        grow_prob=0.05,
        lightning_prob=0.001
    )
    
    print("🔥 Forest Fire Simulation 🌲")
    print("Watch as fires spread and forests regrow...")
    
    for step_num in range(steps):
        print(f"\n{'=' * 60}")
        print(f"Step {step_num + 1}/{steps}")
        sim.display()
        sim.step()
        time.sleep(delay)


if __name__ == "__main__":
    # Run a demo simulation
    # On each step: fires spread to adjacent trees, burned areas clear,
    # empty spaces slowly regrow, and occasional lightning strikes start new fires
    run_simulation(steps=40, width=25, height=15, delay=0.3)