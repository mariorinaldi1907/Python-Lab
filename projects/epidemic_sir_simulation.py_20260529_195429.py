"""
Date: 2026-05-29
Simulated disease spread through a population using the SIR compartmental model — wanted to understand how infection and recovery rates affect outbreak dynamics.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulator

Simulates disease spread through a population using the Susceptible-Infected-Recovered
compartmental model. Each day, susceptible people can get infected based on contact
with infected individuals, and infected people can recover after a certain period.
"""

import random
from typing import List, Tuple


class Person:
    """
    Represents an individual in the population.
    
    Tracks infection status and days since infection to determine when recovery occurs.
    """
    
    def __init__(self, person_id: int):
        self.id = person_id
        self.status = "S"  # S = Susceptible, I = Infected, R = Recovered
        self.days_infected = 0
    
    def infect(self):
        """Mark this person as infected."""
        if self.status == "S":
            self.status = "I"
            self.days_infected = 0
    
    def progress_infection(self, recovery_days: int):
        """
        Progress infection by one day. Recover if infection duration exceeded.
        
        Args:
            recovery_days: Number of days before an infected person recovers
        """
        if self.status == "I":
            self.days_infected += 1
            if self.days_infected >= recovery_days:
                self.status = "R"


class EpidemicSimulation:
    """
    Simulates disease spread through a population using the SIR model.
    
    Each day, infected individuals have a chance to infect susceptible people
    they come into contact with. Infection lasts for a fixed duration.
    """
    
    def __init__(self, population_size: int, initial_infected: int, 
                 transmission_rate: float, contacts_per_day: int, recovery_days: int):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of people in the simulation
            initial_infected: How many people start infected
            transmission_rate: Probability of transmission per contact (0.0 to 1.0)
            contacts_per_day: Average number of people each person encounters daily
            recovery_days: Days until an infected person recovers
        """
        self.population_size = population_size
        self.transmission_rate = transmission_rate
        self.contacts_per_day = contacts_per_day
        self.recovery_days = recovery_days
        self.day = 0
        
        # Create population
        self.people = [Person(i) for i in range(population_size)]
        
        # Infect initial people randomly
        initial_infected_people = random.sample(self.people, initial_infected)
        for person in initial_infected_people:
            person.infect()
    
    def get_counts(self) -> Tuple[int, int, int]:
        """
        Count current S, I, R populations.
        
        Returns:
            Tuple of (susceptible_count, infected_count, recovered_count)
        """
        s_count = sum(1 for p in self.people if p.status == "S")
        i_count = sum(1 for p in self.people if p.status == "I")
        r_count = sum(1 for p in self.people if p.status == "R")
        return s_count, i_count, r_count
    
    def simulate_day(self):
        """
        Simulate one day of the epidemic.
        
        Each infected person has contact with a random subset of the population,
        potentially transmitting the disease. Then all infections progress toward recovery.
        """
        self.day += 1
        
        # Get lists of infected and susceptible people
        infected = [p for p in self.people if p.status == "I"]
        susceptible = [p for p in self.people if p.status == "S"]
        
        # Each infected person makes contacts
        for infected_person in infected:
            # Randomly select people to contact (with replacement for simplicity)
            # In reality you'd want without replacement but this is simpler
            num_contacts = min(self.contacts_per_day, len(susceptible))
            if num_contacts > 0:
                contacts = random.choices(self.people, k=self.contacts_per_day)
                
                for contact in contacts:
                    # Only susceptible people can be infected
                    if contact.status == "S":
                        # Transmission occurs with probability transmission_rate
                        if random.random() < self.transmission_rate:
                            contact.infect()
        
        # Progress all infections (move toward recovery)
        for person in self.people:
            person.progress_infection(self.recovery_days)
    
    def run(self, max_days: int = 100) -> List[Tuple[int, int, int, int]]:
        """
        Run the simulation until the outbreak ends or max_days is reached.
        
        Args:
            max_days: Maximum number of days to simulate
            
        Returns:
            List of (day, susceptible, infected, recovered) tuples for each day
        """
        history = []
        
        # Record initial state
        s, i, r = self.get_counts()
        history.append((0, s, i, r))
        
        # Run simulation while there are still infected people
        while self.day < max_days:
            self.simulate_day()
            s, i, r = self.get_counts()
            history.append((self.day, s, i, r))
            
            # Stop if no more infected people
            if i == 0:
                break
        
        return history


def print_simulation_results(history: List[Tuple[int, int, int, int]]):
    """
    Pretty-print the simulation results.
    
    Args:
        history: List of (day, susceptible, infected, recovered) tuples
    """
    print("\n" + "="*60)
    print("EPIDEMIC SIMULATION RESULTS")
    print("="*60)
    print(f"{'Day':<6} {'Susceptible':<15} {'Infected':<15} {'Recovered':<15}")
    print("-"*60)
    
    for day, s, i, r in history:
        # Create simple bar chart visualization using asterisks
        s_bar = "*" * (s // 10 + 1) if s > 0 else ""
        i_bar = "*" * (i // 10 + 1) if i > 0 else ""
        r_bar = "*" * (r // 10 + 1) if r > 0 else ""
        
        print(f"{day:<6} {s:<4} {s_bar:<10} {i:<4} {i_bar:<10} {r:<4} {r_bar:<10}")
    
    print("="*60)
    final_s, final_i, final_r = history[-1][1:]
    total = final_s + final_i + final_r
    print(f"Final state after {history[-1][0]} days:")
    print(f"  Susceptible: {final_s}/{total} ({100*final_s/total:.1f}%)")
    print(f"  Infected:    {final_i}/{total} ({100*final_i/total:.1f}%)")
    print(f"  Recovered:   {final_r}/{total} ({100*final_r/total:.1f}%)")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Set seed for reproducible results (remove this for randomness)
    random.seed(42)
    
    # Scenario: moderate flu-like illness in a small town
    # These parameters roughly model something like seasonal flu
    sim = EpidemicSimulation(
        population_size=500,      # Small town
        initial_infected=5,       # A few people start sick
        transmission_rate=0.05,   # 5% chance per contact
        contacts_per_day=10,      # Each person interacts with ~10 others daily
        recovery_days=7           # Week-long illness
    )
    
    print("\nStarting epidemic simulation...")
    print(f"Population: {sim.population_size}")
    print(f"Initial infected: 5")
    print(f"Transmission rate: {sim.transmission_rate*100}% per contact")
    print(f"Contacts per day: {sim.contacts_per_day}")
    print(f"Recovery period: {sim.recovery_days} days")
    
    # Run the simulation
    history = sim.run(max_days=100)
    
    # Display results
    print_simulation_results(history)