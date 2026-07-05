"""
Date: 2026-07-05
Implemented a Naive Bayes classifier to understand probabilistic ML better — handles text classification with smoothing for unseen features.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier from scratch.

I wanted to understand how probabilistic classifiers work under the hood,
so I built this without any ML libraries. Uses Laplace smoothing to handle
features that don't appear in training data.
"""

import math
from collections import defaultdict


class NaiveBayesClassifier:
    """
    A simple Naive Bayes classifier that works with discrete features.
    
    The "naive" part comes from assuming features are independent given the class,
    which is rarely true in practice but works surprisingly well anyway.
    """
    
    def __init__(self, smoothing=1.0):
        """
        Initialize the classifier.
        
        Args:
            smoothing: Laplace smoothing parameter (alpha). Higher values mean
                      we assume unseen features are more likely. Default of 1.0
                      is standard additive smoothing.
        """
        self.smoothing = smoothing
        self.class_counts = defaultdict(int)
        self.feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.vocabulary = set()
        self.classes = set()
        self.trained = False
    
    def train(self, X, y):
        """
        Train the classifier on labeled data.
        
        Args:
            X: List of feature dictionaries, where each dict maps feature names to values
            y: List of class labels (same length as X)
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        # Count class occurrences
        for label in y:
            self.class_counts[label] += 1
            self.classes.add(label)
        
        # Count feature occurrences per class
        # Structure: feature_counts[class][feature_name][feature_value] = count
        for features, label in zip(X, y):
            for feature_name, feature_value in features.items():
                self.feature_counts[label][feature_name][feature_value] += 1
                self.vocabulary.add((feature_name, feature_value))
        
        self.trained = True
    
    def _calculate_class_log_prior(self, class_label):
        """
        Calculate log P(class) - the prior probability of a class.
        
        Using log probabilities to avoid numerical underflow when multiplying
        many small probabilities together.
        """
        total_samples = sum(self.class_counts.values())
        return math.log(self.class_counts[class_label] / total_samples)
    
    def _calculate_feature_log_likelihood(self, class_label, feature_name, feature_value):
        """
        Calculate log P(feature=value | class) with Laplace smoothing.
        
        The smoothing prevents zero probabilities for unseen features, which would
        otherwise dominate the entire prediction (since we multiply probabilities).
        """
        # Count how many times this specific feature value appeared for this class
        feature_count = self.feature_counts[class_label][feature_name][feature_value]
        
        # Total examples of this class
        total_class_count = self.class_counts[class_label]
        
        # Number of possible values for this feature (for smoothing denominator)
        # We count unique values across all classes
        unique_values = set()
        for c in self.classes:
            unique_values.update(self.feature_counts[c][feature_name].keys())
        vocab_size = len(unique_values) if unique_values else 1
        
        # Laplace smoothing formula
        numerator = feature_count + self.smoothing
        denominator = total_class_count + (self.smoothing * vocab_size)
        
        return math.log(numerator / denominator)
    
    def predict(self, X):
        """
        Predict class labels for a list of feature dictionaries.
        
        Returns:
            List of predicted class labels
        """
        if not self.trained:
            raise ValueError("Classifier must be trained before prediction")
        
        predictions = []
        for features in X:
            predictions.append(self._predict_single(features))
        return predictions
    
    def _predict_single(self, features):
        """
        Predict the class for a single example.
        
        We calculate log P(class | features) ∝ log P(class) + Σ log P(feature | class)
        and pick the class with the highest value.
        """
        class_scores = {}
        
        for class_label in self.classes:
            # Start with the prior
            score = self._calculate_class_log_prior(class_label)
            
            # Add likelihood for each feature
            for feature_name, feature_value in features.items():
                score += self._calculate_feature_log_likelihood(
                    class_label, feature_name, feature_value
                )
            
            class_scores[class_label] = score
        
        # Return class with highest score
        return max(class_scores, key=class_scores.get)


def tokenize_simple(text):
    """Convert text to a simple bag-of-words feature dict."""
    words = text.lower().split()
    return {f"word_{word}": True for word in words}


if __name__ == "__main__":
    # Demo: classify simple movie reviews as positive or negative
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Training data - super simple movie reviews
    train_texts = [
        "this movie was amazing and wonderful",
        "loved the acting great film",
        "best movie ever seen absolutely brilliant",
        "terrible waste of time awful acting",
        "horrible movie very disappointing",
        "worst film boring and dull",
        "fantastic story great performances",
        "poor plot terrible direction"
    ]
    
    train_labels = [
        "positive", "positive", "positive",
        "negative", "negative", "negative",
        "positive", "negative"
    ]
    
    # Convert to feature dictionaries
    X_train = [tokenize_simple(text) for text in train_texts]
    
    # Train classifier
    classifier = NaiveBayesClassifier(smoothing=1.0)
    classifier.train(X_train, train_labels)
    
    print(f"Trained on {len(train_texts)} examples")
    print(f"Classes: {sorted(classifier.classes)}")
    print(f"Vocabulary size: {len(classifier.vocabulary)}\n")
    
    # Test on new reviews
    test_texts = [
        "amazing wonderful brilliant",
        "terrible awful horrible",
        "great acting loved it",
        "waste of time very boring",
        "best film ever"
    ]
    
    X_test = [tokenize_simple(text) for text in test_texts]
    predictions = classifier.predict(X_test)
    
    print("Predictions:")
    print("-" * 60)
    for text, pred in zip(test_texts, predictions):
        print(f"'{text}' → {pred.upper()}")
    
    print("\nDone! The classifier uses word presence as features and assumes")
    print("independence between words (the 'naive' assumption).")