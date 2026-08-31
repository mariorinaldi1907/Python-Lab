"""
Date: 2026-08-31
Created a Bayesian A/B testing tool that uses beta distributions to calculate probabilities and credible intervals — much more intuitive than traditional hypothesis testing.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer

I got tired of dealing with p-values and frequentist stats for A/B tests,
so I built this Bayesian approach using conjugate priors. The beta distribution
is perfect for conversion rate analysis since it's the conjugate prior for
the binomial likelihood. This gives us actual probability statements like
"there's a 95% chance variant B is better" instead of confusing p-values.
"""

import random
from math import gamma, log, exp


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on conversion rates.
    
    The Beta(alpha, beta) distribution is perfect for modeling probabilities.
    We start with a prior (usually uniform: Beta(1,1)) and update it with data.
    """
    
    def __init__(self, alpha=1.0, beta=1.0):
        """Initialize with prior parameters. Beta(1,1) is uniform over [0,1]."""
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """
        Update the distribution with observed data.
        
        This is the beautiful part of conjugate priors: we just add counts.
        Successes increment alpha, failures increment beta.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self):
        """Most likely value (only defined when alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()  # fallback to mean
    
    def variance(self):
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self):
        """
        Draw a random sample using the ratio of two gamma variates.
        
        This is a standard trick: if X ~ Gamma(alpha, 1) and Y ~ Gamma(beta, 1),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence=0.95):
        """
        Compute credible interval using quantile approximation.
        
        I'm using a simple sampling approach here. For production you'd want
        to use the inverse CDF, but this is good enough for most cases.
        """
        samples = sorted([self.sample() for _ in range(10000)])
        lower_idx = int(len(samples) * (1 - confidence) / 2)
        upper_idx = int(len(samples) * (1 + confidence) / 2)
        return samples[lower_idx], samples[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two variants.
    
    Much cleaner than frequentist testing — we get direct probability
    statements about which variant is better.
    """
    
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        """Initialize with priors for both variants."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def update_a(self, successes, failures):
        """Update variant A with conversion data."""
        self.variant_a.update(successes, failures)
    
    def update_b(self, successes, failures):
        """Update variant B with conversion data."""
        self.variant_b.update(successes, failures)
    
    def probability_b_beats_a(self, num_samples=50000):
        """
        Calculate P(B > A) using Monte Carlo simulation.
        
        We draw samples from both distributions and count how often B wins.
        This is the intuitive metric people actually care about.
        """
        b_wins = sum(1 for _ in range(num_samples) 
                     if self.variant_b.sample() > self.variant_a.sample())
        return b_wins / num_samples
    
    def expected_loss(self, num_samples=50000):
        """
        Calculate expected loss if we choose the wrong variant.
        
        This tells us: "If we pick A but B is actually better, how much
        conversion rate are we losing on average?" Useful for risk assessment.
        """
        losses_if_choose_a = []
        losses_if_choose_b = []
        
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            # Loss if we choose A when B is better
            losses_if_choose_a.append(max(0, sample_b - sample_a))
            # Loss if we choose B when A is better
            losses_if_choose_b.append(max(0, sample_a - sample_b))
        
        return {
            'choose_a': sum(losses_if_choose_a) / num_samples,
            'choose_b': sum(losses_if_choose_b) / num_samples
        }
    
    def summary(self):
        """Print a human-readable summary of the test results."""
        print("=== Bayesian A/B Test Results ===\n")
        
        print(f"Variant A:")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        ci_a = self.variant_a.credible_interval()
        print(f"  95% Credible Interval: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
        
        print(f"\nVariant B:")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        ci_b = self.variant_b.credible_interval()
        print(f"  95% Credible Interval: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"\nP(B > A) = {prob_b_wins:.4f}")
        print(f"P(A > B) = {1 - prob_b_wins:.4f}")
        
        losses = self.expected_loss()
        print(f"\nExpected loss if choosing A: {losses['choose_a']:.6f}")
        print(f"Expected loss if choosing B: {losses['choose_b']:.6f}")
        
        # Decision recommendation
        if prob_b_wins > 0.95:
            print("\n✓ Strong evidence for B. Safe to ship.")
        elif prob_b_wins > 0.90:
            print("\n→ Good evidence for B. Probably safe to ship.")
        elif prob_b_wins < 0.10:
            print("\n✓ Strong evidence for A. Stick with control.")
        elif prob_b_wins < 0.05:
            print("\n→ Good evidence for A. Probably stick with control.")
        else:
            print("\n⚠ Inconclusive. Need more data or accept the risk.")


if __name__ == "__main__":
    # Simulating a real A/B test from one of my side projects
    # Variant A (control): 1200 visitors, 84 conversions
    # Variant B (new design): 1150 visitors, 98 conversions
    
    print("Running Bayesian A/B test analysis...\n")
    
    # Using a weakly informative prior (Beta(2,20)) 
    # This encodes our belief that conversion rates are typically low (< 10%)
    # but we're open to the data changing our mind
    test = ABTest(prior_alpha=2.0, prior_beta=20.0)
    
    # Update with actual data
    test.update_a(successes=84, failures=1200-84)
    test.update_b(successes=98, failures=1150-98)
    
    # Show results
    test.summary()
    
    print("\n" + "="*40)
    print("Why I prefer this over frequentist tests:")
    print("- Direct probability statements (not confusing p-values)")
    print("- Incorporates prior knowledge naturally")
    print("- Can stop testing whenever we want (no peeking problem)")
    print("- Expected loss helps with business decisions")