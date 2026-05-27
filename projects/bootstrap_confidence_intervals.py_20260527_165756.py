"""
Date: 2026-05-27
Built a bootstrapping module to estimate confidence intervals and compare samples without assuming normal distributions — been meaning to play with resampling methods for a while.
"""

#!/usr/bin/env python3
"""
Bootstrap resampling module for statistical inference.

I wanted a simple way to compute confidence intervals and run hypothesis tests
without assuming normality. Bootstrap is great for this — just resample with
replacement and let the empirical distribution tell the story.
"""

import random
from typing import List, Callable, Tuple
from collections import Counter


class BootstrapSampler:
    """
    Handles bootstrap resampling to estimate sampling distributions.
    
    The idea: treat your sample as the population, resample with replacement
    many times, and compute your statistic on each resample. The distribution
    of those statistics approximates the sampling distribution.
    """
    
    def __init__(self, data: List[float], n_iterations: int = 10000, seed: int = None):
        """
        Initialize with data and number of bootstrap iterations.
        
        Args:
            data: Original sample data
            n_iterations: How many bootstrap samples to generate
            seed: Random seed for reproducibility (I like being able to debug)
        """
        self.data = data
        self.n_iterations = n_iterations
        self.n = len(data)
        
        if seed is not None:
            random.seed(seed)
    
    def resample(self) -> List[float]:
        """Generate one bootstrap sample (sample with replacement)."""
        return random.choices(self.data, k=self.n)
    
    def bootstrap_statistic(self, statistic: Callable[[List[float]], float]) -> List[float]:
        """
        Compute a statistic on many bootstrap samples.
        
        Args:
            statistic: Function that takes a list and returns a number
        
        Returns:
            List of statistic values, one per bootstrap iteration
        """
        return [statistic(self.resample()) for _ in range(self.n_iterations)]
    
    def confidence_interval(
        self, 
        statistic: Callable[[List[float]], float], 
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Compute a percentile confidence interval for a statistic.
        
        This is the percentile method — just grab the appropriate quantiles
        from the bootstrap distribution. Simple but effective.
        
        Args:
            statistic: Function to compute on each bootstrap sample
            confidence_level: CI level (0.95 = 95% CI)
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(statistic)
        bootstrap_stats.sort()
        
        # Calculate which indices correspond to our CI bounds
        alpha = 1 - confidence_level
        lower_idx = int(alpha / 2 * self.n_iterations)
        upper_idx = int((1 - alpha / 2) * self.n_iterations)
        
        return (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx])


def mean(data: List[float]) -> float:
    """Compute mean — defining this so I can pass it around as a function."""
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    """Compute median."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def std_dev(data: List[float]) -> float:
    """Compute sample standard deviation."""
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / (len(data) - 1)
    return variance ** 0.5


def bootstrap_two_sample_test(
    sample1: List[float],
    sample2: List[float],
    n_iterations: int = 10000,
    seed: int = None
) -> float:
    """
    Permutation test to check if two samples have different means.
    
    Null hypothesis: both samples come from the same distribution.
    We pool them, shuffle, split, and see how often we get a difference
    as extreme as the observed difference.
    
    Args:
        sample1: First sample
        sample2: Second sample
        n_iterations: Number of permutations
        seed: Random seed
    
    Returns:
        p-value (proportion of permutations with difference >= observed)
    """
    if seed is not None:
        random.seed(seed)
    
    # Observed difference in means
    observed_diff = abs(mean(sample1) - mean(sample2))
    
    # Pool the samples
    pooled = sample1 + sample2
    n1 = len(sample1)
    
    # Count how many times we see a difference as extreme as observed
    extreme_count = 0
    
    for _ in range(n_iterations):
        # Shuffle and split
        shuffled = pooled.copy()
        random.shuffle(shuffled)
        
        perm_sample1 = shuffled[:n1]
        perm_sample2 = shuffled[n1:]
        
        perm_diff = abs(mean(perm_sample1) - mean(perm_sample2))
        
        if perm_diff >= observed_diff:
            extreme_count += 1
    
    return extreme_count / n_iterations


if __name__ == "__main__":
    # Demo with some made-up data
    print("=== Bootstrap Confidence Intervals Demo ===\n")
    
    # Simulating response times for two different API endpoints (in ms)
    api_v1_times = [120, 135, 142, 128, 151, 139, 145, 132, 138, 141, 
                    129, 147, 136, 143, 131, 140, 133, 149, 137, 144]
    
    api_v2_times = [98, 105, 102, 110, 95, 108, 103, 99, 107, 101,
                    96, 109, 104, 100, 106, 97, 111, 103, 102, 105]
    
    print("API v1 response times (ms):", api_v1_times[:5], "...\n")
    
    # Bootstrap confidence intervals for v1 mean and median
    bs = BootstrapSampler(api_v1_times, n_iterations=10000, seed=42)
    
    mean_ci = bs.confidence_interval(mean, confidence_level=0.95)
    median_ci = bs.confidence_interval(median, confidence_level=0.95)
    std_ci = bs.confidence_interval(std_dev, confidence_level=0.95)
    
    print(f"API v1 Mean: {mean(api_v1_times):.2f} ms")
    print(f"  95% CI: [{mean_ci[0]:.2f}, {mean_ci[1]:.2f}]\n")
    
    print(f"API v1 Median: {median(api_v1_times):.2f} ms")
    print(f"  95% CI: [{median_ci[0]:.2f}, {median_ci[1]:.2f}]\n")
    
    print(f"API v1 Std Dev: {std_dev(api_v1_times):.2f} ms")
    print(f"  95% CI: [{std_ci[0]:.2f}, {std_ci[1]:.2f}]\n")
    
    # Two-sample test: is v2 actually faster than v1?
    print("=== Comparing API v1 vs v2 ===\n")
    print(f"API v2 Mean: {mean(api_v2_times):.2f} ms")
    
    p_value = bootstrap_two_sample_test(api_v1_times, api_v2_times, 
                                        n_iterations=10000, seed=42)
    
    print(f"\nTwo-sample permutation test p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Result: Statistically significant difference (p < 0.05)")
        print("v2 is legitimately faster — time to deprecate v1!")
    else:
        print("Result: No significant difference (p >= 0.05)")