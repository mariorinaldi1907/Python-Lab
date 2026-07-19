"""
Date: 2026-07-19
Built a Markov chain text generator that learns from input text and produces semi-coherent output — useful for experimenting with simple generative models.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

I wanted to play around with Markov chains for text generation without
pulling in any heavy dependencies. This implementation supports variable
n-gram sizes and tries to respect sentence boundaries so the output
doesn't feel completely random.
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A simple Markov chain text generator.
    
    Uses n-grams to build a probabilistic model of text transitions.
    The chain_length parameter controls how much context we use when
    generating new text (higher = more coherent but less creative).
    """
    
    def __init__(self, chain_length: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            chain_length: Size of the n-gram (number of words to use as state)
        """
        self.chain_length = chain_length
        # Maps a tuple of words to a list of possible next words
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.sentence_starters: List[Tuple[str, ...]] = []
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Break text into words, preserving punctuation as separate tokens.
        
        This helps the model learn about sentence structure rather than
        treating punctuation as part of words.
        """
        # Split on whitespace and punctuation boundaries
        tokens = re.findall(r'\w+|[.,!?;:]', text)
        return tokens
    
    def _is_sentence_start(self, tokens: List[str], index: int) -> bool:
        """
        Check if a token position starts a sentence.
        
        We consider it a sentence start if it's at the beginning or
        follows sentence-ending punctuation.
        """
        if index == 0:
            return True
        if index > 0 and tokens[index - 1] in '.!?':
            return True
        return False
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        Iterates through the text with a sliding window, recording
        what words tend to follow each n-gram.
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.chain_length + 1:
            raise ValueError(f"Text too short for chain_length={self.chain_length}")
        
        # Build the chain with a sliding window
        for i in range(len(tokens) - self.chain_length):
            # Current state is a tuple of chain_length words
            state = tuple(tokens[i:i + self.chain_length])
            next_word = tokens[i + self.chain_length]
            
            self.chain[state].append(next_word)
            
            # Track possible sentence starting states
            if self._is_sentence_start(tokens, i):
                self.sentence_starters.append(state)
    
    def generate(self, length: int = 50, start_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Approximate number of words to generate
            start_state: Optional starting n-gram (if None, picks a sentence starter)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Must train the chain before generating text")
        
        # Pick a starting state
        if start_state is None:
            if self.sentence_starters:
                current_state = random.choice(self.sentence_starters)
            else:
                current_state = random.choice(list(self.chain.keys()))
        else:
            current_state = start_state
        
        result = list(current_state)
        
        # Generate words one at a time
        for _ in range(length - self.chain_length):
            if current_state not in self.chain:
                # Dead end, try to restart from a sentence beginning
                if self.sentence_starters:
                    current_state = random.choice(self.sentence_starters)
                else:
                    break
            
            # Pick a random next word based on the current state
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the window forward
            current_state = tuple(result[-self.chain_length:])
        
        # Reconstruct text with proper spacing around punctuation
        output = []
        for i, token in enumerate(result):
            if token in '.,!?;:':
                # Punctuation goes directly after previous word
                output.append(token)
            else:
                if i > 0 and result[i - 1] not in '.,!?;:':
                    output.append(' ')
                output.append(token)
        
        return ''.join(output)


if __name__ == "__main__":
    # Sample training text - using some classic literature public domain text
    training_text = """
    It was the best of times, it was the worst of times. It was the age of wisdom,
    it was the age of foolishness. It was the epoch of belief, it was the epoch of
    incredulity. It was the season of light, it was the season of darkness. It was
    the spring of hope, it was the winter of despair. We had everything before us,
    we had nothing before us. We were all going direct to heaven, we were all going
    direct the other way. In short, the period was so far like the present period,
    that some of its noisiest authorities insisted on its being received, for good
    or for evil, in the superlative degree of comparison only.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Test with different chain lengths to show the difference
    for chain_length in [1, 2, 3]:
        print(f"--- Chain length = {chain_length} ---")
        markov = MarkovChain(chain_length=chain_length)
        markov.train(training_text)
        
        generated = markov.generate(length=40)
        print(f"{generated}\n")
    
    print("Notice how higher chain lengths produce more coherent (but less creative) text!")
```