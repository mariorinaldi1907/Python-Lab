"""
Date: 2026-07-21
Implemented a Markov chain text generator with variable order n-grams because I wanted to see how coherent randomly generated text could get with proper prefix tracking.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds a statistical model from input text and generates new text that
mimics the style. I used a dictionary-based approach where keys are
n-grams (tuples of words) and values are lists of possible next words.
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A Markov chain text generator that learns word patterns from input text.
    
    The order determines how many previous words influence the next word choice.
    Higher order = more coherent but less creative output.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of words to use as context (1, 2, or 3 works best)
        """
        self.order = order
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_words: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Convert text into a list of words, preserving punctuation as separate tokens.
        
        I split on whitespace but keep punctuation attached when it makes sense,
        so "hello, world!" becomes ["hello,", "world!"] not ["hello", ",", "world", "!"]
        """
        # Simple whitespace tokenization - good enough for this use case
        words = text.split()
        return [word for word in words if word.strip()]
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain model from input text.
        
        This walks through the text and records what words follow each n-gram.
        For order=2, we track what word comes after each pair of words.
        """
        words = self.tokenize(text)
        
        if len(words) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order} chain")
        
        # Build the chain by sliding a window through the text
        for i in range(len(words) - self.order):
            # The current state is a tuple of 'order' words
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            
            # Track what word comes after this state
            self.chain[state].append(next_word)
            
            # Remember states that start sentences (capitalized first word)
            if i == 0 or self._is_sentence_start(words[i]):
                if state not in self.start_words:
                    self.start_words.append(state)
    
    def _is_sentence_start(self, word: str) -> bool:
        """
        Check if a word looks like it starts a sentence.
        
        Simple heuristic: capitalized and previous word ended with sentence punctuation.
        """
        return word[0].isupper() if word else False
    
    def generate(self, max_words: int = 100, seed: str = None) -> str:
        """
        Generate new text using the trained model.
        
        Args:
            max_words: Maximum number of words to generate
            seed: Optional starting phrase (will be tokenized)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise ValueError("Model not trained yet - call train() first")
        
        # Choose a starting state
        if seed:
            seed_words = self.tokenize(seed)
            if len(seed_words) >= self.order:
                current = tuple(seed_words[-self.order:])
                output = list(seed_words)
            else:
                # Seed too short, use random start and append seed
                current = random.choice(self.start_words or list(self.chain.keys()))
                output = list(current) + seed_words
        else:
            # Pick a random starting point, preferring sentence starts
            current = random.choice(self.start_words or list(self.chain.keys()))
            output = list(current)
        
        # Generate words one at a time
        for _ in range(max_words - len(output)):
            if current not in self.chain:
                # Dead end - pick a new random state to continue
                current = random.choice(list(self.chain.keys()))
                output.append("...")  # Visual indicator of the jump
            
            # Randomly choose one of the possible next words
            next_word = random.choice(self.chain[current])
            output.append(next_word)
            
            # Slide the window forward
            current = tuple(list(current[1:]) + [next_word])
        
        return " ".join(output)


def demo():
    """
    Demo the Markov chain with some classic text.
    
    Using a paragraph I typed out instead of loading a file, since this needs
    to run standalone without any external dependencies.
    """
    sample_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused by this display.
    The fox, being quite clever, decided to jump again. This time the dog chased the fox.
    The clever fox ran through the forest. The forest was dense and dark.
    In the forest, many creatures lived in harmony. The fox found a safe hiding spot.
    Meanwhile, the dog searched everywhere. The dog eventually gave up the search.
    The fox emerged victorious from this encounter. Victory was sweet for the clever animal.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Train with different orders to show the difference
    for order in [1, 2]:
        print(f"--- Order {order} Chain ---")
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        # Generate a few samples
        for i in range(3):
            generated = markov.generate(max_words=30)
            print(f"Sample {i+1}: {generated}\n")
        
        print()


if __name__ == "__main__":
    demo()