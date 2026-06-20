"""
Date: 2026-06-20
Built a Gaussian and Multinomial Naive Bayes classifier to understand probabilistic classification better — handles both continuous and discrete features.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier from scratch.

I wanted to really understand how probabilistic classifiers work, so I built
both Gaussian (for continuous data) and Multinomial (for count data) versions.
The math is surprisingly simple once you break it down.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Gaussian Naive Bayes for continuous features.
    
    Assumes features follow a normal distribution within each class.
    I'm using the classic mean/variance approach here.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and variance per feature per class
        
    def fit(self, X, y):
        """
        Train the model by calculating priors and feature statistics.
        
        X: list of feature vectors (each vector is a list of numbers)
        y: list of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        n_samples = len(y)
        n_features = len(X[0])
        
        # Calculate priors and feature statistics for each class
        for cls in self.classes:
            samples = class_samples[cls]
            self.class_priors[cls] = len(samples) / n_samples
            
            # Calculate mean and variance for each feature
            self.feature_stats[cls] = []
            for feature_idx in range(n_features):
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                # Using sample variance (dividing by n-1), but n works too
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                # Avoid division by zero in probability calculation
                variance = max(variance, 1e-9)
                self.feature_stats[cls].append((mean, variance))
    
    def _gaussian_probability(self, x, mean, variance):
        """Calculate probability density using Gaussian formula."""
        exponent = math.exp(-((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * math.pi * variance)) * exponent
    
    def predict(self, X):
        """Predict class labels for samples in X."""
        predictions = []
        for features in X:
            predictions.append(self._predict_single(features))
        return predictions
    
    def _predict_single(self, features):
        """Predict class for a single sample using Bayes theorem."""
        posteriors = {}
        
        for cls in self.classes:
            # Start with log prior to avoid underflow
            posterior = math.log(self.class_priors[cls])
            
            # Multiply likelihoods for each feature (add in log space)
            for idx, value in enumerate(features):
                mean, variance = self.feature_stats[cls][idx]
                likelihood = self._gaussian_probability(value, mean, variance)
                # Add small epsilon to avoid log(0)
                posterior += math.log(likelihood + 1e-9)
            
            posteriors[cls] = posterior
        
        # Return class with highest posterior probability
        return max(posteriors, key=posteriors.get)


class MultinomialNaiveBayes:
    """
    Multinomial Naive Bayes for discrete count features.
    
    Perfect for text classification where features are word counts.
    I added Laplace smoothing to handle unseen words.
    """
    
    def __init__(self, alpha=1.0):
        """
        alpha: Laplace smoothing parameter (1.0 = standard Laplace smoothing)
        """
        self.alpha = alpha
        self.classes = []
        self.class_priors = {}
        self.feature_probs = {}  # P(feature | class)
        self.vocab_size = 0
    
    def fit(self, X, y):
        """
        Train the model on count data.
        
        X: list of feature count vectors (typically word counts)
        y: list of class labels
        """
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        self.vocab_size = len(X[0])
        n_samples = len(y)
        
        for cls in self.classes:
            samples = class_samples[cls]
            self.class_priors[cls] = len(samples) / n_samples
            
            # Sum all feature counts for this class
            feature_counts = [0] * self.vocab_size
            for sample in samples:
                for idx, count in enumerate(sample):
                    feature_counts[idx] += count
            
            # Calculate probabilities with Laplace smoothing
            total_count = sum(feature_counts)
            self.feature_probs[cls] = []
            for count in feature_counts:
                # Laplace smoothing prevents zero probabilities
                prob = (count + self.alpha) / (total_count + self.alpha * self.vocab_size)
                self.feature_probs[cls].append(prob)
    
    def predict(self, X):
        """Predict class labels for samples in X."""
        predictions = []
        for features in X:
            predictions.append(self._predict_single(features))
        return predictions
    
    def _predict_single(self, features):
        """Predict class for a single sample."""
        posteriors = {}
        
        for cls in self.classes:
            posterior = math.log(self.class_priors[cls])
            
            # Multiply feature probabilities (add logs)
            for idx, count in enumerate(features):
                if count > 0:  # Only consider features that appear
                    posterior += count * math.log(self.feature_probs[cls][idx])
            
            posteriors[cls] = posterior
        
        return max(posteriors, key=posteriors.get)


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Demo ===")
    print("Classifying iris-like data (synthetic)\n")
    
    # Simple synthetic data: [sepal_length, petal_length]
    # Class 0: small flowers, Class 1: large flowers
    X_train = [
        [5.1, 1.4], [4.9, 1.4], [4.7, 1.3],  # Class 0
        [6.5, 5.5], [6.7, 5.8], [6.9, 5.1],  # Class 1
    ]
    y_train = [0, 0, 0, 1, 1, 1]
    
    gnb = GaussianNaiveBayes()
    gnb.fit(X_train, y_train)
    
    X_test = [[5.0, 1.5], [6.8, 5.4]]
    predictions = gnb.predict(X_test)
    
    for features, pred in zip(X_test, predictions):
        print(f"Features {features} → Class {pred}")
    
    print("\n=== Multinomial Naive Bayes Demo ===")
    print("Text classification (simple word counts)\n")
    
    # Word counts: [count('good'), count('bad'), count('movie'), count('boring')]
    # Class 0: negative review, Class 1: positive review
    X_text_train = [
        [0, 2, 1, 1],  # "bad movie boring" - negative
        [0, 3, 1, 2],  # "bad bad bad movie boring boring" - negative
        [3, 0, 1, 0],  # "good good good movie" - positive
        [2, 0, 1, 0],  # "good good movie" - positive
    ]
    y_text_train = [0, 0, 1, 1]
    
    mnb = MultinomialNaiveBayes(alpha=1.0)
    mnb.fit(X_text_train, y_text_train)
    
    X_text_test = [[1, 1, 1, 0], [2, 0, 1, 0]]
    text_predictions = mnb.predict(X_text_test)
    
    labels = {0: "Negative", 1: "Positive"}
    for features, pred in zip(X_text_test, text_predictions):
        print(f"Word counts {features} → {labels[pred]}")