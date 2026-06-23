"""
Date: 2026-06-23
Implemented a discrete-time SIR (Susceptible-Infected-Recovered) epidemic model to watch disease dynamics play out in a small population.
"""

#!/usr/bin/env python3
"""
Simple SIR epidemic model simulator.

This models disease spread in a population where individuals can be:
- Susceptible (S): can catch the disease
- Infected (I): currently sick and can spread it
- Recovered (R): immune and can't spread or catch it

Uses a discrete time step approach with probabilistic state transitions.
"""

import random
from dataclasses import dataclass
from typing import List


@dataclass
class SimulationConfig:
    """Configuration parameters for the epidemic simulation."""
    population_size: int
    initial_infected: int
    infection_probability: float  # chance of transmission on contact
    recovery_rate: float  # chance of recovery per time step
    contact_rate: int  # average number of contacts per person per day
    duration_days: int


class Person:
    """Represents a single person in the epidemic simulation."""
    
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    RECOVERED = 'R'
    
    def __init__(self, state: str = SUSCEPTIBLE):
        """
        Initialize a person with a given health state.
        
        Args:
            state: Initial state (S, I, or R)
        """
        self.state = state
        self.days_infected = 0
    
    def is_susceptible(self) -> bool:
        """Check if person can catch the disease."""
        return self.state == self.SUSCEPTIBLE
    
    def is_infected(self) -> bool:
        """Check if person is currently sick."""
        return self.state == self.INFECTED
    
    def infect(self):
        """Transition to infected state."""
        self.state = self.INFECTED
        self.days_infected = 0
    
    def try_recover(self, recovery_rate: float) -> bool:
        """
        Attempt recovery based on probability.
        
        Args:
            recovery_rate: Probability of recovery per day
            
        Returns:
            True if recovered, False otherwise
        """
        if self.is_infected() and random.random() < recovery_rate:
            self.state = self.RECOVERED
            return True
        return False


class EpidemicSimulation:
    """Runs a discrete-time SIR epidemic simulation."""
    
    def __init__(self, config: SimulationConfig):
        """
        Initialize the simulation with given configuration.
        
        Args:
            config: SimulationConfig object with all parameters
        """
        self.config = config
        self.population: List[Person] = []
        self.history = {
            'susceptible': [],
            'infected': [],
            'recovered': []
        }
        
        # Create population - most susceptible, some initially infected
        for i in range(config.population_size):
            if i < config.initial_infected:
                self.population.append(Person(Person.INFECTED))
            else:
                self.population.append(Person(Person.SUSCEPTIBLE))
        
        # Shuffle so infected people aren't all at the start
        random.shuffle(self.population)
    
    def count_states(self) -> dict:
        """Count how many people are in each state."""
        counts = {
            'susceptible': sum(1 for p in self.population if p.is_susceptible()),
            'infected': sum(1 for p in self.population if p.is_infected()),
            'recovered': sum(1 for p in self.population if p.state == Person.RECOVERED)
        }
        return counts
    
    def simulate_contacts(self):
        """
        Simulate random contacts between people.
        
        Each infected person has a chance to infect susceptible contacts.
        This is a simplified model - real epidemic models would consider
        network structure, spatial proximity, etc.
        """
        infected_people = [p for p in self.population if p.is_infected()]
        
        for infected in infected_people:
            # Each infected person contacts a random number of people
            num_contacts = random.randint(
                max(1, self.config.contact_rate - 2),
                self.config.contact_rate + 2
            )
            
            contacts = random.sample(self.population, min(num_contacts, len(self.population)))
            
            for contact in contacts:
                if contact.is_susceptible():
                    # Transmission happens with some probability
                    if random.random() < self.config.infection_probability:
                        contact.infect()
    
    def simulate_day(self):
        """Run one day of the simulation."""
        # First, handle recoveries
        for person in self.population:
            person.try_recover(self.config.recovery_rate)
        
        # Then simulate contacts and potential new infections
        self.simulate_contacts()
        
        # Record current state
        counts = self.count_states()
        for state, count in counts.items():
            self.history[state].append(count)
    
    def run(self):
        """Execute the full simulation."""
        print(f"Starting epidemic simulation:")
        print(f"Population: {self.config.population_size}")
        print(f"Initially infected: {self.config.initial_infected}")
        print(f"Infection probability: {self.config.infection_probability:.2%}")
        print(f"Recovery rate: {self.config.recovery_rate:.2%}")
        print()
        
        for day in range(self.config.duration_days):
            self.simulate_day()
        
        self.print_results()
    
    def print_results(self):
        """Display simulation results as ASCII chart."""
        print("Day | Susceptible | Infected | Recovered | Visualization")
        print("-" * 70)
        
        for day in range(len(self.history['susceptible'])):
            s = self.history['susceptible'][day]
            i = self.history['infected'][day]
            r = self.history['recovered'][day]
            
            # Create a simple bar chart using characters
            total = self.config.population_size
            s_bar = '█' * int((s / total) * 30)
            i_bar = '▓' * int((i / total) * 30)
            r_bar = '░' * int((r / total) * 30)
            
            print(f"{day:3d} | {s:11d} | {i:8d} | {r:9d} | {s_bar}{i_bar}{r_bar}")


if __name__ == "__main__":
    # Set random seed for reproducibility during testing
    random.seed(42)
    
    # Configure a realistic-ish scenario
    # Similar to a flu with moderate transmission
    config = SimulationConfig(
        population_size=200,
        initial_infected=5,
        infection_probability=0.15,  # 15% chance per contact
        recovery_rate=0.20,  # average 5 days to recover
        contact_rate=8,  # each person contacts ~8 others per day
        duration_days=30
    )
    
    sim = EpidemicSimulation(config)
    sim.run()
    
    # Print final statistics
    final = sim.count_states()
    print()
    print("Final outcome:")
    print(f"  Never infected: {final['susceptible']}")
    print(f"  Still sick: {final['infected']}")
    print(f"  Recovered: {final['recovered']}")
    print(f"  Attack rate: {(config.population_size - final['susceptible']) / config.population_size:.1%}")