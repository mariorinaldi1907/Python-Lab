"""
Date: 2026-07-12
Implemented a Bayesian A/B test framework with Beta-Bernoulli conjugate priors so I can actually tell if my UI tweaks are real improvements or just noise.
"""

#!/usr/bin/env env python3
"""
Bayesian A/B Test Analyzer
Mario's personal stats toolkit for analyzing conversion rates.

Uses Beta-Bernoulli conjugate priors to compute posterior distributions
and probability of one variant beating another. Way cleaner than frequentist
p-values when you have small sample sizes.
"""

import random
from math import gamma, log, exp


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian analysis of conversion rates.
    
    The Beta distribution is conjugate to the Bernoulli, which means updating
    is just adding counts. Super elegant.
    """
    
    def __init__(self, alpha=1.0, beta=1.0):
        """
        Initialize with prior parameters.
        
        alpha, beta = 1, 1 gives uniform prior (no assumptions).
        Higher values = stronger prior beliefs.
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """Update the distribution with new observations."""
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self):
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def mode(self):
        """Most likely value (only defined when alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return None
    
    def sample(self, n=1):
        """
        Draw random samples from the Beta distribution.
        
        Uses the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta). Standard library has gamma sampler.
        """
        samples = []
        for _ in range(n):
            x = random.gammavariate(self.alpha, 1)
            y = random.gammavariate(self.beta, 1)
            samples.append(x / (x + y))
        return samples if n > 1 else samples[0]
    
    def credible_interval(self, confidence=0.95, samples=10000):
        """
        Compute credible interval via sampling.
        
        This is the Bayesian equivalent of a confidence interval.
        It actually means what people think CI means.
        """
        data = sorted(self.sample(samples))
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        return (data[lower_idx], data[upper_idx])


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    I prefer this to t-tests because it gives me a direct answer:
    "What's the probability that B is better than A?"
    """
    
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        """Initialize with uniform priors for both variants."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_observations(self, variant, successes, failures):
        """Add conversion data for a variant ('A' or 'B')."""
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, samples=10000):
        """
        Monte Carlo estimate of P(B > A).
        
        This is what I actually care about: how confident am I that B is better?
        """
        a_samples = self.variant_a.sample(samples)
        b_samples = self.variant_b.sample(samples)
        
        wins = sum(1 for a, b in zip(a_samples, b_samples) if b > a)
        return wins / samples
    
    def expected_loss(self, samples=10000):
        """
        Expected loss if we pick the wrong variant.
        
        Useful for deciding when to stop the test. If expected loss is tiny,
        who cares which one wins?
        """
        a_samples = self.variant_a.sample(samples)
        b_samples = self.variant_b.sample(samples)
        
        loss_if_pick_a = sum(max(0, b - a) for a, b in zip(a_samples, b_samples)) / samples
        loss_if_pick_b = sum(max(0, a - b) for a, b in zip(a_samples, b_samples)) / samples
        
        return {'pick_a': loss_if_pick_a, 'pick_b': loss_if_pick_b}
    
    def summary(self):
        """Print a human-readable summary of the test results."""
        print("=== A/B Test Summary ===\n")
        
        print(f"Variant A:")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        print(f"  95% Credible Interval: {self.variant_a.credible_interval()}")
        print()
        
        print(f"Variant B:")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        print(f"  95% Credible Interval: {self.variant_b.credible_interval()}")
        print()
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"Probability B > A: {prob_b_wins:.2%}")
        print(f"Probability A > B: {(1 - prob_b_wins):.2%}")
        print()
        
        loss = self.expected_loss()
        print(f"Expected loss if we pick A: {loss['pick_a']:.6f}")
        print(f"Expected loss if we pick B: {loss['pick_b']:.6f}")
        print()
        
        # Decision logic I use in practice
        if prob_b_wins > 0.95:
            print("✓ Strong evidence for B. Ship it!")
        elif prob_b_wins < 0.05:
            print("✓ Strong evidence for A. Keep the original.")
        else:
            print("⚠ Inconclusive. Need more data or the difference doesn't matter.")


if __name__ == "__main__":
    print("Simulating an A/B test on button color conversion rates...\n")
    
    # Real-world scenario: testing a new button color
    # Control (A): blue button, 120 clicks out of 1000 visitors
    # Treatment (B): green button, 145 clicks out of 1000 visitors
    
    test = ABTest(prior_alpha=1, prior_beta=1)  # Uniform prior
    
    # Add the actual observed data
    test.add_observations('A', successes=120, failures=880)
    test.add_observations('B', successes=145, failures=855)
    
    test.summary()
    
    print("\n" + "="*50)
    print("Demo: What if we had less data?")
    print("="*50 + "\n")
    
    # Same proportions but 10x less traffic
    small_test = ABTest()
    small_test.add_observations('A', successes=12, failures=88)
    small_test.add_observations('B', successes=14, failures=86)
    
    small_test.summary()