"""
Date: 2026-06-06
Created a Bayesian A/B testing module that uses conjugate priors (Beta-Binomial) to compute posterior distributions and probabilities of superiority — way more intuitive than traditional hypothesis testing.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module
Uses Beta-Binomial conjugate priors to analyze conversion rates between two variants.
This approach gives you actual probabilities instead of confusing p-values.
"""

import random
from math import gamma, lgamma
from typing import Tuple, List


class BetaPrior:
    """
    Represents a Beta distribution, the conjugate prior for binomial likelihood.
    Beta(alpha, beta) where alpha and beta are shape parameters.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta prior.
        Default alpha=1, beta=1 gives uniform prior (no initial belief).
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int) -> 'BetaPrior':
        """
        Bayesian update: new_alpha = alpha + successes, new_beta = beta + failures.
        Returns a new BetaPrior with updated parameters.
        """
        return BetaPrior(self.alpha + successes, self.beta + failures)
    
    def mean(self) -> float:
        """Expected value of the Beta distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self) -> float:
        """Mode of the Beta distribution (most likely value)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()  # Fall back to mean for edge cases
    
    def variance(self) -> float:
        """Variance of the Beta distribution."""
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b ** 2 * (a_plus_b + 1))
    
    def sample(self, n: int = 1) -> List[float]:
        """
        Draw random samples from the Beta distribution.
        Uses the fact that if X~Gamma(alpha) and Y~Gamma(beta), then X/(X+Y)~Beta(alpha,beta).
        """
        samples = []
        for _ in range(n):
            x = random.gammavariate(self.alpha, 1)
            y = random.gammavariate(self.beta, 1)
            samples.append(x / (x + y))
        return samples


class ABTest:
    """
    Bayesian A/B test analyzer comparing two conversion rates.
    Uses Monte Carlo sampling from posterior distributions.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with prior beliefs (default is uniform/non-informative).
        """
        self.prior = BetaPrior(prior_alpha, prior_beta)
        self.variant_a = None
        self.variant_b = None
    
    def set_data(self, a_successes: int, a_trials: int, b_successes: int, b_trials: int):
        """
        Feed in observed data for both variants.
        """
        a_failures = a_trials - a_successes
        b_failures = b_trials - b_successes
        
        # Update priors with observed data to get posteriors
        self.variant_a = self.prior.update(a_successes, a_failures)
        self.variant_b = self.prior.update(b_successes, b_failures)
    
    def probability_b_beats_a(self, samples: int = 100000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        This is the probability that variant B has a higher conversion rate than A.
        """
        if self.variant_a is None or self.variant_b is None:
            raise ValueError("Must call set_data() first")
        
        # Draw samples from both posterior distributions
        a_samples = self.variant_a.sample(samples)
        b_samples = self.variant_b.sample(samples)
        
        # Count how often B beats A
        b_wins = sum(1 for a, b in zip(a_samples, b_samples) if b > a)
        return b_wins / samples
    
    def expected_loss(self, samples: int = 100000) -> Tuple[float, float]:
        """
        Calculate expected loss if we choose the wrong variant.
        Returns (loss_if_choose_a, loss_if_choose_b).
        
        Expected loss = average amount we'd lose by choosing the wrong one.
        """
        if self.variant_a is None or self.variant_b is None:
            raise ValueError("Must call set_data() first")
        
        a_samples = self.variant_a.sample(samples)
        b_samples = self.variant_b.sample(samples)
        
        # Loss if we pick A but B is better
        loss_a = sum(max(0, b - a) for a, b in zip(a_samples, b_samples)) / samples
        
        # Loss if we pick B but A is better
        loss_b = sum(max(0, a - b) for a, b in zip(a_samples, b_samples)) / samples
        
        return loss_a, loss_b
    
    def get_summary(self) -> dict:
        """
        Return a summary dictionary with all key metrics.
        """
        if self.variant_a is None or self.variant_b is None:
            raise ValueError("Must call set_data() first")
        
        prob_b_wins = self.probability_b_beats_a()
        loss_a, loss_b = self.expected_loss()
        
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_a_mode': self.variant_a.mode(),
            'variant_b_mean': self.variant_b.mean(),
            'variant_b_mode': self.variant_b.mode(),
            'prob_b_beats_a': prob_b_wins,
            'prob_a_beats_b': 1 - prob_b_wins,
            'expected_loss_if_choose_a': loss_a,
            'expected_loss_if_choose_b': loss_b,
        }


if __name__ == "__main__":
    print("=== Bayesian A/B Test Analyzer ===\n")
    
    # Simulate a realistic scenario: testing two landing page designs
    print("Scenario: Testing two landing page variants")
    print("-" * 50)
    
    # Variant A: Control (current design)
    a_visitors = 1000
    a_conversions = 47  # 4.7% conversion rate
    
    # Variant B: New design
    b_visitors = 1000
    b_conversions = 58  # 5.8% conversion rate
    
    print(f"Variant A: {a_conversions}/{a_visitors} conversions ({100*a_conversions/a_visitors:.2f}%)")
    print(f"Variant B: {b_conversions}/{b_visitors} conversions ({100*b_conversions/b_visitors:.2f}%)")
    print()
    
    # Run the Bayesian analysis
    test = ABTest()
    test.set_data(a_conversions, a_visitors, b_conversions, b_visitors)
    
    summary = test.get_summary()
    
    print("Posterior Estimates:")
    print(f"  Variant A conversion rate: {100*summary['variant_a_mean']:.3f}%")
    print(f"  Variant B conversion rate: {100*summary['variant_b_mean']:.3f}%")
    print()
    
    print("Decision Metrics:")
    print(f"  P(B > A) = {100*summary['prob_b_beats_a']:.2f}%")
    print(f"  P(A > B) = {100*summary['prob_a_beats_b']:.2f}%")
    print()
    
    print("Expected Loss (opportunity cost):")
    print(f"  If we choose A: {100*summary['expected_loss_if_choose_a']:.4f}% lost conversions")
    print(f"  If we choose B: {100*summary['expected_loss_if_choose_b']:.4f}% lost conversions")
    print()
    
    # Make a recommendation
    if summary['prob_b_beats_a'] > 0.95:
        print("✓ RECOMMENDATION: Switch to Variant B (>95% probability it's better)")
    elif summary['prob_b_beats_a'] < 0.05:
        print("✓ RECOMMENDATION: Keep Variant A (>95% probability it's better)")
    else:
        print("⚠ RECOMMENDATION: Inconclusive — collect more data")
        print(f"  (Only {100*max(summary['prob_b_beats_a'], summary['prob_a_beats_b']):.1f}% confident)")