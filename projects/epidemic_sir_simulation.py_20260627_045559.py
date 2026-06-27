"""
Date: 2026-06-27
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic model on a 2D grid where infection spreads to neighbors probabilistically — shows how outbreaks evolve over time.
"""

#!/usr/bin/env python3
"""
Spatial SIR Epidemic Simulation

A simple grid-based epidemic model where individuals can be:
- S (Susceptible): healthy but can get infected
- I (Infected): sick and can spread disease
- R (Recovered): immune and cannot be reinfected

The simulation runs on a 2D grid where infected cells can spread
the disease to their neighbors with a given probability.
"""

import random
from collections import namedtuple
from typing import List, Tuple

# State constants
SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2

SimulationStats = namedtuple('SimulationStats', ['susceptible', 'infected', 'recovered'])


class EpidemicGrid:
    """
    Manages a 2D grid where each cell represents an individual's health state.
    
    Infection spreads to neighboring cells (including diagonals) based on
    transmission probability. Infected individuals recover after a set duration.
    """
    
    def __init__(self, width: int, height: int, infection_prob: float = 0.3, recovery_time: int = 5):
        """
        Initialize the epidemic grid.
        
        Args:
            width: Grid width
            height: Grid height
            infection_prob: Probability of transmission to a susceptible neighbor
            recovery_time: Number of steps before an infected individual recovers
        """
        self.width = width
        self.height = height
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time
        
        # Grid stores the state (S, I, R)
        self.grid = [[SUSCEPTIBLE for _ in range(width)] for _ in range(height)]
        
        # Track how long each cell has been infected (only matters for infected cells)
        self.infection_timer = [[0 for _ in range(width)] for _ in range(height)]
    
    def infect_random(self, count: int = 1):
        """Randomly infect a number of individuals to start the outbreak."""
        infected = 0
        while infected < count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] == SUSCEPTIBLE:
                self.grid[y][x] = INFECTED
                self.infection_timer[y][x] = 0
                infected += 1
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all 8 neighbors (including diagonals) of a cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        Process:
        1. Infected individuals spread to susceptible neighbors
        2. Infected individuals recover after recovery_time steps
        """
        # Track new infections to avoid modifying grid while iterating
        new_infections = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == INFECTED:
                    # Increment infection timer
                    self.infection_timer[y][x] += 1
                    
                    # Try to infect neighbors
                    for nx, ny in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == SUSCEPTIBLE:
                            if random.random() < self.infection_prob:
                                new_infections.append((nx, ny))
                    
                    # Check for recovery
                    if self.infection_timer[y][x] >= self.recovery_time:
                        self.grid[y][x] = RECOVERED
                        self.infection_timer[y][x] = 0
        
        # Apply new infections
        for x, y in new_infections:
            self.grid[y][x] = INFECTED
            self.infection_timer[y][x] = 0
    
    def get_stats(self) -> SimulationStats:
        """Count the number of individuals in each state."""
        s_count = sum(row.count(SUSCEPTIBLE) for row in self.grid)
        i_count = sum(row.count(INFECTED) for row in self.grid)
        r_count = sum(row.count(RECOVERED) for row in self.grid)
        return SimulationStats(s_count, i_count, r_count)
    
    def visualize(self) -> str:
        """
        Create a simple ASCII visualization of the grid.
        
        . = Susceptible
        # = Infected
        + = Recovered
        """
        symbols = {SUSCEPTIBLE: '.', INFECTED: '#', RECOVERED: '+'}
        lines = []
        for row in self.grid:
            lines.append(''.join(symbols[cell] for cell in row))
        return '\n'.join(lines)


def run_simulation(steps: int = 30, grid_size: int = 40, initial_infected: int = 3):
    """
    Run the epidemic simulation and print results at intervals.
    
    I chose to print every few steps because watching every single frame
    gets overwhelming in the terminal. The key insights come from seeing
    the waves of infection and eventual stabilization.
    """
    print(f"Starting epidemic simulation on {grid_size}x{grid_size} grid")
    print(f"Infection probability: 30%, Recovery time: 5 steps\n")
    
    grid = EpidemicGrid(grid_size, grid_size, infection_prob=0.3, recovery_time=5)
    grid.infect_random(initial_infected)
    
    for step in range(steps):
        stats = grid.get_stats()
        
        # Print visualization and stats every 5 steps to avoid spam
        if step % 5 == 0:
            print(f"=== Step {step} ===")
            print(grid.visualize())
            print(f"Susceptible: {stats.susceptible} | Infected: {stats.infected} | Recovered: {stats.recovered}")
            print()
        
        grid.step()
        
        # Stop early if no more infected individuals
        if stats.infected == 0:
            print(f"Outbreak ended at step {step}")
            print(grid.visualize())
            final_stats = grid.get_stats()
            print(f"Final - S: {final_stats.susceptible} | I: {final_stats.infected} | R: {final_stats.recovered}")
            break


if __name__ == "__main__":
    # Run with default parameters - usually shows a nice infection wave
    # that peaks around step 10-15 and then dies out
    run_simulation(steps=30, grid_size=40, initial_infected=3)