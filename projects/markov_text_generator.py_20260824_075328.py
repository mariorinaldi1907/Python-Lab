"""
Date: 2026-08-24
Implemented a configurable Markov chain generator to procedurally create text from source material — wanted something that could mimic writing styles for fun.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Reads input text and generates new text by modeling n-gram transitions.
I wanted something that could learn patterns from any text and spit out
semi-coherent output. Great for generating nonsense that sounds real.
"""

import random
import re
from collections import defaultdict, deque


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The 'order' determines how many previous tokens influence the next token.
    Higher order = more coherent but less creative output.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous tokens to consider (default 2 for trigrams)
        """
        self.order = order
        # Using defaultdict to store possible next tokens for each state
        self.chain = defaultdict(list)
        self.start_states = []  # Track valid starting states
        
    def tokenize(self, text):
        """
        Split text into tokens (words and punctuation).
        
        I'm keeping punctuation as separate tokens because it affects
        the flow of generated text significantly.
        """
        # Split on whitespace but keep punctuation as separate tokens
        tokens = re.findall(r'\w+|[.,!?;:]', text)
        return tokens
    
    def train(self, text):
        """
        Build the Markov chain from input text.
        
        Creates a mapping of n-gram states to possible next tokens.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build the chain by sliding a window across tokens
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' tokens
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            self.chain[state].append(next_token)
            
            # Track sentence start states (after period, or at beginning)
            if i == 0 or tokens[i - 1] in '.!?':
                self.start_states.append(state)
        
        # Fallback if no sentence boundaries found
        if not self.start_states and self.chain:
            self.start_states = [list(self.chain.keys())[0]]
    
    def generate(self, length=50, seed_state=None):
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Approximate number of tokens to generate
            seed_state: Optional starting state (tuple of tokens)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return ""
        
        # Pick a random starting state, preferring sentence starts
        if seed_state and seed_state in self.chain:
            current_state = seed_state
        elif self.start_states:
            current_state = random.choice(self.start_states)
        else:
            current_state = random.choice(list(self.chain.keys()))
        
        result = list(current_state)
        
        # Generate tokens one by one
        for _ in range(length - self.order):
            if current_state not in self.chain:
                # Dead end — try to restart from a valid state
                if self.start_states:
                    current_state = random.choice(self.start_states)
                else:
                    break
            
            # Pick a random next token based on current state
            next_token = random.choice(self.chain[current_state])
            result.append(next_token)
            
            # Slide the window forward
            current_state = tuple(result[-self.order:])
        
        # Reconstruct text with proper spacing
        return self._detokenize(result)
    
    def _detokenize(self, tokens):
        """
        Convert tokens back to readable text.
        
        Handles spacing around punctuation so output looks natural.
        """
        text = ""
        for i, token in enumerate(tokens):
            if i == 0:
                text = token
            elif token in '.,!?;:':
                # No space before punctuation
                text += token
            else:
                text += " " + token
        
        return text


def main():
    """
    Demo the Markov chain generator with sample text.
    """
    # Sample training text — using a mix of styles to see what happens
    sample_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused.
    Meanwhile, the fox was quite pleased with itself. The moon shone brightly
    over the quiet forest. A gentle breeze rustled through the trees.
    The fox thought about jumping again. The dog decided to take a nap.
    Life in the forest was peaceful. The stars twinkled in the night sky.
    Tomorrow would bring new adventures. The fox smiled at the thought.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    
    # Try different chain orders to show the difference
    for order in [1, 2, 3]:
        print(f"--- Order {order} (using {order}-grams) ---")
        
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        # Generate a couple of samples
        for i in range(2):
            generated = markov.generate(length=25)
            print(f"Sample {i+1}: {generated}")
        
        print()
    
    # Show statistics
    print(f"Training corpus size: {len(sample_text.split())} words")
    print(f"Unique states learned (order=2): {len(MarkovChain(order=2).chain)} after training")


if __name__ == "__main__":
    main()