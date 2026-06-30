"""
Date: 2026-06-30
Implemented a Markov chain text generator with variable-length n-grams because I wanted to experiment with probabilistic text generation without touching ML libraries.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds a statistical model from input text and generates new random text.
Uses n-grams (sequences of n tokens) to predict what comes next.
"""

import random
import re
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Deque


class MarkovChain:
    """
    A simple Markov chain text generator.
    
    The chain_length parameter controls how many previous tokens we look at
    when deciding what comes next. Longer chains = more coherent but less creative.
    """
    
    def __init__(self, chain_length: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            chain_length: Number of tokens to use as state (n-gram size)
        """
        self.chain_length = chain_length
        # Maps state (tuple of tokens) -> list of possible next tokens
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_states: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens (words + punctuation).
        
        I'm keeping punctuation as separate tokens so the generated text
        has some structure, not just word salad.
        """
        # Split on whitespace but keep punctuation
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        This creates the state transition table by sliding a window
        across the tokens and recording what follows each state.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.chain_length + 1:
            raise ValueError(f"Text too short for chain length {self.chain_length}")
        
        # Use a deque as a sliding window for efficiency
        state_window: Deque[str] = deque(maxlen=self.chain_length)
        
        # Build up the initial state
        for i in range(self.chain_length):
            state_window.append(tokens[i])
        
        # Record this as a possible starting state
        self.start_states.append(tuple(state_window))
        
        # Slide the window across remaining tokens
        for next_token in tokens[self.chain_length:]:
            state = tuple(state_window)
            self.chain[state].append(next_token)
            
            # Slide window forward
            state_window.append(next_token)
            
            # Track states that start sentences (after periods)
            if next_token in '.!?':
                # Next state might be a good sentence start
                if len(tokens) > tokens.index(next_token) + self.chain_length:
                    future_state = tuple(state_window)
                    self.start_states.append(future_state)
    
    def generate(self, max_tokens: int = 100, seed_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained chain.
        
        Args:
            max_tokens: Maximum number of tokens to generate
            seed_state: Optional starting state; if None, picks randomly
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise ValueError("Chain not trained yet - call train() first")
        
        # Pick a random starting state if not provided
        if seed_state is None:
            current_state = random.choice(self.start_states)
        else:
            current_state = seed_state
        
        # Start with the tokens from our initial state
        result = list(current_state)
        
        # Generate tokens one at a time
        for _ in range(max_tokens - self.chain_length):
            if current_state not in self.chain:
                # Dead end - no recorded transitions from this state
                break
            
            # Pick a random next token based on what we've seen before
            possible_next = self.chain[current_state]
            next_token = random.choice(possible_next)
            result.append(next_token)
            
            # Update state by shifting window
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        # Reconstruct text, handling spacing around punctuation
        output = []
        for i, token in enumerate(result):
            if i == 0:
                output.append(token)
            elif token in ',.!?;:)]}':
                # Punctuation sticks to previous word
                output.append(token)
            elif result[i-1] in '([{':
                # No space after opening brackets
                output.append(token)
            else:
                output.append(' ' + token)
        
        return ''.join(output)


if __name__ == "__main__":
    # Demo with some sample text (a bit of philosophical rambling)
    sample_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused.
    The fox, being quick and brown, decided to jump again. This time the dog
    chased the fox. The chase was exciting. The fox ran quickly through the forest.
    The dog followed, barking loudly. Eventually, the fox escaped into a hole.
    The dog sat outside the hole, waiting patiently. The fox never came out.
    After an hour, the dog gave up and went home. The end of the chase was
    anticlimactic. The fox celebrated inside the hole. Victory tastes sweet when
    you are a quick brown fox. The dog learned a valuable lesson that day.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    
    # Try with different chain lengths to show the difference
    for length in [1, 2, 3]:
        print(f"--- Chain Length: {length} ---")
        markov = MarkovChain(chain_length=length)
        markov.train(sample_text)
        
        # Generate a few samples
        for i in range(2):
            generated = markov.generate(max_tokens=30)
            print(f"Sample {i+1}: {generated}")
        print()
    
    print("Notice how longer chains produce more coherent text but are less creative.")
    print("Chain length 1 = random word soup, Chain length 3 = almost verbatim quotes")
```