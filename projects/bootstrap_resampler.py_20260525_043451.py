# Lets you estimate confidence intervals for stats using bootstrap resampling, pretty handy for when you don't want to assume normal distributions.
# written: 2026-05-25

"""
Bootstrap resampling module for statistical inference.

Mario's experiments with non-parametric statistics.
"""

import random
import statistics
from typing import List, Callable, Tuple


def bootstrap_resample(data: List[float], statistic: Callable, n_iterations: int = 10000, 
                       confidence_level: float = 0.95, seed: int = None) -> dict:
    """
    Perform bootstrap resampling to estimate confidence intervals.
    
    Args:
        data: The original dataset
        statistic: Function that computes the statistic (e.g., statistics.mean)
        n_iterations: Number of bootstrap samples to generate
        confidence_level: Confidence level for the interval (default 95%)
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with original statistic, bootstrap estimates, and CI
    """
    if seed is not None:
        random.seed(seed)
    
    n = len(data)
    bootstrap_stats = []
    
    # Generate bootstrap samples and compute statistic for each
    for _ in range(n_iterations):
        # Resample with replacement
        sample = [random.choice(data) for _ in range(n)]
        bootstrap_stats.append(statistic(sample))
    
    bootstrap_stats.sort()
    
    # Calculate confidence interval using percentile method
    alpha = 1 - confidence_level
    lower_idx = int(n_iterations * (alpha / 2))
    upper_idx = int(n_iterations * (1 - alpha / 2))
    
    return {
        'original_statistic': statistic(data),
        'bootstrap_mean': statistics.mean(bootstrap_stats),
        'confidence_interval': (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx]),
        'confidence_level': confidence_level,
        'n_iterations': n_iterations
    }


def compare_means(group1: List[float], group2: List[float], n_iterations: int = 10000, 
                  seed: int = None) -> dict:
    """
    Test if two groups have different means using bootstrap.
    
    This is basically a permutation test approach - we check if the observed
    difference could have happened by chance.
    
    Args:
        group1: First group of observations
        group2: Second group of observations
        n_iterations: Number of permutations
        seed: Random seed
        
    Returns:
        Dictionary with test results and p-value estimate
    """
    if seed is not None:
        random.seed(seed)
    
    observed_diff = statistics.mean(group1) - statistics.mean(group2)
    
    # Pool all data together
    combined = group1 + group2
    n1 = len(group1)
    
    # Count how many times we see a difference as extreme or more
    extreme_count = 0
    
    for _ in range(n_iterations):
        # Shuffle and split
        shuffled = combined.copy()
        random.shuffle(shuffled)
        perm_group1 = shuffled[:n1]
        perm_group2 = shuffled[n1:]
        
        perm_diff = statistics.mean(perm_group1) - statistics.mean(perm_group2)
        
        # Two-tailed test
        if abs(perm_diff) >= abs(observed_diff):
            extreme_count += 1
    
    p_value = extreme_count / n_iterations
    
    return {
        'observed_difference': observed_diff,
        'p_value': p_value,
        'n_iterations': n_iterations,
        'significant_at_0.05': p_value < 0.05
    }


def jackknife_variance(data: List[float], statistic: Callable) -> Tuple[float, float]:
    """
    Estimate the variance of a statistic using jackknife resampling.
    
    Jackknife is like bootstrap's older cousin - instead of sampling with replacement,
    we systematically leave out one observation at a time.
    
    Args:
        data: The dataset
        statistic: Function to compute the statistic
        
    Returns:
        Tuple of (estimated statistic, estimated standard error)
    """
    n = len(data)
    jackknife_stats = []
    
    # Leave-one-out resampling
    for i in range(n):
        sample = data[:i] + data[i+1:]
        jackknife_stats.append(statistic(sample))
    
    # Jackknife estimate and variance
    jack_mean = statistics.mean(jackknife_stats)
    jack_variance = ((n - 1) / n) * sum((x - jack_mean)**2 for x in jackknife_stats)
    jack_se = jack_variance ** 0.5
    
    return statistic(data), jack_se


if __name__ == "__main__":
    print("=== Bootstrap Resampling Demo ===\n")
    
    # Example 1: Confidence interval for mean
    print("1. Estimating confidence interval for mean:")
    sample_data = [23, 25, 28, 29, 30, 31, 32, 34, 35, 36, 38, 40, 42]
    result = bootstrap_resample(sample_data, statistics.mean, n_iterations=10000, seed=42)
    
    print(f"   Original mean: {result['original_statistic']:.2f}")
    print(f"   Bootstrap mean: {result['bootstrap_mean']:.2f}")
    print(f"   95% CI: ({result['confidence_interval'][0]:.2f}, {result['confidence_interval'][1]:.2f})")
    
    # Example 2: Confidence interval for median (non-parametric!)
    print("\n2. Estimating confidence interval for median:")
    result_median = bootstrap_resample(sample_data, statistics.median, n_iterations=10000, seed=42)
    print(f"   Original median: {result_median['original_statistic']:.2f}")
    print(f"   95% CI: ({result_median['confidence_interval'][0]:.2f}, {result_median['confidence_interval'][1]:.2f})")
    
    # Example 3: Comparing two groups
    print("\n3. Comparing means of two groups:")
    control = [20, 22, 25, 27, 28, 30, 32]
    treatment = [28, 30, 33, 35, 36, 38, 40, 42]
    
    comparison = compare_means(control, treatment, n_iterations=10000, seed=42)
    print(f"   Control mean: {statistics.mean(control):.2f}")
    print(f"   Treatment mean: {statistics.mean(treatment):.2f}")
    print(f"   Observed difference: {comparison['observed_difference']:.2f}")
    print(f"   P-value: {comparison['p_value']:.4f}")
    print(f"   Significant? {comparison['significant_at_0.05']}")
    
    # Example 4: Jackknife standard error
    print("\n4. Jackknife standard error estimation:")
    stat, se = jackknife_variance(sample_data, statistics.mean)
    print(f"   Mean: {stat:.2f}")
    print(f"   Standard error: {se:.2f}")