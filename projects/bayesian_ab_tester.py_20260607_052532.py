"""
Date: 2026-06-07
Implemented a Bayesian A/B test analyzer using beta distributions to calculate probabilities of variant superiority — includes credible intervals and expected loss calculations.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

Uses beta distributions to analyze A/B test results. Much more intuitive than
p-values — you get actual probabilities like "there's a 94% chance B is better."
"""

import random
import math
from typing import Tuple, Dict


class BayesianABTest:
    """
    Bayesian A/B test using beta distributions.
    
    The beta distribution is perfect for modeling conversion rates because:
    - It's conjugate to the binomial (math stays clean)
    - Parameters (alpha, beta) directly map to (successes + 1, failures + 1)
    - Easy to sample from and compute probabilities
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs.
        
        Args:
            alpha_prior: Prior pseudo-successes (default 1 = uniform prior)
            beta_prior: Prior pseudo-failures (default 1 = uniform prior)
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        self.variants = {}
    
    def add_variant(self, name: str, successes: int, trials: int):
        """
        Add or update a variant with observed data.
        
        Args:
            name: Variant identifier (e.g., "control", "variant_b")
            successes: Number of conversions
            trials: Total number of trials
        """
        failures = trials - successes
        # Posterior parameters = prior + observed data
        self.variants[name] = {
            'alpha': self.alpha_prior + successes,
            'beta': self.beta_prior + failures,
            'successes': successes,
            'trials': trials
        }
    
    def sample_posterior(self, name: str, n_samples: int = 10000) -> list:
        """
        Draw samples from the posterior distribution.
        
        Using random sampling because computing beta CDFs analytically is painful.
        Monte Carlo makes this super straightforward.
        """
        variant = self.variants[name]
        return [random.betavariate(variant['alpha'], variant['beta']) 
                for _ in range(n_samples)]
    
    def probability_b_beats_a(self, name_a: str, name_b: str, 
                              n_samples: int = 10000) -> float:
        """
        Calculate P(B > A) via Monte Carlo sampling.
        
        This is the key metric — way more useful than a p-value.
        """
        samples_a = self.sample_posterior(name_a, n_samples)
        samples_b = self.sample_posterior(name_b, n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def credible_interval(self, name: str, confidence: float = 0.95,
                          n_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate credible interval (Bayesian confidence interval).
        
        Unlike frequentist CI, this actually means "95% probability the true
        value is in this range" — which is what people think CI means anyway.
        """
        samples = sorted(self.sample_posterior(name, n_samples))
        lower_idx = int((1 - confidence) / 2 * n_samples)
        upper_idx = int((1 + confidence) / 2 * n_samples)
        return samples[lower_idx], samples[upper_idx]
    
    def expected_loss(self, name_a: str, name_b: str,
                      n_samples: int = 10000) -> Dict[str, float]:
        """
        Calculate expected loss if we pick the wrong variant.
        
        Expected loss = average amount we'd lose if we chose A but B is better.
        Helps make the business case for when to stop testing.
        """
        samples_a = self.sample_posterior(name_a, n_samples)
        samples_b = self.sample_posterior(name_b, n_samples)
        
        # Loss if we choose A but B is better
        loss_a = sum(max(0, b - a) for a, b in zip(samples_a, samples_b)) / n_samples
        # Loss if we choose B but A is better
        loss_b = sum(max(0, a - b) for a, b in zip(samples_a, samples_b)) / n_samples
        
        return {name_a: loss_a, name_b: loss_b}
    
    def get_summary(self, name: str) -> Dict[str, float]:
        """Get key statistics for a variant."""
        variant = self.variants[name]
        
        # Mean of beta distribution
        mean = variant['alpha'] / (variant['alpha'] + variant['beta'])
        
        # Mode (most likely value) if alpha, beta > 1
        if variant['alpha'] > 1 and variant['beta'] > 1:
            mode = (variant['alpha'] - 1) / (variant['alpha'] + variant['beta'] - 2)
        else:
            mode = mean  # Fallback to mean
        
        ci_low, ci_high = self.credible_interval(name)
        
        return {
            'observed_rate': variant['successes'] / variant['trials'],
            'posterior_mean': mean,
            'posterior_mode': mode,
            'ci_95_lower': ci_low,
            'ci_95_upper': ci_high
        }


if __name__ == "__main__":
    print("=== Bayesian A/B Test Demo ===\n")
    
    # Simulate an A/B test scenario
    # Control: 120 conversions out of 1000 visitors (12%)
    # Variant: 145 conversions out of 1000 visitors (14.5%)
    
    test = BayesianABTest(alpha_prior=1, beta_prior=1)  # Uniform prior
    
    test.add_variant("control", successes=120, trials=1000)
    test.add_variant("variant_b", successes=145, trials=1000)
    
    print("Control Group:")
    control_stats = test.get_summary("control")
    print(f"  Observed rate: {control_stats['observed_rate']:.2%}")
    print(f"  Posterior mean: {control_stats['posterior_mean']:.2%}")
    print(f"  95% CI: [{control_stats['ci_95_lower']:.2%}, {control_stats['ci_95_upper']:.2%}]")
    
    print("\nVariant B:")
    variant_stats = test.get_summary("variant_b")
    print(f"  Observed rate: {variant_stats['observed_rate']:.2%}")
    print(f"  Posterior mean: {variant_stats['posterior_mean']:.2%}")
    print(f"  95% CI: [{variant_stats['ci_95_lower']:.2%}, {variant_stats['ci_95_upper']:.2%}]")
    
    # The money question: how likely is B better than A?
    prob_b_wins = test.probability_b_beats_a("control", "variant_b")
    print(f"\n🎯 Probability that Variant B beats Control: {prob_b_wins:.1%}")
    
    # Expected loss helps decide when to stop testing
    losses = test.expected_loss("control", "variant_b")
    print(f"\nExpected Loss:")
    print(f"  If we choose Control: {losses['control']:.4f}")
    print(f"  If we choose Variant B: {losses['variant_b']:.4f}")
    
    # Decision logic I actually use
    print("\n💡 Decision:")
    if prob_b_wins > 0.95:
        print(f"   Ship Variant B! (>{95}% confident it's better)")
    elif prob_b_wins < 0.05:
        print(f"   Stick with Control! (>{95}% confident it's better)")
    else:
        print(f"   Keep testing — not confident enough yet")
        print(f"   (Need ~95% probability, currently at {prob_b_wins:.1%})")