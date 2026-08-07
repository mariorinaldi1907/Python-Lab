"""
Date: 2026-08-07
Created a Bayesian AB testing module that actually tells you the probability one variant is better, plus credible intervals — way more intuitive than frequentist stats.
"""

#!/usr/bin/env python3
"""
Bayesian AB Testing Module

I got tired of wrestling with p-values and confidence intervals that don't mean
what most people think they mean. This module uses Bayesian statistics to answer
the actual question: "What's the probability that variant B is better than A?"

Uses Beta distributions for conversion rates since they're conjugate priors for
binomial data (conversions/trials). Makes the math clean and interpretable.
"""

import random
import math
from typing import Tuple, List


class BayesianABTest:
    """
    Bayesian AB test analyzer using Beta-Binomial conjugate pairs.
    
    The Beta distribution is perfect for modeling conversion rates because:
    1. It's bounded between 0 and 1 (like probabilities)
    2. It's the conjugate prior for binomial likelihood (math works out cleanly)
    3. We can update it incrementally as data comes in
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs about conversion rates.
        
        Args:
            alpha_prior: Prior "successes" (uniform prior = 1)
            beta_prior: Prior "failures" (uniform prior = 1)
        
        Using alpha=1, beta=1 gives a uniform prior (no initial bias).
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
    
    def update_posterior(self, conversions: int, trials: int) -> Tuple[float, float]:
        """
        Update our beliefs given observed data.
        
        This is the magic of conjugate priors — the posterior is also Beta distributed.
        We just add observations to the prior parameters.
        """
        alpha_post = self.alpha_prior + conversions
        beta_post = self.beta_prior + (trials - conversions)
        return alpha_post, beta_post
    
    def sample_beta(self, alpha: float, beta: float, n_samples: int = 10000) -> List[float]:
        """
        Generate samples from a Beta distribution using acceptance-rejection.
        
        I know there's numpy, but keeping it stdlib-only. This is less efficient
        but works fine for our purposes.
        """
        samples = []
        # Using a simple method: gamma ratio trick
        # Beta(alpha, beta) = Gamma(alpha) / (Gamma(alpha) + Gamma(beta))
        for _ in range(n_samples):
            # Generate two gamma random variables
            g1 = self._sample_gamma(alpha)
            g2 = self._sample_gamma(beta)
            samples.append(g1 / (g1 + g2))
        return samples
    
    def _sample_gamma(self, shape: float) -> float:
        """
        Sample from Gamma distribution using Marsaglia and Tsang's method.
        
        This is a bit involved but it's the standard way without external deps.
        For shape >= 1, we use the squeeze method.
        """
        if shape < 1:
            # For shape < 1, use the fact that Gamma(shape) = Gamma(shape+1) * U^(1/shape)
            return self._sample_gamma(shape + 1) * (random.random() ** (1.0 / shape))
        
        # Marsaglia and Tsang's method for shape >= 1
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            # Generate normal(0,1) using Box-Muller
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            
            v = (1.0 + c * z) ** 3
            if v <= 0:
                continue
            
            u = random.random()
            if u < 1 - 0.0331 * (z ** 4):
                return d * v
            if math.log(u) < 0.5 * z * z + d * (1 - v + math.log(v)):
                return d * v
    
    def probability_b_beats_a(self, a_conversions: int, a_trials: int,
                              b_conversions: int, b_trials: int,
                              n_samples: int = 10000) -> float:
        """
        Calculate P(B > A) — the probability that variant B is truly better.
        
        This is the core insight of Bayesian AB testing: we can directly answer
        "what's the probability this variant is better?" instead of the weird
        frequentist "if there's no difference, how weird is this data?"
        """
        alpha_a, beta_a = self.update_posterior(a_conversions, a_trials)
        alpha_b, beta_b = self.update_posterior(b_conversions, b_trials)
        
        samples_a = self.sample_beta(alpha_a, beta_a, n_samples)
        samples_b = self.sample_beta(alpha_b, beta_b, n_samples)
        
        # Count how many times B > A
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def credible_interval(self, conversions: int, trials: int,
                         credibility: float = 0.95) -> Tuple[float, float]:
        """
        Calculate credible interval (Bayesian version of confidence interval).
        
        Unlike confidence intervals, this actually means what you think it means:
        "There's a 95% probability the true value is in this range."
        """
        alpha, beta = self.update_posterior(conversions, trials)
        samples = self.sample_beta(alpha, beta, 10000)
        samples.sort()
        
        lower_idx = int((1 - credibility) / 2 * len(samples))
        upper_idx = int((1 + credibility) / 2 * len(samples))
        
        return samples[lower_idx], samples[upper_idx]


if __name__ == "__main__":
    # Real-world scenario: testing two landing page variants
    print("=== Bayesian AB Testing Demo ===\n")
    
    # Simulate some test data
    # Variant A: 120 conversions out of 1000 visitors (12% conversion rate)
    # Variant B: 145 conversions out of 1000 visitors (14.5% conversion rate)
    a_conversions, a_trials = 120, 1000
    b_conversions, b_trials = 145, 1000
    
    print(f"Variant A: {a_conversions}/{a_trials} conversions ({a_conversions/a_trials:.2%})")
    print(f"Variant B: {b_conversions}/{b_trials} conversions ({b_conversions/b_trials:.2%})")
    print()
    
    tester = BayesianABTest()
    
    # The money question: what's the probability B is actually better?
    prob_b_wins = tester.probability_b_beats_a(
        a_conversions, a_trials,
        b_conversions, b_trials
    )
    
    print(f"Probability that B is better than A: {prob_b_wins:.1%}")
    print()
    
    # Get credible intervals for each variant
    ci_a = tester.credible_interval(a_conversions, a_trials, credibility=0.95)
    ci_b = tester.credible_interval(b_conversions, b_trials, credibility=0.95)
    
    print(f"95% Credible Interval for A: [{ci_a[0]:.3f}, {ci_a[1]:.3f}]")
    print(f"95% Credible Interval for B: [{ci_b[0]:.3f}, {ci_b[1]:.3f}]")
    print()
    
    # Decision guidance
    if prob_b_wins > 0.95:
        print("✓ Strong evidence for B — ship it!")
    elif prob_b_wins > 0.90:
        print("→ Moderate evidence for B — probably worth switching")
    elif prob_b_wins < 0.10:
        print("✗ Strong evidence B is worse — stick with A")
    else:
        print("? Inconclusive — need more data or the difference doesn't matter")