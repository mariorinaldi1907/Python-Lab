"""
Date: 2026-08-05
Implemented a configurable Markov chain generator that learns from input text and generates new text with adjustable context windows — preserves sentence structure better than basic word-level chains.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Generates pseudo-random text based on statistical patterns learned from input text.
Uses n-grams to maintain some coherence while introducing randomness.
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A Markov chain text generator that learns from input text.
    
    Uses n-grams (sequences of n words) as states, and tracks which words
    commonly follow each state. This approach preserves local context better
    than single-word chains.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The number of words to use as context (default 2).
                   Higher order = more coherent but less creative output.
        """
        self.order = order
        # Maps n-gram tuples to lists of possible next words
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_states: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words, preserving sentence-ending punctuation.
        
        I'm keeping periods, question marks, and exclamation points as separate
        tokens so the generator knows where sentences naturally end.
        """
        # Split on whitespace but keep sentence-ending punctuation separate
        tokens = re.findall(r'\b\w+\b|[.!?]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Learn patterns from input text.
        
        Builds the transition table by sliding a window across the text
        and recording what words follow each n-gram sequence.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order} chain")
        
        # Slide a window across the tokens
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            self.chain[state].append(next_word)
            
            # Track states that start sentences (after punctuation or at the beginning)
            if i == 0 or tokens[i - 1] in '.!?':
                if state not in self.start_states:
                    self.start_states.append(state)
    
    def generate(self, max_words: int = 50, seed: str = None) -> str:
        """
        Generate new text based on learned patterns.
        
        Args:
            max_words: Maximum number of words to generate
            seed: Optional starting phrase (must match the chain's order)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise ValueError("Chain not trained yet - call train() first")
        
        # Pick a starting state
        if seed:
            seed_tokens = self.tokenize(seed)
            if len(seed_tokens) < self.order:
                raise ValueError(f"Seed must have at least {self.order} words")
            current_state = tuple(seed_tokens[-self.order:])
            output = list(current_state)
        else:
            current_state = random.choice(self.start_states) if self.start_states else random.choice(list(self.chain.keys()))
            output = list(current_state)
        
        # Generate words until we hit max_words or naturally end a sentence
        words_generated = len(output)
        
        while words_generated < max_words:
            if current_state not in self.chain:
                # Dead end - pick a new random state
                current_state = random.choice(list(self.chain.keys()))
                output.extend(current_state)
                words_generated += self.order
                continue
            
            # Pick a random next word from the possibilities
            next_word = random.choice(self.chain[current_state])
            output.append(next_word)
            words_generated += 1
            
            # Slide the window forward
            current_state = tuple(output[-self.order:])
            
            # Stop if we've generated a reasonable amount and hit sentence-ending punctuation
            if words_generated > 10 and next_word in '.!?':
                break
        
        # Reconstruct the text, handling punctuation spacing
        result = []
        for word in output:
            if word in '.!?,;:':
                # Punctuation attaches to previous word
                if result:
                    result[-1] += word
            else:
                result.append(word)
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some sample text - using a mix of classic literature snippets
    sample_text = """
    It was the best of times, it was the worst of times, it was the age of wisdom,
    it was the age of foolishness. In the beginning God created the heaven and the earth.
    And the earth was without form, and void. Call me Ishmael. Some years ago, never mind
    how long precisely, having little or no money in my purse, I thought I would sail about
    a little and see the watery part of the world. It is a truth universally acknowledged,
    that a single man in possession of a good fortune, must be in want of a wife. All happy
    families are alike, each unhappy family is unhappy in its own way. It was a bright cold
    day in April, and the clocks were striking thirteen. The sun did not shine, it was too
    wet to play, so we sat in the house all that cold, cold, wet day.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Create and train a second-order chain
    print("Training on sample text (order=2)...")
    chain = MarkovChain(order=2)
    chain.train(sample_text)
    print(f"Learned {len(chain.chain)} unique states\n")
    
    # Generate a few samples
    print("Generated text samples:\n")
    for i in range(3):
        generated = chain.generate(max_words=30)
        print(f"{i+1}. {generated}\n")
    
    # Show the difference with a higher-order chain
    print("\n--- Trying order=3 (more coherent, less creative) ---\n")
    chain3 = MarkovChain(order=3)
    chain3.train(sample_text)
    print(f"Learned {len(chain3.chain)} unique states\n")
    
    for i in range(2):
        generated = chain3.generate(max_words=25)
        print(f"{i+1}. {generated}\n")
```