"""
Date: 2026-08-09
Wrote an epidemic simulator using the SIR compartmental model to see how diseases spread through populations with different R0 values.
"""

#!/usr/bin/env python3
"""
Simple SIR (Susceptible-Infected-Recovered) epidemic simulation.
Uses a stochastic agent-based model where individuals interact randomly.

Mario - personal experiment with epidemic modeling
"""

import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Person:
    """
    Represents an individual in the simulation.
    
    State can be: 'S' (susceptible), 'I' (infected), 'R' (recovered/removed)
    """
    state: str = 'S'
    days_infected: int = 0


class EpidemicSimulation:
    """
    Agent-based SIR epidemic model with random mixing.
    
    Each day, infected individuals have a chance to infect susceptible ones
    they encounter. After a certain period, infected individuals recover.
    """
    
    def __init__(
        self,
        population_size: int,
        initial_infected: int,
        transmission_rate: float,
        recovery_days: int,
        contacts_per_day: int
    ):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of individuals
            initial_infected: Number of people infected at day 0
            transmission_rate: Probability of transmission per contact (0-1)
            recovery_days: Days until an infected person recovers
            contacts_per_day: Average number of random contacts per person per day
        """
        self.population = [Person() for _ in range(population_size)]
        self.transmission_rate = transmission_rate
        self.recovery_days = recovery_days
        self.contacts_per_day = contacts_per_day
        
        # Infect random initial people
        for person in random.sample(self.population, initial_infected):
            person.state = 'I'
            person.days_infected = 0
    
    def count_states(self) -> Tuple[int, int, int]:
        """Count susceptible, infected, and recovered individuals."""
        s = sum(1 for p in self.population if p.state == 'S')
        i = sum(1 for p in self.population if p.state == 'I')
        r = sum(1 for p in self.population if p.state == 'R')
        return s, i, r
    
    def simulate_day(self) -> None:
        """
        Run one day of the simulation.
        
        Process:
        1. Random contacts happen between individuals
        2. Transmission occurs with some probability
        3. Infected individuals progress toward recovery
        """
        new_infections = []
        
        # Each person makes random contacts
        for person in self.population:
            if person.state == 'I':
                # Infected people make contacts and potentially spread disease
                contacts = random.sample(
                    self.population,
                    min(self.contacts_per_day, len(self.population))
                )
                
                for contact in contacts:
                    if contact.state == 'S':
                        # Transmission happens with probability transmission_rate
                        if random.random() < self.transmission_rate:
                            new_infections.append(contact)
        
        # Apply new infections (don't modify during iteration above)
        for person in new_infections:
            person.state = 'I'
            person.days_infected = 0
        
        # Progress disease in infected individuals
        for person in self.population:
            if person.state == 'I':
                person.days_infected += 1
                if person.days_infected >= self.recovery_days:
                    person.state = 'R'
    
    def run(self, days: int, verbose: bool = True) -> List[Tuple[int, int, int]]:
        """
        Run the simulation for a specified number of days.
        
        Args:
            days: Number of days to simulate
            verbose: Print daily statistics
        
        Returns:
            List of (S, I, R) counts for each day
        """
        history = []
        
        for day in range(days):
            s, i, r = self.count_states()
            history.append((s, i, r))
            
            if verbose:
                print(f"Day {day:3d}: S={s:4d} I={i:4d} R={r:4d} | "
                      f"Active: {i/len(self.population)*100:5.1f}%")
            
            # Stop early if no more infections
            if i == 0:
                if verbose:
                    print(f"\nEpidemic ended on day {day} (no active cases)")
                break
            
            self.simulate_day()
        
        return history


def calculate_r0(transmission_rate: float, contacts_per_day: int, recovery_days: int) -> float:
    """
    Calculate basic reproduction number (R0).
    
    R0 = transmission_rate * contacts_per_day * recovery_days
    This is a simplified calculation assuming fully susceptible population.
    """
    return transmission_rate * contacts_per_day * recovery_days


if __name__ == "__main__":
    print("=" * 70)
    print("SIR EPIDEMIC SIMULATION")
    print("=" * 70)
    
    # Simulation parameters - tuned to show interesting dynamics
    pop_size = 1000
    initial_cases = 5
    trans_rate = 0.05  # 5% chance per contact
    recovery = 7       # recover after 7 days
    contacts = 10      # each person contacts 10 others per day
    
    r0 = calculate_r0(trans_rate, contacts, recovery)
    print(f"\nPopulation: {pop_size}")
    print(f"Initial infections: {initial_cases}")
    print(f"Transmission rate: {trans_rate:.1%} per contact")
    print(f"Recovery period: {recovery} days")
    print(f"Contacts per day: {contacts}")
    print(f"Estimated R0: {r0:.2f}")
    print(f"\n(R0 > 1 means epidemic will likely spread)\n")
    print("-" * 70)
    
    # Create and run simulation
    sim = EpidemicSimulation(
        population_size=pop_size,
        initial_infected=initial_cases,
        transmission_rate=trans_rate,
        recovery_days=recovery,
        contacts_per_day=contacts
    )
    
    history = sim.run(days=100, verbose=True)
    
    # Summary statistics
    print("-" * 70)
    print("\nFINAL SUMMARY:")
    final_s, final_i, final_r = sim.count_states()
    attack_rate = final_r / pop_size * 100
    print(f"Total infected during epidemic: {final_r} ({attack_rate:.1f}%)")
    print(f"Never infected: {final_s} ({final_s/pop_size*100:.1f}%)")