"""
Date: 2026-08-06
Created a cellular automaton that models wildfire propagation across a grid with probabilistic spread, wind direction influence, and ASCII visualization.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton that models how wildfires spread across a landscape.
Each cell can be: empty, tree, burning, or burnt.
Fire spreads probabilistically to neighboring trees, influenced by wind direction.
"""

import random
import time
from enum import Enum


class CellState(Enum):
    """Represents the possible states of a cell in the forest grid."""
    EMPTY = 0
    TREE = 1
    BURNING = 2
    BURNT = 3


class ForestFire:
    """
    Simulates fire spreading through a forest grid.
    
    The fire spreads from burning cells to adjacent tree cells with some probability.
    Wind direction increases spread probability in the downwind direction.
    """
    
    def __init__(self, width=50, height=25, tree_density=0.65, spread_prob=0.5):
        """
        Initialize the forest fire simulation.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability that a cell starts with a tree (0-1)
            spread_prob: Base probability that fire spreads to adjacent cell (0-1)
        """
        self.width = width
        self.height = height
        self.spread_prob = spread_prob
        self.grid = [[CellState.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Populate forest with trees randomly
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = CellState.TREE
        
        # Wind affects spread probability: (dy, dx, probability_multiplier)
        # Simulating wind blowing east (positive x direction)
        self.wind_direction = (0, 1)
        self.wind_strength = 1.5
    
    def ignite(self, x, y):
        """
        Start a fire at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        if 0 <= y < self.height and 0 <= x < self.width:
            if self.grid[y][x] == CellState.TREE:
                self.grid[y][x] = CellState.BURNING
    
    def get_neighbors(self, x, y):
        """
        Get valid neighboring coordinates (4-connected grid).
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            List of (x, y, wind_modifier) tuples for valid neighbors
        """
        neighbors = []
        # Check all 4 cardinal directions
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Calculate wind influence - fire spreads faster downwind
                wind_modifier = 1.0
                if (dy, dx) == self.wind_direction:
                    wind_modifier = self.wind_strength
                elif (dy, dx) == (-self.wind_direction[0], -self.wind_direction[1]):
                    # Spreading against wind is harder
                    wind_modifier = 0.6
                
                neighbors.append((nx, ny, wind_modifier))
        return neighbors
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        Fire spreads from burning cells to neighboring trees.
        Burning cells turn to burnt ash.
        
        Returns:
            True if fire is still burning, False if simulation is complete
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        fire_active = False
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellState.BURNING:
                    # Burning trees become burnt
                    new_grid[y][x] = CellState.BURNT
                    fire_active = True
                    
                    # Try to ignite neighboring trees
                    for nx, ny, wind_mod in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == CellState.TREE:
                            # Probabilistic spread with wind influence
                            if random.random() < self.spread_prob * wind_mod:
                                new_grid[ny][nx] = CellState.BURNING
        
        self.grid = new_grid
        return fire_active
    
    def display(self):
        """Print the current state of the forest to console."""
        symbols = {
            CellState.EMPTY: ' ',
            CellState.TREE: '🌲',
            CellState.BURNING: '🔥',
            CellState.BURNT: '▓'
        }
        
        print('\n' + '=' * (self.width * 2))
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))
        print('=' * (self.width * 2))
    
    def get_statistics(self):
        """
        Calculate current forest statistics.
        
        Returns:
            Dictionary with counts of each cell type
        """
        stats = {state: 0 for state in CellState}
        for row in self.grid:
            for cell in row:
                stats[cell] += 1
        return stats


if __name__ == "__main__":
    # Create a forest and start some fires
    print("🌲 Forest Fire Simulation 🔥")
    print("Wind blowing east →")
    
    forest = ForestFire(width=40, height=20, tree_density=0.7, spread_prob=0.45)
    
    # Start fires at multiple points
    forest.ignite(5, 10)
    forest.ignite(35, 10)
    
    forest.display()
    time.sleep(1)
    
    step_count = 0
    while forest.step():
        step_count += 1
        forest.display()
        
        stats = forest.get_statistics()
        print(f"Step {step_count} | Trees: {stats[CellState.TREE]} | "
              f"Burning: {stats[CellState.BURNING]} | Burnt: {stats[CellState.BURNT]}")
        
        time.sleep(0.3)  # Slow down animation
    
    # Final report
    print("\n🔥 Fire has burned out!")
    final_stats = forest.get_statistics()
    total_cells = forest.width * forest.height
    burn_percentage = (final_stats[CellState.BURNT] / total_cells) * 100
    print(f"Final damage: {final_stats[CellState.BURNT]} cells burnt ({burn_percentage:.1f}% of forest)")