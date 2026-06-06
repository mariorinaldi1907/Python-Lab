"""
Date: 2026-06-06
Implemented a Naive Bayes classifier to revisit probabilistic ML fundamentals — handles categorical features and includes smoothing for unseen values.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier - built from scratch
Uses the probabilistic approach: P(class|features) ∝ P(class) * ∏P(feature|class)
"""

from collections import defaultdict
from typing import List, Dict, Any, Tuple
import math


class NaiveBayesClassifier:
    """
    A simple Naive Bayes classifier for categorical features.
    Uses Laplace smoothing (add-one smoothing) to handle unseen feature values.
    """
    
    def __init__(self, smoothing: float = 1.0):
        """
        Initialize the classifier.
        
        Args:
            smoothing: Laplace smoothing parameter (default 1.0 for add-one smoothing)
        """
        self.smoothing = smoothing
        self.class_counts = defaultdict(int)  # Count of samples per class
        self.feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.classes = set()
        self.feature_values = defaultdict(set)  # Track all possible values per feature
        self.total_samples = 0
        
    def fit(self, X: List[Dict[str, Any]], y: List[str]) -> None:
        """
        Train the classifier on the given data.
        
        Args:
            X: List of feature dictionaries (each dict maps feature_name -> value)
            y: List of class labels corresponding to each sample
        """
        self.total_samples = len(y)
        
        # Count occurrences for probability calculations
        for features, label in zip(X, y):
            self.classes.add(label)
            self.class_counts[label] += 1
            
            for feature_name, feature_value in features.items():
                self.feature_counts[label][feature_name][feature_value] += 1
                self.feature_values[feature_name].add(feature_value)
    
    def _calculate_class_probability(self, class_label: str) -> float:
        """
        Calculate P(class) - the prior probability of a class.
        
        Args:
            class_label: The class to calculate probability for
            
        Returns:
            Log probability of the class
        """
        # Using log probabilities to avoid underflow with many features
        return math.log(self.class_counts[class_label] / self.total_samples)
    
    def _calculate_feature_probability(self, class_label: str, 
                                      feature_name: str, 
                                      feature_value: Any) -> float:
        """
        Calculate P(feature_value|class) with Laplace smoothing.
        
        Args:
            class_label: The class label
            feature_name: Name of the feature
            feature_value: Value of the feature
            
        Returns:
            Log probability of the feature given the class
        """
        # Laplace smoothing: (count + α) / (total + α * num_possible_values)
        count = self.feature_counts[class_label][feature_name][feature_value]
        total = self.class_counts[class_label]
        num_values = len(self.feature_values[feature_name])
        
        smoothed_prob = (count + self.smoothing) / (total + self.smoothing * num_values)
        return math.log(smoothed_prob)
    
    def predict_single(self, features: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        """
        Predict the class for a single sample.
        
        Args:
            features: Dictionary mapping feature names to values
            
        Returns:
            Tuple of (predicted_class, probability_dict)
        """
        class_scores = {}
        
        for class_label in self.classes:
            # Start with prior probability P(class)
            score = self._calculate_class_probability(class_label)
            
            # Multiply by P(feature|class) for each feature (addition in log space)
            for feature_name, feature_value in features.items():
                score += self._calculate_feature_probability(
                    class_label, feature_name, feature_value
                )
            
            class_scores[class_label] = score
        
        # Return class with highest score
        predicted_class = max(class_scores, key=class_scores.get)
        return predicted_class, class_scores
    
    def predict(self, X: List[Dict[str, Any]]) -> List[str]:
        """
        Predict classes for multiple samples.
        
        Args:
            X: List of feature dictionaries
            
        Returns:
            List of predicted class labels
        """
        return [self.predict_single(features)[0] for features in X]
    
    def evaluate(self, X: List[Dict[str, Any]], y: List[str]) -> float:
        """
        Evaluate accuracy on test data.
        
        Args:
            X: List of feature dictionaries
            y: True class labels
            
        Returns:
            Accuracy as a float between 0 and 1
        """
        predictions = self.predict(X)
        correct = sum(1 for pred, true in zip(predictions, y) if pred == true)
        return correct / len(y)


if __name__ == "__main__":
    # Demo with a simple fruit classification dataset
    # Features: color, shape, size
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Training data - classifying fruits
    train_X = [
        {"color": "red", "shape": "round", "size": "small"},
        {"color": "red", "shape": "round", "size": "medium"},
        {"color": "yellow", "shape": "long", "size": "medium"},
        {"color": "yellow", "shape": "long", "size": "large"},
        {"color": "orange", "shape": "round", "size": "medium"},
        {"color": "orange", "shape": "round", "size": "large"},
        {"color": "green", "shape": "round", "size": "small"},
        {"color": "green", "shape": "round", "size": "medium"},
        {"color": "yellow", "shape": "round", "size": "small"},
        {"color": "red", "shape": "round", "size": "large"},
    ]
    
    train_y = ["apple", "apple", "banana", "banana", "orange", 
               "orange", "apple", "apple", "lemon", "apple"]
    
    # Train the model
    classifier = NaiveBayesClassifier(smoothing=1.0)
    classifier.fit(train_X, train_y)
    
    print(f"Trained on {len(train_y)} samples")
    print(f"Classes found: {sorted(classifier.classes)}\n")
    
    # Test predictions
    test_cases = [
        {"color": "red", "shape": "round", "size": "small"},
        {"color": "yellow", "shape": "long", "size": "large"},
        {"color": "orange", "shape": "round", "size": "medium"},
        {"color": "green", "shape": "round", "size": "large"},  # never seen this combo
    ]
    
    print("--- Predictions ---")
    for i, features in enumerate(test_cases, 1):
        predicted, scores = classifier.predict_single(features)
        print(f"\nTest {i}: {features}")
        print(f"Predicted: {predicted}")
        print(f"Scores (log probabilities): {dict(sorted(scores.items()))}")
    
    # Accuracy on training data (just for demo purposes)
    train_accuracy = classifier.evaluate(train_X, train_y)
    print(f"\n--- Training Accuracy: {train_accuracy:.2%} ---")