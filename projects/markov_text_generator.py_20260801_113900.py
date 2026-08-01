"""
Date: 2026-08-01
Created a Markov chain text generator with configurable n-gram order because I wanted to experiment with probabilistic text generation using just the standard library.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds n-gram models from input text and generates new text that mimics the style.
I wanted something simple but flexible enough to experiment with different chain orders.
"""

import random
from collections import defaultdict
from typing import List, Tuple, Optional


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The chain stores transitions between n-grams (sequences of n words) and their
    possible next words. Higher orders capture more context but need more training data.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The number of previous words to consider (n-gram size - 1).
                   order=1 means bigrams, order=2 means trigrams, etc.
        """
        if order < 1:
            raise ValueError("Order must be at least 1")
        
        self.order = order
        # Maps n-grams (tuples of words) to lists of possible next words
        self.chain = defaultdict(list)
        # Store starting n-grams for generating text from scratch
        self.starts = []
    
    def train(self, text: str) -> None:
        """
        Train the Markov chain on input text.
        
        Args:
            text: The training text. Will be tokenized by whitespace.
        """
        words = text.split()
        
        if len(words) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build the chain by sliding a window through the text
        for i in range(len(words) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            
            # Record this transition
            self.chain[state].append(next_word)
            
            # If this is at the start, remember it as a valid starting state
            if i == 0:
                self.starts.append(state)
        
        # Also capture states that start sentences (after periods, etc.)
        # This makes generated text more coherent
        for i in range(1, len(words) - self.order):
            if words[i - 1].endswith('.') or words[i - 1].endswith('!') or words[i - 1].endswith('?'):
                state = tuple(words[i:i + self.order])
                if state not in self.starts:
                    self.starts.append(state)
    
    def generate(self, max_words: int = 50, seed_state: Optional[Tuple[str, ...]] = None) -> str:
        """
        Generate text using the trained Markov chain.
        
        Args:
            max_words: Maximum number of words to generate.
            seed_state: Optional starting state. If None, picks randomly from starts.
        
        Returns:
            Generated text as a string.
        """
        if not self.chain:
            raise RuntimeError("Chain not trained yet. Call train() first.")
        
        # Pick starting state
        if seed_state is not None:
            if seed_state not in self.chain:
                raise ValueError(f"Seed state {seed_state} not found in chain")
            current_state = seed_state
        else:
            if not self.starts:
                # Fallback: pick any state
                current_state = random.choice(list(self.chain.keys()))
            else:
                current_state = random.choice(self.starts)
        
        # Start with the seed state words
        result = list(current_state)
        
        # Generate words one at a time
        for _ in range(max_words - self.order):
            if current_state not in self.chain:
                # Dead end — no more transitions available
                break
            
            # Pick a random next word based on the current state
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Shift the state window: drop first word, add new word
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        return ' '.join(result)


def demo():
    """
    Demonstrate the Markov chain generator with sample text.
    """
    # Sample training text — using something with a bit of variety
    training_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused by the fox.
    The fox, however, was quite pleased with itself. It had successfully jumped over the dog.
    Meanwhile, the cat watched from a distance. The cat thought the whole situation was ridiculous.
    Why would a fox jump over a dog? The cat would never do such a thing.
    Cats are far too dignified for such antics. The dog eventually gave up and went to sleep.
    The fox continued its mischievous adventures in the forest. The forest was full of interesting creatures.
    Some creatures were friendly, while others were not so welcoming. The fox learned to be careful.
    """
    
    print("=" * 70)
    print("Markov Chain Text Generator Demo")
    print("=" * 70)
    print()
    
    # Test with different orders
    for order in [1, 2, 3]:
        print(f"Order {order} (using {order+1}-grams):")
        print("-" * 70)
        
        chain = MarkovChain(order=order)
        chain.train(training_text)
        
        # Generate a few samples
        for i in range(3):
            generated = chain.generate(max_words=30)
            print(f"  Sample {i+1}: {generated}")
        
        print()
    
    # Show what happens with a seed state
    print("Using seed state ('The', 'fox') with order 2:")
    print("-" * 70)
    chain = MarkovChain(order=2)
    chain.train(training_text)
    seeded = chain.generate(max_words=25, seed_state=('The', 'fox'))
    print(f"  {seeded}")
    print()


if __name__ == "__main__":
    demo()