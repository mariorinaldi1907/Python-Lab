"""
Date: 2026-07-05
Created a cellular automaton that simulates wildfire spreading through a forest with wind effects and probabilistic ignition — purely for fun and to visualize emergent behavior.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton where fires spread through trees based on wind direction
and random chance. Empty cells can regrow trees over time.
"""

import random
import time
from typing import List, Tuple


class ForestFireSimulation:
    """
    Simulates wildfire spreading through a forest grid.
    
    Cell states:
    - 0: Empty (burned out or naturally empty)
    - 1: Tree
    - 2: Burning
    """
    
    def __init__(self, width: int = 40, height: int = 20, tree_density: float = 0.6):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Initial probability of a cell containing a tree (0-1)
        """
        self.width = width
        self.height = height
        self.grid = [[1 if random.random() < tree_density else 0 
                      for _ in range(width)] for _ in range(height)]
        
        # Wind affects spread probability in certain directions
        # Format: (dy, dx) -> probability multiplier
        self.wind_direction = (0, 1)  # Blowing east
        self.steps = 0
        
    def ignite_random(self, count: int = 3):
        """Start fires at random tree locations."""
        trees = [(y, x) for y in range(self.height) 
                 for x in range(self.width) if self.grid[y][x] == 1]
        
        if trees:
            for _ in range(min(count, len(trees))):
                y, x = random.choice(trees)
                self.grid[y][x] = 2
                trees.remove((y, x))
    
    def step(self, spread_prob: float = 0.4, regrow_prob: float = 0.01):
        """
        Advance simulation by one step.
        
        Args:
            spread_prob: Base probability fire spreads to adjacent tree
            regrow_prob: Probability empty cell grows a tree
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 2:
                    # Burning tree spreads fire then burns out
                    self._spread_fire(y, x, new_grid, spread_prob)
                    new_grid[y][x] = 0
                elif self.grid[y][x] == 0:
                    # Empty cell might regrow
                    if random.random() < regrow_prob:
                        new_grid[y][x] = 1
        
        self.grid = new_grid
        self.steps += 1
    
    def _spread_fire(self, y: int, x: int, new_grid: List[List[int]], base_prob: float):
        """
        Spread fire from burning cell to neighbors.
        Wind direction increases spread probability.
        """
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
        
        for dy, dx in neighbors:
            ny, nx = y + dy, x + dx
            
            if 0 <= ny < self.height and 0 <= nx < self.width:
                if self.grid[ny][nx] == 1:  # There's a tree
                    # Wind boosts probability in its direction
                    prob = base_prob
                    if (dy, dx) == self.wind_direction:
                        prob *= 1.8
                    elif (dy, dx) == (-self.wind_direction[0], -self.wind_direction[1]):
                        prob *= 0.3  # Against the wind
                    
                    if random.random() < prob:
                        new_grid[ny][nx] = 2
    
    def render(self) -> str:
        """
        Render the grid as a string.
        
        Returns colored representation using ANSI codes.
        """
        symbols = {
            0: '·',  # Empty
            1: '🌲',  # Tree (using emoji for fun)
            2: '🔥',  # Fire
        }
        
        # Fallback for terminals that don't like emoji
        simple_symbols = {
            0: ' ',
            1: 'T',
            2: '*',
        }
        
        try:
            lines = [''.join(symbols[cell] for cell in row) for row in self.grid]
        except UnicodeEncodeError:
            # Fall back to ASCII if emoji breaks
            lines = [''.join(simple_symbols[cell] for cell in row) for row in self.grid]
        
        return '\n'.join(lines)
    
    def count_cells(self) -> Tuple[int, int, int]:
        """Count empty, tree, and burning cells."""
        empty = sum(row.count(0) for row in self.grid)
        trees = sum(row.count(1) for row in self.grid)
        burning = sum(row.count(2) for row in self.grid)
        return empty, trees, burning


def clear_screen():
    """Print enough newlines to simulate clearing (works cross-platform)."""
    print('\n' * 2)


if __name__ == "__main__":
    # Set up the simulation
    sim = ForestFireSimulation(width=50, height=20, tree_density=0.65)
    
    print("=== Forest Fire Simulation ===")
    print("Wind blowing EAST (fires spread faster to the right)")
    print("Starting 3 random fires...\n")
    
    sim.ignite_random(count=3)
    
    # Run for a bunch of steps or until fire dies out
    max_steps = 60
    for step in range(max_steps):
        clear_screen()
        print(f"Step {sim.steps}")
        print(sim.render())
        
        empty, trees, burning = sim.count_cells()
        total = sim.width * sim.height
        print(f"\nStats: {trees} trees ({100*trees/total:.1f}%), "
              f"{burning} burning, {empty} empty")
        
        if burning == 0:
            print("\n🔥 Fire has burned out!")
            break
        
        # Each step lets fire spread and empty cells occasionally regrow
        sim.step(spread_prob=0.5, regrow_prob=0.005)
        
        time.sleep(0.2)  # Slow it down so we can watch
    
    print(f"\nSimulation ended after {sim.steps} steps.")