"""
Date: 2026-05-29
Implemented a Naive Bayes classifier to understand probabilistic classification better — handles text and categorical features with smoothing to avoid zero probabilities.
"""

"""
Naive Bayes classifier built from scratch.
Uses Laplace smoothing to handle unseen features gracefully.
"""

from collections import defaultdict
from math import log


class NaiveBayesClassifier:
    """
    A simple Naive Bayes classifier for categorical/text data.
    
    Uses log probabilities internally to avoid numerical underflow,
    and applies Laplace (add-one) smoothing to handle zero counts.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Smoothing parameter (default 1.0 for Laplace smoothing)
        """
        self.alpha = alpha
        self.class_counts = defaultdict(int)
        self.feature_counts = defaultdict(lambda: defaultdict(int))
        self.vocab = set()
        self.total_samples = 0
        
    def fit(self, X, y):
        """
        Train the classifier on labeled data.
        
        Args:
            X: List of feature sets (each feature set is a list/set of tokens)
            y: List of labels corresponding to each sample
        """
        self.total_samples = len(y)
        
        # Count class occurrences and feature occurrences per class
        for features, label in zip(X, y):
            self.class_counts[label] += 1
            
            for feature in features:
                self.vocab.add(feature)
                self.feature_counts[label][feature] += 1
        
    def _log_prior(self, label):
        """
        Calculate log prior probability of a class.
        
        P(class) = count(class) / total_samples
        """
        return log(self.class_counts[label] / self.total_samples)
    
    def _log_likelihood(self, feature, label):
        """
        Calculate log likelihood of a feature given a class.
        
        Uses Laplace smoothing:
        P(feature|class) = (count(feature, class) + alpha) / (count(class) + alpha * vocab_size)
        
        The denominator accounts for all possible features in the vocabulary,
        which is why we multiply alpha by vocab size.
        """
        feature_count = self.feature_counts[label][feature]
        total_features_in_class = sum(self.feature_counts[label].values())
        vocab_size = len(self.vocab)
        
        # Laplace smoothing prevents zero probabilities
        numerator = feature_count + self.alpha
        denominator = total_features_in_class + self.alpha * vocab_size
        
        return log(numerator / denominator)
    
    def predict(self, X):
        """
        Predict labels for a list of feature sets.
        
        Args:
            X: List of feature sets to classify
            
        Returns:
            List of predicted labels
        """
        return [self._predict_single(features) for features in X]
    
    def _predict_single(self, features):
        """
        Predict the label for a single feature set.
        
        For each class, we calculate:
        log P(class|features) ∝ log P(class) + Σ log P(feature|class)
        
        The class with the highest log probability wins.
        """
        scores = {}
        
        for label in self.class_counts:
            # Start with the prior
            score = self._log_prior(label)
            
            # Add log likelihoods for each feature
            for feature in features:
                score += self._log_likelihood(feature, label)
            
            scores[label] = score
        
        # Return the class with maximum score
        return max(scores, key=scores.get)


def tokenize(text):
    """Simple tokenizer that splits on whitespace and lowercases."""
    return text.lower().split()


if __name__ == "__main__":
    # Demo: Simple sentiment classification
    print("=== Naive Bayes Text Classifier Demo ===\n")
    
    # Training data: simple movie reviews
    train_texts = [
        "love this movie great acting",
        "amazing film best ever",
        "wonderful story loved it",
        "fantastic performance brilliant",
        "terrible movie worst ever",
        "awful film hated it",
        "boring waste of time",
        "horrible acting bad story",
    ]
    
    train_labels = [
        "positive", "positive", "positive", "positive",
        "negative", "negative", "negative", "negative"
    ]
    
    # Tokenize the training data
    X_train = [tokenize(text) for text in train_texts]
    
    # Train the classifier
    nb = NaiveBayesClassifier(alpha=1.0)
    nb.fit(X_train, train_labels)
    
    print(f"Trained on {len(train_texts)} samples")
    print(f"Vocabulary size: {len(nb.vocab)}\n")
    
    # Test on new reviews
    test_texts = [
        "love the brilliant acting",
        "terrible and boring film",
        "amazing story wonderful",
        "worst movie ever hated",
        "great performance",
    ]
    
    X_test = [tokenize(text) for text in test_texts]
    predictions = nb.predict(X_test)
    
    print("Predictions on test data:")
    print("-" * 50)
    for text, pred in zip(test_texts, predictions):
        print(f"'{text}' → {pred.upper()}")
    
    # Show some probability details for one example
    print("\n" + "=" * 50)
    print("Detailed scoring for: 'love the brilliant acting'")
    print("=" * 50)
    
    test_features = tokenize("love the brilliant acting")
    for label in nb.class_counts:
        score = nb._log_prior(label)
        print(f"\n{label.upper()}:")
        print(f"  Log prior: {score:.4f}")
        
        for feature in test_features:
            feat_score = nb._log_likelihood(feature, label)
            score += feat_score
            print(f"  + log P('{feature}'|{label}): {feat_score:.4f}")
        
        print(f"  Total score: {score:.4f}")