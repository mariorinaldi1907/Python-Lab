"""
Date: 2026-07-03
Implemented a Gaussian Naive Bayes classifier with laplace smoothing because I wanted to understand how probabilistic classifiers actually work under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.
Uses Gaussian distribution for continuous features and handles categorical features too.
Built this to really understand how probability-based classification works.
"""

import math
from collections import defaultdict


class NaiveBayesClassifier:
    """
    Naive Bayes classifier supporting both continuous (Gaussian) and categorical features.
    
    Uses log probabilities internally to prevent numerical underflow when multiplying
    many small probability values together.
    """
    
    def __init__(self, feature_types=None):
        """
        Initialize the classifier.
        
        Args:
            feature_types: List indicating 'continuous' or 'categorical' for each feature.
                          If None, assumes all features are continuous.
        """
        self.feature_types = feature_types
        self.classes = []
        self.class_priors = {}
        # For continuous features: store mean and std dev per class
        self.continuous_params = defaultdict(lambda: defaultdict(dict))
        # For categorical features: store count of each value per class
        self.categorical_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.class_counts = defaultdict(int)
        
    def fit(self, X, y):
        """
        Train the Naive Bayes classifier on the given data.
        
        Args:
            X: List of feature vectors (each vector is a list of feature values)
            y: List of class labels
        """
        self.classes = list(set(y))
        n_samples = len(y)
        n_features = len(X[0])
        
        # Default to all continuous if not specified
        if self.feature_types is None:
            self.feature_types = ['continuous'] * n_features
        
        # Count samples per class
        for label in y:
            self.class_counts[label] += 1
        
        # Calculate class priors (using log probabilities)
        for cls in self.classes:
            self.class_priors[cls] = math.log(self.class_counts[cls] / n_samples)
        
        # Calculate feature parameters for each class
        for cls in self.classes:
            # Get all samples belonging to this class
            class_samples = [X[i] for i in range(len(X)) if y[i] == cls]
            
            for feature_idx in range(n_features):
                feature_values = [sample[feature_idx] for sample in class_samples]
                
                if self.feature_types[feature_idx] == 'continuous':
                    # Calculate mean and standard deviation
                    mean = sum(feature_values) / len(feature_values)
                    variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                    # Add small epsilon to avoid division by zero
                    std_dev = math.sqrt(variance + 1e-9)
                    
                    self.continuous_params[cls][feature_idx] = {
                        'mean': mean,
                        'std': std_dev
                    }
                else:
                    # Count occurrences of each categorical value
                    for value in feature_values:
                        self.categorical_counts[cls][feature_idx][value] += 1
    
    def _gaussian_probability(self, x, mean, std):
        """
        Calculate log probability of x given Gaussian distribution with mean and std.
        
        Using log probability to avoid underflow issues.
        """
        exponent = -((x - mean) ** 2) / (2 * std ** 2)
        log_coefficient = -math.log(std * math.sqrt(2 * math.pi))
        return log_coefficient + exponent
    
    def _categorical_probability(self, value, cls, feature_idx):
        """
        Calculate log probability of a categorical value using Laplace smoothing.
        
        Laplace smoothing adds 1 to all counts to handle unseen values gracefully.
        """
        count = self.categorical_counts[cls][feature_idx].get(value, 0)
        total = sum(self.categorical_counts[cls][feature_idx].values())
        n_values = len(self.categorical_counts[cls][feature_idx]) + 1  # +1 for unseen values
        
        # Laplace smoothing: add 1 to numerator and n_values to denominator
        probability = (count + 1) / (total + n_values)
        return math.log(probability)
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Args:
            X: List of feature vectors
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        
        for sample in X:
            class_scores = {}
            
            for cls in self.classes:
                # Start with class prior (already in log space)
                score = self.class_priors[cls]
                
                # Add log probability for each feature
                for feature_idx, value in enumerate(sample):
                    if self.feature_types[feature_idx] == 'continuous':
                        params = self.continuous_params[cls][feature_idx]
                        score += self._gaussian_probability(value, params['mean'], params['std'])
                    else:
                        score += self._categorical_probability(value, cls, feature_idx)
                
                class_scores[cls] = score
            
            # Predict class with highest score
            predicted_class = max(class_scores, key=class_scores.get)
            predictions.append(predicted_class)
        
        return predictions


def calculate_accuracy(y_true, y_pred):
    """Calculate classification accuracy."""
    correct = sum(1 for true, pred in zip(y_true, y_pred) if true == pred)
    return correct / len(y_true)


if __name__ == "__main__":
    # Demo: Classify iris-like flowers using synthetic data
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Training data: [sepal_length, sepal_width, color]
    # First two features are continuous, last is categorical
    X_train = [
        [5.1, 3.5, 'light'], [4.9, 3.0, 'light'], [4.7, 3.2, 'light'],
        [7.0, 3.2, 'dark'], [6.4, 3.2, 'dark'], [6.9, 3.1, 'dark'],
        [5.8, 2.7, 'medium'], [5.7, 2.8, 'medium'], [6.0, 2.9, 'medium'],
        [5.0, 3.6, 'light'], [4.6, 3.1, 'light'],
        [6.7, 3.0, 'dark'], [6.3, 3.3, 'dark'],
        [5.9, 2.8, 'medium'], [6.1, 2.9, 'medium']
    ]
    
    y_train = [
        'setosa', 'setosa', 'setosa',
        'virginica', 'virginica', 'virginica',
        'versicolor', 'versicolor', 'versicolor',
        'setosa', 'setosa',
        'virginica', 'virginica',
        'versicolor', 'versicolor'
    ]
    
    # Test data
    X_test = [
        [5.0, 3.4, 'light'],      # Should be setosa
        [6.8, 3.2, 'dark'],       # Should be virginica
        [5.8, 2.8, 'medium'],     # Should be versicolor
        [4.8, 3.0, 'light'],      # Should be setosa
    ]
    
    y_test = ['setosa', 'virginica', 'versicolor', 'setosa']
    
    # Train the classifier
    classifier = NaiveBayesClassifier(feature_types=['continuous', 'continuous', 'categorical'])
    classifier.fit(X_train, y_train)
    
    print("Training completed on {} samples".format(len(X_train)))
    print("Classes found:", classifier.classes)
    print()
    
    # Make predictions on test data
    predictions = classifier.predict(X_test)
    
    print("Test Results:")
    print("-" * 60)
    for i, (features, true_label, predicted) in enumerate(zip(X_test, y_test, predictions)):
        status = "✓" if true_label == predicted else "✗"
        print(f"{status} Sample {i+1}: {features}")
        print(f"  True: {true_label:12s} | Predicted: {predicted:12s}")
    
    print("-" * 60)
    accuracy = calculate_accuracy(y_test, predictions)
    print(f"\nAccuracy: {accuracy:.1%} ({sum(1 for t, p in zip(y_test, predictions) if t == p)}/{len(y_test)} correct)")