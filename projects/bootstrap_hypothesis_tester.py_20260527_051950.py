"""
Date: 2026-05-27
Implemented bootstrap resampling from scratch to estimate confidence intervals and run hypothesis tests without assuming normal distributions — way more robust than t-tests for weird data.
"""

"""
Bootstrap resampling and hypothesis testing module.

I kept running into situations where my data didn't look normal at all,
and parametric tests felt sketchy. Bootstrap resampling lets you estimate
sampling distributions empirically, which is super useful for real-world data.
"""

import random
import statistics
from typing import List, Callable, Tuple, Optional


class BootstrapResampler:
    """
    Performs bootstrap resampling to estimate confidence intervals and test hypotheses.
    
    Bootstrap resampling works by sampling with replacement from your data
    to create many "pseudo-samples" that mimic the sampling distribution.
    """
    
    def __init__(self, data: List[float], n_resamples: int = 10000, seed: Optional[int] = None):
        """
        Initialize the bootstrap resampler.
        
        Args:
            data: Original sample data
            n_resamples: Number of bootstrap samples to generate
            seed: Random seed for reproducibility
        """
        self.data = data
        self.n_resamples = n_resamples
        if seed is not None:
            random.seed(seed)
    
    def resample(self) -> List[float]:
        """Generate a single bootstrap sample by sampling with replacement."""
        return random.choices(self.data, k=len(self.data))
    
    def bootstrap_statistic(self, statistic_func: Callable[[List[float]], float]) -> List[float]:
        """
        Compute a statistic on many bootstrap samples.
        
        Args:
            statistic_func: Function that takes a list and returns a scalar statistic
            
        Returns:
            List of bootstrap statistic values
        """
        bootstrap_stats = []
        for _ in range(self.n_resamples):
            sample = self.resample()
            bootstrap_stats.append(statistic_func(sample))
        return bootstrap_stats
    
    def confidence_interval(
        self, 
        statistic_func: Callable[[List[float]], float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval for a statistic.
        
        Uses the percentile method — simple and intuitive.
        
        Args:
            statistic_func: Function to compute statistic
            confidence_level: Confidence level (e.g., 0.95 for 95% CI)
            
        Returns:
            Tuple of (point_estimate, lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(statistic_func)
        bootstrap_stats.sort()
        
        # Calculate percentiles for the confidence interval
        alpha = 1 - confidence_level
        lower_idx = int(self.n_resamples * alpha / 2)
        upper_idx = int(self.n_resamples * (1 - alpha / 2))
        
        point_estimate = statistic_func(self.data)
        lower_bound = bootstrap_stats[lower_idx]
        upper_bound = bootstrap_stats[upper_idx]
        
        return point_estimate, lower_bound, upper_bound


def bootstrap_hypothesis_test(
    group_a: List[float],
    group_b: List[float],
    statistic_func: Callable[[List[float]], float] = statistics.mean,
    n_resamples: int = 10000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Perform a bootstrap hypothesis test comparing two groups.
    
    Tests the null hypothesis that both groups come from the same distribution.
    We pool the data, resample under the null, and see how extreme our
    observed difference is.
    
    Args:
        group_a: First group of observations
        group_b: Second group of observations
        statistic_func: Function to compute the statistic (default: mean)
        n_resamples: Number of bootstrap resamples
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (observed_difference, p_value)
    """
    if seed is not None:
        random.seed(seed)
    
    # Calculate observed difference
    observed_diff = abs(statistic_func(group_a) - statistic_func(group_b))
    
    # Pool the data under the null hypothesis
    pooled = group_a + group_b
    n_a = len(group_a)
    n_b = len(group_b)
    
    # Generate bootstrap samples under the null
    null_diffs = []
    for _ in range(n_resamples):
        # Shuffle and split to simulate null hypothesis
        shuffled = random.sample(pooled, len(pooled))
        bootstrap_a = shuffled[:n_a]
        bootstrap_b = shuffled[n_a:]
        
        diff = abs(statistic_func(bootstrap_a) - statistic_func(bootstrap_b))
        null_diffs.append(diff)
    
    # Calculate p-value: proportion of null diffs >= observed diff
    p_value = sum(1 for d in null_diffs if d >= observed_diff) / n_resamples
    
    return observed_diff, p_value


def median_absolute_deviation(data: List[float]) -> float:
    """
    Calculate the Median Absolute Deviation (MAD).
    
    More robust to outliers than standard deviation. I use this a lot
    when dealing with noisy sensor data.
    """
    median = statistics.median(data)
    deviations = [abs(x - median) for x in data]
    return statistics.median(deviations)


if __name__ == "__main__":
    print("=== Bootstrap Resampling Demo ===\n")
    
    # Simulating some experiment data that's not normally distributed
    # Let's say these are page load times (in seconds) before and after optimization
    before_optimization = [2.3, 3.1, 2.8, 4.5, 2.9, 3.3, 2.7, 5.1, 3.0, 2.6, 
                          3.8, 2.9, 3.2, 4.0, 2.8, 3.1, 2.9, 3.4, 2.7, 3.0]
    
    after_optimization = [2.1, 2.5, 2.3, 2.8, 2.4, 2.6, 2.2, 2.9, 2.3, 2.1,
                         2.7, 2.4, 2.5, 2.6, 2.2, 2.4, 2.3, 2.5, 2.1, 2.4]
    
    print("Page load times before optimization (seconds):")
    print(f"  Mean: {statistics.mean(before_optimization):.2f}")
    print(f"  Median: {statistics.median(before_optimization):.2f}")
    print(f"  MAD: {median_absolute_deviation(before_optimization):.2f}\n")
    
    # Bootstrap confidence interval for the mean after optimization
    print("Bootstrap 95% CI for mean load time AFTER optimization:")
    resampler = BootstrapResampler(after_optimization, n_resamples=10000, seed=42)
    estimate, lower, upper = resampler.confidence_interval(statistics.mean, confidence_level=0.95)
    print(f"  Point estimate: {estimate:.3f} seconds")
    print(f"  95% CI: [{lower:.3f}, {upper:.3f}] seconds\n")
    
    # Hypothesis test: did optimization actually help?
    print("Hypothesis test: Before vs. After optimization")
    print("  H0: No difference in load times")
        
    observed_diff, p_value = bootstrap_hypothesis_test(
        before_optimization,
        after_optimization,
        statistic_func=statistics.mean,
        n_resamples=10000,
        seed=42
    )
    
    print(f"  Observed difference in means: {observed_diff:.3f} seconds")
    print(f"  Bootstrap p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("  ✓ Significant difference detected (p < 0.05)")
        print("    The optimization appears to have worked!")
    else:
        print("  ✗ No significant difference (p >= 0.05)")
    
    # Also test with median for robustness
    print("\nUsing median instead of mean (more robust to outliers):")
    observed_diff_med, p_value_med = bootstrap_hypothesis_test(
        before_optimization,
        after_optimization,
        statistic_func=statistics.median,
        n_resamples=10000,
        seed=42
    )
    print(f"  Observed difference in medians: {observed_diff_med:.3f} seconds")
    print(f"  Bootstrap p-value: {p_value_med:.4f}")