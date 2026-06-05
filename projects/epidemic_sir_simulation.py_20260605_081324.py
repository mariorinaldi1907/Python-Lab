"""
Date: 2026-06-05
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic simulator that shows how infections propagate through a grid-based population over time.
"""

#!/usr/bin/env python3
"""
A simple spatial SIR (Susceptible-Infected-Recovered) epidemic model.
People live on a grid and can infect their neighbors. I wanted to see
how different infection rates and recovery times affect outbreak size.
"""

import random
from typing import List, Tuple


class Person:
    """Represents an individual in the simulation with a health state."""
    
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    
    def __init__(self, x: int, y: int):
        """Initialize a person at grid position (x, y)."""
        self.x = x
        self.y = y
        self.state = Person.SUSCEPTIBLE
        self.days_infected = 0  # Track how long they've been sick


class EpidemicSimulation:
    """
    Simulates disease spread on a 2D grid.
    
    Each day, infected people can spread to susceptible neighbors,
    and after a certain number of days, infected people recover.
    """
    
    def __init__(self, grid_size: int, infection_rate: float, recovery_days: int):
        """
        Set up the simulation grid.
        
        Args:
            grid_size: Width and height of the population grid
            infection_rate: Probability that an infected person infects a neighbor (0-1)
            recovery_days: How many days until an infected person recovers
        """
        self.grid_size = grid_size
        self.infection_rate = infection_rate
        self.recovery_days = recovery_days
        
        # Create a 2D grid of people
        self.grid: List[List[Person]] = []
        for x in range(grid_size):
            row = []
            for y in range(grid_size):
                row.append(Person(x, y))
            self.grid.append(row)
        
        self.day = 0
    
    def infect_random(self, count: int = 1):
        """Start the outbreak by infecting random people."""
        infected = 0
        while infected < count:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            person = self.grid[x][y]
            if person.state == Person.SUSCEPTIBLE:
                person.state = Person.INFECTED
                infected += 1
    
    def get_neighbors(self, x: int, y: int) -> List[Person]:
        """Get the four adjacent neighbors (up, down, left, right)."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            # Make sure we stay within bounds
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append(self.grid[nx][ny])
        return neighbors
    
    def step(self):
        """Simulate one day of the epidemic."""
        self.day += 1
        
        # Track new infections separately so we don't infect people twice in one step
        newly_infected = []
        
        # First, let infected people try to spread the disease
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                person = self.grid[x][y]
                
                if person.state == Person.INFECTED:
                    # Try to infect neighbors
                    neighbors = self.get_neighbors(x, y)
                    for neighbor in neighbors:
                        if neighbor.state == Person.SUSCEPTIBLE:
                            # Roll the dice to see if transmission happens
                            if random.random() < self.infection_rate:
                                newly_infected.append(neighbor)
                    
                    # Increment infection duration
                    person.days_infected += 1
        
        # Apply new infections
        for person in newly_infected:
            person.state = Person.INFECTED
            person.days_infected = 0
        
        # Now check for recoveries
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                person = self.grid[x][y]
                if person.state == Person.INFECTED and person.days_infected >= self.recovery_days:
                    person.state = Person.RECOVERED
    
    def get_counts(self) -> Tuple[int, int, int]:
        """Return (susceptible_count, infected_count, recovered_count)."""
        s_count = 0
        i_count = 0
        r_count = 0
        
        for row in self.grid:
            for person in row:
                if person.state == Person.SUSCEPTIBLE:
                    s_count += 1
                elif person.state == Person.INFECTED:
                    i_count += 1
                elif person.state == Person.RECOVERED:
                    r_count += 1
        
        return s_count, i_count, r_count
    
    def print_status(self):
        """Print the current state of the simulation."""
        s, i, r = self.get_counts()
        total = self.grid_size * self.grid_size
        print(f"Day {self.day:3d} | S: {s:4d} ({100*s/total:5.1f}%) | "
              f"I: {i:4d} ({100*i/total:5.1f}%) | "
              f"R: {r:4d} ({100*r/total:5.1f}%)")
    
    def is_outbreak_over(self) -> bool:
        """Check if there are any infected people left."""
        _, infected, _ = self.get_counts()
        return infected == 0


if __name__ == "__main__":
    # Set up a simulation with a 30x30 grid
    # Infection rate of 0.3 means 30% chance of transmission per contact per day
    # People recover after 7 days
    print("Starting epidemic simulation...")
    print("=" * 70)
    
    sim = EpidemicSimulation(grid_size=30, infection_rate=0.3, recovery_days=7)
    
    # Start with 3 infected people in random locations
    sim.infect_random(count=3)
    
    # Print initial state
    sim.print_status()
    
    # Run the simulation until no one is infected anymore
    while not sim.is_outbreak_over() and sim.day < 100:  # Cap at 100 days for safety
        sim.step()
        # Print every 5 days to avoid too much output
        if sim.day % 5 == 0:
            sim.print_status()
    
    # Always print the final state
    if sim.day % 5 != 0:
        sim.print_status()
    
    print("=" * 70)
    print("Outbreak finished!")
    
    final_s, final_i, final_r = sim.get_counts()
    total_pop = sim.grid_size * sim.grid_size
    print(f"\nFinal stats after {sim.day} days:")
    print(f"  Never infected: {final_s} ({100*final_s/total_pop:.1f}%)")
    print(f"  Total infected at some point: {final_r} ({100*final_r/total_pop:.1f}%)")
```