"""
Date: 2026-07-14
Implemented a Bayesian A/B testing module with Beta-Binomial conjugate priors so I can get actual probability estimates that variant B beats variant A, plus credible intervals.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

I kept running into situations where classical frequentist A/B tests gave me
p-values but not the thing I actually cared about: "what's the probability
that B is better than A?" So I built this to use Bayesian inference with
Beta distributions as conjugate priors for binomial data.
"""

import random
from typing import Tuple, List


class BayesianABTest:
    """
    Bayesian A/B test using Beta-Binomial conjugate priors.
    
    The Beta distribution is perfect for modeling conversion rates because
    it's the conjugate prior for the Binomial likelihood. This means our
    posterior is also Beta distributed, which makes the math clean.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs.
        
        Args:
            alpha_prior: Prior successes (uniform prior is alpha=1, beta=1)
            beta_prior: Prior failures (uniform prior is alpha=1, beta=1)
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        
    def update_posterior(self, successes: int, trials: int) -> Tuple[float, float]:
        """
        Update Beta posterior with observed data.
        
        Args:
            successes: Number of conversions/successes
            trials: Total number of trials
            
        Returns:
            Tuple of (alpha_posterior, beta_posterior)
        """
        failures = trials - successes
        alpha_post = self.alpha_prior + successes
        beta_post = self.beta_prior + failures
        return alpha_post, beta_post
    
    def sample_beta(self, alpha: float, beta: float, n_samples: int = 10000) -> List[float]:
        """
        Generate samples from a Beta distribution using acceptance-rejection.
        
        I'm using a simple method here since we can't use numpy. For production
        I'd probably want something more efficient, but this works fine for
        moderate sample sizes.
        """
        samples = []
        for _ in range(n_samples):
            # Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
            # then X/(X+Y) ~ Beta(alpha, beta)
            x = self._gamma_sample(alpha)
            y = self._gamma_sample(beta)
            samples.append(x / (x + y))
        return samples
    
    def _gamma_sample(self, shape: float) -> float:
        """
        Sample from Gamma distribution using Marsaglia and Tsang's method.
        
        This is a simple approach that works well enough for our purposes.
        """
        if shape < 1:
            # Use the transformation for shape < 1
            return self._gamma_sample(shape + 1) * (random.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / (9.0 * d) ** 0.5
        
        while True:
            # Box-Muller for normal samples
            u1, u2 = random.random(), random.random()
            z = (-2 * (u1 + 1e-10) ** 0.5) * (2 * 3.14159265359 * u2) ** 0.5
            v = (1.0 + c * z) ** 3
            
            if v > 0:
                u = random.random()
                if u < 1 - 0.0331 * z ** 4 or u < v * v * 0.5 * (z ** 2 + d - d * v + d * v) - d:
                    return d * v
    
    def probability_b_beats_a(self, alpha_a: float, beta_a: float,
                              alpha_b: float, beta_b: float,
                              n_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is the key insight of Bayesian A/B testing: we can directly
        compute the probability that variant B has a higher conversion rate
        than variant A, which is what we actually care about.
        """
        samples_a = self.sample_beta(alpha_a, beta_a, n_samples)
        samples_b = self.sample_beta(alpha_b, beta_b, n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def credible_interval(self, alpha: float, beta: float,
                         confidence: float = 0.95,
                         n_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate Bayesian credible interval (analogous to confidence interval).
        
        Unlike frequentist confidence intervals, this actually means what people
        think it means: there's a 95% probability the true rate is in this range.
        """
        samples = self.sample_beta(alpha, beta, n_samples)
        samples.sort()
        
        lower_idx = int((1 - confidence) / 2 * n_samples)
        upper_idx = int((1 + confidence) / 2 * n_samples)
        
        return samples[lower_idx], samples[upper_idx]
    
    def expected_loss(self, alpha_a: float, beta_a: float,
                     alpha_b: float, beta_b: float,
                     n_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate expected loss for choosing each variant.
        
        Expected loss tells you: if you pick variant A but B is actually better,
        how much conversion rate are you giving up on average?
        """
        samples_a = self.sample_beta(alpha_a, beta_a, n_samples)
        samples_b = self.sample_beta(alpha_b, beta_b, n_samples)
        
        # Loss for choosing A when B is better
        loss_a = sum(max(0, b - a) for a, b in zip(samples_a, samples_b)) / n_samples
        # Loss for choosing B when A is better
        loss_b = sum(max(0, a - b) for a, b in zip(samples_a, samples_b)) / n_samples
        
        return loss_a, loss_b


if __name__ == "__main__":
    # Real scenario: testing two landing page variants
    # Variant A (control): 120 conversions out of 1000 visitors
    # Variant B (treatment): 145 conversions out of 1000 visitors
    
    print("=== Bayesian A/B Test Analysis ===\n")
    
    tester = BayesianABTest(alpha_prior=1.0, beta_prior=1.0)
    
    # Variant A data
    conversions_a = 120
    visitors_a = 1000
    alpha_a, beta_a = tester.update_posterior(conversions_a, visitors_a)
    
    # Variant B data
    conversions_b = 145
    visitors_b = 1000
    alpha_b, beta_b = tester.update_posterior(conversions_b, visitors_b)
    
    print(f"Variant A: {conversions_a}/{visitors_a} conversions ({conversions_a/visitors_a:.2%})")
    print(f"Variant B: {conversions_b}/{visitors_b} conversions ({conversions_b/visitors_b:.2%})")
    print()
    
    # Calculate probability B beats A
    prob_b_wins = tester.probability_b_beats_a(alpha_a, beta_a, alpha_b, beta_b)
    print(f"P(B > A) = {prob_b_wins:.2%}")
    print(f"P(A > B) = {1 - prob_b_wins:.2%}")
    print()
    
    # Credible intervals
    ci_a = tester.credible_interval(alpha_a, beta_a)
    ci_b = tester.credible_interval(alpha_b, beta_b)
    print(f"95% Credible Interval for A: [{ci_a[0]:.2%}, {ci_a[1]:.2%}]")
    print(f"95% Credible Interval for B: [{ci_b[0]:.2%}, {ci_b[1]:.2%}]")
    print()
    
    # Expected loss
    loss_a, loss_b = tester.expected_loss(alpha_a, beta_a, alpha_b, beta_b)
    print(f"Expected loss if we choose A: {loss_a:.4f} ({loss_a*100:.2f} percentage points)")
    print(f"Expected loss if we choose B: {loss_b:.4f} ({loss_b*100:.2f} percentage points)")
    print()
    
    # Decision recommendation
    if prob_b_wins > 0.95:
        print("✓ Strong evidence for B. Switch to variant B.")
    elif prob_b_wins > 0.90:
        print("⚠ Moderate evidence for B. Consider switching or collecting more data.")
    elif prob_b_wins < 0.10:
        print("✓ Strong evidence for A. Stick with variant A.")
    elif prob_b_wins < 0.05:
        print("⚠ Moderate evidence for A. Probably keep current variant