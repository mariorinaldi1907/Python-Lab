"""
Date: 2026-07-10
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic simulator on a 2D grid where infection spreads to neighbors and you can watch it propagate in the terminal.
"""

#!/usr/bin/env python3
"""
Simple spatial SIR epidemic model simulation.

People live on a grid and can be:
- S: Susceptible (healthy but can catch it)
- I: Infected (sick and spreading)
- R: Recovered (immune, can't get sick again)

Infection spreads to neighboring cells based on transmission probability.
After some days, infected people recover.
"""

import random
import time
from collections import namedtuple

# Config holds all the knobs I can turn to make the epidemic more/less severe
Config = namedtuple('Config', [
    'grid_size',           # NxN grid of people
    'initial_infected',    # how many patient zeros
    'transmission_prob',   # chance of spreading to a neighbor per day
    'recovery_days',       # days until an infected person recovers
    'simulation_days'      # total days to simulate
])


class EpidemicGrid:
    """
    Represents the population grid where the epidemic spreads.
    
    Each cell is either 'S', 'I', or 'R'.
    Infected cells track how long they've been sick.
    """
    
    def __init__(self, config):
        """Initialize a grid where everyone starts susceptible except a few infected."""
        self.config = config
        self.size = config.grid_size
        
        # Everyone starts susceptible
        self.state = [['S' for _ in range(self.size)] for _ in range(self.size)]
        
        # Track days infected (only matters for 'I' cells)
        self.days_infected = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Randomly infect initial people
        infected_count = 0
        while infected_count < config.initial_infected:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.state[x][y] == 'S':
                self.state[x][y] = 'I'
                self.days_infected[x][y] = 1
                infected_count += 1
    
    def get_neighbors(self, x, y):
        """Get the coordinates of all adjacent cells (up/down/left/right)."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors
    
    def step(self):
        """
        Simulate one day of the epidemic.
        
        For each infected person:
        - Try to infect susceptible neighbors
        - Increment their infection counter
        - Recover if they've been sick long enough
        """
        new_infections = []
        recoveries = []
        
        # Process infections and track recoveries
        for x in range(self.size):
            for y in range(self.size):
                if self.state[x][y] == 'I':
                    # Try to infect neighbors
                    for nx, ny in self.get_neighbors(x, y):
                        if self.state[nx][ny] == 'S':
                            if random.random() < self.config.transmission_prob:
                                new_infections.append((nx, ny))
                    
                    # Increment infection time
                    self.days_infected[x][y] += 1
                    
                    # Check if ready to recover
                    if self.days_infected[x][y] >= self.config.recovery_days:
                        recoveries.append((x, y))
        
        # Apply new infections
        for x, y in new_infections:
            self.state[x][y] = 'I'
            self.days_infected[x][y] = 1
        
        # Apply recoveries
        for x, y in recoveries:
            self.state[x][y] = 'R'
            self.days_infected[x][y] = 0
    
    def count_states(self):
        """Return counts of (susceptible, infected, recovered)."""
        counts = {'S': 0, 'I': 0, 'R': 0}
        for row in self.state:
            for cell in row:
                counts[cell] += 1
        return counts['S'], counts['I'], counts['R']
    
    def display(self):
        """Print the grid with color-ish ASCII representation."""
        symbols = {
            'S': '·',  # susceptible: small dot
            'I': '█',  # infected: solid block
            'R': '░'   # recovered: light shade
        }
        
        for row in self.state:
            print(''.join(symbols[cell] for cell in row))


def run_simulation(config, display_grid=True, delay=0.1):
    """
    Run the full epidemic simulation.
    
    I wanted to see it animate in real-time, so there's a configurable delay.
    Returns the final counts for each state.
    """
    grid = EpidemicGrid(config)
    
    print(f"Starting epidemic simulation on {config.grid_size}x{config.grid_size} grid")
    print(f"Initial infected: {config.initial_infected}")
    print(f"Transmission probability: {config.transmission_prob:.1%}")
    print(f"Recovery time: {config.recovery_days} days\n")
    
    for day in range(config.simulation_days):
        s, i, r = grid.count_states()
        
        if display_grid:
            print(f"\n--- Day {day} ---")
            print(f"Susceptible: {s}  Infected: {i}  Recovered: {r}")
            grid.display()
            
            # Slow it down so I can actually watch
            if i > 0:  # Keep going while there are infected
                time.sleep(delay)
            else:
                print("\nEpidemic has ended (no more infected).")
                break
        
        grid.step()
    
    s, i, r = grid.count_states()
    print(f"\n=== Final Statistics ===")
    print(f"Susceptible: {s}")
    print(f"Infected: {i}")
    print(f"Recovered: {r}")
    print(f"Attack rate: {r / (config.grid_size ** 2):.1%}")
    
    return s, i, r


if __name__ == "__main__":
    # These parameters give a nice visual spread without being too fast or slow
    config = Config(
        grid_size=30,
        initial_infected=3,
        transmission_prob=0.3,  # 30% chance per day to infect a neighbor
        recovery_days=7,        # sick for a week
        simulation_days=50
    )
    
    run_simulation(config, display_grid=True, delay=0.15)