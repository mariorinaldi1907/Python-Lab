"""
Date: 2026-07-12
Created a Bayesian A/B testing tool that updates beliefs in real-time and tells you the probability that variant B beats A — way more intuitive than p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

I got frustrated with traditional frequentist A/B testing where you have to wait
for some arbitrary sample size. This uses Bayesian inference with Beta distributions
to give you real-time probabilities about which variant is winning.
"""

import random
from math import lgamma, exp


class BetaDistribution:
    """
    Represents a Beta distribution for conversion rates.
    
    Using Beta(alpha, beta) because it's the conjugate prior for binomial data,
    which makes the math clean. Alpha represents successes + 1, beta represents
    failures + 1 (using uniform prior).
    """
    
    def __init__(self, alpha=1, beta=1):
        """Initialize with prior parameters (default is uniform prior)."""
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """Update the distribution with observed data."""
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the conversion rate."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self):
        """Variance of the conversion rate."""
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))
    
    def sample(self):
        """
        Draw a random sample from this Beta distribution.
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta)
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, samples=10000, confidence=0.95):
        """
        Compute credible interval using sampling.
        This is the Bayesian equivalent of a confidence interval.
        """
        draws = sorted([self.sample() for _ in range(samples)])
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        return draws[lower_idx], draws[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    This tracks two variants and can tell you the probability that B beats A
    at any point during the test.
    """
    
    def __init__(self, prior_alpha=1, prior_beta=1):
        """Initialize with two variants using the same prior."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_observation(self, variant, success):
        """
        Add a single observation to a variant.
        
        Args:
            variant: 'A' or 'B'
            success: True if conversion, False otherwise
        """
        if variant.upper() == 'A':
            if success:
                self.variant_a.update(1, 0)
            else:
                self.variant_a.update(0, 1)
        elif variant.upper() == 'B':
            if success:
                self.variant_b.update(1, 0)
            else:
                self.variant_b.update(0, 1)
        else:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
    
    def add_batch(self, variant, successes, failures):
        """Add multiple observations at once."""
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
    
    def probability_b_beats_a(self, simulations=10000):
        """
        Calculate P(B > A) using Monte Carlo simulation.
        
        This is the key metric - it directly answers "what's the probability
        that variant B has a higher conversion rate than A?"
        """
        b_wins = 0
        for _ in range(simulations):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        return b_wins / simulations
    
    def expected_loss(self, simulations=10000):
        """
        Calculate expected loss if we choose the wrong variant.
        
        Returns (loss_if_choose_a, loss_if_choose_b) as a tuple.
        Loss is measured in conversion rate points.
        """
        loss_a = 0
        loss_b = 0
        
        for _ in range(simulations):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            # Loss if we choose A but B is better
            if sample_b > sample_a:
                loss_a += sample_b - sample_a
            # Loss if we choose B but A is better
            else:
                loss_b += sample_a - sample_b
        
        return loss_a / simulations, loss_b / simulations
    
    def summary(self):
        """Print a human-readable summary of the current state."""
        print(f"Variant A: {self.variant_a.alpha - 1} successes, {self.variant_a.beta - 1} failures")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        a_lower, a_upper = self.variant_a.credible_interval()
        print(f"  95% credible interval: [{a_lower:.4f}, {a_upper:.4f}]")
        
        print(f"\nVariant B: {self.variant_b.alpha - 1} successes, {self.variant_b.beta - 1} failures")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        b_lower, b_upper = self.variant_b.credible_interval()
        print(f"  95% credible interval: [{b_lower:.4f}, {b_upper:.4f}]")
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"\nP(B > A): {prob_b_wins:.4f}")
        
        loss_a, loss_b = self.expected_loss()
        print(f"\nExpected loss if choosing A: {loss_a:.6f}")
        print(f"Expected loss if choosing B: {loss_b:.6f}")
        
        # Give a recommendation
        if prob_b_wins > 0.95:
            print("\n✓ Strong evidence for B")
        elif prob_b_wins < 0.05:
            print("\n✓ Strong evidence for A")
        else:
            print("\n→ Keep testing, no clear winner yet")


if __name__ == "__main__":
    print("=== Bayesian A/B Test Demo ===\n")
    
    # Simulating a real A/B test scenario
    # Let's say we're testing two button colors on a landing page
    print("Scenario: Testing button colors (A=blue, B=red) on a landing page\n")
    
    test = ABTest()
    
    # Simulate data coming in over time
    # True conversion rates: A=0.10, B=0.12 (B is actually better)
    random.seed(42)
    
    print("--- After 100 visitors per variant ---")
    # Generate realistic data
    for _ in range(100):
        test.add_observation('A', random.random() < 0.10)
        test.add_observation('B', random.random() < 0.12)
    
    test.summary()
    
    print("\n" + "="*50 + "\n")
    print("--- After 500 visitors per variant ---")
    for _ in range(400):
        test.add_observation('A', random.random() < 0.10)
        test.add_observation('B', random.random() < 0.12)
    
    test.summary()
    
    print("\n" + "="*50 + "\n")
    print("--- After 1000 visitors per variant ---")
    for _ in range(500):
        test.add_observation('A', random.random() < 0.10)
        test.add_observation('B', random.random() < 0.12)
    
    test.summary()