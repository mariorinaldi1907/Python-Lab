"""
Date: 2026-06-26
Implemented a Bayesian A/B testing framework with Beta distributions to get actual probabilities instead of cryptic p-values when comparing conversion rates.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Framework

I built this because traditional frequentist A/B tests with p-values never felt
intuitive to me. With Bayesian analysis, I can actually say "there's an 87% 
chance variant B is better" instead of "we reject the null hypothesis at p<0.05".

This uses Beta distributions as priors/posteriors for conversion rates, which is
the conjugate prior for binomial data (success/failure outcomes).
"""

import random
from math import gamma, log


class BetaDistribution:
    """
    Represents a Beta distribution for modeling conversion rates.
    
    The Beta distribution is perfect for this because:
    - It's bounded between 0 and 1 (like probabilities)
    - It's the conjugate prior for binomial data
    - Updating is just adding counts (super clean math)
    """
    
    def __init__(self, alpha=1, beta=1):
        """
        Initialize Beta distribution with shape parameters.
        
        alpha=1, beta=1 gives uniform prior (no assumptions).
        Higher alpha = more successes observed
        Higher beta = more failures observed
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """Update the distribution with new data (this is Bayesian updating)."""
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self):
        """Most likely value (only defined when alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()
    
    def variance(self):
        """Variance of the distribution."""
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))
    
    def sample(self):
        """
        Draw a random sample from this Beta distribution.
        
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta). Python's random.gammavariate
        makes this easy.
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, samples=10000, confidence=0.95):
        """
        Compute credible interval using sampling.
        
        This is the Bayesian version of a confidence interval - there's a
        95% probability the true value is in this range (much more intuitive
        than the frequentist interpretation).
        """
        sample_values = sorted([self.sample() for _ in range(samples)])
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        return sample_values[lower_idx], sample_values[upper_idx]


class ABTest:
    """
    A/B test analyzer using Bayesian methods.
    
    This lets me compare two variants and get actual probabilities about
    which one is better, instead of just rejecting/not rejecting hypotheses.
    """
    
    def __init__(self, prior_alpha=1, prior_beta=1):
        """
        Initialize A/B test with priors for both variants.
        
        Using uniform priors (alpha=1, beta=1) by default because I usually
        don't have strong prior beliefs about conversion rates.
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant, successes, failures):
        """Add observed data for a variant."""
        if variant.lower() == 'a':
            self.variant_a.update(successes, failures)
        elif variant.lower() == 'b':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'a' or 'b'")
    
    def probability_b_better(self, samples=10000):
        """
        Calculate probability that B has higher conversion rate than A.
        
        This is the key metric I care about - a direct answer to
        "what's the chance B is actually better?"
        """
        b_better_count = 0
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_better_count += 1
        
        return b_better_count / samples
    
    def expected_lift(self, samples=10000):
        """
        Expected percentage lift of B over A.
        
        This tells me not just IF B is better, but by HOW MUCH on average.
        """
        lifts = []
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_a > 0:  # Avoid division by zero
                lift = (sample_b - sample_a) / sample_a
                lifts.append(lift)
        
        return sum(lifts) / len(lifts) if lifts else 0
    
    def summary(self):
        """Print a nice summary of the A/B test results."""
        print("=" * 60)
        print("A/B TEST RESULTS (Bayesian Analysis)")
        print("=" * 60)
        print(f"\nVariant A:")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        print(f"  95% credible interval: {self.variant_a.credible_interval()}")
        
        print(f"\nVariant B:")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        print(f"  95% credible interval: {self.variant_b.credible_interval()}")
        
        prob_b_better = self.probability_b_better()
        lift = self.expected_lift()
        
        print(f"\nComparison:")
        print(f"  P(B > A) = {prob_b_better:.2%}")
        print(f"  Expected lift: {lift:+.2%}")
        
        # My rule of thumb: need >90% probability to consider it meaningful
        if prob_b_better > 0.90:
            print(f"\n✓ Strong evidence that B is better!")
        elif prob_b_better < 0.10:
            print(f"\n✗ Strong evidence that A is better!")
        else:
            print(f"\n~ Results are inconclusive, need more data.")
        
        print("=" * 60)


if __name__ == "__main__":
    # Demo with a realistic scenario: testing two landing page designs
    print("Testing two landing page variants...\n")
    
    test = ABTest()
    
    # Variant A (control): 120 conversions out of 1000 visitors
    test.add_data('a', successes=120, failures=880)
    
    # Variant B (new design): 145 conversions out of 1000 visitors
    test.add_data('b', successes=145, failures=855)
    
    test.summary()
    
    print("\n" + "=" * 60)
    print("SMALL SAMPLE TEST (to show uncertainty)")
    print("=" * 60)
    
    # What if we only had 100 visitors per variant?
    small_test = ABTest()
    small_test.add_data('a', successes=12, failures=88)
    small_test.add_data('b', successes=15, failures=85)
    
    small_test.summary()