"""
Date: 2026-07-29
Created a Bayesian A/B testing tool that updates beliefs about conversion rates using conjugate priors — way more intuitive than frequentist approaches for real product decisions.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Tool
A proper Bayesian approach to A/B testing using Beta-Binomial conjugate priors.
I built this because frequentist p-values don't tell you what you actually want to know.
"""

import math
import random
from typing import Tuple, List


def beta_pdf(x: float, alpha: float, beta: float) -> float:
    """
    Compute the Beta distribution PDF at point x.
    
    Using the definition: Beta(x; α, β) = x^(α-1) * (1-x)^(β-1) / B(α, β)
    where B(α, β) is the beta function.
    """
    if x <= 0 or x >= 1:
        return 0.0
    
    # Log-space computation to avoid numerical overflow
    log_numerator = (alpha - 1) * math.log(x) + (beta - 1) * math.log(1 - x)
    log_beta_func = math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
    
    return math.exp(log_numerator - log_beta_func)


def beta_sample(alpha: float, beta: float) -> float:
    """
    Draw a random sample from Beta(alpha, beta) using the rejection method.
    
    This isn't the most efficient algorithm but it's pure Python and works well enough.
    For production I'd use numpy's built-in, but keeping this dependency-free.
    """
    # Use gamma variates to generate beta (standard transformation)
    # If X ~ Gamma(α, 1) and Y ~ Gamma(β, 1), then X/(X+Y) ~ Beta(α, β)
    x = random.gammavariate(alpha, 1.0)
    y = random.gammavariate(beta, 1.0)
    return x / (x + y)


class BayesianABTest:
    """
    A/B test analyzer using Bayesian inference with Beta-Binomial model.
    
    The Beta distribution is conjugate to the Binomial, which makes updates clean:
    - Prior: Beta(α, β)
    - Data: k successes in n trials
    - Posterior: Beta(α + k, β + n - k)
    
    This lets us quantify actual probabilities like "Prob(A > B)" which is what
    product managers actually care about, not some arbitrary p-value threshold.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with a prior belief about conversion rates.
        
        Default is uniform prior (α=1, β=1) meaning "no strong beliefs".
        You could use α=β=0.5 for Jeffreys prior, or something informative based
        on historical data.
        """
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        
        # Storage for variant data
        self.variants = {}
    
    def add_variant(self, name: str, successes: int, trials: int):
        """
        Add or update a variant's data.
        
        Args:
            name: Variant identifier (e.g., "control" or "treatment")
            successes: Number of conversions/successes
            trials: Total number of observations
        """
        # Posterior is just prior + data (conjugacy is beautiful)
        posterior_alpha = self.prior_alpha + successes
        posterior_beta = self.prior_beta + (trials - successes)
        
        self.variants[name] = {
            'successes': successes,
            'trials': trials,
            'posterior_alpha': posterior_alpha,
            'posterior_beta': posterior_beta
        }
    
    def get_posterior_mean(self, variant: str) -> float:
        """
        Get the expected conversion rate (posterior mean) for a variant.
        
        For Beta(α, β), the mean is α / (α + β).
        """
        v = self.variants[variant]
        alpha = v['posterior_alpha']
        beta = v['posterior_beta']
        return alpha / (alpha + beta)
    
    def get_credible_interval(self, variant: str, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute a credible interval for the conversion rate.
        
        This is the Bayesian equivalent of a confidence interval, but actually means
        what people think confidence intervals mean: "95% probability the true rate
        is in this range given the data."
        
        Using quantile approximation since we don't have scipy.
        """
        v = self.variants[variant]
        alpha = v['posterior_alpha']
        beta = v['posterior_beta']
        
        # Generate samples and compute empirical quantiles
        samples = [beta_sample(alpha, beta) for _ in range(10000)]
        samples.sort()
        
        lower_idx = int((1 - confidence) / 2 * len(samples))
        upper_idx = int((1 + confidence) / 2 * len(samples))
        
        return samples[lower_idx], samples[upper_idx]
    
    def probability_b_beats_a(self, variant_a: str, variant_b: str, samples: int = 50000) -> float:
        """
        Calculate P(B > A) - the probability that variant B's true conversion rate
        is higher than variant A's.
        
        This is THE key metric for decision making. If this is 95%+, you can be
        pretty confident B is actually better.
        
        We estimate this by sampling from both posteriors and counting.
        """
        va = self.variants[variant_a]
        vb = self.variants[variant_b]
        
        wins = 0
        for _ in range(samples):
            sample_a = beta_sample(va['posterior_alpha'], va['posterior_beta'])
            sample_b = beta_sample(vb['posterior_alpha'], vb['posterior_beta'])
            if sample_b > sample_a:
                wins += 1
        
        return wins / samples
    
    def expected_loss(self, variant_a: str, variant_b: str, samples: int = 50000) -> float:
        """
        Expected loss if we choose A when B is actually better (or vice versa).
        
        This quantifies risk: "If I pick the wrong variant, how much conversion rate
        am I giving up on average?"
        """
        va = self.variants[variant_a]
        vb = self.variants[variant_b]
        
        total_loss = 0.0
        for _ in range(samples):
            sample_a = beta_sample(va['posterior_alpha'], va['posterior_beta'])
            sample_b = beta_sample(vb['posterior_alpha'], vb['posterior_beta'])
            # Loss is the gap when we're wrong
            total_loss += max(0, sample_b - sample_a)
        
        return total_loss / samples


if __name__ == "__main__":
    print("=" * 70)
    print("Bayesian A/B Test Demo")
    print("=" * 70)
    print()
    
    # Simulate a realistic scenario: testing a new checkout flow
    # Control: 520 conversions out of 10,000 visitors (5.2% conversion)
    # Treatment: 580 conversions out of 10,000 visitors (5.8% conversion)
    
    test = BayesianABTest(prior_alpha=1, prior_beta=1)  # Uniform prior
    
    test.add_variant("control", successes=520, trials=10000)
    test.add_variant("treatment", successes=580, trials=10000)
    
    print("Variant Data:")
    print(f"  Control:   520 / 10,000 conversions (5.20%)")
    print(f"  Treatment: 580 / 10,000 conversions (5.80%)")
    print()
    
    print("Posterior Analysis:")
    print("-" * 70)
    
    for variant in ["control", "treatment"]:
        mean = test.get_posterior_mean(variant)
        lower, upper = test.get_credible_interval(variant, confidence=0.95)
        
        print(f"\n{variant.upper()}:")
        print(f"  Expected conversion rate: {mean:.4f} ({mean*100:.2f}%)")
        print(f"  95% credible interval: [{lower:.4f}, {upper:.4f}]")
    
    print()
    print("-" * 70)
    
    prob_treatment_wins = test.probability_b_beats_a("control", "treatment")
    print(f"\nProbability treatment beats control: {prob_treatment_wins:.4f} ({prob_treatment_wins*100:.1f}%)")
    
    loss = test.expected_loss("control", "treatment")
    print(f"Expected loss if we stick with control: {loss:.6f} ({loss*100:.4f}% conversion rate)")
    
    print()
    print("=" * 70)
    print("Decision Recommendation:")
    print("=" * 70)
    
    if prob_treatment_wins > 0.95:
        print("✓ Ship the treatment! Very strong evidence it's better.")
    elif prob_treatment_wins > 0.90:
        print("→ Treatment looks promising, but consider collecting more data.")
    else:
        print("⊗ Not enough evidence yet. Keep testing or stick with control.")
    
    print()