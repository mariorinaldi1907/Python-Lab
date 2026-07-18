"""
Date: 2026-07-18
Created a Bayesian A/B testing tool that updates beliefs with Beta distributions and runs Monte Carlo simulations to estimate win probabilities — way more intuitive than frequentist approaches.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Framework

I got tired of traditional p-value-based A/B testing that doesn't give you
what you actually want to know: "what's the probability that variant B is
better than variant A?" This uses Beta distributions as conjugate priors
for binomial data, which is perfect for conversion rates.
"""

import random
import math
from collections import namedtuple


class BayesianABTest:
    """
    Bayesian A/B test using Beta-Binomial conjugate pairs.
    
    The Beta distribution is the conjugate prior for binomial likelihood,
    which makes updating beliefs mathematically clean. Alpha and beta
    parameters represent (successes + 1) and (failures + 1) respectively.
    """
    
    def __init__(self, prior_alpha=1, prior_beta=1):
        """
        Initialize with prior belief (default is uniform prior).
        
        Args:
            prior_alpha: Prior successes + 1 (default 1 = uninformed)
            prior_beta: Prior failures + 1 (default 1 = uninformed)
        """
        self.variants = {}
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
    
    def add_variant(self, name, successes=0, trials=0):
        """
        Add or update a variant with observed data.
        
        Args:
            name: Variant identifier (e.g., 'A', 'B', 'control')
            successes: Number of conversions/successes
            trials: Total number of trials/visitors
        """
        failures = trials - successes
        # Posterior is just prior + observed data
        self.variants[name] = {
            'alpha': self.prior_alpha + successes,
            'beta': self.prior_beta + failures,
            'successes': successes,
            'trials': trials
        }
    
    def sample_beta(self, alpha, beta):
        """
        Draw a sample from Beta(alpha, beta) using gamma variables.
        
        I'm using the fact that if X ~ Gamma(a,1) and Y ~ Gamma(b,1),
        then X/(X+Y) ~ Beta(a,b). Python's random.gammavariate makes this easy.
        """
        x = random.gammavariate(alpha, 1)
        y = random.gammavariate(beta, 1)
        return x / (x + y)
    
    def monte_carlo_probability(self, variant_a, variant_b, simulations=10000):
        """
        Estimate P(variant_a > variant_b) using Monte Carlo sampling.
        
        This is the probability that variant A's true conversion rate
        is higher than B's. Way more interpretable than a p-value.
        
        Args:
            variant_a: Name of first variant
            variant_b: Name of second variant
            simulations: Number of Monte Carlo draws
            
        Returns:
            Probability that A > B (float between 0 and 1)
        """
        if variant_a not in self.variants or variant_b not in self.variants:
            raise ValueError("Both variants must exist in the test")
        
        params_a = self.variants[variant_a]
        params_b = self.variants[variant_b]
        
        wins = 0
        for _ in range(simulations):
            sample_a = self.sample_beta(params_a['alpha'], params_a['beta'])
            sample_b = self.sample_beta(params_b['alpha'], params_b['beta'])
            if sample_a > sample_b:
                wins += 1
        
        return wins / simulations
    
    def expected_value(self, variant):
        """
        Calculate the expected conversion rate (mean of posterior).
        
        For Beta(alpha, beta), the mean is alpha / (alpha + beta).
        """
        params = self.variants[variant]
        return params['alpha'] / (params['alpha'] + params['beta'])
    
    def credible_interval(self, variant, confidence=0.95):
        """
        Compute Bayesian credible interval using quantiles.
        
        Unlike confidence intervals, you can actually say "there's a 95%
        probability the true rate is in this range" — much more intuitive.
        
        Args:
            variant: Name of the variant
            confidence: Confidence level (default 0.95 for 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        params = self.variants[variant]
        alpha = params['alpha']
        beta = params['beta']
        
        # Generate many samples and use percentiles as credible interval
        samples = [self.sample_beta(alpha, beta) for _ in range(10000)]
        samples.sort()
        
        lower_idx = int((1 - confidence) / 2 * len(samples))
        upper_idx = int((1 + confidence) / 2 * len(samples))
        
        return (samples[lower_idx], samples[upper_idx])
    
    def report(self):
        """Print a summary report of all variants."""
        print("\n" + "="*60)
        print("BAYESIAN A/B TEST REPORT")
        print("="*60)
        
        for name, params in self.variants.items():
            expected = self.expected_value(name)
            lower, upper = self.credible_interval(name)
            
            print(f"\nVariant: {name}")
            print(f"  Data: {params['successes']}/{params['trials']} conversions")
            print(f"  Expected Rate: {expected:.4f}")
            print(f"  95% Credible Interval: [{lower:.4f}, {upper:.4f}]")
        
        # Compare all pairs
        variant_names = list(self.variants.keys())
        if len(variant_names) >= 2:
            print("\n" + "-"*60)
            print("PAIRWISE COMPARISONS")
            print("-"*60)
            for i in range(len(variant_names)):
                for j in range(i + 1, len(variant_names)):
                    prob = self.monte_carlo_probability(
                        variant_names[i], 
                        variant_names[j]
                    )
                    print(f"P({variant_names[i]} > {variant_names[j]}): {prob:.4f}")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    print("Demo: Bayesian A/B Testing for Landing Page Conversion")
    print("\nScenario: We tested two landing page designs")
    
    # Create the Bayesian test with a weakly informative prior
    # Using alpha=beta=2 means we start with a slight belief that
    # conversion rates are around 50%, but we're very uncertain
    test = BayesianABTest(prior_alpha=2, prior_beta=2)
    
    # Add observed data from our experiment
    # Control: 120 conversions out of 1000 visitors
    test.add_variant('Control', successes=120, trials=1000)
    
    # New Design: 145 conversions out of 1000 visitors
    # Looks better, but is it significantly better?
    test.add_variant('New_Design', successes=145, trials=1000)
    
    # Generate the full report
    test.report()
    
    # Let's also test with a smaller sample to show uncertainty
    print("\nNow testing with less data (early results):")
    small_test = BayesianABTest()
    small_test.add_variant('Control', successes=12, trials=100)
    small_test.add_variant('New_Design', successes=18, trials=100)
    small_test.report()
    
    print("Notice how the credible intervals are wider with less data!")
    print("That's Bayesian inference naturally accounting for uncertainty.")