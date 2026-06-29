"""
Date: 2026-06-29
Built a Gaussian Naive Bayes classifier to understand probabilistic ML better — handles continuous features with class priors and likelihoods.
"""

#!/usr/bin/env python3
"""
Gaussian Naive Bayes classifier implementation from scratch.
Uses maximum likelihood estimation for class priors and Gaussian parameters.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier assuming features follow Gaussian distribution.
    
    The classifier learns mean and variance for each feature per class,
    then uses Bayes theorem to predict the most probable class.
    """
    
    def __init__(self, smoothing=1e-9):
        """
        Initialize the classifier.
        
        Args:
            smoothing: Small value added to variance to prevent division by zero
        """
        self.smoothing = smoothing
        self.classes = []
        self.class_priors = {}
        # Store mean and variance for each feature in each class
        self.feature_stats = defaultdict(lambda: defaultdict(dict))
        
    def fit(self, X, y):
        """
        Train the classifier on features X and labels y.
        
        Args:
            X: List of feature vectors (each is a list of numbers)
            y: List of class labels
        """
        n_samples = len(X)
        n_features = len(X[0])
        
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = sorted(class_samples.keys())
        
        # Calculate class priors (probability of each class)
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and variance for each feature in each class
        for cls in self.classes:
            samples = class_samples[cls]
            n_cls_samples = len(samples)
            
            for feature_idx in range(n_features):
                # Extract all values for this feature in this class
                values = [sample[feature_idx] for sample in samples]
                
                # Calculate mean
                mean = sum(values) / n_cls_samples
                
                # Calculate variance (with smoothing to avoid zero variance)
                variance = sum((x - mean) ** 2 for x in values) / n_cls_samples
                variance += self.smoothing
                
                self.feature_stats[cls][feature_idx] = {
                    'mean': mean,
                    'variance': variance
                }
    
    def _gaussian_probability(self, x, mean, variance):
        """
        Calculate probability density using Gaussian distribution.
        
        Args:
            x: Feature value
            mean: Mean of the distribution
            variance: Variance of the distribution
            
        Returns:
            Probability density at x
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * math.pi * variance)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate log probability of features given class.
        
        Using log probabilities to avoid numerical underflow when multiplying
        many small probabilities together.
        
        Args:
            features: Feature vector
            cls: Class label
            
        Returns:
            Log probability
        """
        # Start with log of class prior
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply (add in log space) probabilities for each feature
        for idx, value in enumerate(features):
            mean = self.feature_stats[cls][idx]['mean']
            variance = self.feature_stats[cls][idx]['variance']
            
            # Add log of feature probability
            feature_prob = self._gaussian_probability(value, mean, variance)
            log_prob += math.log(feature_prob + 1e-10)  # Avoid log(0)
        
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
            # Calculate probability for each class
            class_probabilities = {}
            for cls in self.classes:
                class_probabilities[cls] = self._calculate_class_probability(features, cls)
            
            # Pick class with highest probability
            predicted_class = max(class_probabilities, key=class_probabilities.get)
            predictions.append(predicted_class)
        
        return predictions


def generate_synthetic_data(n_samples=150):
    """
    Generate synthetic dataset similar to iris dataset.
    Three classes with different feature distributions.
    """
    random.seed(42)
    X, y = [], []
    
    # Class 0: smaller values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(5.0, 0.5),
            random.gauss(3.4, 0.4),
            random.gauss(1.5, 0.3),
            random.gauss(0.3, 0.1)
        ])
        y.append(0)
    
    # Class 1: medium values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.0, 0.6),
            random.gauss(2.8, 0.4),
            random.gauss(4.5, 0.5),
            random.gauss(1.4, 0.3)
        ])
        y.append(1)
    
    # Class 2: larger values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.5, 0.7),
            random.gauss(3.0, 0.5),
            random.gauss(5.5, 0.6),
            random.gauss(2.0, 0.4)
        ])
        y.append(2)
    
    return X, y


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier ===\n")
    
    # Generate synthetic data
    X, y = generate_synthetic_data(150)
    
    # Split into train and test (80/20 split)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train classifier
    print(f"Training on {len(X_train)} samples...")
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
    accuracy = correct / len(y_test)
    
    print(f"\nTested on {len(X_test)} samples")
    print(f"Accuracy: {accuracy:.2%} ({correct}/{len(y_test)} correct)\n")
    
    # Show some example predictions
    print("Sample predictions:")
    for i in range(min(10, len(X_test))):
        print(f"  True: {y_test[i]}, Predicted: {predictions[i]} {'✓' if predictions[i] == y_test[i] else '✗'}")
    
    # Show learned parameters for one class
    print(f"\nLearned parameters for Class 0:")
    print(f"  Prior probability: {nb.class_priors[0]:.3f}")
    for feat_idx in range(4):
        stats = nb.feature_stats[0][feat_idx]
        print(f"  Feature {feat_idx}: mean={stats['mean']:.3f}, var={stats['variance']:.3f}")