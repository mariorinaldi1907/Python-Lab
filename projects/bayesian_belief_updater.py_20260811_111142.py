"""
Date: 2026-08-11
Implemented a Bayesian belief network that updates probabilities as evidence comes in — useful for when I need to reason under uncertainty without hardcoding rules.
"""

#!/usr/bin/env python3
"""
Bayesian Belief Updater

A simple framework for updating beliefs about competing hypotheses
as new evidence arrives. Uses Bayes' theorem under the hood.
"""

from typing import Dict, List, Tuple
from collections import defaultdict
import math


class BayesianUpdater:
    """
    Maintains probabilities for multiple hypotheses and updates them
    as evidence is observed.
    
    I wanted something lightweight to play with Bayesian reasoning
    without pulling in heavy ML libraries.
    """
    
    def __init__(self, hypotheses: List[str], priors: Dict[str, float] = None):
        """
        Initialize with a list of mutually exclusive hypotheses.
        
        Args:
            hypotheses: List of hypothesis names
            priors: Optional dict mapping hypothesis -> prior probability
                   If None, uniform distribution is assumed
        """
        self.hypotheses = hypotheses
        
        # Start with uniform priors if none provided
        if priors is None:
            prior_prob = 1.0 / len(hypotheses)
            self.beliefs = {h: prior_prob for h in hypotheses}
        else:
            # Normalize the priors just in case they don't sum to 1
            total = sum(priors.values())
            self.beliefs = {h: priors.get(h, 0) / total for h in hypotheses}
        
        # Keep history for debugging/analysis
        self.history = [self.beliefs.copy()]
    
    def update(self, likelihoods: Dict[str, float]):
        """
        Update beliefs given likelihoods P(evidence | hypothesis).
        
        This is the core Bayes update: P(H|E) ∝ P(E|H) * P(H)
        
        Args:
            likelihoods: Dict mapping hypothesis -> P(evidence | hypothesis)
        """
        # Multiply prior by likelihood for each hypothesis
        unnormalized = {
            h: self.beliefs[h] * likelihoods.get(h, 0)
            for h in self.hypotheses
        }
        
        # Normalize so probabilities sum to 1
        total = sum(unnormalized.values())
        
        if total == 0:
            # Edge case: evidence impossible under all hypotheses
            # Keep beliefs unchanged
            return
        
        self.beliefs = {h: unnormalized[h] / total for h in self.hypotheses}
        self.history.append(self.beliefs.copy())
    
    def get_best_hypothesis(self) -> Tuple[str, float]:
        """Return the hypothesis with highest probability."""
        best = max(self.beliefs.items(), key=lambda x: x[1])
        return best
    
    def get_entropy(self) -> float:
        """
        Calculate Shannon entropy of current belief distribution.
        High entropy = uncertain, low entropy = confident.
        """
        entropy = 0.0
        for prob in self.beliefs.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        return entropy
    
    def reset(self):
        """Reset to initial priors."""
        self.beliefs = self.history[0].copy()
        self.history = [self.beliefs.copy()]
    
    def __repr__(self):
        """Pretty print current beliefs."""
        sorted_beliefs = sorted(
            self.beliefs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        lines = ["Current Beliefs:"]
        for hyp, prob in sorted_beliefs:
            bar = "█" * int(prob * 40)
            lines.append(f"  {hyp:20s} {prob:6.2%} {bar}")
        return "\n".join(lines)


def demo_medical_diagnosis():
    """
    Demo: diagnosing a disease based on symptoms.
    Classic Bayesian inference problem.
    """
    print("=" * 60)
    print("MEDICAL DIAGNOSIS DEMO")
    print("=" * 60)
    
    # Three competing diagnoses
    diseases = ["Common Cold", "Flu", "COVID-19"]
    
    # Base rates (how common each disease is)
    priors = {
        "Common Cold": 0.60,
        "Flu": 0.30,
        "COVID-19": 0.10
    }
    
    updater = BayesianUpdater(diseases, priors)
    print("\nInitial priors (before any symptoms):")
    print(updater)
    print(f"Entropy: {updater.get_entropy():.3f} bits\n")
    
    # Patient reports fever
    # P(fever | disease) for each condition
    print("\n[Evidence 1: Patient has fever]")
    fever_likelihoods = {
        "Common Cold": 0.20,
        "Flu": 0.90,
        "COVID-19": 0.85
    }
    updater.update(fever_likelihoods)
    print(updater)
    print(f"Entropy: {updater.get_entropy():.3f} bits\n")
    
    # Patient reports loss of taste
    print("\n[Evidence 2: Patient reports loss of taste]")
    taste_likelihoods = {
        "Common Cold": 0.05,
        "Flu": 0.10,
        "COVID-19": 0.70  # Much more specific to COVID
    }
    updater.update(taste_likelihoods)
    print(updater)
    print(f"Entropy: {updater.get_entropy():.3f} bits\n")
    
    best_diagnosis, confidence = updater.get_best_hypothesis()
    print(f"Best diagnosis: {best_diagnosis} ({confidence:.1%} confident)")


def demo_coin_bias():
    """
    Demo: inferring if a coin is fair or biased based on flips.
    """
    print("\n" + "=" * 60)
    print("COIN BIAS INFERENCE DEMO")
    print("=" * 60)
    
    hypotheses = ["Fair Coin", "Biased Heads", "Biased Tails"]
    
    # Start agnostic
    updater = BayesianUpdater(hypotheses)
    print("\nInitial beliefs:")
    print(updater)
    
    # Simulate observing 7 heads out of 10 flips
    observations = "HHHHTHHTHH"
    
    print(f"\nObserving flips: {observations}\n")
    
    for i, flip in enumerate(observations, 1):
        if flip == "H":
            # Likelihood of seeing heads under each hypothesis
            likelihoods = {
                "Fair Coin": 0.50,
                "Biased Heads": 0.80,  # This coin loves heads
                "Biased Tails": 0.20
            }
        else:
            likelihoods = {
                "Fair Coin": 0.50,
                "Biased Heads": 0.20,
                "Biased Tails": 0.80
            }
        
        updater.update(likelihoods)
        
        if i % 3 == 0 or i == len(observations):
            print(f"After flip {i}:")
            best, conf = updater.get_best_hypothesis()
            print(f"  Leading: {best} ({conf:.1%})")
    
    print("\nFinal beliefs:")
    print(updater)


if __name__ == "__main__":
    demo_medical_diagnosis()
    demo_coin_bias()
    
    print("\n" + "=" * 60)
    print("Done! The updater handles sequential evidence nicely.")
    print("Entropy decreases as we become more certain.")
    print("=" * 60)