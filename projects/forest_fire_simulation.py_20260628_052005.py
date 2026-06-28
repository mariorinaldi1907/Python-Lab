"""
Date: 2026-06-28
Created a cellular automaton that simulates wildfire spreading through a forest grid with wind direction, moisture, and probabilistic ignition mechanics.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation - A cellular automaton model of wildfire spread.

Each cell can be: Empty, Tree, Burning, or Ash.
Fire spreads based on wind direction, tree density, and random chance.
"""

import random
import time
from enum import IntEnum


class CellState(IntEnum):
    """Represents the state of a single cell in the forest grid."""
    EMPTY = 0
    TREE = 1
    BURNING = 2
    ASH = 3


class ForestFireSimulation:
    """
    Simulates wildfire propagation across a 2D grid.
    
    The simulation considers wind direction and uses probabilistic
    fire spread to neighboring cells. Trees burn for one timestep,
    then turn to ash.
    """
    
    def __init__(self, width=40, height=20, tree_density=0.65, wind_direction='E'):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability (0-1) that a cell starts with a tree
            wind_direction: One of 'N', 'S', 'E', 'W' for wind direction
        """
        self.width = width
        self.height = height
        self.wind_direction = wind_direction
        self.grid = [[CellState.EMPTY for _ in range(width)] for _ in range(height)]
        self.timestep = 0
        
        # Populate forest with trees based on density
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = CellState.TREE
    
    def ignite(self, x, y):
        """Start a fire at the given coordinates."""
        if 0 <= y < self.height and 0 <= x < self.width:
            if self.grid[y][x] == CellState.TREE:
                self.grid[y][x] = CellState.BURNING
    
    def _get_neighbors(self, x, y):
        """
        Get neighboring cells with weighted probabilities based on wind.
        
        Wind direction increases spread chance in that direction.
        Returns list of (x, y, spread_probability) tuples.
        """
        # Base spread probabilities for each direction
        neighbors = []
        directions = {
            'N': (0, -1),
            'S': (0, 1),
            'E': (1, 0),
            'W': (-1, 0),
            'NE': (1, -1),
            'SE': (1, 1),
            'NW': (-1, -1),
            'SW': (-1, 1),
        }
        
        base_prob = 0.3  # Base spread chance
        wind_boost = 0.4  # Additional chance when spreading with wind
        
        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Boost probability if spreading in wind direction
                prob = base_prob
                if self.wind_direction in direction:
                    prob += wind_boost
                neighbors.append((nx, ny, prob))
        
        return neighbors
    
    def step(self):
        """
        Advance simulation by one timestep.
        
        Burning cells try to ignite neighbors, then turn to ash.
        This uses a two-pass approach to avoid modifying the grid
        while iterating over it.
        """
        self.timestep += 1
        new_fires = []
        cells_to_ash = []
        
        # First pass: find all burning cells and calculate spread
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellState.BURNING:
                    # This cell will turn to ash
                    cells_to_ash.append((x, y))
                    
                    # Try to spread to neighbors
                    for nx, ny, prob in self._get_neighbors(x, y):
                        if self.grid[ny][nx] == CellState.TREE:
                            if random.random() < prob:
                                new_fires.append((nx, ny))
        
        # Second pass: apply state changes
        for x, y in cells_to_ash:
            self.grid[y][x] = CellState.ASH
        
        for x, y in new_fires:
            self.grid[y][x] = CellState.BURNING
    
    def is_burning(self):
        """Check if any cells are currently on fire."""
        for row in self.grid:
            if CellState.BURNING in row:
                return True
        return False
    
    def render(self):
        """
        Render the current grid state to a string.
        
        Uses different characters for visual representation:
        . = empty, T = tree, # = burning, * = ash
        """
        symbols = {
            CellState.EMPTY: ' ',
            CellState.TREE: '🌲',
            CellState.BURNING: '🔥',
            CellState.ASH: '⚫',
        }
        
        output = [f"=== Timestep {self.timestep} ==="]
        for row in self.grid:
            output.append(''.join(symbols[cell] for cell in row))
        return '\n'.join(output)
    
    def get_stats(self):
        """Calculate current statistics about the forest."""
        counts = {state: 0 for state in CellState}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        
        total = self.width * self.height
        return {
            'trees': counts[CellState.TREE],
            'burning': counts[CellState.BURNING],
            'ash': counts[CellState.ASH],
            'burned_pct': (counts[CellState.ASH] / total) * 100
        }


if __name__ == "__main__":
    # Run a simulation with eastward wind
    print("Forest Fire Simulation")
    print("Wind blowing East — watch it spread!\n")
    
    sim = ForestFireSimulation(width=30, height=15, tree_density=0.7, wind_direction='E')
    
    # Start a fire in the western side
    sim.ignite(3, 7)
    sim.ignite(3, 8)
    
    print(sim.render())
    print()
    
    # Run until fire burns out
    while sim.is_burning() and sim.timestep < 50:
        time.sleep(0.3)  # Slow down for visibility
        sim.step()
        print(sim.render())
        
        stats = sim.get_stats()
        print(f"Trees: {stats['trees']} | Burning: {stats['burning']} | "
              f"Burned: {stats['burned_pct']:.1f}%\n")
    
    final_stats = sim.get_stats()
    print(f"\n🔥 Fire burned out after {sim.timestep} timesteps")
    print(f"Total area burned: {final_stats['burned_pct']:.1f}%")