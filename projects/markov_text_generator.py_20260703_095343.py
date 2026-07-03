"""
Date: 2026-07-03
Created a configurable Markov chain generator that learns from input text and produces semi-coherent output while respecting sentence boundaries.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Generates semi-random text based on statistical patterns learned from input text.
I wanted something that could mimic writing style without being completely nonsensical.
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A Markov chain text generator that learns transition probabilities from input text.
    
    Uses n-grams (default bigrams) to build a state transition table, then generates
    new text by randomly walking through states weighted by their occurrence frequency.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The number of words to use as state (n-gram size).
                   order=1 means each word depends only on the previous word.
                   order=2 means each word depends on the previous 2 words, etc.
        """
        self.order = order
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_states: List[Tuple[str, ...]] = []
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from input text.
        
        I split by sentences first to avoid generating text that bleeds across
        sentence boundaries in weird ways. Each sentence becomes a training sequence.
        
        Args:
            text: The training corpus as a string.
        """
        # Split into sentences using basic punctuation as delimiters
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            # Tokenize: split on whitespace and filter out empty strings
            words = [w for w in sentence.split() if w]
            
            if len(words) < self.order + 1:
                continue  # Skip sentences too short for our n-gram order
            
            # Record this as a potential starting state
            start_state = tuple(words[:self.order])
            self.start_states.append(start_state)
            
            # Build the transition table
            for i in range(len(words) - self.order):
                state = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.chain[state].append(next_word)
    
    def generate(self, length: int = 50, seed: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Maximum number of words to generate.
            seed: Optional starting state. If None, picks randomly from sentence starts.
        
        Returns:
            Generated text as a string.
        """
        if not self.chain:
            return ""
        
        # Pick a starting state
        if seed and seed in self.chain:
            current_state = seed
        elif self.start_states:
            current_state = random.choice(self.start_states)
        else:
            current_state = random.choice(list(self.chain.keys()))
        
        result = list(current_state)
        
        # Generate words by following the chain
        for _ in range(length - self.order):
            if current_state not in self.chain:
                # Dead end — try to pick a new start
                if self.start_states:
                    current_state = random.choice(self.start_states)
                    result.extend(current_state)
                else:
                    break
            
            # Pick next word weighted by frequency (duplicates in list = higher probability)
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the window: drop first word, add new word
            current_state = tuple(result[-self.order:])
        
        return ' '.join(result)


def load_sample_text() -> str:
    """
    Returns a sample text for demonstration purposes.
    Using some public domain text since I can't rely on external files.
    """
    return """
    The quick brown fox jumps over the lazy dog. The dog was not amused by this behavior.
    The fox, being quite clever, decided to jump again. This time the dog chased the fox.
    The fox ran quickly through the forest. The forest was dark and mysterious.
    The mysterious sounds echoed through the trees. The trees swayed in the gentle wind.
    The wind carried the scent of pine. The pine trees stood tall and proud.
    The proud fox finally escaped. The dog returned home tired but happy.
    The happy ending pleased everyone. Everyone cheered for the clever fox.
    The clever fox became a legend. The legend spread far and wide.
    The wide world heard the tale. The tale was told for generations.
    """


if __name__ == "__main__":
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Load training data
    sample_text = load_sample_text()
    print("Training text excerpt:")
    print(sample_text[:150] + "...\n")
    
    # Train different order models to show the difference
    for order in [1, 2, 3]:
        print(f"--- Order {order} Markov Chain ---")
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        # Generate a few samples
        for i in range(2):
            generated = markov.generate(length=30)
            print(f"Sample {i+1}: {generated}")
        print()
    
    # Demonstrate seeded generation
    print("--- Seeded Generation (order=2, seed='The fox') ---")
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    
    # Show what happens when we force a specific start
    seeded = markov.generate(length=25, seed=('The', 'fox'))
    print(f"Seeded output: {seeded}")
    print("\n✓ Demo complete!")
```