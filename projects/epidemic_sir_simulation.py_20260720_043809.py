"""
Date: 2026-07-20
Implemented a stochastic SIR (Susceptible-Infected-Recovered) epidemic model to explore disease dynamics — adjustable infection rate, recovery time, and population mixing.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulation

A simple stochastic simulation of disease spread through a population.
Each person can be Susceptible, Infected, or Recovered. Infected people
have a chance to infect susceptible contacts each day, and eventually recover.
"""

import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SimulationParams:
    """Configuration parameters for the epidemic simulation."""
    population_size: int
    initial_infected: int
    infection_probability: float  # chance of transmission per contact
    contacts_per_day: int  # how many people each person encounters
    recovery_days: int  # days until an infected person recovers
    simulation_days: int


class Person:
    """
    Represents an individual in the population.
    
    Tracks infection status and days since infection for recovery timing.
    """
    
    def __init__(self, person_id: int):
        self.id = person_id
        self.status = 'S'  # S = Susceptible, I = Infected, R = Recovered
        self.days_infected = 0
    
    def infect(self):
        """Mark this person as infected."""
        if self.status == 'S':
            self.status = 'I'
            self.days_infected = 0
    
    def update(self, recovery_days: int):
        """
        Update infection status for a new day.
        
        Infected people progress toward recovery based on recovery_days threshold.
        """
        if self.status == 'I':
            self.days_infected += 1
            if self.days_infected >= recovery_days:
                self.status = 'R'


class EpidemicSimulation:
    """
    Runs a stochastic SIR epidemic model.
    
    Each day, infected individuals randomly contact others and may transmit
    the disease. This continues until no infected individuals remain or
    the simulation time limit is reached.
    """
    
    def __init__(self, params: SimulationParams):
        self.params = params
        self.population: List[Person] = []
        self.history: List[Tuple[int, int, int]] = []  # (S, I, R) counts per day
        
        # Initialize population
        for i in range(params.population_size):
            self.population.append(Person(i))
        
        # Infect initial people randomly
        initial_infected_people = random.sample(
            self.population, 
            params.initial_infected
        )
        for person in initial_infected_people:
            person.infect()
    
    def get_counts(self) -> Tuple[int, int, int]:
        """Return current (susceptible, infected, recovered) counts."""
        s_count = sum(1 for p in self.population if p.status == 'S')
        i_count = sum(1 for p in self.population if p.status == 'I')
        r_count = sum(1 for p in self.population if p.status == 'R')
        return (s_count, i_count, r_count)
    
    def simulate_day(self):
        """
        Simulate one day of the epidemic.
        
        Each infected person contacts random others and may infect susceptibles.
        Then all people update their status (infected -> recovered if time).
        """
        infected_people = [p for p in self.population if p.status == 'I']
        
        # Each infected person makes contacts
        for infected in infected_people:
            # Random contacts from the population
            contacts = random.choices(
                self.population, 
                k=self.params.contacts_per_day
            )
            
            for contact in contacts:
                if contact.status == 'S':
                    # Attempt transmission
                    if random.random() < self.params.infection_probability:
                        contact.infect()
        
        # Update everyone's status (for recovery)
        for person in self.population:
            person.update(self.params.recovery_days)
    
    def run(self) -> List[Tuple[int, int, int]]:
        """
        Run the full simulation and return history of (S, I, R) counts.
        
        Continues for specified days or until no infected individuals remain.
        """
        for day in range(self.params.simulation_days):
            counts = self.get_counts()
            self.history.append(counts)
            
            # Stop if no one is infected
            if counts[1] == 0:
                break
            
            self.simulate_day()
        
        # Record final state
        self.history.append(self.get_counts())
        return self.history


def print_results(history: List[Tuple[int, int, int]], params: SimulationParams):
    """Pretty print the simulation results with a simple text visualization."""
    print("=" * 60)
    print("EPIDEMIC SIMULATION RESULTS")
    print("=" * 60)
    print(f"Population: {params.population_size}")
    print(f"Initial infected: {params.initial_infected}")
    print(f"Infection probability: {params.infection_probability:.1%}")
    print(f"Contacts per day: {params.contacts_per_day}")
    print(f"Recovery period: {params.recovery_days} days")
    print("=" * 60)
    print()
    
    print(f"{'Day':<5} {'S':>6} {'I':>6} {'R':>6}   Visualization")
    print("-" * 60)
    
    for day, (s, i, r) in enumerate(history):
        # Create a simple bar visualization
        total = params.population_size
        s_bar = int((s / total) * 30)
        i_bar = int((i / total) * 30)
        r_bar = int((r / total) * 30)
        
        viz = f"{'S' * s_bar}{'I' * i_bar}{'R' * r_bar}"
        print(f"{day:<5} {s:>6} {i:>6} {r:>6}   {viz}")
    
    print("=" * 60)
    final_s, final_i, final_r = history[-1]
    print(f"Final: {final_r} recovered, {final_s} never infected")
    print(f"Attack rate: {(final_r / params.population_size):.1%}")
    print("=" * 60)


if __name__ == "__main__":
    # Configure the simulation with realistic-ish parameters for a mild outbreak
    params = SimulationParams(
        population_size=200,
        initial_infected=3,
        infection_probability=0.15,  # 15% chance per contact
        contacts_per_day=5,
        recovery_days=7,
        simulation_days=60
    )
    
    print("Starting epidemic simulation...")
    print(f"Running with {params.population_size} people, "
          f"{params.initial_infected} initially infected")
    print()
    
    # Run it
    sim = EpidemicSimulation(params)
    history = sim.run()
    
    # Show the results
    print_results(history, params)