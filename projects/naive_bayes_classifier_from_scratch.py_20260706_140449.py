"""
Date: 2026-07-06
Built a Naive Bayes classifier to understand probabilistic classification better — handles both categorical and text data with smoothing to avoid zero probabilities.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.

I wanted to really understand how probabilistic classification works under the hood,
so I built this without any ML libraries. Uses Laplace smoothing to handle unseen
features gracefully.
"""

import math
from collections import defaultdict, Counter


class NaiveBayesClassifier:
    """
    A from-scratch Naive Bayes classifier using maximum likelihood estimation.
    
    Works by calculating P(class|features) using Bayes theorem:
    P(class|features) ∝ P(class) * P(feature1|class) * P(feature2|class) * ...
    
    I'm using log probabilities to avoid numerical underflow when multiplying
    lots of small probabilities together.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Laplace smoothing parameter. Set to 1.0 for add-one smoothing,
                   which prevents zero probabilities for unseen features.
        """
        self.alpha = alpha
        self.class_counts = Counter()
        self.feature_counts = defaultdict(lambda: defaultdict(Counter))
        self.classes = set()
        self.vocabulary = set()
        
    def fit(self, X, y):
        """
        Train the classifier on labeled data.
        
        Args:
            X: List of feature dictionaries, where each dict maps feature names to values
            y: List of class labels corresponding to each sample in X
        """
        if len(X) != len(y):
            raise ValueError("X and y must have the same length")
        
        # Reset state in case fit is called multiple times
        self.class_counts.clear()
        self.feature_counts.clear()
        self.classes.clear()
        self.vocabulary.clear()
        
        # Count everything we need for probability estimation
        for features, label in zip(X, y):
            self.classes.add(label)
            self.class_counts[label] += 1
            
            for feature_name, feature_value in features.items():
                self.vocabulary.add(feature_name)
                self.feature_counts[label][feature_name][feature_value] += 1
    
    def _calculate_class_log_prior(self, class_label):
        """
        Calculate log P(class).
        
        This is just the proportion of training samples with this class.
        """
        total_samples = sum(self.class_counts.values())
        return math.log(self.class_counts[class_label] / total_samples)
    
    def _calculate_feature_log_likelihood(self, class_label, feature_name, feature_value):
        """
        Calculate log P(feature=value|class) with Laplace smoothing.
        
        The smoothing adds alpha to all counts, which prevents zeros and makes
        the model more robust to unseen data. This was a key insight for me —
        without smoothing, one unseen word could zero out entire predictions.
        """
        feature_given_class = self.feature_counts[class_label][feature_name]
        value_count = feature_given_class[feature_value]
        
        # Number of unique values we've seen for this feature in this class
        num_unique_values = len(feature_given_class)
        
        # Total occurrences of this feature in this class
        total_count = sum(feature_given_class.values())
        
        # Laplace smoothing: add alpha to numerator, alpha * vocab_size to denominator
        # I'm using a rough estimate of vocab size here based on observed values
        vocab_size = max(num_unique_values, 2)  # At least 2 for binary features
        
        smoothed_prob = (value_count + self.alpha) / (total_count + self.alpha * vocab_size)
        return math.log(smoothed_prob)
    
    def predict_log_proba(self, features):
        """
        Calculate log probabilities for each class given the features.
        
        Returns a dict mapping class labels to log probabilities.
        """
        log_probs = {}
        
        for class_label in self.classes:
            # Start with the prior probability of this class
            log_prob = self._calculate_class_log_prior(class_label)
            
            # Multiply (add in log space) the likelihood of each feature
            for feature_name, feature_value in features.items():
                if feature_name in self.vocabulary:
                    log_prob += self._calculate_feature_log_likelihood(
                        class_label, feature_name, feature_value
                    )
            
            log_probs[class_label] = log_prob
        
        return log_probs
    
    def predict(self, features):
        """
        Predict the most likely class for the given features.
        
        Returns the class with the highest posterior probability.
        """
        log_probs = self.predict_log_proba(features)
        return max(log_probs, key=log_probs.get)


def tokenize(text):
    """
    Simple tokenizer that splits on whitespace and lowercases.
    
    In a real project I'd use something fancier, but this works for demo purposes.
    """
    return text.lower().split()


def text_to_features(text):
    """
    Convert text to a bag-of-words feature dictionary.
    
    Each unique word becomes a feature with its count as the value.
    """
    tokens = tokenize(text)
    return dict(Counter(tokens))


if __name__ == "__main__":
    # Demo: Sentiment classification on some made-up movie reviews
    # This is obviously toy data, but it shows how the classifier works
    
    print("=== Naive Bayes Classifier Demo ===\n")
    
    train_data = [
        ("I loved this movie it was fantastic and amazing", "positive"),
        ("Great film with wonderful acting and beautiful scenes", "positive"),
        ("Absolutely amazing I enjoyed every minute of it", "positive"),
        ("Best movie I have seen in years truly outstanding", "positive"),
        ("This movie was terrible and boring I hated it", "negative"),
        ("Awful film waste of time and money", "negative"),
        ("I hated every second of this terrible movie", "negative"),
        ("Worst film ever made completely unwatchable", "negative"),
    ]
    
    # Convert text to feature dictionaries
    X_train = [text_to_features(text) for text, _ in train_data]
    y_train = [label for _, label in train_data]
    
    # Train the classifier
    classifier = NaiveBayesClassifier(alpha=1.0)
    classifier.fit(X_train, y_train)
    
    print("Training complete!\n")
    print(f"Learned {len(classifier.vocabulary)} unique words")
    print(f"Classes: {classifier.classes}\n")
    
    # Test on new reviews
    test_reviews = [
        "This movie was wonderful and amazing",
        "I hated this terrible film",
        "Great acting but boring story",  # This one is ambiguous
    ]
    
    print("=== Predictions ===\n")
    for review in test_reviews:
        features = text_to_features(review)
        prediction = classifier.predict(features)
        log_probs = classifier.predict_log_proba(features)
        
        print(f"Review: '{review}'")
        print(f"Predicted: {prediction}")
        print(f"Log probabilities: {log_probs}")
        print()