"""
Date: 2026-07-18
Implemented a stochastic SIR (Susceptible-Infected-Recovered) epidemic model to experiment with disease spread dynamics and see how parameters affect outbreak severity.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulator

A simple stochastic simulation of disease spread through a population.
Each person can be Susceptible, Infected, or Recovered. I wanted to see
how changing beta (infection rate) and gamma (recovery rate) affects
the outbreak curve.
"""

import random
from collections import Counter
from typing import List, Tuple


class Person:
    """Represents an individual in the population with a disease state."""
    
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    RECOVERED = 'R'
    
    def __init__(self, state: str = SUSCEPTIBLE):
        """
        Initialize a person with a given state.
        
        Args:
            state: Initial disease state (S, I, or R)
        """
        self.state = state
        self.days_infected = 0  # Track how long they've been sick
    
    def is_susceptible(self) -> bool:
        return self.state == self.SUSCEPTIBLE
    
    def is_infected(self) -> bool:
        return self.state == self.INFECTED
    
    def is_recovered(self) -> bool:
        return self.state == self.RECOVERED
    
    def infect(self):
        """Change state to infected."""
        if self.is_susceptible():
            self.state = self.INFECTED
            self.days_infected = 0
    
    def recover(self):
        """Change state to recovered."""
        if self.is_infected():
            self.state = self.RECOVERED


class EpidemicSimulation:
    """Simulates disease spread using the SIR model with random contacts."""
    
    def __init__(self, population_size: int, initial_infected: int,
                 beta: float, gamma: float, contacts_per_day: int):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of people
            initial_infected: Number of infected individuals at start
            beta: Probability of transmission per contact (0-1)
            gamma: Probability of recovery per day (0-1)
            contacts_per_day: Average number of contacts each person makes
        """
        self.beta = beta
        self.gamma = gamma
        self.contacts_per_day = contacts_per_day
        
        # Create population with some initially infected
        self.population = [Person(Person.INFECTED) for _ in range(initial_infected)]
        self.population.extend([Person(Person.SUSCEPTIBLE) 
                               for _ in range(population_size - initial_infected)])
        
        self.history = []  # Track state counts over time
        self.day = 0
    
    def get_state_counts(self) -> Counter:
        """Return counts of S, I, R in current population."""
        return Counter(person.state for person in self.population)
    
    def simulate_contacts(self):
        """
        Simulate random contacts between people for one day.
        
        Each infected person makes random contacts and might spread the disease.
        Using random sampling because in reality people don't contact everyone.
        """
        infected_people = [p for p in self.population if p.is_infected()]
        susceptible_people = [p for p in self.population if p.is_susceptible()]
        
        if not infected_people or not susceptible_people:
            return  # No spread possible
        
        for infected in infected_people:
            # Each infected person contacts several random people
            num_contacts = min(self.contacts_per_day, len(self.population) - 1)
            contacts = random.sample(self.population, num_contacts)
            
            for contact in contacts:
                if contact.is_susceptible() and random.random() < self.beta:
                    contact.infect()
    
    def simulate_recoveries(self):
        """Process recovery for infected individuals based on gamma."""
        for person in self.population:
            if person.is_infected():
                person.days_infected += 1
                # Recovery is probabilistic each day
                if random.random() < self.gamma:
                    person.recover()
    
    def step(self):
        """Advance simulation by one day."""
        self.simulate_contacts()
        self.simulate_recoveries()
        self.day += 1
        self.history.append(self.get_state_counts())
    
    def run(self, days: int) -> List[Counter]:
        """
        Run simulation for specified number of days.
        
        Args:
            days: Number of days to simulate
            
        Returns:
            List of state counts for each day
        """
        # Record initial state
        self.history = [self.get_state_counts()]
        
        for _ in range(days):
            self.step()
            # Stop early if no more infected people
            if self.history[-1]['I'] == 0:
                break
        
        return self.history
    
    def print_summary(self):
        """Print a text-based visualization of the epidemic curve."""
        print(f"\nEpidemic Simulation Results (β={self.beta}, γ={self.gamma})")
        print("=" * 60)
        print(f"{'Day':<5} {'S':<8} {'I':<8} {'R':<8} {'Chart (I)'}")
        print("-" * 60)
        
        max_infected = max(counts['I'] for counts in self.history)
        
        for day, counts in enumerate(self.history):
            s, i, r = counts['S'], counts['I'], counts['R']
            # Simple bar chart using asterisks
            bar_length = int((i / max_infected) * 30) if max_infected > 0 else 0
            bar = '*' * bar_length
            print(f"{day:<5} {s:<8} {i:<8} {r:<8} {bar}")
        
        final = self.history[-1]
        print("\nFinal State:")
        print(f"  Never infected: {final['S']} ({100*final['S']/len(self.population):.1f}%)")
        print(f"  Total recovered: {final['R']} ({100*final['R']/len(self.population):.1f}%)")


if __name__ == "__main__":
    # Seed for reproducibility during testing, but feel free to comment out
    random.seed(42)
    
    # Run a moderately contagious disease scenario
    print("Scenario 1: Moderate outbreak (flu-like)")
    sim = EpidemicSimulation(
        population_size=200,
        initial_infected=5,
        beta=0.3,           # 30% chance of transmission per contact
        gamma=0.15,         # ~7 day average infection duration
        contacts_per_day=8  # Each person contacts 8 others daily
    )
    sim.run(days=100)
    sim.print_summary()
    
    # Run a more contagious scenario for comparison
    print("\n\nScenario 2: Highly contagious outbreak")
    sim2 = EpidemicSimulation(
        population_size=200,
        initial_infected=5,
        beta=0.5,           # 50% transmission rate
        gamma=0.1,          # Longer infectious period
        contacts_per_day=10
    )
    sim2.run(days=100)
    sim2.print_summary()