"""
Date: 2026-06-02
Built a Naive Bayes classifier to understand probabilistic ML better — handles discrete features and includes smoothing to avoid zero probabilities.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier - Built from scratch
============================================

A simple implementation of the Naive Bayes algorithm for classification.
Uses Laplace smoothing to handle unseen features and avoid zero probabilities.

I wanted to understand the math behind this probabilistic classifier, so I
coded it up without any ML libraries. Works pretty well for text-like data!
"""

import math
from collections import defaultdict, Counter


class NaiveBayesClassifier:
    """
    A Naive Bayes classifier using maximum likelihood estimation.
    
    The "naive" assumption is that all features are conditionally independent
    given the class label. This rarely holds in reality, but it works surprisingly
    well in practice, especially for text classification.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Laplace smoothing parameter. Setting alpha=1.0 gives us
                   additive smoothing to avoid zero probabilities when we
                   encounter features we haven't seen during training.
        """
        self.alpha = alpha
        self.class_counts = Counter()
        self.feature_counts = defaultdict(lambda: defaultdict(int))
        self.class_feature_totals = defaultdict(int)
        self.vocabulary = set()
        self.classes = set()
        
    def fit(self, X, y):
        """
        Train the classifier on labeled data.
        
        Args:
            X: List of feature dictionaries. Each dict maps feature names to counts.
               Example: [{"word_hello": 2, "word_world": 1}, ...]
            y: List of class labels corresponding to X.
        
        The method calculates:
        - P(class) for each class
        - P(feature|class) for each feature given each class
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        # Count how many times each class appears (for prior probabilities)
        for label in y:
            self.class_counts[label] += 1
            self.classes.add(label)
        
        # Count feature occurrences per class (for likelihood)
        for features, label in zip(X, y):
            for feature, count in features.items():
                self.vocabulary.add(feature)
                self.feature_counts[label][feature] += count
                self.class_feature_totals[label] += count
    
    def _log_prior(self, class_label):
        """
        Calculate log P(class).
        
        Using log probabilities to avoid numerical underflow when multiplying
        many small probabilities together.
        """
        total_samples = sum(self.class_counts.values())
        return math.log(self.class_counts[class_label] / total_samples)
    
    def _log_likelihood(self, feature, count, class_label):
        """
        Calculate log P(feature|class) with Laplace smoothing.
        
        The smoothing ensures we never multiply by zero, which would destroy
        all our probability calculations. Alpha=1.0 means we pretend we've
        seen every possible feature once in every class.
        """
        numerator = self.feature_counts[class_label][feature] + self.alpha
        denominator = self.class_feature_totals[class_label] + (self.alpha * len(self.vocabulary))
        return count * math.log(numerator / denominator)
    
    def predict_log_proba(self, features):
        """
        Calculate log probabilities for each class given the features.
        
        Returns a dict mapping class labels to their log probabilities.
        We use the Naive Bayes formula:
        P(class|features) ∝ P(class) * ∏ P(feature|class)
        """
        log_probas = {}
        
        for class_label in self.classes:
            # Start with the prior probability
            log_prob = self._log_prior(class_label)
            
            # Multiply by the likelihood of each feature (in log space = addition)
            for feature, count in features.items():
                if feature in self.vocabulary:
                    log_prob += self._log_likelihood(feature, count, class_label)
            
            log_probas[class_label] = log_prob
        
        return log_probas
    
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
            log_probas = self.predict_log_proba(features)
            # Pick the class with the highest probability
            predicted_class = max(log_probas.items(), key=lambda x: x[1])[0]
            predictions.append(predicted_class)
        
        return predictions


def tokenize_simple(text):
    """
    Super basic tokenizer for demo purposes.
    
    In a real project I'd use regex or a proper NLP library, but keeping
    this dependency-free. Just splits on whitespace and lowercases.
    """
    return [word.strip('.,!?;:').lower() for word in text.split()]


def text_to_features(text):
    """Convert text to a feature dictionary (bag of words)."""
    words = tokenize_simple(text)
    return Counter(words)


if __name__ == "__main__":
    # Demo: Sentiment classification with toy data
    # I'm using very obvious examples so the classifier succeeds even with tiny training data
    
    print("=" * 60)
    print("Naive Bayes Classifier Demo - Sentiment Analysis")
    print("=" * 60)
    
    # Training data: simple movie reviews
    training_texts = [
        "I love this movie it is amazing and wonderful",
        "This movie is great and fantastic I enjoyed it",
        "Best film ever so good and awesome",
        "I hate this movie it is terrible and boring",
        "This movie is awful and horrible waste of time",
        "Worst film ever so bad and dreadful",
    ]
    
    training_labels = ["positive", "positive", "positive", "negative", "negative", "negative"]
    
    # Convert texts to feature dictionaries
    X_train = [text_to_features(text) for text in training_texts]
    
    # Train the classifier
    classifier = NaiveBayesClassifier(alpha=1.0)
    classifier.fit(X_train, training_labels)
    
    print("\nTraining completed!")
    print(f"Classes learned: {sorted(classifier.classes)}")
    print(f"Vocabulary size: {len(classifier.vocabulary)} unique words")
    
    # Test on new examples
    test_texts = [
        "I love it this is wonderful",
        "This is terrible and boring",
        "An awesome and amazing experience",
        "Horrible waste of my time",
    ]
    
    print("\n" + "-" * 60)
    print("Predictions on new reviews:")
    print("-" * 60)
    
    X_test = [text_to_features(text) for text in test_texts]
    predictions = classifier.predict(X_test)
    
    for text, prediction in zip(test_texts, predictions):
        # Also show the probability breakdown for transparency
        features = text_to_features(text)
        log_probas = classifier.predict_log_proba(features)
        
        print(f"\nText: \"{text}\"")
        print(f"Prediction: {prediction.upper()}")
        print("Log probabilities:")
        for label, log_prob in sorted(log_probas.items()):
            print(f"  {label}: {log_prob:.2f}")