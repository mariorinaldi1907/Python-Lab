"""
Date: 2026-06-06
Built a bootstrapping module to compute confidence intervals without assuming normal distributions — really useful for small or skewed datasets.
"""

#!/usr/bin/env python3
"""
Bootstrap resampling implementation for statistical inference.

I wrote this because I often have small datasets where I can't assume normality,
and bootstrapping gives me confidence intervals without those assumptions.
"""

import random
import statistics
from typing import Callable, List, Tuple


def bootstrap_resample(data: List[float], n_iterations: int = 10000, 
                       statistic: Callable = statistics.mean, 
                       confidence_level: float = 0.95,
                       seed: int = None) -> Tuple[float, Tuple[float, float]]:
    """
    Perform bootstrap resampling to estimate confidence intervals.
    
    The idea is simple: repeatedly sample with replacement from the data,
    calculate the statistic each time, then use percentiles of those
    bootstrap statistics as confidence interval bounds.
    
    Args:
        data: Original dataset (list of numbers)
        n_iterations: Number of bootstrap samples to generate
        statistic: Function to compute on each resample (mean, median, etc.)
        confidence_level: Confidence level (e.g., 0.95 for 95% CI)
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (point_estimate, (lower_bound, upper_bound))
    """
    if seed is not None:
        random.seed(seed)
    
    n = len(data)
    bootstrap_statistics = []
    
    # Generate bootstrap samples and compute statistic for each
    for _ in range(n_iterations):
        # Sample with replacement - this is the core of bootstrapping
        resample = [random.choice(data) for _ in range(n)]
        bootstrap_statistics.append(statistic(resample))
    
    # Calculate confidence interval using percentile method
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    bootstrap_statistics.sort()
    lower_idx = int(n_iterations * alpha / 2)
    upper_idx = int(n_iterations * (1 - alpha / 2))
    
    point_estimate = statistic(data)
    ci_lower = bootstrap_statistics[lower_idx]
    ci_upper = bootstrap_statistics[upper_idx]
    
    return point_estimate, (ci_lower, ci_upper)


def bootstrap_hypothesis_test(data1: List[float], data2: List[float],
                              n_iterations: int = 10000,
                              statistic: Callable = statistics.mean,
                              seed: int = None) -> float:
    """
    Perform a permutation test to compare two samples.
    
    This tests the null hypothesis that both samples come from the same
    distribution by randomly shuffling labels between groups and seeing
    how extreme the observed difference is.
    
    Args:
        data1: First sample
        data2: Second sample
        n_iterations: Number of permutations
        statistic: Function to compute (usually mean or median)
        seed: Random seed
    
    Returns:
        p-value (proportion of permutations with difference >= observed)
    """
    if seed is not None:
        random.seed(seed)
    
    # Calculate observed difference
    observed_diff = abs(statistic(data1) - statistic(data2))
    
    # Combine all data for permutation
    combined = data1 + data2
    n1 = len(data1)
    
    # Count how many permutations give a difference >= observed
    extreme_count = 0
    
    for _ in range(n_iterations):
        # Shuffle and split into two groups
        shuffled = combined.copy()
        random.shuffle(shuffled)
        perm_group1 = shuffled[:n1]
        perm_group2 = shuffled[n1:]
        
        perm_diff = abs(statistic(perm_group1) - statistic(perm_group2))
        
        if perm_diff >= observed_diff:
            extreme_count += 1
    
    return extreme_count / n_iterations


def jackknife_variance(data: List[float], statistic: Callable = statistics.mean) -> float:
    """
    Estimate variance of a statistic using jackknife resampling.
    
    Jackknife is an older technique than bootstrap but still useful.
    It systematically leaves out one observation at a time and computes
    the statistic on the remaining data.
    
    Args:
        data: Original dataset
        statistic: Function to compute variance for
    
    Returns:
        Estimated variance of the statistic
    """
    n = len(data)
    jackknife_statistics = []
    
    # Leave one out at a time
    for i in range(n):
        # Create sample without the i-th element
        sample = data[:i] + data[i+1:]
        jackknife_statistics.append(statistic(sample))
    
    # Jackknife variance formula
    mean_jackknife = statistics.mean(jackknife_statistics)
    variance = ((n - 1) / n) * sum((x - mean_jackknife) ** 2 
                                    for x in jackknife_statistics)
    
    return variance


if __name__ == "__main__":
    # Demo with some real-world-ish data
    # Let's say these are response times in milliseconds for a web service
    response_times = [
        45, 52, 48, 51, 49, 53, 47, 50, 46, 54,
        48, 49, 51, 50, 52, 200, 48, 49, 50, 51  # Note the outlier at 200ms
    ]
    
    print("Bootstrap Confidence Intervals Demo")
    print("=" * 50)
    print(f"Dataset: {response_times}")
    print(f"Sample size: {len(response_times)}")
    print()
    
    # Bootstrap for mean (sensitive to outliers)
    mean_est, mean_ci = bootstrap_resample(
        response_times, 
        n_iterations=10000,
        statistic=statistics.mean,
        confidence_level=0.95,
        seed=42
    )
    print(f"Mean estimate: {mean_est:.2f}ms")
    print(f"95% CI for mean: ({mean_ci[0]:.2f}, {mean_ci[1]:.2f})ms")
    print()
    
    # Bootstrap for median (robust to outliers)
    median_est, median_ci = bootstrap_resample(
        response_times,
        n_iterations=10000,
        statistic=statistics.median,
        confidence_level=0.95,
        seed=42
    )
    print(f"Median estimate: {median_est:.2f}ms")
    print(f"95% CI for median: ({median_ci[0]:.2f}, {median_ci[1]:.2f})ms")
    print()
    
    # Compare two samples - did the new cache help?
    before_cache = [52, 48, 51, 49, 53, 47, 50, 46, 54, 48]
    after_cache = [38, 42, 40, 39, 41, 43, 38, 40, 42, 39]
    
    print("Hypothesis Testing Demo")
    print("=" * 50)
    print(f"Response times before cache: {before_cache}")
    print(f"Response times after cache: {after_cache}")
    print()
    
    p_value = bootstrap_hypothesis_test(
        before_cache,
        after_cache,
        n_iterations=10000,
        statistic=statistics.mean,
        seed=42
    )
    print(f"Permutation test p-value: {p_value:.4f}")
    print(f"Conclusion: Cache {'significantly' if p_value < 0.05 else 'not significantly'} improved performance")
    print()
    
    # Jackknife variance estimation
    jack_var = jackknife_variance(response_times, statistics.mean)
    print("Jackknife Variance Estimation")
    print("=" * 50)
    print(f"Estimated variance of sample mean: {jack_var:.2f}")
    print(f"Estimated standard error: {jack_var ** 0.5:.2f}")