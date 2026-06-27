"""
Date: 2026-06-27
Built a bootstrap and permutation testing module from scratch because I wanted to actually understand what's happening under the hood instead of just calling library functions.
"""

#!/usr/bin/env python3
"""
Bootstrap resampling and permutation testing module.
Implements hypothesis testing without relying on parametric assumptions.
"""

import random
from typing import List, Callable, Tuple
from statistics import mean, stdev


def bootstrap_resample(data: List[float], n_iterations: int = 10000,
                       statistic: Callable = mean, seed: int = None) -> List[float]:
    """
    Perform bootstrap resampling on data to estimate sampling distribution.
    
    Randomly samples WITH replacement from the data to build up a distribution
    of the statistic. This lets us calculate confidence intervals without
    assuming normality.
    
    Args:
        data: Original dataset
        n_iterations: Number of bootstrap samples to generate
        statistic: Function to apply to each resample (default: mean)
        seed: Random seed for reproducibility
    
    Returns:
        List of statistic values from each bootstrap sample
    """
    if seed is not None:
        random.seed(seed)
    
    n = len(data)
    bootstrap_stats = []
    
    for _ in range(n_iterations):
        # Sample with replacement
        resample = [random.choice(data) for _ in range(n)]
        bootstrap_stats.append(statistic(resample))
    
    return bootstrap_stats


def bootstrap_confidence_interval(data: List[float], confidence: float = 0.95,
                                  n_iterations: int = 10000, 
                                  statistic: Callable = mean) -> Tuple[float, float]:
    """
    Calculate confidence interval using bootstrap method.
    
    Args:
        data: Original dataset
        confidence: Confidence level (e.g., 0.95 for 95%)
        n_iterations: Number of bootstrap samples
        statistic: Function to compute statistic
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    bootstrap_stats = bootstrap_resample(data, n_iterations, statistic)
    bootstrap_stats.sort()
    
    # Calculate percentile positions
    alpha = 1 - confidence
    lower_idx = int(n_iterations * (alpha / 2))
    upper_idx = int(n_iterations * (1 - alpha / 2))
    
    return (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx])


def permutation_test(group1: List[float], group2: List[float],
                    n_iterations: int = 10000, seed: int = None) -> float:
    """
    Perform permutation test to check if two groups have different means.
    
    The idea: if groups are from same distribution, randomly shuffling labels
    shouldn't matter. We compare the actual difference to the distribution of
    differences under random permutations.
    
    Args:
        group1: First group of observations
        group2: Second group of observations
        n_iterations: Number of permutations to test
        seed: Random seed for reproducibility
    
    Returns:
        p-value (proportion of permutations with difference >= observed)
    """
    if seed is not None:
        random.seed(seed)
    
    # Calculate observed difference
    observed_diff = abs(mean(group1) - mean(group2))
    
    # Combine all data
    combined = group1 + group2
    n1 = len(group1)
    n_extreme = 0
    
    for _ in range(n_iterations):
        # Randomly shuffle and split
        shuffled = combined.copy()
        random.shuffle(shuffled)
        
        perm_group1 = shuffled[:n1]
        perm_group2 = shuffled[n1:]
        
        perm_diff = abs(mean(perm_group1) - mean(perm_group2))
        
        # Count how many times we see a difference as extreme
        if perm_diff >= observed_diff:
            n_extreme += 1
    
    return n_extreme / n_iterations


def effect_size_cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Calculate Cohen's d effect size between two groups.
    
    This measures how many standard deviations apart the groups are.
    Rule of thumb: 0.2 = small, 0.5 = medium, 0.8 = large effect
    
    Args:
        group1: First group
        group2: Second group
    
    Returns:
        Cohen's d value
    """
    mean1, mean2 = mean(group1), mean(group2)
    std1, std2 = stdev(group1), stdev(group2)
    n1, n2 = len(group1), len(group2)
    
    # Pooled standard deviation
    pooled_std = ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
    pooled_std = pooled_std ** 0.5
    
    return (mean1 - mean2) / pooled_std


if __name__ == "__main__":
    print("=" * 60)
    print("Bootstrap Resampling & Permutation Testing Demo")
    print("=" * 60)
    
    # Simulate some experimental data
    # Let's say we're testing a new study technique
    control_group = [72, 68, 71, 75, 70, 73, 69, 74, 71, 72, 70, 68]  # Traditional study
    treatment_group = [78, 82, 79, 85, 80, 83, 81, 84, 79, 82, 80, 86]  # New technique
    
    print("\n--- Dataset ---")
    print(f"Control group (n={len(control_group)}): {control_group}")
    print(f"  Mean: {mean(control_group):.2f}, StdDev: {stdev(control_group):.2f}")
    print(f"\nTreatment group (n={len(treatment_group)}): {treatment_group}")
    print(f"  Mean: {mean(treatment_group):.2f}, StdDev: {stdev(treatment_group):.2f}")
    
    # Bootstrap confidence interval for treatment group mean
    print("\n--- Bootstrap Analysis (Treatment Group) ---")
    ci_lower, ci_upper = bootstrap_confidence_interval(
        treatment_group, 
        confidence=0.95, 
        n_iterations=10000
    )
    print(f"95% Confidence Interval for mean: [{ci_lower:.2f}, {ci_upper:.2f}]")
    
    # Permutation test to see if groups actually differ
    print("\n--- Permutation Test ---")
    p_value = permutation_test(control_group, treatment_group, n_iterations=10000, seed=42)
    print(f"P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("Result: Statistically significant difference (p < 0.05)")
    else:
        print("Result: No significant difference (p >= 0.05)")
    
    # Effect size
    print("\n--- Effect Size ---")
    cohens_d = effect_size_cohens_d(control_group, treatment_group)
    print(f"Cohen's d: {cohens_d:.3f}")
    if abs(cohens_d) < 0.2:
        interpretation = "negligible"
    elif abs(cohens_d) < 0.5:
        interpretation = "small"
    elif abs(cohens_d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"
    print(f"Interpretation: {interpretation} effect size")
    
    print("\n" + "=" * 60)
    print("Conclusion: The new study technique appears to have a")
    print(f"statistically significant effect (p={p_value:.4f}) with a")
    print(f"{interpretation} effect size (d={cohens_d:.3f}).")
    print("=" * 60)