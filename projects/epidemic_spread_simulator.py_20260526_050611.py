"""
Date: 2026-05-26
Simulated disease spread on a 2D grid using the SIR model where people move randomly and infect nearby susceptible individuals — helps visualize how infection waves propagate.
"""

#!/usr/bin/env python3
"""
Epidemic spread simulator using a spatial SIR model.

People are placed on a grid and can be Susceptible, Infected, or Recovered.
Infected individuals can spread disease to nearby susceptibles, then eventually recover.
Movement is random walk, which creates interesting clustering patterns.
"""

import random
from collections import namedtuple
from typing import List, Tuple

# Simple person representation: position and state
Person = namedtuple('Person', ['x', 'y', 'state'])

class EpidemicSimulator:
    """
    Simulates disease spread on a 2D grid with mobile agents.
    
    Uses SIR model: Susceptible -> Infected -> Recovered
    Movement creates spatial clustering that affects transmission dynamics.
    """
    
    def __init__(self, grid_size=50, population=200, initial_infected=5,
                 infection_radius=2.0, infection_prob=0.3, recovery_time=10):
        """
        Initialize the simulation parameters.
        
        Args:
            grid_size: Size of the square grid
            population: Total number of people
            initial_infected: Number of initially infected individuals
            infection_radius: Max distance for disease transmission
            infection_prob: Probability of infection per contact
            recovery_time: Average timesteps until recovery
        """
        self.grid_size = grid_size
        self.population = population
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time
        
        # Track people and their infection timers
        self.people = []
        self.infection_timers = {}  # person_id -> timesteps infected
        
        # Initialize population
        for i in range(population):
            x = random.uniform(0, grid_size)
            y = random.uniform(0, grid_size)
            state = 'I' if i < initial_infected else 'S'
            self.people.append(Person(x, y, state))
            if state == 'I':
                self.infection_timers[i] = 0
    
    def _distance(self, p1: Person, p2: Person) -> float:
        """Calculate Euclidean distance between two people."""
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
    
    def _move_person(self, person: Person) -> Person:
        """
        Move person randomly (random walk).
        
        Keeps them within grid boundaries using reflection.
        """
        # Random step in each direction
        dx = random.gauss(0, 0.5)
        dy = random.gauss(0, 0.5)
        
        new_x = person.x + dx
        new_y = person.y + dy
        
        # Boundary reflection instead of wrapping
        if new_x < 0:
            new_x = -new_x
        elif new_x > self.grid_size:
            new_x = 2 * self.grid_size - new_x
            
        if new_y < 0:
            new_y = -new_y
        elif new_y > self.grid_size:
            new_y = 2 * self.grid_size - new_y
        
        return Person(new_x, new_y, person.state)
    
    def step(self) -> dict:
        """
        Advance simulation by one timestep.
        
        Returns counts of each state for tracking.
        """
        new_people = []
        new_infections = []
        
        # Move everyone first
        for i, person in enumerate(self.people):
            new_people.append(self._move_person(person))
        
        # Check for new infections
        for i, person in enumerate(new_people):
            if person.state == 'S':
                # Check if any infected person is nearby
                for j, other in enumerate(new_people):
                    if other.state == 'I':
                        if self._distance(person, other) < self.infection_radius:
                            if random.random() < self.infection_prob:
                                # New infection!
                                new_infections.append(i)
                                break
        
        # Apply new infections
        for i in new_infections:
            person = new_people[i]
            new_people[i] = Person(person.x, person.y, 'I')
            self.infection_timers[i] = 0
        
        # Update infection timers and handle recoveries
        for i, person in enumerate(new_people):
            if person.state == 'I':
                self.infection_timers[i] += 1
                # Stochastic recovery based on average recovery time
                if random.random() < 1.0 / self.recovery_time:
                    new_people[i] = Person(person.x, person.y, 'R')
                    del self.infection_timers[i]
        
        self.people = new_people
        
        # Count states
        counts = {'S': 0, 'I': 0, 'R': 0}
        for person in self.people:
            counts[person.state] += 1
        
        return counts
    
    def run(self, timesteps: int) -> List[dict]:
        """
        Run simulation for specified number of timesteps.
        
        Returns history of state counts at each timestep.
        """
        history = []
        for t in range(timesteps):
            counts = self.step()
            history.append(counts)
        return history


def print_summary(history: List[dict]):
    """Print a nice summary of the epidemic progression."""
    print("\nEpidemic Simulation Results")
    print("=" * 60)
    print(f"{'Time':<8} {'Susceptible':<15} {'Infected':<15} {'Recovered':<15}")
    print("-" * 60)
    
    # Print every 10th timestep to keep output reasonable
    for t, counts in enumerate(history):
        if t % 10 == 0 or t == len(history) - 1:
            s_bar = '█' * (counts['S'] // 5)
            i_bar = '█' * (counts['I'] // 5)
            r_bar = '█' * (counts['R'] // 5)
            print(f"{t:<8} {counts['S']:<4} {s_bar:<10} {counts['I']:<4} {i_bar:<10} {counts['R']:<4} {r_bar}")
    
    print("-" * 60)
    final = history[-1]
    total = sum(final.values())
    print(f"\nFinal state: {final['S']} susceptible, {final['I']} infected, {final['R']} recovered")
    print(f"Attack rate: {final['R'] / total * 100:.1f}% of population infected at some point")


if __name__ == "__main__":
    # Run a demo simulation
    print("Starting epidemic simulation with spatial dynamics...")
    print("Population moves randomly, infection spreads through proximity\n")
    
    sim = EpidemicSimulator(
        grid_size=50,
        population=200,
        initial_infected=3,
        infection_radius=2.5,
        infection_prob=0.25,
        recovery_time=15
    )
    
    history = sim.run(timesteps=100)
    print_summary(history)
    
    # Check if epidemic burned out or is still active
    if history[-1]['I'] == 0:
        print("\n✓ Epidemic has burned out (no active infections)")
    else:
        print(f"\n⚠ Epidemic still active with {history[-1]['I']} infected individuals")