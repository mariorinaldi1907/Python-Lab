"""
Date: 2026-07-14
Created a Markov chain text generator that learns from sample text and produces semi-coherent output — added state length customization because bigrams alone produce nonsense.
"""

#!/usr/bin/env python3
"""
Markov chain text generator that learns patterns from input text.
I wanted to see how coherent output gets with different n-gram sizes.
"""

import random
from collections import defaultdict, deque
from typing import List, Tuple


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The state_length determines how much context is used to predict
    the next word. Higher values = more coherent but less creative.
    """
    
    def __init__(self, state_length: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            state_length: Number of words to use as context (default 2 for bigrams)
        """
        self.state_length = state_length
        # Maps a tuple of words (state) to a list of possible next words
        self.chain = defaultdict(list)
        self.start_states = []  # Valid states that can start a sentence
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        I'm tokenizing naively here (just splitting on whitespace) because
        proper tokenization would need regex and I want to keep this simple.
        
        Args:
            text: Training corpus as a single string
        """
        words = text.split()
        
        if len(words) < self.state_length + 1:
            raise ValueError(f"Text too short for state_length={self.state_length}")
        
        # Build the chain by sliding a window across the text
        for i in range(len(words) - self.state_length):
            # Current state is a tuple of state_length words
            state = tuple(words[i:i + self.state_length])
            next_word = words[i + self.state_length]
            
            self.chain[state].append(next_word)
            
            # Track states that start with capital letters (sentence starts)
            if i == 0 or words[i][0].isupper():
                self.start_states.append(state)
        
        if not self.start_states:
            # Fallback: use any state as a start state
            self.start_states = list(self.chain.keys())
    
    def generate(self, max_length: int = 50, seed: str = None) -> str:
        """
        Generate text using the trained Markov chain.
        
        Args:
            max_length: Maximum number of words to generate
            seed: Optional starting phrase (must match state_length words)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Chain not trained yet. Call train() first.")
        
        # Choose starting state
        if seed:
            seed_words = seed.split()
            if len(seed_words) != self.state_length:
                raise ValueError(f"Seed must be exactly {self.state_length} words")
            current_state = tuple(seed_words)
            if current_state not in self.chain:
                raise ValueError(f"Seed '{seed}' not found in trained data")
        else:
            current_state = random.choice(self.start_states)
        
        result = list(current_state)
        
        # Generate words by following the chain
        for _ in range(max_length - self.state_length):
            if current_state not in self.chain:
                # Dead end — this state wasn't seen during training
                break
            
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the state window forward
            current_state = tuple(result[-self.state_length:])
        
        return ' '.join(result)
    
    def get_stats(self) -> dict:
        """Return some statistics about the trained model."""
        total_transitions = sum(len(nexts) for nexts in self.chain.values())
        return {
            'unique_states': len(self.chain),
            'total_transitions': total_transitions,
            'start_states': len(self.start_states),
            'avg_transitions_per_state': total_transitions / len(self.chain) if self.chain else 0
        }


def demo():
    """
    Demo the Markov chain with some sample text.
    Using a paragraph about programming because why not.
    """
    sample_text = """
    Python is a high-level programming language. Programming in Python is fun and intuitive.
    Python has a simple syntax that makes it easy to learn. Many developers love Python because
    it is versatile and powerful. The Python community is welcoming and helpful. Python can be
    used for web development, data science, automation, and more. Learning Python opens many doors.
    Python code is readable and elegant. The Zen of Python emphasizes simplicity and clarity.
    Python is widely used in industry and academia. Python continues to grow in popularity.
    """
    
    print("=" * 60)
    print("MARKOV CHAIN TEXT GENERATOR")
    print("=" * 60)
    
    # Try different state lengths to see the quality difference
    for state_len in [1, 2, 3]:
        print(f"\n{'─' * 60}")
        print(f"STATE LENGTH: {state_len} (using {state_len}-grams)")
        print('─' * 60)
        
        markov = MarkovChain(state_length=state_len)
        markov.train(sample_text)
        
        stats = markov.get_stats()
        print(f"Stats: {stats['unique_states']} unique states, "
              f"{stats['total_transitions']} transitions")
        
        # Generate a few examples
        for i in range(3):
            generated = markov.generate(max_length=20)
            print(f"\nGeneration {i+1}:")
            print(f"  {generated}")


if __name__ == "__main__":
    demo()