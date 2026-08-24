"""
Date: 2026-08-24
Created a Markov chain text generator that feels more natural by tracking sentence boundaries and preserving original word casing instead of just lowercasing everything.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Generates semi-coherent text based on input samples by building transition
probabilities between word sequences. I wanted this to preserve punctuation
and capitalization better than most simple implementations I've seen online.
"""

import random
import re
from collections import defaultdict
from typing import List, Tuple


class MarkovChain:
    """
    A Markov chain text generator that builds n-gram transition tables.
    
    I'm using tuples of words as keys to track context, which gives more
    coherent output than single-word chains. The tricky part was handling
    sentence boundaries properly so generated text doesn't just trail off.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous words to consider (chain order).
                   Higher = more coherent but less creative.
        """
        self.order = order
        self.chain = defaultdict(list)
        self.sentence_starters = []
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens while preserving punctuation.
        
        I'm keeping punctuation attached to words because "hello," and "hello"
        should be different tokens for natural-looking output.
        """
        # Split on whitespace but keep everything else intact
        tokens = text.split()
        return [token for token in tokens if token]
    
    def _is_sentence_end(self, token: str) -> bool:
        """Check if a token ends a sentence (ends with .!?)"""
        return bool(re.search(r'[.!?]$', token))
    
    def _is_sentence_start(self, token: str) -> bool:
        """
        Check if a token should start a sentence.
        
        Looking for capitalized words that aren't acronyms or weird edge cases.
        Not perfect but good enough for most text.
        """
        return token and token[0].isupper() and len(token) > 1
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        This walks through the text building a mapping from each n-gram
        to all possible following words. I also track valid sentence starters
        so generation doesn't begin mid-thought.
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Training text too short for order {self.order}")
        
        # Build the chain
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of `order` words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            self.chain[state].append(next_word)
            
            # Track sentence starters (sequences that begin sentences)
            if i == 0 or self._is_sentence_end(tokens[i - 1]):
                if state not in self.sentence_starters:
                    self.sentence_starters.append(state)
    
    def generate(self, length: int = 50, seed: Tuple[str, ...] = None) -> str:
        """
        Generate text using the trained Markov chain.
        
        Args:
            length: Maximum number of words to generate
            seed: Optional starting n-gram (must be tuple of size=order)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise ValueError("Chain not trained yet - call train() first")
        
        # Pick starting state
        if seed:
            if len(seed) != self.order:
                raise ValueError(f"Seed must be tuple of length {self.order}")
            if seed not in self.chain:
                raise ValueError(f"Seed {seed} not found in trained chain")
            state = seed
        else:
            # Start with a sentence beginning if possible
            state = random.choice(self.sentence_starters if self.sentence_starters 
                                 else list(self.chain.keys()))
        
        result = list(state)
        
        # Generate words by following the chain
        for _ in range(length - self.order):
            if state not in self.chain:
                # Dead end - try to finish gracefully
                break
            
            next_word = random.choice(self.chain[state])
            result.append(next_word)
            
            # If we hit a sentence end and we're past minimum length,
            # maybe stop here for a natural ending
            if self._is_sentence_end(next_word) and len(result) > 20:
                if random.random() < 0.3:  # 30% chance to end at sentence boundary
                    break
            
            # Slide the window forward
            state = tuple(result[-self.order:])
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some sample text (using public domain content)
    sample_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused by this display.
    Meanwhile, the fox continued jumping over various obstacles. Jumping is what foxes do best.
    Some say the lazy dog eventually learned to jump too. However, this remains unconfirmed.
    The brown fox preferred jumping at dawn. Dawn is the best time for athletic foxes.
    Other foxes disagreed with this assessment. They preferred jumping at dusk instead.
    The lazy dog just wanted to sleep. Sleep is what lazy dogs do best, after all.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on sample text about foxes and dogs...\n")
    
    # Create and train the chain
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    
    # Generate a few samples
    print("Generated samples:\n")
    for i in range(3):
        print(f"Sample {i + 1}:")
        generated = markov.generate(length=30)
        print(f"  {generated}\n")
    
    # Show the internal chain structure for educational purposes
    print("Chain structure (first 5 entries):")
    for i, (state, followers) in enumerate(list(markov.chain.items())[:5]):
        print(f"  {state} -> {followers}")
        if i >= 4:
            break