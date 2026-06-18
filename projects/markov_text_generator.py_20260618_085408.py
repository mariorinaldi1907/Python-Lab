"""
Date: 2026-06-18
Implemented a Markov chain text generator that learns from input text and produces random but statistically similar output — adjustable n-gram size for different coherence levels.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds a probabilistic model from input text and generates new text that
mimics the statistical patterns of the original.
"""

import random
import sys
from collections import defaultdict, deque
from typing import List, Tuple, Dict


class MarkovChain:
    """
    A Markov chain text generator that uses n-grams to model text patterns.
    
    The state_size parameter controls how many words we look back to predict
    the next word. Higher values = more coherent but less creative output.
    """
    
    def __init__(self, state_size: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            state_size: Number of words to use as state (default 2 = bigram)
        """
        self.state_size = state_size
        # Maps tuples of words to lists of possible next words
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        # Track all states that could start a sentence (begin with capital)
        self.start_states: List[Tuple[str, ...]] = []
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from input text.
        
        Args:
            text: Input text to learn from
        """
        # Tokenize - simple split on whitespace preserves punctuation
        words = text.split()
        
        if len(words) < self.state_size + 1:
            raise ValueError(f"Text too short for state_size={self.state_size}")
        
        # Build the chain using a sliding window
        for i in range(len(words) - self.state_size):
            # Current state is a tuple of state_size words
            state = tuple(words[i:i + self.state_size])
            next_word = words[i + self.state_size]
            
            self.chain[state].append(next_word)
            
            # Track states that could start sentences
            # Simple heuristic: first word starts with capital
            if state[0][0].isupper() and state not in self.start_states:
                self.start_states.append(state)
        
        # If no capital-starting states found, just use any state
        if not self.start_states:
            self.start_states = list(self.chain.keys())
    
    def generate(self, length: int = 50, seed_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Number of words to generate
            seed_state: Optional starting state (tuple of words)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Chain not trained yet - call train() first")
        
        # Pick a random starting state if none provided
        if seed_state is None:
            state = random.choice(self.start_states)
        else:
            if len(seed_state) != self.state_size:
                raise ValueError(f"seed_state must have length {self.state_size}")
            state = seed_state
        
        # Start output with the initial state
        output = list(state)
        
        # Generate words one at a time
        for _ in range(length - self.state_size):
            if state not in self.chain:
                # Dead end - pick a new random state to continue
                state = random.choice(list(self.chain.keys()))
            
            # Pick a random next word from the possible options
            next_word = random.choice(self.chain[state])
            output.append(next_word)
            
            # Slide the window: drop first word, add new word
            state = tuple(list(state[1:]) + [next_word])
        
        return ' '.join(output)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the trained model.
        
        Returns:
            Dictionary with model statistics
        """
        total_transitions = sum(len(nexts) for nexts in self.chain.values())
        return {
            'unique_states': len(self.chain),
            'total_transitions': total_transitions,
            'start_states': len(self.start_states),
            'state_size': self.state_size
        }


if __name__ == "__main__":
    # Sample text - a few paragraphs about programming
    # In real use, you'd load this from a file
    sample_text = """
    Python is a high-level programming language. Python emphasizes code readability
    and simplicity. The language provides constructs for clear programming on both
    small and large scales. Python supports multiple programming paradigms including
    object-oriented programming and functional programming. Python is dynamically typed
    and garbage-collected. Python was created by Guido van Rossum and first released
    in 1991. The Python community is known for being welcoming to newcomers.
    Programming in Python is often described as fun. Python has a comprehensive
    standard library. The language is widely used in web development and data science.
    Python code is easy to read and write. Many developers love Python for its elegance.
    """
    
    print("=" * 60)
    print("Markov Chain Text Generator Demo")
    print("=" * 60)
    
    # Test with different state sizes
    for state_size in [1, 2, 3]:
        print(f"\n--- State Size: {state_size} ---")
        
        markov = MarkovChain(state_size=state_size)
        markov.train(sample_text)
        
        stats = markov.get_stats()
        print(f"Model stats: {stats}")
        
        # Generate a few samples
        print("\nGenerated samples:")
        for i in range(2):
            generated = markov.generate(length=30)
            print(f"  {i+1}. {generated}")
    
    print("\n" + "=" * 60)
    print("Notice how higher state_size = more coherent output")
    print("but lower creativity. State size 1 is chaotic but weird!")
    print("=" * 60)