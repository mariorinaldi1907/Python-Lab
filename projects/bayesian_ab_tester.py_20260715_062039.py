"""
Date: 2026-07-15
Created a Bayesian A/B testing module that updates beliefs in real-time and actually tells you the probability one variant is better — way more intuitive than p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

I built this because traditional frequentist A/B tests make you wait forever
for significance, and honestly the results are harder to interpret. With Bayesian
methods, you get a direct "probability that B beats A" which is what everyone
actually wants to know anyway.

Uses Beta distributions for conversion rates (clicks, signups, etc.) because
they're conjugate priors for binomial data — math just works out cleanly.
"""

import random
import math
from typing import Tuple, List


class BayesianABTest:
    """
    Tracks two variants (A and B) and computes probability that B > A.
    
    Uses Beta distribution because it's the conjugate prior for binomial data.
    Starting with Beta(1,1) is a uniform prior — no assumptions about conversion rate.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs.
        
        Args:
            alpha_prior: successes + alpha forms the Beta distribution
            beta_prior: failures + beta forms the Beta distribution
        
        Default (1,1) is uniform — equally likely to see any conversion rate.
        """
        self.variants = {
            'A': {'successes': 0, 'failures': 0, 'alpha': alpha_prior, 'beta': beta_prior},
            'B': {'successes': 0, 'failures': 0, 'alpha': alpha_prior, 'beta': beta_prior}
        }
    
    def add_observation(self, variant: str, success: bool):
        """
        Record a single observation (e.g., user clicked or didn't click).
        
        Args:
            variant: 'A' or 'B'
            success: True if conversion happened, False otherwise
        """
        if variant not in self.variants:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
        
        if success:
            self.variants[variant]['successes'] += 1
        else:
            self.variants[variant]['failures'] += 1
    
    def add_batch(self, variant: str, successes: int, failures: int):
        """Add multiple observations at once — useful for importing existing data."""
        if variant not in self.variants:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
        
        self.variants[variant]['successes'] += successes
        self.variants[variant]['failures'] += failures
    
    def get_posterior_params(self, variant: str) -> Tuple[float, float]:
        """
        Get the posterior Beta distribution parameters for a variant.
        
        Posterior is just prior + observed data because Beta is conjugate.
        """
        v = self.variants[variant]
        alpha_post = v['alpha'] + v['successes']
        beta_post = v['beta'] + v['failures']
        return alpha_post, beta_post
    
    def sample_posterior(self, variant: str, n_samples: int = 10000) -> List[float]:
        """
        Draw samples from the posterior distribution.
        
        Using random.betavariate from standard library — no numpy needed.
        """
        alpha, beta = self.get_posterior_params(variant)
        return [random.betavariate(alpha, beta) for _ in range(n_samples)]
    
    def probability_b_beats_a(self, n_samples: int = 10000) -> float:
        """
        Monte Carlo estimate: what's P(B > A)?
        
        This is the key insight of Bayesian A/B testing — you get a direct
        probability statement instead of a confusing p-value.
        """
        samples_a = self.sample_posterior('A', n_samples)
        samples_b = self.sample_posterior('B', n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def expected_loss(self, variant: str, n_samples: int = 10000) -> float:
        """
        Expected loss if we choose this variant but the other is actually better.
        
        This helps with decision-making: if expected loss is tiny, just pick a winner.
        """
        samples_a = self.sample_posterior('A', n_samples)
        samples_b = self.sample_posterior('B', n_samples)
        
        if variant == 'A':
            # If we pick A, loss is max(0, B - A) when B is better
            losses = [max(0, b - a) for a, b in zip(samples_a, samples_b)]
        else:
            losses = [max(0, a - b) for a, b in zip(samples_a, samples_b)]
        
        return sum(losses) / len(losses)
    
    def get_summary(self) -> dict:
        """Get a human-readable summary of the test state."""
        summary = {}
        
        for variant in ['A', 'B']:
            v = self.variants[variant]
            total = v['successes'] + v['failures']
            observed_rate = v['successes'] / total if total > 0 else 0
            alpha, beta = self.get_posterior_params(variant)
            # Mean of Beta(alpha, beta) is alpha / (alpha + beta)
            posterior_mean = alpha / (alpha + beta)
            
            summary[variant] = {
                'observations': total,
                'successes': v['successes'],
                'observed_rate': observed_rate,
                'posterior_mean': posterior_mean
            }
        
        summary['prob_b_beats_a'] = self.probability_b_beats_a()
        summary['expected_loss_a'] = self.expected_loss('A')
        summary['expected_loss_b'] = self.expected_loss('B')
        
        return summary


def simulate_ab_test(true_rate_a: float, true_rate_b: float, n_per_variant: int):
    """
    Simulate an A/B test with known true rates to validate the module.
    
    In real life we don't know the true rates, but for testing the code
    it's useful to simulate and see if our estimates converge to truth.
    """
    test = BayesianABTest()
    
    # Simulate observations
    for _ in range(n_per_variant):
        success_a = random.random() < true_rate_a
        success_b = random.random() < true_rate_b
        test.add_observation('A', success_a)
        test.add_observation('B', success_b)
    
    return test


if __name__ == "__main__":
    print("=== Bayesian A/B Test Demo ===\n")
    
    # Scenario: testing two landing page designs
    # A has 10% conversion, B has 12% (B is actually better)
    print("Simulating landing page test:")
    print("  Variant A: 10% true conversion rate")
    print("  Variant B: 12% true conversion rate")
    print("  1000 visitors per variant\n")
    
    test = simulate_ab_test(true_rate_a=0.10, true_rate_b=0.12, n_per_variant=1000)
    summary = test.get_summary()
    
    print("Results:")
    print(f"  A: {summary['A']['successes']}/{summary['A']['observations']} conversions " +
          f"({summary['A']['observed_rate']:.1%} observed, {summary['A']['posterior_mean']:.1%} posterior mean)")
    print(f"  B: {summary['B']['successes']}/{summary['B']['observations']} conversions " +
          f"({summary['B']['observed_rate']:.1%} observed, {summary['B']['posterior_mean']:.1%} posterior mean)")
    
    print(f"\nProbability that B beats A: {summary['prob_b_beats_a']:.1%}")
    print(f"Expected loss if we choose A: {summary['expected_loss_a']:.4f}")
    print(f"Expected loss if we choose B: {summary['expected_loss_b']:.4f}")
    
    # Decision rule I usually use: if prob > 95% and expected loss < 0.001, pick winner
    if summary['prob_b_beats_a'] > 0.95 and summary['expected_loss_b'] < 0.001:
        print("\n✓ Decision: Choose B (high confidence, low risk)")
    elif summary['prob_b_beats_a'] < 0.05 and summary['expected_loss_a'] < 0.001:
        print("\n✓ Decision: Choose A (high confidence, low risk)")
    else:
        print("\n⚠ Decision: Keep testing (not enough evidence yet)")
    
    print("\n---\n")
    print("Note: With only 2% true difference, we might need more data")
    print("for really high confidence. But we can make decisions earlier")
    print("than with classical tests, and the interpretation is clearer.")