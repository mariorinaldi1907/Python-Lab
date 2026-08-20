"""
Date: 2026-08-20
Simulated forest fire spread across a grid with trees that catch fire from neighbors, burn out, and slowly regrow over time.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation - Cellular Automaton

A simple grid-based simulation where:
- Trees can catch fire from burning neighbors
- Fires burn out after one step
- Empty spaces gradually regrow trees
- Lightning can randomly start fires

States: 0=empty, 1=tree, 2=burning
"""

import random
import time
import os


class ForestFireSimulation:
    """
    Simulates forest fire dynamics on a 2D grid.
    
    The model captures how fires spread through forests and how
    the ecosystem recovers. Useful for understanding percolation
    and spatial dynamics.
    """
    
    def __init__(self, width=40, height=20, tree_density=0.6, 
                 lightning_prob=0.00005, regrowth_prob=0.01):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Initial proportion of trees (0-1)
            lightning_prob: Chance of random fire starting per cell per step
            regrowth_prob: Chance of empty cell becoming tree per step
        """
        self.width = width
        self.height = height
        self.lightning_prob = lightning_prob
        self.regrowth_prob = regrowth_prob
        
        # Create initial forest - mostly trees with some random spacing
        self.grid = [[1 if random.random() < tree_density else 0 
                     for _ in range(width)] for _ in range(height)]
        
        # Start a few fires to get things going
        for _ in range(3):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            self.grid[y][x] = 2
    
    def get_neighbors(self, x, y):
        """
        Get the 8 neighbors around a cell (Moore neighborhood).
        
        Returns list of (nx, ny) coordinate tuples.
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                # Wrap around at edges for toroidal topology
                nx = nx % self.width
                ny = ny % self.height
                neighbors.append((nx, ny))
        return neighbors
    
    def step(self):
        """
        Advance simulation by one time step.
        
        Rules applied simultaneously across the grid:
        - Burning cells become empty
        - Trees catch fire if any neighbor is burning
        - Lightning can start new fires randomly
        - Empty cells can regrow trees
        """
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                
                if cell == 2:  # Currently burning
                    # Burns out to empty
                    new_grid[y][x] = 0
                
                elif cell == 1:  # Tree
                    # Check if any neighbor is on fire
                    neighbors = self.get_neighbors(x, y)
                    burning_nearby = any(self.grid[ny][nx] == 2 
                                        for nx, ny in neighbors)
                    
                    if burning_nearby:
                        new_grid[y][x] = 2  # Catch fire
                    elif random.random() < self.lightning_prob:
                        new_grid[y][x] = 2  # Lightning strike!
                    else:
                        new_grid[y][x] = 1  # Stay as tree
                
                else:  # Empty
                    # Chance to regrow
                    if random.random() < self.regrowth_prob:
                        new_grid[y][x] = 1
                    else:
                        new_grid[y][x] = 0
        
        self.grid = new_grid
    
    def render(self):
        """
        Return a string representation of the current grid.
        
        Uses unicode characters for visual clarity:
        . = empty, ▓ = tree, ◆ = fire
        """
        symbols = {0: ' ', 1: '▓', 2: '◆'}
        lines = []
        lines.append('┌' + '─' * self.width + '┐')
        for row in self.grid:
            lines.append('│' + ''.join(symbols[cell] for cell in row) + '│')
        lines.append('└' + '─' * self.width + '┘')
        return '\n'.join(lines)
    
    def count_cells(self):
        """Return tuple of (empty_count, tree_count, fire_count)."""
        counts = {0: 0, 1: 0, 2: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts[0], counts[1], counts[2]


def clear_screen():
    """Clear terminal screen (works on unix and windows)."""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    # Run the simulation with a nice visual display
    print("Forest Fire Simulation")
    print("=" * 42)
    print("Watch fires spread and forests regrow!")
    print("Press Ctrl+C to stop\n")
    
    time.sleep(2)
    
    sim = ForestFireSimulation(width=50, height=25, tree_density=0.65,
                              lightning_prob=0.00008, regrowth_prob=0.015)
    
    step_count = 0
    try:
        while True:
            clear_screen()
            print(f"Step: {step_count}")
            print(sim.render())
            
            empty, trees, fires = sim.count_cells()
            total = empty + trees + fires
            print(f"\nEmpty: {empty:4d} ({100*empty/total:5.1f}%)  ", end='')
            print(f"Trees: {trees:4d} ({100*trees/total:5.1f}%)  ", end='')
            print(f"Fires: {fires:4d} ({100*fires/total:5.1f}%)")
            
            sim.step()
            step_count += 1
            time.sleep(0.15)  # Slow down so we can actually see what's happening
            
    except KeyboardInterrupt:
        print("\n\nSimulation stopped. Final state shown above.")