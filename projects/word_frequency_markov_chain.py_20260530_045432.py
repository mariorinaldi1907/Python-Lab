"""
Date: 2026-05-30
Created a Markov chain text generator that also does word frequency analysis — wanted something fun to mess around with for generating pseudo-coherent sentences from sample text.
"""

#!/usr/bin/env python3
"""
Word frequency analyzer and Markov chain text generator.
Analyzes input text and generates new sentences based on word transition probabilities.
"""

import random
import re
from collections import defaultdict, Counter


class MarkovChain:
    """
    A simple Markov chain text generator.
    Builds transition probabilities from input text and generates new sequences.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous words to consider for predictions (n-gram size - 1)
        """
        self.order = order
        self.chain = defaultdict(list)  # Maps state tuples to lists of possible next words
        self.start_states = []  # States that can begin a sentence
        
    def train(self, text):
        """
        Train the model on input text.
        
        Args:
            text: Input string to learn from
        """
        # Split into sentences, then words
        # Keep punctuation attached to words for more natural output
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) <= self.order:
                continue  # Skip sentences that are too short
                
            # First state can be a sentence starter
            self.start_states.append(tuple(words[:self.order]))
            
            # Build the chain by sliding a window through the sentence
            for i in range(len(words) - self.order):
                state = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.chain[state].append(next_word)
    
    def generate(self, length=20, seed=None):
        """
        Generate text using the trained model.
        
        Args:
            length: Maximum number of words to generate
            seed: Random seed for reproducibility (optional)
            
        Returns:
            Generated text as a string
        """
        if not self.start_states:
            return ""
        
        if seed is not None:
            random.seed(seed)
        
        # Start with a random beginning state
        current_state = list(random.choice(self.start_states))
        result = list(current_state)
        
        for _ in range(length - self.order):
            state_tuple = tuple(current_state[-self.order:])
            
            # If we've reached a dead end, stop early
            if state_tuple not in self.chain:
                break
            
            # Pick a random next word based on what we've seen follow this state
            next_word = random.choice(self.chain[state_tuple])
            result.append(next_word)
            current_state.append(next_word)
        
        return ' '.join(result)


class WordFrequencyAnalyzer:
    """
    Analyzes word frequencies in text and provides statistics.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.word_counts = Counter()
        self.total_words = 0
    
    def analyze(self, text):
        """
        Analyze the word frequencies in the given text.
        
        Args:
            text: Input string to analyze
        """
        # Normalize: lowercase and extract words (excluding punctuation)
        words = re.findall(r'\b[a-z]+\b', text.lower())
        self.word_counts.update(words)
        self.total_words = sum(self.word_counts.values())
    
    def top_words(self, n=10):
        """
        Get the n most common words.
        
        Args:
            n: Number of top words to return
            
        Returns:
            List of (word, count) tuples
        """
        return self.word_counts.most_common(n)
    
    def get_stats(self):
        """
        Get basic statistics about the analyzed text.
        
        Returns:
            Dictionary with vocabulary size and total word count
        """
        return {
            'vocabulary_size': len(self.word_counts),
            'total_words': self.total_words,
            'unique_ratio': len(self.word_counts) / self.total_words if self.total_words > 0 else 0
        }


if __name__ == "__main__":
    # Sample text - a mix of classic literature snippets
    sample_text = """
    It was the best of times, it was the worst of times, it was the age of wisdom,
    it was the age of foolishness. The sun did not shine, it was too wet to play,
    so we sat in the house all that cold, cold, wet day. All happy families are alike,
    each unhappy family is unhappy in its own way. Call me Ishmael. Some years ago,
    never mind how long precisely, having little or no money in my purse, I thought
    I would sail about a little and see the watery part of the world. It is a truth
    universally acknowledged that a single man in possession of a good fortune must
    be in want of a wife.
    """
    
    print("=" * 70)
    print("WORD FREQUENCY ANALYSIS")
    print("=" * 70)
    
    analyzer = WordFrequencyAnalyzer()
    analyzer.analyze(sample_text)
    
    stats = analyzer.get_stats()
    print(f"\nVocabulary size: {stats['vocabulary_size']} unique words")
    print(f"Total words: {stats['total_words']}")
    print(f"Unique ratio: {stats['unique_ratio']:.2%}")
    
    print("\nTop 10 most common words:")
    for word, count in analyzer.top_words(10):
        print(f"  {word:15} {count:3} times")
    
    print("\n" + "=" * 70)
    print("MARKOV CHAIN TEXT GENERATION")
    print("=" * 70)
    
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    
    print("\nGenerating 3 random sentences (order=2):\n")
    for i in range(3):
        generated = markov.generate(length=15, seed=None)
        print(f"{i+1}. {generated}")
    
    print("\n" + "=" * 70)