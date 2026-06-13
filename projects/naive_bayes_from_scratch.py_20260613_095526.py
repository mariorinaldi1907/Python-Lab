"""
Date: 2026-06-13
Implemented Gaussian Naive Bayes to really understand how probabilistic classification works under the hood — surprisingly simple math once you break it down.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier built from scratch using only the standard library.
Uses Gaussian (normal) distribution for continuous features.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier assuming features follow a Gaussian distribution.
    
    The 'naive' part means we assume features are independent given the class,
    which is rarely true but works surprisingly well in practice.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating statistics for each feature.
        
        Args:
            X: List of feature vectors (each is a list of numbers)
            y: List of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        n_samples = len(y)
        
        # Calculate prior probabilities for each class
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and std for each feature in each class
        # This is the heart of Gaussian Naive Bayes
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_samples[cls]
            n_features = len(samples[0])
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                # Extract all values for this feature
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation (with Bessel's correction)
                variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
                std = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls].append({'mean': mean, 'std': std})
    
    def _gaussian_probability(self, x, mean, std):
        """
        Calculate probability density using Gaussian (normal) distribution.
        
        This is the classic bell curve formula from statistics.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class | features) using Bayes' theorem.
        
        We actually calculate log probabilities to avoid numerical underflow
        (multiplying many small probabilities gets really tiny really fast).
        """
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply probabilities for each feature (add logs instead)
        for idx, value in enumerate(features):
            stats = self.feature_stats[cls][idx]
            prob = self._gaussian_probability(value, stats['mean'], stats['std'])
            # Add small epsilon to avoid log(0)
            log_prob += math.log(prob + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples.
        
        For each sample, we calculate probability for each class
        and pick the highest one (maximum a posteriori).
        """
        predictions = []
        for features in X:
            class_probs = {}
            for cls in self.classes:
                class_probs[cls] = self._calculate_class_probability(features, cls)
            
            # Pick class with highest probability
            predicted_class = max(class_probs, key=class_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Return probability estimates for each class.
        """
        probabilities = []
        for features in X:
            log_probs = {}
            for cls in self.classes:
                log_probs[cls] = self._calculate_class_probability(features, cls)
            
            # Convert log probabilities back to probabilities and normalize
            max_log = max(log_probs.values())
            probs = {cls: math.exp(log_prob - max_log) for cls, log_prob in log_probs.items()}
            total = sum(probs.values())
            probs = {cls: p / total for cls, p in probs.items()}
            
            probabilities.append(probs)
        
        return probabilities


if __name__ == "__main__":
    # Demo with the classic Iris dataset (manually entered subset)
    # Features: [sepal_length, sepal_width, petal_length, petal_width]
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Training data - small subset of iris dataset
    X_train = [
        [5.1, 3.5, 1.4, 0.2],  # setosa
        [4.9, 3.0, 1.4, 0.2],  # setosa
        [4.7, 3.2, 1.3, 0.2],  # setosa
        [7.0, 3.2, 4.7, 1.4],  # versicolor
        [6.4, 3.2, 4.5, 1.5],  # versicolor
        [6.9, 3.1, 4.9, 1.5],  # versicolor
        [6.3, 3.3, 6.0, 2.5],  # virginica
        [5.8, 2.7, 5.1, 1.9],  # virginica
        [7.1, 3.0, 5.9, 2.1],  # virginica
    ]
    
    y_train = ['setosa', 'setosa', 'setosa',
               'versicolor', 'versicolor', 'versicolor',
               'virginica', 'virginica', 'virginica']
    
    # Train the classifier
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("Training complete!")
    print(f"Classes found: {nb.classes}\n")
    
    # Test samples
    X_test = [
        [5.0, 3.4, 1.5, 0.2],  # should be setosa
        [6.7, 3.1, 4.7, 1.5],  # should be versicolor
        [6.5, 3.0, 5.8, 2.2],  # should be virginica
    ]
    
    print("Making predictions on test samples:")
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    for i, (features, pred, probs) in enumerate(zip(X_test, predictions, probabilities)):
        print(f"\nSample {i+1}: {features}")
        print(f"  Predicted class: {pred}")
        print(f"  Probabilities:")
        for cls in sorted(probs.keys()):
            print(f"    {cls}: {probs[cls]:.4f}")
    
    print("\n✓ Classifier working as expected!")