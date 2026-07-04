"""
Date: 2026-07-04
Implemented a Bayesian A/B testing framework with Beta-Binomial conjugate priors so I can actually quantify probability of improvement instead of just rejecting null hypotheses.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

I needed a way to analyze conversion rates for different UI variants on my
projects without relying on frequentist p-values. This uses Beta-Binomial
conjugate priors which makes the math tractable and interpretable.
"""

import random
from typing import Tuple, List
import math


class BayesianABTest:
    """
    A/B test analyzer using Bayesian inference with Beta priors.
    
    The Beta distribution is conjugate to the Binomial, which means we can
    update our beliefs about conversion rates analytically without MCMC.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with Beta prior parameters.
        
        Args:
            alpha_prior: Prior successes (default 1.0 = uniform prior)
            beta_prior: Prior failures (default 1.0 = uniform prior)
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        
        # Variant A and B posteriors
        self.variant_a = {"successes": 0, "failures": 0}
        self.variant_b = {"successes": 0, "failures": 0}
    
    def add_observations(self, variant: str, successes: int, failures: int):
        """
        Add observed data for a variant.
        
        Args:
            variant: Either 'A' or 'B'
            successes: Number of conversions
            failures: Number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a["successes"] += successes
            self.variant_a["failures"] += failures
        elif variant.upper() == 'B':
            self.variant_b["successes"] += successes
            self.variant_b["failures"] += failures
        else:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
    
    def sample_beta(self, alpha: float, beta: float) -> float:
        """
        Sample from a Beta distribution using the ratio of Gammas method.
        
        I'm using this instead of importing numpy because I want to keep
        this dependency-free for quick deployment.
        """
        # Beta(a,b) = Gamma(a) / (Gamma(a) + Gamma(b))
        x = random.gammavariate(alpha, 1)
        y = random.gammavariate(beta, 1)
        return x / (x + y)
    
    def probability_b_beats_a(self, samples: int = 10000) -> float:
        """
        Estimate P(theta_B > theta_A) via Monte Carlo sampling.
        
        This is the key metric: what's the probability that variant B
        actually has a higher conversion rate than A?
        
        Args:
            samples: Number of Monte Carlo samples to draw
            
        Returns:
            Probability that B's conversion rate exceeds A's
        """
        alpha_a = self.alpha_prior + self.variant_a["successes"]
        beta_a = self.beta_prior + self.variant_a["failures"]
        
        alpha_b = self.alpha_prior + self.variant_b["successes"]
        beta_b = self.beta_prior + self.variant_b["failures"]
        
        b_wins = 0
        for _ in range(samples):
            theta_a = self.sample_beta(alpha_a, beta_a)
            theta_b = self.sample_beta(alpha_b, beta_b)
            if theta_b > theta_a:
                b_wins += 1
        
        return b_wins / samples
    
    def get_posterior_mean(self, variant: str) -> float:
        """
        Get the posterior mean conversion rate for a variant.
        
        For Beta(alpha, beta), the mean is alpha / (alpha + beta).
        """
        if variant.upper() == 'A':
            alpha = self.alpha_prior + self.variant_a["successes"]
            beta = self.beta_prior + self.variant_a["failures"]
        else:
            alpha = self.alpha_prior + self.variant_b["successes"]
            beta = self.beta_prior + self.variant_b["failures"]
        
        return alpha / (alpha + beta)
    
    def get_credible_interval(self, variant: str, confidence: float = 0.95,
                              samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate the Bayesian credible interval for a variant's conversion rate.
        
        Unlike confidence intervals, credible intervals have the interpretation
        we actually want: there's a 95% probability the true rate is in this range.
        """
        if variant.upper() == 'A':
            alpha = self.alpha_prior + self.variant_a["successes"]
            beta = self.beta_prior + self.variant_a["failures"]
        else:
            alpha = self.alpha_prior + self.variant_b["successes"]
            beta = self.beta_prior + self.variant_b["failures"]
        
        # Draw samples and compute percentiles
        samples_list = [self.sample_beta(alpha, beta) for _ in range(samples)]
        samples_list.sort()
        
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        
        return samples_list[lower_idx], samples_list[upper_idx]
    
    def summary(self):
        """Print a human-readable summary of the A/B test results."""
        print("=" * 60)
        print("BAYESIAN A/B TEST SUMMARY")
        print("=" * 60)
        
        mean_a = self.get_posterior_mean('A')
        mean_b = self.get_posterior_mean('B')
        ci_a = self.get_credible_interval('A')
        ci_b = self.get_credible_interval('B')
        prob_b_wins = self.probability_b_beats_a()
        
        print(f"\nVariant A:")
        print(f"  Observations: {self.variant_a['successes']} successes, "
              f"{self.variant_a['failures']} failures")
        print(f"  Posterior mean: {mean_a:.4f}")
        print(f"  95% Credible interval: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
        
        print(f"\nVariant B:")
        print(f"  Observations: {self.variant_b['successes']} successes, "
              f"{self.variant_b['failures']} failures")
        print(f"  Posterior mean: {mean_b:.4f}")
        print(f"  95% Credible interval: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
        
        print(f"\nP(B > A) = {prob_b_wins:.4f}")
        
        # Give a recommendation based on typical decision thresholds
        if prob_b_wins > 0.95:
            print("\n✓ Strong evidence that B is better. Ship it!")
        elif prob_b_wins > 0.90:
            print("\n→ Moderate evidence for B. Consider shipping or collecting more data.")
        elif prob_b_wins < 0.05:
            print("\n✗ Strong evidence that A is better. Stick with A.")
        else:
            print("\n? Inconclusive. Need more data to make a confident decision.")
        
        print("=" * 60)


if __name__ == "__main__":
    # Simulate a realistic A/B test scenario from one of my landing page experiments
    print("Simulating A/B test: Control vs. New CTA Button Color\n")
    
    test = BayesianABTest(alpha_prior=1.0, beta_prior=1.0)
    
    # Variant A (control): 120 conversions out of 1000 visitors
    test.add_observations('A', successes=120, failures=880)
    
    # Variant B (new design): 145 conversions out of 1000 visitors
    test.add_observations('B', successes=145, failures=855)
    
    test.summary()
    
    print("\n" + "="*60)
    print("Running another test with less clear results...")
    print("="*60 + "\n")
    
    # Example where the difference is smaller
    test2 = BayesianABTest()
    test2.add_observations('A', successes=52, failures=448)
    test2.add_observations('B', successes=58, failures=442)
    
    test2.summary()