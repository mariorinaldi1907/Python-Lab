"""
Date: 2026-06-09
Built a Naive Bayes classifier to understand probabilistic classification better — handles categorical features and includes additive smoothing to deal with unseen values.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.

I wanted to really understand how probabilistic classifiers work under the hood,
so I built this without any ML libraries. Uses Laplace smoothing to handle
features we haven't seen during training.
"""

from collections import defaultdict
import math


class NaiveBayesClassifier:
    """
    A simple Naive Bayes classifier for categorical features.
    
    This implementation uses Laplace (additive) smoothing to avoid zero probabilities
    when we encounter feature values that didn't appear in the training set.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Smoothing parameter (Laplace smoothing). Default is 1.0.
                   Setting alpha=0 means no smoothing (not recommended).
        """
        self.alpha = alpha
        self.class_priors = {}  # P(class)
        self.feature_probs = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        # Structure: feature_probs[class][feature_idx][feature_value] = probability
        self.classes = set()
        self.feature_values = defaultdict(set)  # Track all possible values per feature
        
    def fit(self, X, y):
        """
        Train the classifier on the given data.
        
        Args:
            X: List of feature vectors (each vector is a list/tuple of feature values)
            y: List of class labels corresponding to X
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        n_samples = len(X)
        class_counts = defaultdict(int)
        
        # Count occurrences for each class and feature combination
        feature_class_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        for features, label in zip(X, y):
            self.classes.add(label)
            class_counts[label] += 1
            
            for feature_idx, feature_value in enumerate(features):
                feature_class_counts[label][feature_idx][feature_value] += 1
                self.feature_values[feature_idx].add(feature_value)
        
        # Calculate class priors: P(class)
        for cls in self.classes:
            self.class_priors[cls] = class_counts[cls] / n_samples
        
        # Calculate conditional probabilities: P(feature|class) with Laplace smoothing
        for cls in self.classes:
            for feature_idx in range(len(X[0])):
                n_feature_values = len(self.feature_values[feature_idx])
                total_count = class_counts[cls]
                
                for feature_value in self.feature_values[feature_idx]:
                    count = feature_class_counts[cls][feature_idx][feature_value]
                    # Laplace smoothing: (count + alpha) / (total + alpha * n_values)
                    prob = (count + self.alpha) / (total_count + self.alpha * n_feature_values)
                    self.feature_probs[cls][feature_idx][feature_value] = prob
    
    def _calculate_log_probability(self, features, cls):
        """
        Calculate log probability of features given a class.
        
        Using log probabilities prevents underflow when multiplying many small probabilities.
        
        Args:
            features: A feature vector
            cls: The class label
            
        Returns:
            Log probability of P(class) * P(features|class)
        """
        # Start with log of class prior
        log_prob = math.log(self.class_priors[cls])
        
        for feature_idx, feature_value in enumerate(features):
            # Get the probability for this feature value given the class
            if feature_value in self.feature_probs[cls][feature_idx]:
                prob = self.feature_probs[cls][feature_idx][feature_value]
            else:
                # Unseen feature value - use smoothing
                n_feature_values = len(self.feature_values[feature_idx])
                prob = self.alpha / (sum(1 for _ in self.feature_probs[cls][feature_idx].values()) + 
                                    self.alpha * n_feature_values)
            
            log_prob += math.log(prob)
        
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
            class_scores = {}
            for cls in self.classes:
                class_scores[cls] = self._calculate_log_probability(features, cls)
            
            # Pick class with highest probability
            predicted_class = max(class_scores, key=class_scores.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Predict class probabilities for samples in X.
        
        Args:
            X: List of feature vectors
            
        Returns:
            List of dictionaries mapping class -> probability
        """
        probabilities = []
        
        for features in X:
            log_probs = {}
            for cls in self.classes:
                log_probs[cls] = self._calculate_log_probability(features, cls)
            
            # Convert log probabilities back to probabilities
            # Subtract max for numerical stability
            max_log_prob = max(log_probs.values())
            probs = {cls: math.exp(lp - max_log_prob) for cls, lp in log_probs.items()}
            
            # Normalize to sum to 1
            total = sum(probs.values())
            probs = {cls: p / total for cls, p in probs.items()}
            
            probabilities.append(probs)
        
        return probabilities


if __name__ == "__main__":
    # Simple text classification example: spam vs ham based on word presence
    # Each feature represents whether a specific word appears in the message
    # Features: [contains_"free", contains_"winner", contains_"meeting", contains_"lunch"]
    
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Training data: simple spam/ham classification
    X_train = [
        [1, 1, 0, 0],  # "free winner" -> spam
        [1, 0, 0, 0],  # "free" -> spam
        [1, 1, 1, 0],  # "free winner meeting" -> spam
        [0, 0, 1, 1],  # "meeting lunch" -> ham
        [0, 0, 1, 0],  # "meeting" -> ham
        [0, 0, 1, 1],  # "meeting lunch" -> ham
        [1, 0, 0, 0],  # "free" -> spam
        [0, 0, 0, 1],  # "lunch" -> ham
    ]
    
    y_train = ['spam', 'spam', 'spam', 'ham', 'ham', 'ham', 'spam', 'ham']
    
    # Initialize and train the classifier
    nb = NaiveBayesClassifier(alpha=1.0)
    nb.fit(X_train, y_train)
    
    print("Training complete!")
    print(f"Classes found: {sorted(nb.classes)}")
    print(f"Class priors: {dict(nb.class_priors)}\n")
    
    # Test data
    X_test = [
        [1, 1, 0, 0],  # "free winner" -> should be spam
        [0, 0, 1, 1],  # "meeting lunch" -> should be ham
        [1, 0, 1, 0],  # "free meeting" -> mixed signal
    ]
    
    test_descriptions = [
        "Message: 'free winner'",
        "Message: 'meeting lunch'",
        "Message: 'free meeting' (mixed)"
    ]
    
    # Make predictions
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    print("=== Predictions ===\n")
    for desc, pred, probs in zip(test_descriptions, predictions, probabilities):
        print(f"{desc}")
        print(f"  Predicted: {pred}")
        print(f"  Probabilities: spam={probs['spam']:.3f}, ham={probs['ham']:.3f}")
        print()