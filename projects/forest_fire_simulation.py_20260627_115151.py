"""
Date: 2026-06-27
Created a cellular automaton that simulates wildfire spread across a grid with configurable wind direction, tree density, and moisture levels.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton where fire spreads from tree to tree based on wind,
moisture, and random chance. Watching patterns emerge is pretty cool.
"""

import random
import time
from enum import Enum


class CellState(Enum):
    """Represents the state of a single cell in the forest grid."""
    EMPTY = 0
    TREE = 1
    BURNING = 2
    ASH = 3


class ForestFireSimulation:
    """
    Simulates fire spreading through a forest grid.
    
    Fire spreads to adjacent trees with probability influenced by:
    - Wind direction (increases spread chance in wind direction)
    - Moisture level (global dampening factor)
    - Random chance
    """
    
    def __init__(self, width=40, height=20, tree_density=0.6, moisture=0.3):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability a cell starts as a tree (0.0-1.0)
            moisture: Dampens fire spread (0.0=dry, 1.0=wet)
        """
        self.width = width
        self.height = height
        self.moisture = moisture
        self.grid = [[CellState.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Populate with trees randomly
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = CellState.TREE
        
        # Wind direction: (dy, dx) — positive y is down, positive x is right
        # This represents a southeast wind, which pushes fire northwest
        self.wind = (-1, -1)
    
    def ignite(self, x, y):
        """Start a fire at the given coordinates if there's a tree."""
        if 0 <= y < self.height and 0 <= x < self.width:
            if self.grid[y][x] == CellState.TREE:
                self.grid[y][x] = CellState.BURNING
    
    def get_neighbors(self, x, y):
        """
        Get all valid neighboring cells (8-directional).
        
        Returns list of (nx, ny, direction_bonus) tuples.
        direction_bonus is higher if wind is blowing toward that neighbor.
        """
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Wind bonus: if wind direction matches spread direction
                    wind_bonus = 0.0
                    if (dy, dx) == self.wind:
                        wind_bonus = 0.3  # Strong boost in wind direction
                    elif dy == self.wind[0] or dx == self.wind[1]:
                        wind_bonus = 0.1  # Slight boost in partial wind direction
                    
                    neighbors.append((nx, ny, wind_bonus))
        return neighbors
    
    def step(self):
        """
        Execute one simulation step.
        
        - Burning trees spread fire to neighbors
        - Burning trees turn to ash
        - Returns True if any cells are still burning
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        any_burning = False
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellState.BURNING:
                    # This burning tree will turn to ash
                    new_grid[y][x] = CellState.ASH
                    
                    # Try to spread fire to neighbors
                    for nx, ny, wind_bonus in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == CellState.TREE:
                            # Base spread probability, reduced by moisture
                            spread_chance = 0.5 * (1.0 - self.moisture) + wind_bonus
                            if random.random() < spread_chance:
                                new_grid[ny][nx] = CellState.BURNING
                                any_burning = True
                elif self.grid[y][x] == CellState.BURNING:
                    any_burning = True
        
        # Check if new grid still has burning cells
        for row in new_grid:
            if CellState.BURNING in row:
                any_burning = True
                break
        
        self.grid = new_grid
        return any_burning
    
    def render(self):
        """Render the current grid state as a string."""
        symbols = {
            CellState.EMPTY: ' ',
            CellState.TREE: '🌲',
            CellState.BURNING: '🔥',
            CellState.ASH: '·'
        }
        lines = []
        lines.append('┌' + '─' * (self.width * 2) + '┐')
        for row in self.grid:
            line = '│' + ''.join(symbols[cell] for cell in row) + '│'
            lines.append(line)
        lines.append('└' + '─' * (self.width * 2) + '┘')
        return '\n'.join(lines)
    
    def count_states(self):
        """Return a dict with counts of each cell state."""
        counts = {state: 0 for state in CellState}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts


if __name__ == "__main__":
    print("🌲 Forest Fire Simulation 🔥\n")
    
    # Create a forest with moderate tree density and low moisture (dry conditions)
    sim = ForestFireSimulation(width=40, height=20, tree_density=0.65, moisture=0.2)
    
    # Start fire in the bottom-right corner
    # Wind blows northwest, so fire should spread up and left
    sim.ignite(35, 18)
    
    step = 0
    print(f"Step {step}:")
    print(sim.render())
    
    counts = sim.count_states()
    print(f"Trees: {counts[CellState.TREE]}, Burning: {counts[CellState.BURNING]}, Ash: {counts[CellState.ASH]}\n")
    
    time.sleep(1)
    
    # Run simulation until fire stops spreading
    while True:
        step += 1
        still_burning = sim.step()
        
        print(f"Step {step}:")
        print(sim.render())
        
        counts = sim.count_states()
        print(f"Trees: {counts[CellState.TREE]}, Burning: {counts[CellState.BURNING]}, Ash: {counts[CellState.ASH]}\n")
        
        if not still_burning:
            print("Fire has burned out.")
            break
        
        time.sleep(0.5)  # Slow down for visibility
        
        if step > 50:  # Safety limit
            print("Reached step limit.")
            break