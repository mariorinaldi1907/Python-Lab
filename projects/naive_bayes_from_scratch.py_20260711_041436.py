"""
Date: 2026-07-11
Implemented a Gaussian Naive Bayes classifier without any ML libraries to really understand the probability math behind it.
"""

#!/usr/bin/env python3
"""
Gaussian Naive Bayes Classifier - Built from scratch
Mario's implementation to understand the underlying probability mechanics.

This uses the Gaussian (normal) distribution assumption for continuous features.
Works surprisingly well for a lot of real-world problems despite the "naive"
independence assumption between features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A from-scratch Naive Bayes classifier using Gaussian distribution for continuous features.
    
    The 'naive' part means we assume features are independent given the class,
    which rarely holds in practice but works well anyway.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Train the model by calculating mean, std dev, and priors for each class.
        
        X: list of feature vectors (each vector is a list of numbers)
        y: list of class labels
        """
        # Group data by class
        class_data = defaultdict(list)
        for features, label in zip(X, y):
            class_data[label].append(features)
        
        self.classes = list(class_data.keys())
        total_samples = len(y)
        
        # Calculate priors and feature statistics for each class
        for cls in self.classes:
            samples = class_data[cls]
            self.class_priors[cls] = len(samples) / total_samples
            
            # Calculate mean and std dev for each feature dimension
            num_features = len(samples[0])
            self.feature_stats[cls] = []
            
            for feature_idx in range(num_features):
                feature_values = [sample[feature_idx] for sample in samples]
                mean = sum(feature_values) / len(feature_values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                std_dev = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls].append({'mean': mean, 'std': std_dev})
    
    def _gaussian_probability(self, x, mean, std_dev):
        """
        Calculate probability density using Gaussian distribution formula.
        
        This is the classic bell curve formula: (1/√(2πσ²)) * e^(-(x-μ)²/2σ²)
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std_dev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std_dev)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class|features) using Bayes theorem.
        
        We actually calculate log probabilities to avoid numerical underflow
        when multiplying many small probabilities together.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply by likelihood of each feature (add in log space)
        for idx, feature_value in enumerate(features):
            stats = self.feature_stats[cls][idx]
            prob = self._gaussian_probability(feature_value, stats['mean'], stats['std'])
            # Avoid log(0) by adding small epsilon
            log_prob += math.log(prob + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for a list of feature vectors.
        
        Returns the class with highest posterior probability for each sample.
        """
        predictions = []
        for features in X:
            class_probs = {}
            for cls in self.classes:
                class_probs[cls] = self._calculate_class_probability(features, cls)
            
            # Pick class with highest log probability
            predicted_class = max(class_probs, key=class_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, features):
        """
        Return probability distribution over classes for a single sample.
        Useful for understanding model confidence.
        """
        log_probs = {cls: self._calculate_class_probability(features, cls) 
                     for cls in self.classes}
        
        # Convert log probabilities back to probabilities using exp
        # Normalize so they sum to 1
        max_log_prob = max(log_probs.values())
        probs = {cls: math.exp(log_prob - max_log_prob) 
                 for cls, log_prob in log_probs.items()}
        
        total = sum(probs.values())
        return {cls: prob / total for cls, prob in probs.items()}


def generate_iris_like_data():
    """
    Generate synthetic data similar to the iris dataset.
    Three classes with different means, some overlap to make it interesting.
    """
    data = []
    labels = []
    
    # Class 0: small flowers
    for _ in range(50):
        data.append([random.gauss(5.0, 0.5), random.gauss(3.4, 0.4)])
        labels.append('setosa')
    
    # Class 1: medium flowers
    for _ in range(50):
        data.append([random.gauss(6.0, 0.6), random.gauss(2.8, 0.5)])
        labels.append('versicolor')
    
    # Class 2: large flowers
    for _ in range(50):
        data.append([random.gauss(6.5, 0.7), random.gauss(3.0, 0.5)])
        labels.append('virginica')
    
    return data, labels


if __name__ == "__main__":
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Generate synthetic dataset
    X, y = generate_iris_like_data()
    
    # Train/test split (80/20)
    random.seed(42)
    indices = list(range(len(X)))
    random.shuffle(indices)
    
    split_idx = int(0.8 * len(X))
    train_idx = indices[:split_idx]
    test_idx = indices[split_idx:]
    
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    
    # Train the model
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print(f"Trained on {len(X_train)} samples")
    print(f"Testing on {len(X_test)} samples\n")
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
    accuracy = correct / len(y_test)
    
    print(f"Accuracy: {accuracy:.2%} ({correct}/{len(y_test)} correct)\n")
    
    # Show some example predictions with probabilities
    print("Sample predictions with confidence:")
    for i in range(min(5, len(X_test))):
        probs = nb.predict_proba(X_test[i])
        print(f"  Features: {[f'{x:.2f}' for x in X_test[i]]}")
        print(f"  True: {y_test[i]}, Predicted: {predictions[i]}")
        print(f"  Probabilities: {', '.join(f'{k}: {v:.2%}' for k, v in sorted(probs.items()))}")
        print()