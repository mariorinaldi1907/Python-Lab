"""
Date: 2026-07-22
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic simulator on a 2D grid where infection spreads to neighbors probabilistically.
"""

#!/usr/bin/env python3
"""
Spatial SIR Epidemic Model Simulation

A simple implementation of the classic epidemiological model where individuals
are placed on a grid and infection spreads to adjacent cells based on transmission
probability. I wanted to visualize how spatial structure affects disease dynamics.
"""

import random
import time
from collections import defaultdict


class SIREpidemicSimulation:
    """
    Simulates an epidemic on a 2D grid using the SIR model.
    
    States:
    - S (Susceptible): Can be infected
    - I (Infected): Currently infectious, can spread to neighbors
    - R (Recovered): Immune, cannot be infected again
    """
    
    def __init__(self, width, height, initial_infected=1, 
                 transmission_prob=0.3, recovery_time=5):
        """
        Initialize the epidemic grid.
        
        Args:
            width: Grid width
            height: Grid height
            initial_infected: Number of initially infected individuals
            transmission_prob: Probability of transmission to adjacent susceptible
            recovery_time: Days until an infected person recovers
        """
        self.width = width
        self.height = height
        self.transmission_prob = transmission_prob
        self.recovery_time = recovery_time
        
        # Grid stores tuples: (state, days_infected)
        # state is 'S', 'I', or 'R'
        # days_infected only matters for 'I' state
        self.grid = [['S' for _ in range(width)] for _ in range(height)]
        self.infection_days = [[0 for _ in range(width)] for _ in range(height)]
        
        # Seed initial infections randomly
        for _ in range(initial_infected):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            self.grid[y][x] = 'I'
            self.infection_days[y][x] = 0
        
        self.day = 0
        self.history = []  # Track counts over time
    
    def get_neighbors(self, x, y):
        """Get valid adjacent cells (4-connectivity, no diagonals)."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors
    
    def count_states(self):
        """Count how many individuals are in each state."""
        counts = {'S': 0, 'I': 0, 'R': 0}
        for row in self.grid:
            for state in row:
                counts[state] += 1
        return counts
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        Process:
        1. Infected individuals have a chance to infect susceptible neighbors
        2. Infected individuals who've been sick long enough recover
        """
        new_infections = []
        recoveries = []
        
        # First pass: determine all new infections and recoveries
        # We don't modify the grid yet because all events should be "simultaneous"
        for y in range(self.height):
            for x in range(self.width):
                state = self.grid[y][x]
                
                if state == 'I':
                    # Check if this person recovers
                    if self.infection_days[y][x] >= self.recovery_time:
                        recoveries.append((x, y))
                    else:
                        # Try to infect neighbors
                        for nx, ny in self.get_neighbors(x, y):
                            if self.grid[ny][nx] == 'S':
                                if random.random() < self.transmission_prob:
                                    new_infections.append((nx, ny))
                        
                        # Increment infection duration
                        self.infection_days[y][x] += 1
        
        # Second pass: apply all changes
        for x, y in new_infections:
            if self.grid[y][x] == 'S':  # Could have been infected multiple times
                self.grid[y][x] = 'I'
                self.infection_days[y][x] = 0
        
        for x, y in recoveries:
            self.grid[y][x] = 'R'
            self.infection_days[y][x] = 0
        
        self.day += 1
        counts = self.count_states()
        self.history.append(counts)
        
        return counts
    
    def is_active(self):
        """Check if there are any infected individuals left."""
        return any(self.grid[y][x] == 'I' 
                   for y in range(self.height) 
                   for x in range(self.width))
    
    def display(self):
        """Print a visual representation of the grid."""
        symbols = {'S': '·', 'I': '█', 'R': '○'}
        print(f"\nDay {self.day}:")
        for row in self.grid:
            print(' '.join(symbols[state] for state in row))
    
    def print_stats(self):
        """Print current statistics."""
        counts = self.count_states()
        total = sum(counts.values())
        print(f"Susceptible: {counts['S']:3d} ({100*counts['S']/total:5.1f}%)  "
              f"Infected: {counts['I']:3d} ({100*counts['I']/total:5.1f}%)  "
              f"Recovered: {counts['R']:3d} ({100*counts['R']/total:5.1f}%)")


def run_simulation(width=20, height=15, initial_infected=3, 
                   transmission_prob=0.25, recovery_time=4, 
                   display_steps=True, step_delay=0.3):
    """
    Run a complete epidemic simulation until no infections remain.
    
    Returns the simulation object with full history.
    """
    sim = SIREpidemicSimulation(
        width=width,
        height=height,
        initial_infected=initial_infected,
        transmission_prob=transmission_prob,
        recovery_time=recovery_time
    )
    
    print("=" * 60)
    print("SPATIAL SIR EPIDEMIC SIMULATION")
    print("=" * 60)
    print(f"Grid: {width}x{height}, Initial infected: {initial_infected}")
    print(f"Transmission probability: {transmission_prob}, Recovery time: {recovery_time} days")
    print("\nLegend: · = Susceptible, █ = Infected, ○ = Recovered")
    
    if display_steps:
        sim.display()
        sim.print_stats()
    
    # Run until no more infections
    while sim.is_active():
        sim.step()
        
        if display_steps:
            time.sleep(step_delay)
            sim.display()
            sim.print_stats()
    
    print("\n" + "=" * 60)
    print(f"EPIDEMIC ENDED after {sim.day} days")
    final = sim.count_states()
    total = sum(final.values())
    print(f"Final attack rate: {100 * final['R'] / total:.1f}% of population infected")
    print("=" * 60)
    
    return sim


if __name__ == "__main__":
    # Run a demo simulation with reasonable parameters
    # I'm using smaller values and slower display so you can actually watch it unfold
    simulation = run_simulation(
        width=25,
        height=18,
        initial_infected=2,
        transmission_prob=0.28,
        recovery_time=5,
        display_steps=True,
        step_delay=0.2
    )