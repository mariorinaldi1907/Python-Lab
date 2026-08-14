"""
Date: 2026-08-14
Implemented a Bayesian A/B testing framework using beta distributions to calculate probabilities of one variant being better than another — handles conversion rate experiments with proper credible intervals.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Evaluator
Uses Beta distributions to compare conversion rates between two variants.
I got tired of relying on p-values for small sample A/B tests, so I built this.
"""

import random
import math
from typing import Tuple, Dict


class BayesianABTest:
    """
    Bayesian A/B test using Beta distributions.
    
    The Beta distribution is the conjugate prior for binomial data,
    which makes the math clean for conversion rate testing.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs.
        
        Args:
            alpha_prior: Prior successes (uniform prior when alpha=beta=1)
            beta_prior: Prior failures
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        
        # Variant A and B data
        self.variant_a = {'successes': 0, 'failures': 0}
        self.variant_b = {'successes': 0, 'failures': 0}
    
    def update(self, variant: str, successes: int, failures: int) -> None:
        """
        Update the model with observed data.
        
        Args:
            variant: Either 'A' or 'B'
            successes: Number of conversions
            failures: Number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a['successes'] += successes
            self.variant_a['failures'] += failures
        elif variant.upper() == 'B':
            self.variant_b['successes'] += successes
            self.variant_b['failures'] += failures
        else:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
    
    def get_posterior_params(self, variant: str) -> Tuple[float, float]:
        """
        Get the posterior Beta distribution parameters for a variant.
        
        Returns:
            (alpha, beta) parameters for the Beta distribution
        """
        data = self.variant_a if variant.upper() == 'A' else self.variant_b
        alpha = self.alpha_prior + data['successes']
        beta = self.beta_prior + data['failures']
        return alpha, beta
    
    def sample_posterior(self, variant: str, n_samples: int = 10000) -> list:
        """
        Draw samples from the posterior distribution.
        
        This uses inverse transform sampling for the Beta distribution.
        I could've used numpy here, but keeping it stdlib only.
        """
        alpha, beta = self.get_posterior_params(variant)
        samples = []
        
        # Beta distribution sampling using gamma variates
        # Beta(a,b) = Gamma(a) / (Gamma(a) + Gamma(b))
        for _ in range(n_samples):
            x = random.gammavariate(alpha, 1)
            y = random.gammavariate(beta, 1)
            samples.append(x / (x + y))
        
        return samples
    
    def probability_b_beats_a(self, n_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is the key metric: what's the probability that variant B
        actually has a higher conversion rate than variant A?
        """
        samples_a = self.sample_posterior('A', n_samples)
        samples_b = self.sample_posterior('B', n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def get_credible_interval(self, variant: str, credibility: float = 0.95,
                             n_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate the credible interval for a variant's conversion rate.
        
        Unlike confidence intervals, this actually means "there's a 95% probability
        the true rate is in this range" which is what people think CIs mean anyway.
        """
        samples = self.sample_posterior(variant, n_samples)
        samples.sort()
        
        lower_idx = int((1 - credibility) / 2 * n_samples)
        upper_idx = int((1 + credibility) / 2 * n_samples)
        
        return samples[lower_idx], samples[upper_idx]
    
    def expected_conversion_rate(self, variant: str) -> float:
        """
        Get the expected (mean) conversion rate for a variant.
        
        For Beta(alpha, beta), the mean is alpha / (alpha + beta).
        """
        alpha, beta = self.get_posterior_params(variant)
        return alpha / (alpha + beta)
    
    def get_summary(self) -> Dict:
        """Return a complete summary of the test results."""
        prob_b_wins = self.probability_b_beats_a()
        
        return {
            'variant_a': {
                'successes': self.variant_a['successes'],
                'failures': self.variant_a['failures'],
                'expected_rate': self.expected_conversion_rate('A'),
                'credible_interval': self.get_credible_interval('A'),
            },
            'variant_b': {
                'successes': self.variant_b['successes'],
                'failures': self.variant_b['failures'],
                'expected_rate': self.expected_conversion_rate('B'),
                'credible_interval': self.get_credible_interval('B'),
            },
            'probability_b_beats_a': prob_b_wins,
            'probability_a_beats_b': 1 - prob_b_wins,
        }


if __name__ == "__main__":
    # Simulate a real A/B test scenario
    print("=" * 60)
    print("Bayesian A/B Test Demo")
    print("=" * 60)
    print("\nScenario: Testing two landing page variants")
    print("Variant A (control): 120 conversions, 1000 visitors")
    print("Variant B (treatment): 145 conversions, 1000 visitors")
    print()
    
    # Initialize test with uniform prior
    test = BayesianABTest(alpha_prior=1.0, beta_prior=1.0)
    
    # Add data for variant A (control)
    test.update('A', successes=120, failures=880)
    
    # Add data for variant B (treatment)
    test.update('B', successes=145, failures=855)
    
    # Get results
    summary = test.get_summary()
    
    print("RESULTS")
    print("-" * 60)
    print(f"\nVariant A:")
    print(f"  Conversions: {summary['variant_a']['successes']}")
    print(f"  Expected conversion rate: {summary['variant_a']['expected_rate']:.4f}")
    print(f"  95% Credible Interval: [{summary['variant_a']['credible_interval'][0]:.4f}, "
          f"{summary['variant_a']['credible_interval'][1]:.4f}]")
    
    print(f"\nVariant B:")
    print(f"  Conversions: {summary['variant_b']['successes']}")
    print(f"  Expected conversion rate: {summary['variant_b']['expected_rate']:.4f}")
    print(f"  95% Credible Interval: [{summary['variant_b']['credible_interval'][0]:.4f}, "
          f"{summary['variant_b']['credible_interval'][1]:.4f}]")
    
    print(f"\nProbability that B beats A: {summary['probability_b_beats_a']:.2%}")
    print(f"Probability that A beats B: {summary['probability_a_beats_b']:.2%}")
    
    # Decision guidance
    print("\n" + "=" * 60)
    if summary['probability_b_beats_a'] > 0.95:
        print("DECISION: Strong evidence for variant B. Ship it!")
    elif summary['probability_b_beats_a'] > 0.90:
        print("DECISION: Good evidence for B, but maybe collect more data.")
    elif summary['probability_b_beats_a'] < 0.10:
        print("DECISION: Strong evidence for variant A. Keep the control.")
    else:
        print("DECISION: Inconclusive. Need more data or the difference is negligible.")
    print("=" * 60)