"""
Date: 2026-05-29
Implemented a Gaussian Naive Bayes classifier to really understand how probabilistic classification works under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier from scratch.

I wanted to understand how Naive Bayes actually works without relying on sklearn,
so I implemented Gaussian Naive Bayes which assumes features follow a normal distribution.
This is surprisingly effective for a lot of real-world classification tasks.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Gaussian Naive Bayes classifier.
    
    Assumes each feature follows a Gaussian (normal) distribution within each class.
    Uses maximum likelihood estimation to fit parameters, then Bayes' theorem for prediction.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.means = {}  # mean of each feature per class
        self.variances = {}  # variance of each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating statistics for each class.
        
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
        
        # Calculate prior probabilities and feature statistics for each class
        for cls in self.classes:
            samples = class_samples[cls]
            self.class_priors[cls] = len(samples) / n_samples
            
            # Calculate mean and variance for each feature in this class
            self.means[cls] = []
            self.variances[cls] = []
            
            for feature_idx in range(n_features):
                feature_values = [sample[feature_idx] for sample in samples]
                mean = sum(feature_values) / len(feature_values)
                
                # Variance calculation with Bessel's correction (n-1)
                # Adding small epsilon to avoid division by zero
                variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                variance = max(variance, 1e-9)  # prevent zero variance
                
                self.means[cls].append(mean)
                self.variances[cls].append(variance)
    
    def _gaussian_probability(self, x, mean, variance):
        """
        Calculate probability density using Gaussian distribution.
        
        This is the classic bell curve formula: the likelihood of seeing
        value x given that it comes from a distribution with this mean/variance.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * math.pi * variance)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class | features) using Bayes' theorem.
        
        We use log probabilities to avoid numerical underflow since multiplying
        many small probabilities can lead to floating point errors.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply by likelihood of each feature (add in log space)
        for idx, feature_value in enumerate(features):
            mean = self.means[cls][idx]
            variance = self.variances[cls][idx]
            likelihood = self._gaussian_probability(feature_value, mean, variance)
            log_prob += math.log(likelihood + 1e-10)  # small epsilon to avoid log(0)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Returns the class with highest posterior probability for each sample.
        """
        predictions = []
        
        for features in X:
            # Calculate probability for each class and pick the highest
            class_probabilities = {
                cls: self._calculate_class_probability(features, cls)
                for cls in self.classes
            }
            predicted_class = max(class_probabilities, key=class_probabilities.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Return probability estimates for each class.
        
        Normalizes log probabilities back to proper probabilities that sum to 1.
        """
        probabilities = []
        
        for features in X:
            log_probs = {
                cls: self._calculate_class_probability(features, cls)
                for cls in self.classes
            }
            
            # Convert from log space and normalize
            max_log = max(log_probs.values())
            exp_probs = {cls: math.exp(log_prob - max_log) for cls, log_prob in log_probs.items()}
            total = sum(exp_probs.values())
            normalized = {cls: prob / total for cls, prob in exp_probs.items()}
            
            probabilities.append(normalized)
        
        return probabilities


if __name__ == "__main__":
    # Demo with the classic Iris dataset (simplified version with 2 classes)
    # Features: sepal length, sepal width, petal length, petal width
    
    # Class 0: Iris Setosa (smaller petals)
    # Class 1: Iris Versicolor (larger petals)
    X_train = [
        [5.1, 3.5, 1.4, 0.2],
        [4.9, 3.0, 1.4, 0.2],
        [4.7, 3.2, 1.3, 0.2],
        [5.0, 3.6, 1.4, 0.2],
        [5.4, 3.9, 1.7, 0.4],
        [7.0, 3.2, 4.7, 1.4],
        [6.4, 3.2, 4.5, 1.5],
        [6.9, 3.1, 4.9, 1.5],
        [5.5, 2.3, 4.0, 1.3],
        [6.5, 2.8, 4.6, 1.5],
    ]
    y_train = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    
    X_test = [
        [5.0, 3.4, 1.5, 0.2],  # Should be class 0
        [6.7, 3.1, 4.4, 1.4],  # Should be class 1
        [4.8, 3.1, 1.6, 0.2],  # Should be class 0
    ]
    
    # Train the classifier
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("Naive Bayes Classifier Demo")
    print("=" * 50)
    print(f"Trained on {len(X_train)} samples with {len(nb.classes)} classes")
    print(f"Class priors: {nb.class_priors}")
    print()
    
    # Make predictions
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    print("Test Predictions:")
    for i, (features, pred, probs) in enumerate(zip(X_test, predictions, probabilities)):
        print(f"\nSample {i + 1}: {features}")
        print(f"  Predicted class: {pred}")
        print(f"  Probabilities: {probs}")
    
    # Show accuracy on training set (just for demonstration)
    train_preds = nb.predict(X_train)
    accuracy = sum(1 for true, pred in zip(y_train, train_preds) if true == pred) / len(y_train)
    print(f"\nTraining accuracy: {accuracy * 100:.1f}%")