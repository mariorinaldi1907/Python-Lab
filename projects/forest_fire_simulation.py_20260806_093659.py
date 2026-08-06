"""
Date: 2026-08-06
Implemented a forest fire simulation using cellular automata rules where trees grow randomly, lightning can strike, and fires spread to adjacent cells before burning out.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation - A cellular automaton model

Rules:
- Empty cells can grow a tree with probability p
- Trees can be struck by lightning with probability f
- Burning trees ignite adjacent trees (N/S/E/W)
- Burning trees become empty in the next step

This is a classic example of self-organized criticality.
"""

import random
import time
from enum import IntEnum


class CellState(IntEnum):
    """Possible states for each cell in the forest."""
    EMPTY = 0
    TREE = 1
    BURNING = 2


class ForestFire:
    """
    Cellular automaton simulating forest fire dynamics.
    
    The model demonstrates how small random events (lightning strikes)
    can lead to large-scale cascading effects (forest fires).
    """
    
    def __init__(self, width, height, tree_growth_prob=0.01, lightning_prob=0.0001):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_growth_prob: Probability an empty cell grows a tree each step
            lightning_prob: Probability a tree is struck by lightning each step
        """
        self.width = width
        self.height = height
        self.p_growth = tree_growth_prob
        self.p_lightning = lightning_prob
        
        # Start with a partially filled forest (50% trees)
        self.grid = [[CellState.TREE if random.random() < 0.5 else CellState.EMPTY
                      for _ in range(width)] for _ in range(height)]
        
        self.step_count = 0
    
    def get_neighbors(self, row, col):
        """
        Get the 4-connected neighbors (N/S/E/W) of a cell.
        
        Returns:
            List of (row, col) tuples for valid neighbors
        """
        neighbors = []
        # Check all 4 cardinal directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.height and 0 <= new_col < self.width:
                neighbors.append((new_row, new_col))
        return neighbors
    
    def update(self):
        """
        Advance the simulation by one time step.
        
        Creates a new grid based on current state and transition rules.
        This is done in two passes to avoid order-dependent updates.
        """
        new_grid = [[CellState.EMPTY for _ in range(self.width)] 
                    for _ in range(self.height)]
        
        for row in range(self.height):
            for col in range(self.width):
                current = self.grid[row][col]
                
                if current == CellState.BURNING:
                    # Burning trees become empty
                    new_grid[row][col] = CellState.EMPTY
                
                elif current == CellState.TREE:
                    # Check if any neighbor is burning
                    neighbors_burning = any(
                        self.grid[nr][nc] == CellState.BURNING
                        for nr, nc in self.get_neighbors(row, col)
                    )
                    
                    if neighbors_burning:
                        # Fire spreads from neighbors
                        new_grid[row][col] = CellState.BURNING
                    elif random.random() < self.p_lightning:
                        # Lightning strike!
                        new_grid[row][col] = CellState.BURNING
                    else:
                        # Tree survives another day
                        new_grid[row][col] = CellState.TREE
                
                else:  # EMPTY
                    if random.random() < self.p_growth:
                        # A new tree grows
                        new_grid[row][col] = CellState.TREE
                    else:
                        new_grid[row][col] = CellState.EMPTY
        
        self.grid = new_grid
        self.step_count += 1
    
    def count_states(self):
        """Count how many cells are in each state."""
        counts = {state: 0 for state in CellState}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def display(self):
        """
        Render the forest as ASCII art.
        
        . = empty, T = tree, * = burning
        """
        symbols = {
            CellState.EMPTY: '.',
            CellState.TREE: 'T',
            CellState.BURNING: '*'
        }
        
        print(f"\n=== Step {self.step_count} ===")
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))
        
        # Show statistics
        counts = self.count_states()
        total = self.width * self.height
        print(f"\nTrees: {counts[CellState.TREE]} ({100*counts[CellState.TREE]/total:.1f}%)")
        print(f"Burning: {counts[CellState.BURNING]} ({100*counts[CellState.BURNING]/total:.1f}%)")
        print(f"Empty: {counts[CellState.EMPTY]} ({100*counts[CellState.EMPTY]/total:.1f}%)")


def run_simulation(steps=50, width=40, height=20, delay=0.2):
    """
    Run a forest fire simulation with visualization.
    
    I set the default params to show some interesting behavior:
    - Low lightning prob means fires are rare but can get big
    - Moderate growth prob means the forest recovers between fires
    """
    forest = ForestFire(
        width=width,
        height=height,
        tree_growth_prob=0.01,    # 1% chance of tree growth per step
        lightning_prob=0.00008     # Rare lightning strikes create drama
    )
    
    forest.display()
    
    for _ in range(steps):
        time.sleep(delay)
        forest.update()
        forest.display()


if __name__ == "__main__":
    print("Forest Fire Simulation")
    print("=" * 50)
    print("Watch as trees grow, lightning strikes, and fires spread!")
    print("T = Tree, * = Burning, . = Empty\n")
    
    # Run the simulation for 50 steps
    # You can decrease delay or reduce steps if it's too slow
    run_simulation(steps=50, width=40, height=20, delay=0.15)