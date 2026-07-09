"""
Date: 2026-07-09
Implemented a Markov chain text generator that can learn from any text corpus and generate somewhat coherent sentences — fun for generating nonsense from my old commit messages.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Learns patterns from input text and generates new text that sounds similar.
Uses n-grams (default bigrams) to build a probability model.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Optional


class MarkovChain:
    """
    A simple Markov chain text generator.
    
    Learns transitions between n-grams and generates new text based on
    the probability distributions found in the training corpus.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The n-gram size (order). 2 means we look at pairs of words
                   to predict the next one.
        """
        self.order = order
        # Maps from n-gram tuple to possible next words and their counts
        self.chain = defaultdict(Counter)
        self.start_tokens = []  # Store sentence start n-grams
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words, preserving sentence boundaries.
        
        I'm keeping punctuation attached to words because it helps with
        generating more natural-looking output.
        """
        # Split on whitespace but keep punctuation with words
        tokens = text.split()
        return [token for token in tokens if token]
    
    def _get_ngrams(self, tokens: List[str]) -> List[Tuple[str, ...]]:
        """
        Extract overlapping n-grams from token list.
        
        For order=2 and tokens=['the', 'quick', 'brown', 'fox'], this returns:
        [('the', 'quick'), ('quick', 'brown'), ('brown', 'fox')]
        """
        if len(tokens) < self.order:
            return []
        return [tuple(tokens[i:i + self.order]) for i in range(len(tokens) - self.order + 1)]
    
    def train(self, text: str):
        """
        Train the Markov chain on the provided text.
        
        Builds up the transition probabilities by counting which words
        follow which n-grams in the training data.
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            return  # Not enough data to learn anything
        
        # Build the chain: for each n-gram, record what comes next
        for i in range(len(tokens) - self.order):
            current_state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            self.chain[current_state][next_token] += 1
            
            # Track sentence starts (n-grams that start with capital letters)
            # This is a simple heuristic but works okay for demo purposes
            if current_state[0][0].isupper():
                if current_state not in self.start_tokens:
                    self.start_tokens.append(current_state)
    
    def _choose_next_token(self, state: Tuple[str, ...]) -> Optional[str]:
        """
        Choose the next token based on probability distribution.
        
        Randomly samples from the possible next tokens, weighted by how
        often each one appeared in the training data.
        """
        if state not in self.chain:
            return None
        
        next_tokens = self.chain[state]
        total = sum(next_tokens.values())
        
        # Weighted random choice
        rand = random.randint(1, total)
        cumulative = 0
        for token, count in next_tokens.items():
            cumulative += count
            if cumulative >= rand:
                return token
        
        return None
    
    def generate(self, max_length: int = 50, seed: Optional[Tuple[str, ...]] = None) -> str:
        """
        Generate text using the trained Markov chain.
        
        Args:
            max_length: Maximum number of tokens to generate
            seed: Optional starting n-gram. If None, picks randomly from sentence starts
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return ""
        
        # Pick starting state
        if seed and seed in self.chain:
            current_state = seed
        elif self.start_tokens:
            current_state = random.choice(self.start_tokens)
        else:
            current_state = random.choice(list(self.chain.keys()))
        
        result = list(current_state)
        
        # Keep generating until we hit max length or get stuck
        for _ in range(max_length - self.order):
            next_token = self._choose_next_token(current_state)
            
            if next_token is None:
                break
            
            result.append(next_token)
            
            # Slide the window: drop first token, add new one at end
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some tech-related text
    sample_text = """
    Python is a high-level programming language. Python emphasizes code readability.
    The language provides constructs to enable clear programs. Python supports multiple
    programming paradigms. Python features a dynamic type system. Python is widely used
    in data science. Machine learning projects often use Python. Python has a large
    standard library. The Python community is welcoming and active. Python code is easy
    to write and maintain. Many developers love Python for its simplicity.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on sample text about Python...\n")
    
    # Create and train the model
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    
    # Generate a few samples
    print("Generated samples:\n")
    for i in range(5):
        generated = markov.generate(max_length=20)
        print(f"{i+1}. {generated}\n")
    
    print("---")
    print("Note: With more training data, the output gets more interesting!")
    print("Try feeding it your git commit messages or README files.")