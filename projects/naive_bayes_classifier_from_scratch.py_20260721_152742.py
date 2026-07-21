"""
Date: 2026-07-21
Implemented a Gaussian Naive Bayes classifier to understand probabilistic machine learning — calculates class priors and feature likelihoods manually.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier from scratch using only standard library.
Uses Gaussian (normal) distribution for continuous features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier assuming features follow a Gaussian distribution.
    
    The classifier learns the mean and standard deviation of each feature
    for each class, then uses Bayes' theorem to predict new samples.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating statistics for each class.
        
        Args:
            X: List of feature vectors (each vector is a list of numbers)
            y: List of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        n_samples = len(y)
        
        # Calculate prior probability for each class
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and std dev for each feature in each class
        # This is where we assume Gaussian distribution
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_samples[cls]
            n_features = len(samples[0])
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                # Extract all values for this feature in this class
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls].append((mean, std_dev))
    
    def _gaussian_probability(self, x, mean, std_dev):
        """
        Calculate probability density function of Gaussian distribution.
        
        This is the likelihood P(feature|class) under the Gaussian assumption.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std_dev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std_dev)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class|features) using Bayes' theorem.
        
        We actually calculate log probability to avoid numerical underflow
        since multiplying many small probabilities can get too small.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply (add in log space) likelihoods for each feature
        # This is the "naive" part: we assume features are independent
        for idx, feature_value in enumerate(features):
            mean, std_dev = self.feature_stats[cls][idx]
            likelihood = self._gaussian_probability(feature_value, mean, std_dev)
            # Add small epsilon to avoid log(0)
            log_prob += math.log(likelihood + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Args:
            X: List of feature vectors
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        for features in X:
            # Calculate probability for each class and pick the highest
            class_probs = {
                cls: self._calculate_class_probability(features, cls)
                for cls in self.classes
            }
            predicted_class = max(class_probs, key=class_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Return probability estimates for each class.
        
        Note: These are log probabilities, not normalized.
        """
        probabilities = []
        for features in X:
            class_probs = {
                cls: self._calculate_class_probability(features, cls)
                for cls in self.classes
            }
            probabilities.append(class_probs)
        
        return probabilities


def generate_synthetic_data(n_samples=100):
    """
    Generate synthetic 2D data for binary classification.
    
    Creates two clusters with different centers to simulate
    two separable classes. Good for testing the classifier.
    """
    X = []
    y = []
    
    # Class 0: centered around (2, 2)
    for _ in range(n_samples // 2):
        x1 = random.gauss(2.0, 1.0)
        x2 = random.gauss(2.0, 1.0)
        X.append([x1, x2])
        y.append(0)
    
    # Class 1: centered around (8, 8)
    for _ in range(n_samples // 2):
        x1 = random.gauss(8.0, 1.5)
        x2 = random.gauss(8.0, 1.5)
        X.append([x1, x2])
        y.append(1)
    
    # Shuffle the data
    combined = list(zip(X, y))
    random.shuffle(combined)
    X, y = zip(*combined)
    
    return list(X), list(y)


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate synthetic data
    X, y = generate_synthetic_data(n_samples=120)
    
    # Split into train/test (80/20 split)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}\n")
    
    # Train the classifier
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("Learned class priors:")
    for cls, prior in nb.class_priors.items():
        print(f"  Class {cls}: {prior:.3f}")
    
    print("\nLearned feature statistics (mean, std_dev):")
    for cls in nb.classes:
        print(f"  Class {cls}:")
        for idx, (mean, std) in enumerate(nb.feature_stats[cls]):
            print(f"    Feature {idx}: μ={mean:.2f}, σ={std:.2f}")
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
    accuracy = correct / len(y_test)
    
    print(f"\nTest Accuracy: {accuracy:.2%} ({correct}/{len(y_test)} correct)")
    
    # Show some example predictions
    print("\nExample predictions:")
    for i in range(min(5, len(X_test))):
        print(f"  Features: {[f'{x:.2f}' for x in X_test[i]]} "
              f"→ Predicted: {predictions[i]}, Actual: {y_test[i]}")