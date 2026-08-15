"""
Date: 2026-08-15
Implemented a Bayesian A/B testing tool using beta distributions to calculate posterior probabilities and credible intervals — finally ditching p-value madness for something interpretable.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
Implements Beta-Binomial conjugate prior analysis for conversion rate testing.
Also includes a basic bootstrap resampling utility for non-parametric stats.
"""

import random
import math
from typing import List, Tuple


class BayesianABTest:
    """
    A/B test analyzer using Bayesian inference with Beta-Binomial conjugate priors.
    
    The Beta distribution is perfect for modeling conversion rates because it's
    bounded between 0 and 1, and updating with new data is trivial (just add counts).
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs (uniform by default).
        
        Args:
            alpha_prior: Prior successes (alpha=1, beta=1 is uniform/uninformative)
            beta_prior: Prior failures
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
    
    def update_posterior(self, successes: int, trials: int) -> Tuple[float, float]:
        """
        Calculate posterior distribution parameters after observing data.
        
        This is the beauty of conjugate priors — posterior is also Beta distributed.
        Just add observed successes to alpha and failures to beta.
        """
        failures = trials - successes
        alpha_post = self.alpha_prior + successes
        beta_post = self.beta_prior + failures
        return alpha_post, beta_post
    
    def posterior_mean(self, alpha_post: float, beta_post: float) -> float:
        """Expected value (mean) of the posterior Beta distribution."""
        return alpha_post / (alpha_post + beta_post)
    
    def credible_interval(self, alpha_post: float, beta_post: float, 
                         confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate Bayesian credible interval using quantile approximation.
        
        For Beta distributions, I'm using a normal approximation which works well
        when we have enough data. For small samples, you'd want the actual beta quantile.
        """
        mean = self.posterior_mean(alpha_post, beta_post)
        # Variance of Beta(a, b) is ab/((a+b)^2(a+b+1))
        variance = (alpha_post * beta_post) / (
            (alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1)
        )
        std = math.sqrt(variance)
        
        # Normal approximation for the credible interval
        z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
        lower = max(0, mean - z_score * std)
        upper = min(1, mean + z_score * std)
        return lower, upper
    
    def probability_b_beats_a(self, alpha_a: float, beta_a: float,
                              alpha_b: float, beta_b: float,
                              samples: int = 10000) -> float:
        """
        Monte Carlo simulation to estimate P(B > A).
        
        I sample from both posterior distributions and count how often B wins.
        This is way more intuitive than a p-value — it directly answers "what's
        the probability that variant B is actually better?"
        """
        a_samples = [self._sample_beta(alpha_a, beta_a) for _ in range(samples)]
        b_samples = [self._sample_beta(alpha_b, beta_b) for _ in range(samples)]
        
        b_wins = sum(1 for a, b in zip(a_samples, b_samples) if b > a)
        return b_wins / samples
    
    def _sample_beta(self, alpha: float, beta: float) -> float:
        """
        Sample from Beta distribution using the gamma relationship.
        Beta(a,b) = Gamma(a) / (Gamma(a) + Gamma(b))
        """
        # Using the standard library's gammavariate
        gamma_a = random.gammavariate(alpha, 1)
        gamma_b = random.gammavariate(beta, 1)
        return gamma_a / (gamma_a + gamma_b)


def bootstrap_confidence_interval(data: List[float], statistic_func=None,
                                  n_iterations: int = 1000,
                                  confidence: float = 0.95) -> Tuple[float, float]:
    """
    Bootstrap resampling to estimate confidence intervals for any statistic.
    
    This is my go-to when I don't want to assume normality or figure out
    analytical formulas. Just resample with replacement and see what happens.
    
    Args:
        data: Original sample data
        statistic_func: Function to compute on each bootstrap sample (default: mean)
        n_iterations: Number of bootstrap samples to draw
        confidence: Confidence level (0.95 = 95%)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if statistic_func is None:
        statistic_func = lambda x: sum(x) / len(x)  # mean
    
    bootstrap_statistics = []
    n = len(data)
    
    for _ in range(n_iterations):
        # Resample with replacement
        resample = [random.choice(data) for _ in range(n)]
        bootstrap_statistics.append(statistic_func(resample))
    
    bootstrap_statistics.sort()
    
    # Percentile method for confidence interval
    alpha = 1 - confidence
    lower_idx = int(n_iterations * (alpha / 2))
    upper_idx = int(n_iterations * (1 - alpha / 2))
    
    return bootstrap_statistics[lower_idx], bootstrap_statistics[upper_idx]


if __name__ == "__main__":
    print("=" * 60)
    print("Bayesian A/B Test Analysis Demo")
    print("=" * 60)
    
    # Simulating a real A/B test scenario
    # Variant A: 120 conversions out of 1000 visitors
    # Variant B: 145 conversions out of 1000 visitors
    
    visitors_a, conversions_a = 1000, 120
    visitors_b, conversions_b = 1000, 145
    
    print(f"\nVariant A: {conversions_a}/{visitors_a} conversions ({conversions_a/visitors_a:.1%})")
    print(f"Variant B: {conversions_b}/{visitors_b} conversions ({conversions_b/visitors_b:.1%})")
    
    # Initialize Bayesian analyzer with uniform prior
    ab_test = BayesianABTest(alpha_prior=1.0, beta_prior=1.0)
    
    # Calculate posteriors
    alpha_a, beta_a = ab_test.update_posterior(conversions_a, visitors_a)
    alpha_b, beta_b = ab_test.update_posterior(conversions_b, visitors_b)
    
    mean_a = ab_test.posterior_mean(alpha_a, beta_a)
    mean_b = ab_test.posterior_mean(alpha_b, beta_b)
    
    ci_a = ab_test.credible_interval(alpha_a, beta_a)
    ci_b = ab_test.credible_interval(alpha_b, beta_b)
    
    print(f"\nPosterior Estimates:")
    print(f"  Variant A: {mean_a:.3f} (95% CI: [{ci_a[0]:.3f}, {ci_a[1]:.3f}])")
    print(f"  Variant B: {mean_b:.3f} (95% CI: [{ci_b[0]:.3f}, {ci_b[1]:.3f}])")
    
    # The money question: how likely is B better than A?
    prob_b_wins = ab_test.probability_b_beats_a(alpha_a, beta_a, alpha_b, beta_b)
    print(f"\nProbability that B beats A: {prob_b_wins:.1%}")
    
    if prob_b_wins > 0.95:
        print("→ Strong evidence for B! Ship it.")
    elif prob_b_wins > 0.80:
        print("→ Moderate evidence for B. Maybe collect more data.")
    else:
        print("→ Not enough evidence. Keep testing or stick with A.")
    
    # Bootstrap demo with some sample data
    print("\n" + "=" * 60)
    print("Bootstrap Confidence Interval Demo")
    print("=" * 60)
    
    # Simulating response times (definitely not normal distribution)
    response_times = [random.expovariate(1/200) for _ in range(50)]
    observed_median = sorted(response_times)[len(response_times) // 2]
    
    # Bootstrap CI for the median
    ci_lower, ci_upper = bootstrap_confidence_interval(
        response_times,
        statistic_func=lambda x: sorted(x)[len(x) // 2],
        n_iterations=2000
    )
    
    print(f"\nObserved median response time: {observed_median:.1f}ms")
    print(f"95% Bootstrap CI: [{ci_lower:.1f}ms, {ci_upper:.1f}ms]")
    print("\n(Bootstrap is great when you don't want to assume normality!)")