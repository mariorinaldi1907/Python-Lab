"""
Date: 2026-08-22
Implemented a Bayesian A/B testing framework using conjugate priors to get actual probability distributions over conversion rates instead of just binary reject/accept decisions.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer

I got tired of relying on frequentist hypothesis testing for A/B experiments.
This uses Beta-Binomial conjugate priors to give you actual probability
distributions and lets you ask questions like "what's the probability
variant B is better than A?" instead of just getting a p-value.
"""

import math
import random
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution using alpha and beta parameters.
    
    Perfect for modeling conversion rates because it's bounded [0, 1]
    and works as a conjugate prior for binomial likelihood.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: Number of successes + 1 (uniform prior starts at 1)
            beta: Number of failures + 1
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update distribution with new observations.
        This is the magic of conjugate priors - just add counts.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def std(self) -> float:
        """Standard deviation."""
        return math.sqrt(self.variance())
    
    def sample(self) -> float:
        """
        Draw a random sample from this Beta distribution.
        Using the relationship between Gamma and Beta distributions.
        """
        # Beta(a, b) = Gamma(a) / (Gamma(a) + Gamma(b))
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval using sampling.
        This is the Bayesian version of a confidence interval.
        """
        samples = sorted([self.sample() for _ in range(10000)])
        lower_idx = int(len(samples) * (1 - confidence) / 2)
        upper_idx = int(len(samples) * (1 + confidence) / 2)
        return samples[lower_idx], samples[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize A/B test with prior beliefs.
        
        Args:
            prior_alpha: Prior "successes" - use 1 for uniform prior
            prior_beta: Prior "failures" - use 1 for uniform prior
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_observations(self, variant: str, successes: int, failures: int):
        """
        Add observations for a variant.
        
        Args:
            variant: 'A' or 'B'
            successes: Number of conversions
            failures: Number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, samples: int = 50000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is way more intuitive than a p-value. If this returns 0.95,
        there's a 95% probability B's true conversion rate is higher than A's.
        """
        wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(samples)
        )
        return wins / samples
    
    def expected_loss(self, choose_b: bool, samples: int = 50000) -> float:
        """
        Expected loss if we choose a particular variant.
        
        This tells you "if I pick B but A is actually better, how much
        conversion rate am I losing on average?"
        """
        losses = []
        for _ in range(samples):
            a_sample = self.variant_a.sample()
            b_sample = self.variant_b.sample()
            
            if choose_b:
                # Loss if we choose B but A is better
                loss = max(0, a_sample - b_sample)
            else:
                # Loss if we choose A but B is better
                loss = max(0, b_sample - a_sample)
            
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def summary(self) -> dict:
        """Generate a summary of the A/B test results."""
        prob_b_wins = self.probability_b_beats_a()
        
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_b_mean': self.variant_b.mean(),
            'variant_a_std': self.variant_a.std(),
            'variant_b_std': self.variant_b.std(),
            'variant_a_95ci': self.variant_a.credible_interval(),
            'variant_b_95ci': self.variant_b.credible_interval(),
            'prob_b_beats_a': prob_b_wins,
            'prob_a_beats_b': 1 - prob_b_wins,
            'expected_loss_choosing_a': self.expected_loss(choose_b=False),
            'expected_loss_choosing_b': self.expected_loss(choose_b=True),
        }


def print_test_summary(test: ABTest, variant_a_name: str = "A", variant_b_name: str = "B"):
    """Pretty print the A/B test summary."""
    summary = test.summary()
    
    print(f"\n{'='*60}")
    print(f"Bayesian A/B Test Results")
    print(f"{'='*60}\n")
    
    print(f"Variant {variant_a_name}:")
    print(f"  Mean conversion rate: {summary['variant_a_mean']:.4f}")
    print(f"  Std deviation: {summary['variant_a_std']:.4f}")
    print(f"  95% credible interval: [{summary['variant_a_95ci'][0]:.4f}, {summary['variant_a_95ci'][1]:.4f}]")
    
    print(f"\nVariant {variant_b_name}:")
    print(f"  Mean conversion rate: {summary['variant_b_mean']:.4f}")
    print(f"  Std deviation: {summary['variant_b_std']:.4f}")
    print(f"  95% credible interval: [{summary['variant_b_95ci'][0]:.4f}, {summary['variant_b_95ci'][1]:.4f}]")
    
    print(f"\nComparison:")
    print(f"  P({variant_b_name} > {variant_a_name}): {summary['prob_b_beats_a']:.2%}")
    print(f"  P({variant_a_name} > {variant_b_name}): {summary['prob_a_beats_b']:.2%}")
    
    print(f"\nExpected Loss (opportunity cost):")
    print(f"  If you choose {variant_a_name}: {summary['expected_loss_choosing_a']:.4f}")
    print(f"  If you choose {variant_b_name}: {summary['expected_loss_choosing_b']:.4f}")
    
    # Give a recommendation
    if summary['prob_b_beats_a'] > 0.95:
        print(f"\n✓ Strong evidence for {variant_b_name} (>95% probability)")
    elif summary['prob_a_beats_b'] > 0.95:
        print(f"\n✓ Strong evidence for {variant_a_name} (>95% probability)")
    else:
        print(f"\n⚠ Inconclusive - need more data or accept higher risk")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Simulate a real A/B test scenario: testing two landing page variants
    print("Simulating A/B test: Original vs New Landing Page")
    print("Scenario: We're testing a new landing page design\n")
    
    # Create test with uniform prior (no strong beliefs either way)
    test = ABTest(prior_alpha=1, prior_beta=1)
    
    # Variant A (control): 1000 visitors, 85 conversions
    # That's an 8.5% conversion rate
    test.add_observations('A', successes=85, failures=915)
    print("Control page: 85 conversions out of 1000 visitors")