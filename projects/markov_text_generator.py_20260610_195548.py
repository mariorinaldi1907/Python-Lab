"""
Date: 2026-06-10
Implemented a Markov chain text generator that learns from input text and generates semi-coherent sentences based on n-gram probabilities.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Generates text based on learned patterns from input text using n-grams.
I wanted to build this after seeing some hilarious bot-generated tweets.
"""

import random
import re
from collections import defaultdict
from typing import List, Tuple


class MarkovGenerator:
    """
    A Markov chain text generator that learns transition probabilities
    from input text and generates new text based on those patterns.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov generator.
        
        Args:
            order: The n-gram size (how many previous words to consider).
                   order=1 means each word depends only on the previous word.
                   order=2 means each word depends on the previous 2 words, etc.
        """
        self.order = order
        # Maps from a tuple of words to a list of possible next words
        self.chain = defaultdict(list)
        # Keep track of all starting sequences (for sentence generation)
        self.starters = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words, keeping punctuation as separate tokens.
        This helps the generated text have more natural punctuation.
        """
        # Split on whitespace and punctuation, but keep punctuation as tokens
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Learn transition probabilities from the input text.
        Builds up the internal chain dictionary with n-gram patterns.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            # Not enough tokens to build meaningful chains
            return
        
        # Record the first n-gram as a potential sentence starter
        starter = tuple(tokens[:self.order])
        self.starters.append(starter)
        
        # Build the chain by sliding a window across the tokens
        for i in range(len(tokens) - self.order):
            # The "state" is the current n-gram
            state = tuple(tokens[i:i + self.order])
            # The next word is what can follow this state
            next_word = tokens[i + self.order]
            
            # Track this transition
            self.chain[state].append(next_word)
            
            # If this looks like a sentence start (previous token was sentence-ending),
            # remember it as a potential starter
            if i > 0 and tokens[i - 1] in '.!?':
                self.starters.append(state)
    
    def generate(self, max_length: int = 50, start_with: Tuple[str, ...] = None) -> str:
        """
        Generate new text based on learned patterns.
        
        Args:
            max_length: Maximum number of words to generate
            start_with: Optional starting n-gram (must match order size)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return "Error: No training data available. Call train() first."
        
        # Pick a starting state
        if start_with and len(start_with) == self.order:
            current = start_with
        elif self.starters:
            current = random.choice(self.starters)
        else:
            current = random.choice(list(self.chain.keys()))
        
        # Build the output starting with our initial state
        result = list(current)
        
        # Generate words until we hit max_length or run out of options
        for _ in range(max_length - self.order):
            if current not in self.chain:
                # Dead end - no transitions recorded from this state
                break
            
            # Pick a random next word from the possible transitions
            next_word = random.choice(self.chain[current])
            result.append(next_word)
            
            # Slide the window: drop the first word, add the new word
            current = tuple(list(current[1:]) + [next_word])
            
            # Optional: stop at sentence boundaries sometimes for more natural breaks
            if next_word in '.!?' and random.random() < 0.3:
                break
        
        # Join tokens, handling punctuation spacing
        return self._format_output(result)
    
    def _format_output(self, tokens: List[str]) -> str:
        """
        Join tokens into a string with proper spacing around punctuation.
        """
        result = []
        for i, token in enumerate(tokens):
            if i == 0:
                result.append(token)
            elif token in '.,;:!?)':
                # No space before these punctuation marks
                result.append(token)
            elif token in '(':
                # Space before opening paren
                result.append(' ' + token)
            else:
                result.append(' ' + token)
        
        return ''.join(result)


if __name__ == "__main__":
    # Demo with some sample text about programming
    # (Yeah, I made this up quickly - would be cooler with real corpus data)
    training_text = """
    Python is a great programming language. I love writing Python code every day.
    The syntax is clean and readable. Programming in Python feels natural.
    When I write code, I always think about readability. Code should be easy to understand.
    Python makes it easy to write clean code. The community is amazing and helpful.
    I enjoy solving problems with Python. Every day brings new challenges.
    Writing good code takes practice. Practice makes perfect, they say.
    The best code is code that others can read. Readability counts, always.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on sample text about programming...\n")
    
    # Try different order values to see the effect
    for order in [1, 2]:
        print(f"--- Order {order} (considering previous {order} word(s)) ---")
        
        generator = MarkovGenerator(order=order)
        generator.train(training_text)
        
        # Generate a few samples
        for i in range(3):
            generated = generator.generate(max_length=20)
            print(f"  Sample {i+1}: {generated}")
        
        print()
    
    print("Notice how order=2 produces more coherent text than order=1!")
    print("Higher order = more context = more realistic (but less creative)")