"""
Date: 2026-07-21
Built a bootstrap resampling toolkit to estimate sampling distributions and confidence intervals without assuming normality, which I needed for analyzing some personal project metrics.
"""

#!/usr/bin/env python3
"""
Bootstrap Statistics Module
Implements bootstrap resampling for statistical inference without parametric assumptions.
I built this because I was tired of making normality assumptions for small datasets.
"""

import random
from typing import List, Tuple, Callable
from collections import Counter


def bootstrap_resample(data: List[float], n_samples: int = 10000, 
                       statistic: Callable = None, seed: int = None) -> List[float]:
    """
    Generate bootstrap samples and compute a statistic on each.
    
    Args:
        data: Original dataset
        n_samples: Number of bootstrap samples to generate
        statistic: Function to apply to each sample (default: mean)
        seed: Random seed for reproducibility
    
    Returns:
        List of computed statistics from each bootstrap sample
    """
    if seed is not None:
        random.seed(seed)
    
    if statistic is None:
        statistic = lambda x: sum(x) / len(x)  # mean by default
    
    n = len(data)
    bootstrap_stats = []
    
    for _ in range(n_samples):
        # Sample with replacement
        sample = [random.choice(data) for _ in range(n)]
        bootstrap_stats.append(statistic(sample))
    
    return bootstrap_stats


def confidence_interval(bootstrap_stats: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval from bootstrap distribution.
    
    Uses the percentile method — simple and doesn't assume normality.
    
    Args:
        bootstrap_stats: List of bootstrap statistics
        confidence: Confidence level (e.g., 0.95 for 95%)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    sorted_stats = sorted(bootstrap_stats)
    n = len(sorted_stats)
    
    alpha = 1 - confidence
    lower_idx = int(n * (alpha / 2))
    upper_idx = int(n * (1 - alpha / 2))
    
    return sorted_stats[lower_idx], sorted_stats[upper_idx]


def bootstrap_hypothesis_test(data1: List[float], data2: List[float], 
                              n_samples: int = 10000, seed: int = None) -> float:
    """
    Test if two samples have different means using bootstrap permutation test.
    
    This is a non-parametric alternative to t-test. I like it because it doesn't
    care about your data distribution.
    
    Args:
        data1: First sample
        data2: Second sample
        n_samples: Number of permutations
        seed: Random seed
    
    Returns:
        p-value: proportion of permuted differences >= observed difference
    """
    if seed is not None:
        random.seed(seed)
    
    # Observed difference in means
    mean1 = sum(data1) / len(data1)
    mean2 = sum(data2) / len(data2)
    observed_diff = abs(mean1 - mean2)
    
    # Pool the data for permutation
    pooled = data1 + data2
    n1 = len(data1)
    
    # Generate permuted differences
    count_extreme = 0
    for _ in range(n_samples):
        # Shuffle and split
        shuffled = pooled[:]
        random.shuffle(shuffled)
        
        perm_sample1 = shuffled[:n1]
        perm_sample2 = shuffled[n1:]
        
        perm_mean1 = sum(perm_sample1) / len(perm_sample1)
        perm_mean2 = sum(perm_sample2) / len(perm_sample2)
        perm_diff = abs(perm_mean1 - perm_mean2)
        
        if perm_diff >= observed_diff:
            count_extreme += 1
    
    p_value = count_extreme / n_samples
    return p_value


def bootstrap_std_error(data: List[float], n_samples: int = 10000, 
                       statistic: Callable = None, seed: int = None) -> float:
    """
    Estimate standard error of a statistic using bootstrap.
    
    Standard error tells you how much your statistic would vary across
    repeated sampling from the population.
    
    Args:
        data: Original dataset
        n_samples: Number of bootstrap samples
        statistic: Function to compute on each sample
        seed: Random seed
    
    Returns:
        Estimated standard error
    """
    bootstrap_stats = bootstrap_resample(data, n_samples, statistic, seed)
    
    # Standard deviation of bootstrap distribution = standard error
    mean_stat = sum(bootstrap_stats) / len(bootstrap_stats)
    variance = sum((x - mean_stat) ** 2 for x in bootstrap_stats) / (len(bootstrap_stats) - 1)
    std_error = variance ** 0.5
    
    return std_error


def bootstrap_bias(data: List[float], n_samples: int = 10000,
                   statistic: Callable = None, seed: int = None) -> float:
    """
    Estimate bias of a statistic using bootstrap.
    
    Bias is the difference between the expected value of your estimator
    and the true parameter. Bootstrap gives us an empirical estimate.
    
    Args:
        data: Original dataset
        n_samples: Number of bootstrap samples
        statistic: Function to compute on each sample
        seed: Random seed
    
    Returns:
        Estimated bias
    """
    if statistic is None:
        statistic = lambda x: sum(x) / len(x)
    
    # Original statistic
    original_stat = statistic(data)
    
    # Bootstrap distribution
    bootstrap_stats = bootstrap_resample(data, n_samples, statistic, seed)
    mean_bootstrap = sum(bootstrap_stats) / len(bootstrap_stats)
    
    # Bias = E[statistic*] - statistic(original)
    bias = mean_bootstrap - original_stat
    
    return bias


if __name__ == "__main__":
    # Demo with a real-world-ish scenario
    print("=== Bootstrap Statistics Demo ===\n")
    
    # Simulating response times from two different server configurations (ms)
    server_a = [120, 135, 128, 142, 131, 125, 138, 129, 133, 127]
    server_b = [145, 158, 152, 163, 149, 156, 161, 150, 154, 159]
    
    print("Server A response times:", server_a)
    print("Server B response times:", server_b)
    print()
    
    # Bootstrap confidence interval for Server A mean
    bootstrap_means_a = bootstrap_resample(server_a, n_samples=5000, seed=42)
    ci_lower, ci_upper = confidence_interval(bootstrap_means_a, confidence=0.95)
    
    print(f"Server A mean: {sum(server_a) / len(server_a):.2f} ms")
    print(f"95% Bootstrap CI: [{ci_lower:.2f}, {ci_upper:.2f}] ms")
    print()
    
    # Standard error estimation
    std_err = bootstrap_std_error(server_a, n_samples=5000, seed=42)
    print(f"Standard error of mean: {std_err:.2f} ms")
    print()
    
    # Hypothesis test: are the servers significantly different?
    p_value = bootstrap_hypothesis_test(server_a, server_b, n_samples=5000, seed=42)
    print(f"Hypothesis test (Server A vs B):")
    print(f"  p-value = {p_value:.4f}")
    
    if p_value < 0.05:
        print("  Result: Servers have significantly different response times (p < 0.05)")
    else:
        print("  Result: No significant difference detected (p >= 0.05)")
    print()
    
    # Bootstrap for median (more robust to outliers)
    median_func = lambda x: sorted(x)[len(x) // 2]
    bootstrap_medians = bootstrap_resample(server_a, n_samples=5000, 
                                          statistic=median_func, seed=42)
    median_ci_lower, median_ci_upper = confidence_interval(bootstrap_medians)
    
    print(f"Server A median: {median_func(server_a):.2f} ms")
    print(f"95% Bootstrap CI for median: [{median_ci_lower:.2f}, {median_ci_upper:.2f}] ms")
```