"""
Date: 2026-07-16
Implemented a stochastic SIR (Susceptible-Infected-Recovered) epidemic simulator to model disease spread through a population with adjustable infection and recovery rates.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulation

A simple stochastic simulation of disease spread using the SIR compartmental model.
Each day, infected individuals have a chance to infect susceptible neighbors,
and infected individuals can recover based on a recovery probability.
"""

import random
from typing import List, Tuple


class Person:
    """Represents an individual in the population with a health state."""
    
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    RECOVERED = 'R'
    
    def __init__(self, state: str = SUSCEPTIBLE):
        """
        Initialize a person with a given health state.
        
        Args:
            state: Initial health state (S, I, or R)
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
        """Change state from susceptible to infected."""
        if self.is_susceptible():
            self.state = self.INFECTED
            self.days_infected = 0
    
    def recover(self):
        """Change state from infected to recovered."""
        if self.is_infected():
            self.state = self.RECOVERED


class EpidemicSimulation:
    """Simulates disease spread through a population using the SIR model."""
    
    def __init__(self, population_size: int, initial_infected: int, 
                 infection_rate: float, recovery_rate: float, contact_rate: int):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of people
            initial_infected: Number of initially infected individuals
            infection_rate: Probability of transmission per contact (0.0 to 1.0)
            recovery_rate: Probability of recovery per day (0.0 to 1.0)
            contact_rate: Average number of contacts per person per day
        """
        self.population_size = population_size
        self.infection_rate = infection_rate
        self.recovery_rate = recovery_rate
        self.contact_rate = contact_rate
        self.day = 0
        
        # Create population: mostly susceptible, some initially infected
        self.population: List[Person] = [Person() for _ in range(population_size)]
        for i in range(min(initial_infected, population_size)):
            self.population[i].infect()
        
        # Shuffle so infected aren't all at the start
        random.shuffle(self.population)
    
    def get_counts(self) -> Tuple[int, int, int]:
        """Return current counts of (susceptible, infected, recovered)."""
        s = sum(1 for p in self.population if p.is_susceptible())
        i = sum(1 for p in self.population if p.is_infected())
        r = sum(1 for p in self.population if p.is_recovered())
        return s, i, r
    
    def simulate_day(self) -> bool:
        """
        Simulate one day of the epidemic.
        
        Returns:
            True if the epidemic is still active (infected > 0), False otherwise
        """
        self.day += 1
        newly_infected = []
        newly_recovered = []
        
        # Infection phase: infected people make random contacts
        infected_people = [p for p in self.population if p.is_infected()]
        
        for infected_person in infected_people:
            # Each infected person contacts some random people
            contacts = random.choices(self.population, k=self.contact_rate)
            
            for contact in contacts:
                if contact.is_susceptible():
                    # Roll the dice for transmission
                    if random.random() < self.infection_rate:
                        newly_infected.append(contact)
            
            infected_person.days_infected += 1
        
        # Recovery phase: infected people might recover
        for person in infected_people:
            if random.random() < self.recovery_rate:
                newly_recovered.append(person)
        
        # Apply state changes (doing this after to avoid modifying during iteration)
        for person in newly_infected:
            person.infect()
        
        for person in newly_recovered:
            person.recover()
        
        _, infected_count, _ = self.get_counts()
        return infected_count > 0
    
    def run_simulation(self, max_days: int = 100, verbose: bool = True):
        """
        Run the full simulation until no infected remain or max days reached.
        
        Args:
            max_days: Maximum number of days to simulate
            verbose: Whether to print daily updates
        """
        if verbose:
            print(f"Starting epidemic simulation (population: {self.population_size})")
            print(f"Parameters: infection_rate={self.infection_rate:.2f}, "
                  f"recovery_rate={self.recovery_rate:.2f}, contact_rate={self.contact_rate}")
            print("-" * 60)
        
        # Print initial state
        s, i, r = self.get_counts()
        if verbose:
            print(f"Day {self.day:3d}: S={s:5d} I={i:5d} R={r:5d}")
        
        # Run day by day until no more infected or max days
        while self.day < max_days:
            epidemic_active = self.simulate_day()
            
            if verbose:
                s, i, r = self.get_counts()
                print(f"Day {self.day:3d}: S={s:5d} I={i:5d} R={r:5d}")
            
            if not epidemic_active:
                break
        
        # Final summary
        s, i, r = self.get_counts()
        if verbose:
            print("-" * 60)
            print(f"Simulation ended on day {self.day}")
            print(f"Final state: {s} susceptible, {i} infected, {r} recovered")
            print(f"Attack rate: {r / self.population_size * 100:.1f}% of population infected")


if __name__ == "__main__":
    # Run a simulation with reasonable parameters
    # About 2% infection chance per contact, 10% daily recovery, 5 contacts/day
    sim = EpidemicSimulation(
        population_size=1000,
        initial_infected=5,
        infection_rate=0.02,
        recovery_rate=0.10,
        contact_rate=5
    )
    
    sim.run_simulation(max_days=150, verbose=True)