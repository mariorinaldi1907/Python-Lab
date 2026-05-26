"""
Date: 2026-05-26
Implemented a basic SIR (Susceptible-Infected-Recovered) epidemic simulator to explore how diseases spread through populations with different transmission rates.
"""

#!/usr/bin/env python3
"""
Simple SIR Epidemic Model Simulation

This simulates disease spread through a population using the classic
compartmental model where people are either Susceptible, Infected, or Recovered.
Each day, infected people can transmit to susceptibles, and eventually recover.

I wanted something that shows realistic-ish epidemic curves without needing
any external libraries, just for learning how these models work.
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SimulationParams:
    """Configuration for the epidemic simulation."""
    population_size: int
    initial_infected: int
    transmission_rate: float  # probability per contact per day
    recovery_rate: float      # probability of recovery per day
    contact_rate: float       # average contacts per person per day
    days: int


class Person:
    """Represents an individual in the population."""
    
    def __init__(self, person_id: int):
        """
        Initialize a person with a unique ID.
        
        Args:
            person_id: Unique identifier for this person
        """
        self.id = person_id
        self.state = 'S'  # S=Susceptible, I=Infected, R=Recovered
        self.days_infected = 0
    
    def is_susceptible(self) -> bool:
        """Check if this person can be infected."""
        return self.state == 'S'
    
    def is_infected(self) -> bool:
        """Check if this person is currently infected."""
        return self.state == 'I'
    
    def is_recovered(self) -> bool:
        """Check if this person has recovered."""
        return self.state == 'R'
    
    def infect(self):
        """Change state to infected."""
        self.state = 'I'
        self.days_infected = 0
    
    def recover(self):
        """Change state to recovered (immune)."""
        self.state = 'R'


class EpidemicSimulation:
    """Runs a discrete-time SIR epidemic simulation."""
    
    def __init__(self, params: SimulationParams):
        """
        Initialize the simulation with given parameters.
        
        Args:
            params: Configuration object with all simulation settings
        """
        self.params = params
        self.population: List[Person] = []
        self.day = 0
        self.history: List[Tuple[int, int, int]] = []  # (S, I, R) counts per day
        
        # Create population
        for i in range(params.population_size):
            self.population.append(Person(i))
        
        # Infect initial cases randomly
        initial_infected_people = random.sample(
            self.population, 
            params.initial_infected
        )
        for person in initial_infected_people:
            person.infect()
    
    def count_states(self) -> Tuple[int, int, int]:
        """
        Count how many people are in each state.
        
        Returns:
            Tuple of (susceptible_count, infected_count, recovered_count)
        """
        s = sum(1 for p in self.population if p.is_susceptible())
        i = sum(1 for p in self.population if p.is_infected())
        r = sum(1 for p in self.population if p.is_recovered())
        return (s, i, r)
    
    def simulate_contacts(self):
        """
        Simulate daily contacts and potential transmissions.
        
        Uses a simplified model where each infected person has a certain number
        of contacts, and we randomly select people they might infect.
        """
        infected = [p for p in self.population if p.is_infected()]
        susceptible = [p for p in self.population if p.is_susceptible()]
        
        if not infected or not susceptible:
            return
        
        # Each infected person makes contacts
        for infected_person in infected:
            # Number of contacts this person makes today (Poisson-ish)
            num_contacts = int(random.gauss(self.params.contact_rate, 1.5))
            num_contacts = max(0, num_contacts)  # Can't be negative
            
            for _ in range(num_contacts):
                # Random contact from the population
                contact = random.choice(self.population)
                
                # Only susceptible people can be infected
                if contact.is_susceptible():
                    # Transmission happens with some probability
                    if random.random() < self.params.transmission_rate:
                        contact.infect()
    
    def simulate_recoveries(self):
        """
        Process potential recoveries for infected individuals.
        
        Each infected person has a probability of recovering each day.
        """
        for person in self.population:
            if person.is_infected():
                person.days_infected += 1
                # Recovery happens with some probability
                if random.random() < self.params.recovery_rate:
                    person.recover()
    
    def step(self):
        """Execute one day of the simulation."""
        self.simulate_contacts()
        self.simulate_recoveries()
        self.day += 1
        
        # Record today's counts
        counts = self.count_states()
        self.history.append(counts)
    
    def run(self):
        """Run the full simulation for the configured number of days."""
        # Record initial state
        self.history.append(self.count_states())
        
        for _ in range(self.params.days):
            self.step()
    
    def print_summary(self):
        """Print a text-based summary of the epidemic progression."""
        print(f"Epidemic Simulation Results")
        print(f"Population: {self.params.population_size}")
        print(f"Initial Infected: {self.params.initial_infected}")
        print(f"Transmission Rate: {self.params.transmission_rate:.2%}")
        print(f"Recovery Rate: {self.params.recovery_rate:.2%}")
        print(f"Avg Daily Contacts: {self.params.contact_rate:.1f}")
        print(f"\nDay | Susceptible | Infected | Recovered")
        print("-" * 45)
        
        # Print every 5th day to keep output manageable
        for day, (s, i, r) in enumerate(self.history):
            if day % 5 == 0 or day == len(self.history) - 1:
                print(f"{day:3d} | {s:11d} | {i:8d} | {r:9d}")
        
        # Peak infection
        max_infected = max(i for _, i, _ in self.history)
        peak_day = next(d for d, (_, i, _) in enumerate(self.history) if i == max_infected)
        print(f"\nPeak infection: {max_infected} people on day {peak_day}")
        
        final_s, final_i, final_r = self.history[-1]
        print(f"Final state: {final_r} recovered ({100*final_r/self.params.population_size:.1f}% attack rate)")


if __name__ == "__main__":
    # Set seed for reproducibility in this demo
    random.seed(42)
    
    # Configure a moderately contagious disease
    params = SimulationParams(
        population_size=1000,
        initial_infected=5,
        transmission_rate=0.03,   # 3% chance per contact
        recovery_rate=0.1,        # Average 10 days to recover
        contact_rate=10.0,        # 10 contacts per day on average
        days=100
    )
    
    sim = EpidemicSimulation(params)
    sim.run()
    sim.print_summary()