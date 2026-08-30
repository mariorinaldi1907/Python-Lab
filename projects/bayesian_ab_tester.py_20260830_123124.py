"""
Date: 2026-08-30
Created a Bayesian A/B testing tool with conjugate priors that gives me actual probability distributions instead of just reject/don't reject decisions.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

I got tired of traditional frequentist A/B tests where you just get a p-value
and have to make some arbitrary decision at 0.05. This uses Beta-Binomial
conjugate priors to give actual probability distributions and lets me ask
questions like "what's the probability that variant B is better than A?"
"""

import random
import math
from typing import Tuple, List


class BayesianABTest:
    """
    Beta-Binomial Bayesian A/B test analyzer.
    
    Uses conjugate priors so we can get closed-form posterior distributions.
    The Beta distribution is conjugate to the Binomial, which makes the math
    clean and fast without needing MCMC sampling.
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with Beta prior parameters.
        
        Args:
            alpha_prior: Prior successes (default 1.0 = uniform prior)
            beta_prior: Prior failures (default 1.0 = uniform prior)
        
        Using alpha=1, beta=1 gives us a uniform prior, meaning we start
        with no assumptions about conversion rates.
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
    
    def update(self, successes: int, failures: int) -> Tuple[float, float]:
        """
        Update beliefs given observed data.
        
        Args:
            successes: Number of conversions
            failures: Number of non-conversions
        
        Returns:
            Posterior (alpha, beta) parameters
        
        The beauty of conjugate priors: just add the observations!
        """
        alpha_post = self.alpha_prior + successes
        beta_post = self.beta_prior + failures
        return alpha_post, beta_post
    
    def sample_posterior(self, alpha: float, beta: float, n_samples: int = 10000) -> List[float]:
        """
        Draw samples from Beta posterior distribution.
        
        Args:
            alpha: Posterior alpha parameter
            beta: Posterior beta parameter
            n_samples: Number of samples to draw
        
        Returns:
            List of sampled conversion rates
        
        Using the built-in random.betavariate because why reinvent the wheel.
        """
        return [random.betavariate(alpha, beta) for _ in range(n_samples)]
    
    def probability_b_beats_a(self, alpha_a: float, beta_a: float,
                             alpha_b: float, beta_b: float,
                             n_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        Args:
            alpha_a, beta_a: Posterior parameters for variant A
            alpha_b, beta_b: Posterior parameters for variant B
            n_samples: Number of Monte Carlo samples
        
        Returns:
            Probability that B's conversion rate exceeds A's
        
        Could do this analytically but sampling is easier to reason about
        and works for any distribution, not just Beta.
        """
        samples_a = self.sample_posterior(alpha_a, beta_a, n_samples)
        samples_b = self.sample_posterior(alpha_b, beta_b, n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples
    
    def expected_loss(self, alpha_a: float, beta_a: float,
                     alpha_b: float, beta_b: float,
                     n_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate expected loss if we pick the wrong variant.
        
        Args:
            alpha_a, beta_a: Posterior parameters for variant A
            alpha_b, beta_b: Posterior parameters for variant B
            n_samples: Number of Monte Carlo samples
        
        Returns:
            (expected_loss_a, expected_loss_b) - loss if we choose that variant
        
        Expected loss tells us: "If I choose A but B is actually better,
        how much conversion rate am I giving up on average?"
        """
        samples_a = self.sample_posterior(alpha_a, beta_a, n_samples)
        samples_b = self.sample_posterior(alpha_b, beta_b, n_samples)
        
        # Loss if we choose A = max(0, B - A) when B > A
        loss_a = sum(max(0, b - a) for a, b in zip(samples_a, samples_b)) / n_samples
        
        # Loss if we choose B = max(0, A - B) when A > B
        loss_b = sum(max(0, a - b) for a, b in zip(samples_a, samples_b)) / n_samples
        
        return loss_a, loss_b
    
    def credible_interval(self, alpha: float, beta: float, 
                         confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate credible interval (Bayesian confidence interval).
        
        Args:
            alpha: Posterior alpha parameter
            beta: Posterior beta parameter
            confidence: Desired confidence level (default 0.95)
        
        Returns:
            (lower_bound, upper_bound) of credible interval
        
        This is what the confidence interval *should* mean: 95% probability
        the true value is in this range, given our data.
        """
        samples = sorted(self.sample_posterior(alpha, beta, 10000))
        tail = (1 - confidence) / 2
        lower_idx = int(tail * len(samples))
        upper_idx = int((1 - tail) * len(samples))
        return samples[lower_idx], samples[upper_idx]


def run_ab_test_demo():
    """
    Demo showing a realistic A/B test scenario.
    
    Imagine I'm testing two landing page variants on my personal site.
    Variant A is the control, B is my new design.
    """
    print("=== Bayesian A/B Test Demo ===\n")
    
    # My test data (made up but realistic)
    visitors_a = 1000
    conversions_a = 47  # 4.7% conversion
    
    visitors_b = 1000
    conversions_b = 58  # 5.8% conversion
    
    print(f"Variant A: {conversions_a}/{visitors_a} conversions ({conversions_a/visitors_a*100:.1f}%)")
    print(f"Variant B: {conversions_b}/{visitors_b} conversions ({conversions_b/visitors_b*100:.1f}%)")
    print()
    
    # Run the Bayesian analysis
    tester = BayesianABTest(alpha_prior=1, beta_prior=1)
    
    # Update beliefs with observed data
    alpha_a, beta_a = tester.update(conversions_a, visitors_a - conversions_a)
    alpha_b, beta_b = tester.update(conversions_b, visitors_b - conversions_b)
    
    print(f"Posterior A: Beta({alpha_a:.1f}, {beta_a:.1f})")
    print(f"Posterior B: Beta({alpha_b:.1f}, {beta_b:.1f})")
    print()
    
    # What's the probability B is actually better?
    prob_b_wins = tester.probability_b_beats_a(alpha_a, beta_a, alpha_b, beta_b)
    print(f"P(B > A) = {prob_b_wins:.1%}")
    print()
    
    # How much am I risking if I choose wrong?
    loss_a, loss_b = tester.expected_loss(alpha_a, beta_a, alpha_b, beta_b)
    print(f"Expected loss if choosing A: {loss_a*100:.3f} percentage points")
    print(f"Expected loss if choosing B: {loss_b*100:.3f} percentage points")
    print()
    
    # Give me credible intervals
    ci_a = tester.credible_interval(alpha_a, beta_a)
    ci_b = tester.credible_interval(alpha_b, beta_b)
    print(f"95% credible interval for A: [{ci_a[0]*100:.1f}%, {ci_a[1]*100:.1f}%]")
    print(f"95% credible interval for B: [{ci_b[0]*100:.1f}%, {ci_b[1]*100:.1f}%]")
    print()
    
    # My decision rule: ship if P(B > A) > 0.95 and expected loss < 0.1%
    if prob_b_wins > 0.95 and loss_b < 0.001:
        print("✓ DECISION: Ship variant B — high confidence and low risk")
    elif prob_b_wins < 0.05 and loss_a < 0.001:
        print("✗ DECISION: Stick with A — B is likely worse")
    else:
        print("⚠ DECISION: Keep testing — not enough evidence yet")


if __name__ == "__main__":
    random.seed(42)  # Reproducible results for the demo
    run_ab_test_demo()