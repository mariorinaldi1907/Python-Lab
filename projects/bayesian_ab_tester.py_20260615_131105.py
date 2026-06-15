"""
Date: 2026-06-15
Created a Bayesian A/B testing module that uses beta distributions to compare conversion rates and compute probability of superiority — much more interpretable than traditional hypothesis testing.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module
Implements Beta-Binomial conjugate prior approach for conversion rate analysis.
Basically lets you compare two variants and get actual probability statements
instead of confusing p-values.
"""

import random
from math import gamma, exp, log


class BetaDistribution:
    """
    Represents a Beta distribution, the conjugate prior for binomial likelihood.
    I'm using this because it naturally models conversion rates (bounded 0-1).
    """
    
    def __init__(self, alpha=1.0, beta=1.0):
        """
        Initialize with prior parameters.
        alpha=1, beta=1 gives uniform prior (no assumptions).
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """
        Bayesian update: posterior is just adding counts to parameters.
        This is the magic of conjugate priors — no complex integration needed.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self):
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self):
        """
        Generate a random sample from this Beta distribution.
        Using acceptance-rejection, not the most efficient but works fine.
        """
        # For Beta distributions, I'll use a simple method
        # Generate two gamma variables and normalize (standard trick)
        x = self._sample_gamma(self.alpha)
        y = self._sample_gamma(self.beta)
        return x / (x + y)
    
    def _sample_gamma(self, shape):
        """
        Sample from Gamma(shape, 1) using Marsaglia and Tsang's method.
        Needed this for the Beta sampler above.
        """
        if shape < 1:
            # Use the transformation for shape < 1
            return self._sample_gamma(shape + 1) * (random.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / (9.0 * d) ** 0.5
        
        while True:
            # Standard normal approximation
            x = random.gauss(0, 1)
            v = (1.0 + c * x) ** 3
            
            if v <= 0:
                continue
            
            u = random.random()
            if u < 1 - 0.0331 * x ** 4:
                return d * v
            
            if log(u) < 0.5 * x ** 2 + d * (1 - v + log(v)):
                return d * v


class ABTest:
    """
    Run Bayesian A/B tests comparing two conversion rates.
    Way better than frequentist testing because you get actual probabilities.
    """
    
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        """
        Initialize test with prior beliefs about conversion rates.
        Default is uniform prior (no strong beliefs).
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant, successes, failures):
        """
        Add observed data for a variant.
        variant: 'A' or 'B'
        successes: number of conversions
        failures: number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_better(self, samples=10000):
        """
        Compute P(B > A) using Monte Carlo sampling.
        This is the key insight: just sample from both posteriors and count
        how often B beats A. Simple and interpretable.
        """
        b_wins = 0
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        return b_wins / samples
    
    def expected_lift(self, samples=10000):
        """
        Expected relative improvement of B over A.
        Returns the mean of (B - A) / A from the posterior.
        """
        lifts = []
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_a > 0:  # Avoid division by zero
                lifts.append((sample_b - sample_a) / sample_a)
        return sum(lifts) / len(lifts) if lifts else 0.0
    
    def summary(self):
        """Print a nice summary of the test results."""
        print("=" * 60)
        print("BAYESIAN A/B TEST RESULTS")
        print("=" * 60)
        print(f"Variant A: {self.variant_a.mean():.4f} conversion rate")
        print(f"           (95% credible interval would need more math)")
        print(f"Variant B: {self.variant_b.mean():.4f} conversion rate")
        print()
        
        prob_b_better = self.probability_b_better()
        print(f"P(B > A) = {prob_b_better:.2%}")
        
        if prob_b_better > 0.95:
            print("→ Strong evidence that B is better")
        elif prob_b_better > 0.90:
            print("→ Moderate evidence that B is better")
        elif prob_b_better < 0.05:
            print("→ Strong evidence that A is better")
        elif prob_b_better < 0.10:
            print("→ Moderate evidence that A is better")
        else:
            print("→ Inconclusive, need more data")
        
        lift = self.expected_lift()
        print(f"\nExpected lift: {lift:+.2%}")
        print("=" * 60)


if __name__ == "__main__":
    # Demo: simulate a realistic A/B test scenario
    print("Running simulated A/B test...\n")
    
    # Set up test with weak prior (uniform)
    test = ABTest(prior_alpha=1, prior_beta=1)
    
    # Simulate scenario: variant A has 10% conversion, B has 12%
    # Let's say we ran 1000 visitors through each
    print("Scenario: Testing new checkout flow")
    print("- Control (A): 1000 visitors, 100 conversions (10%)")
    print("- Treatment (B): 1000 visitors, 120 conversions (12%)")
    print()
    
    test.add_data('A', successes=100, failures=900)
    test.add_data('B', successes=120, failures=880)
    
    test.summary()
    
    # Another example with less data (more uncertainty)
    print("\n\nNow with LESS data (more uncertainty):")
    test2 = ABTest()
    print("- Control (A): 100 visitors, 10 conversions")
    print("- Treatment (B): 100 visitors, 15 conversions")
    print()
    
    test2.add_data('A', successes=10, failures=90)
    test2.add_data('B', successes=15, failures=85)
    
    test2.summary()