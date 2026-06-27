"""
Date: 2026-06-27
Implemented a Bayesian A/B testing framework using beta distributions to compare conversion rates and calculate probability of superiority.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
Uses conjugate Beta-Binomial model for conversion rate comparison.
Way more intuitive than p-values — gives you actual probabilities.
"""

import random
from math import gamma, lgamma
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference.
    Perfect for modeling conversion rates (success/failure outcomes).
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with prior parameters.
        alpha=1, beta=1 gives uniform prior (no assumptions).
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """Update the distribution with observed data (conjugate update)."""
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self) -> float:
        """Most likely value (only defined when alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()
    
    def variance(self) -> float:
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self, n: int = 1) -> List[float]:
        """
        Draw samples using gamma distribution trick.
        Beta(a,b) = Gamma(a) / (Gamma(a) + Gamma(b))
        """
        samples = []
        for _ in range(n):
            x = random.gammavariate(self.alpha, 1)
            y = random.gammavariate(self.beta, 1)
            samples.append(x / (x + y))
        return samples
    
    def pdf(self, x: float) -> float:
        """
        Probability density function at x.
        Using log-gamma for numerical stability.
        """
        if x <= 0 or x >= 1:
            return 0.0
        
        log_beta_function = lgamma(self.alpha) + lgamma(self.beta) - lgamma(self.alpha + self.beta)
        log_pdf = (self.alpha - 1) * (x if x == 0 else lgamma(x)) + \
                  (self.beta - 1) * (1 - x if x == 1 else lgamma(1 - x)) - log_beta_function
        
        # Actually, let me do this properly without logs on x
        return ((x ** (self.alpha - 1)) * ((1 - x) ** (self.beta - 1))) / \
               (gamma(self.alpha) * gamma(self.beta) / gamma(self.alpha + self.beta))


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    No need for power calculations or stopping rules.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """Initialize with priors for both variants."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant: str, successes: int, trials: int):
        """Add observed data for a variant."""
        failures = trials - successes
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, n_samples: int = 10000) -> float:
        """
        Monte Carlo estimation: P(B > A)
        Sample from both posteriors and count how often B wins.
        """
        samples_a = self.variant_a.sample(n_samples)
        samples_b = self.variant_b.sample(n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def expected_loss(self, n_samples: int = 10000) -> Tuple[float, float]:
        """
        Expected loss if we choose the wrong variant.
        Returns (loss_if_choose_a, loss_if_choose_b)
        """
        samples_a = self.variant_a.sample(n_samples)
        samples_b = self.variant_b.sample(n_samples)
        
        # If we pick A but B is better
        loss_a = sum(max(0, b - a) for a, b in zip(samples_a, samples_b)) / n_samples
        # If we pick B but A is better
        loss_b = sum(max(0, a - b) for a, b in zip(samples_a, samples_b)) / n_samples
        
        return loss_a, loss_b
    
    def summary(self):
        """Print a nice summary of the test results."""
        print("=" * 60)
        print("BAYESIAN A/B TEST RESULTS")
        print("=" * 60)
        print(f"\nVariant A:")
        print(f"  Posterior: Beta({self.variant_a.alpha:.1f}, {self.variant_a.beta:.1f})")
        print(f"  Expected conversion rate: {self.variant_a.mean():.4f}")
        print(f"  95% credible std: ±{1.96 * (self.variant_a.variance() ** 0.5):.4f}")
        
        print(f"\nVariant B:")
        print(f"  Posterior: Beta({self.variant_b.alpha:.1f}, {self.variant_b.beta:.1f})")
        print(f"  Expected conversion rate: {self.variant_b.mean():.4f}")
        print(f"  95% credible std: ±{1.96 * (self.variant_b.variance() ** 0.5):.4f}")
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"\nP(B > A) = {prob_b_wins:.4f}")
        print(f"P(A > B) = {1 - prob_b_wins:.4f}")
        
        loss_a, loss_b = self.expected_loss()
        print(f"\nExpected loss:")
        print(f"  If we choose A: {loss_a:.6f}")
        print(f"  If we choose B: {loss_b:.6f}")
        
        # Decision recommendation
        if prob_b_wins > 0.95 and loss_b < 0.001:
            print("\n✓ Strong evidence for B. Ship it!")
        elif prob_b_wins < 0.05 and loss_a < 0.001:
            print("\n✓ Strong evidence for A. Stick with it!")
        else:
            print("\n⚠ Not enough evidence yet. Keep testing or go with prior beliefs.")
        print("=" * 60)


if __name__ == "__main__":
    random.seed(42)  # Reproducible results
    
    print("Simulating an A/B test for a landing page redesign...\n")
    
    # Initialize test with uniform prior (no assumptions)
    test = ABTest(prior_alpha=1, prior_beta=1)
    
    # Old design (A): 100 conversions out of 1000 visitors
    test.add_data('A', successes=100, trials=1000)
    
    # New design (B): 125 conversions out of 1000 visitors  
    test.add_data('B', successes=125, trials=1000)
    
    test.summary()
    
    print("\n\nNow let's see what happens with more data...\n")
    
    # Add more observations (B continues to perform better)
    test.add_data('A', successes=50, trials=500)
    test.add_data('B', successes=70, trials=500)
    
    test.summary()
```