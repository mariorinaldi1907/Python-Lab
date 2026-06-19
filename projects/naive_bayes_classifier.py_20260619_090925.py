"""
Date: 2026-06-19
Built a multinomial naive bayes classifier to understand how probabilistic text classification actually works under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.
Uses multinomial NB which works well for text/discrete features.
"""

import math
from collections import defaultdict, Counter


class NaiveBayesClassifier:
    """
    Multinomial Naive Bayes classifier with Laplace smoothing.
    
    I wanted to really understand how this works, so I built it from the ground up.
    The key insight: we're calculating P(class|features) using Bayes theorem,
    but we assume features are independent (the "naive" part).
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Laplace smoothing parameter. Higher = more smoothing.
                   I default to 1.0 because it's standard and works well.
        """
        self.alpha = alpha
        self.class_priors = {}  # P(class)
        self.feature_probs = defaultdict(lambda: defaultdict(float))  # P(feature|class)
        self.classes = set()
        self.vocabulary = set()
        
    def fit(self, X, y):
        """
        Train the classifier on labeled data.
        
        Args:
            X: List of feature dictionaries (e.g., word counts)
            y: List of class labels
        """
        # Count examples per class
        class_counts = Counter(y)
        total_docs = len(y)
        
        # Calculate class priors: P(class) = count(class) / total_docs
        self.classes = set(y)
        for cls in self.classes:
            self.class_priors[cls] = class_counts[cls] / total_docs
        
        # Count features per class for likelihood calculation
        feature_counts = defaultdict(lambda: defaultdict(int))
        class_feature_totals = defaultdict(int)
        
        for features, label in zip(X, y):
            for feature, count in features.items():
                self.vocabulary.add(feature)
                feature_counts[label][feature] += count
                class_feature_totals[label] += count
        
        # Calculate P(feature|class) with Laplace smoothing
        # The smoothing prevents zero probabilities for unseen features
        vocab_size = len(self.vocabulary)
        
        for cls in self.classes:
            for feature in self.vocabulary:
                # Laplace smoothing: add alpha to numerator, alpha*vocab_size to denominator
                numerator = feature_counts[cls][feature] + self.alpha
                denominator = class_feature_totals[cls] + (self.alpha * vocab_size)
                self.feature_probs[cls][feature] = numerator / denominator
    
    def predict_log_proba(self, features):
        """
        Calculate log probabilities for each class.
        
        I use log probabilities because multiplying many small probabilities
        can cause numerical underflow. Logs turn multiplication into addition.
        
        Args:
            features: Dictionary of feature counts
            
        Returns:
            Dictionary mapping class -> log probability
        """
        log_probs = {}
        
        for cls in self.classes:
            # Start with log of prior probability
            log_prob = math.log(self.class_priors[cls])
            
            # Add log probabilities for each feature
            for feature, count in features.items():
                if feature in self.vocabulary:
                    # Multiply count times because feature appears 'count' times
                    log_prob += count * math.log(self.feature_probs[cls][feature])
            
            log_probs[cls] = log_prob
        
        return log_probs
    
    def predict(self, X):
        """
        Predict class labels for a list of feature dictionaries.
        
        Args:
            X: List of feature dictionaries
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        
        for features in X:
            log_probs = self.predict_log_proba(features)
            # Pick the class with highest log probability
            predicted_class = max(log_probs, key=log_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, features):
        """
        Get actual probabilities (not log) for each class.
        
        Converts log probabilities back to regular probabilities and normalizes.
        """
        log_probs = self.predict_log_proba(features)
        
        # Convert from log space and normalize
        max_log = max(log_probs.values())
        probs = {}
        
        for cls, log_p in log_probs.items():
            probs[cls] = math.exp(log_p - max_log)
        
        # Normalize to sum to 1
        total = sum(probs.values())
        return {cls: p / total for cls, p in probs.items()}


def tokenize(text):
    """Simple word tokenizer that lowercases and splits on whitespace."""
    return text.lower().split()


def text_to_features(text):
    """Convert text into a feature dictionary (bag of words)."""
    tokens = tokenize(text)
    return Counter(tokens)


if __name__ == "__main__":
    # Demo: classify movie reviews as positive or negative
    print("=== Naive Bayes Text Classifier Demo ===\n")
    
    # Training data - simple movie reviews
    train_texts = [
        "great movie loved it amazing acting",
        "wonderful film best ever seen",
        "loved the story great performance",
        "terrible movie worst ever",
        "awful film hated it bad acting",
        "waste of time boring movie",
        "fantastic amazing loved every minute",
        "horrible terrible worst film",
    ]
    
    train_labels = [
        "positive", "positive", "positive",
        "negative", "negative", "negative",
        "positive", "negative"
    ]
    
    # Convert texts to feature dictionaries
    X_train = [text_to_features(text) for text in train_texts]
    
    # Train the classifier
    nb = NaiveBayesClassifier(alpha=1.0)
    nb.fit(X_train, train_labels)
    
    print(f"Trained on {len(train_texts)} examples")
    print(f"Vocabulary size: {len(nb.vocabulary)}\n")
    
    # Test on new reviews
    test_texts = [
        "great acting loved it",
        "terrible waste of time",
        "amazing wonderful film",
        "boring awful movie",
    ]
    
    print("Testing predictions:\n")
    for text in test_texts:
        features = text_to_features(text)
        prediction = nb.predict([features])[0]
        probabilities = nb.predict_proba(features)
        
        print(f"Text: '{text}'")
        print(f"Prediction: {prediction}")
        print(f"Probabilities: positive={probabilities['positive']:.3f}, "
              f"negative={probabilities['negative']:.3f}\n")