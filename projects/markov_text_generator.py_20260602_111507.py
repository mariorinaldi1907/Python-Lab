"""
Date: 2026-06-02
Implemented a Markov chain text generator that can learn from any text corpus and generate new text with adjustable randomness and chain order.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds n-gram models from input text and generates new sequences.
I wanted something that could learn from any text and spit out plausible-sounding gibberish.
"""

import random
import re
from collections import defaultdict, deque
from typing import List, Tuple, Optional


class MarkovChain:
    """
    N-gram based Markov chain for text generation.
    
    The chain learns transition probabilities from input text and can generate
    new sequences that statistically resemble the training data.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The n-gram order (how many previous tokens determine the next one).
                   order=1 is a bigram model, order=2 is trigram, etc.
        """
        self.order = order
        # Using defaultdict to avoid key checks - cleaner and faster
        self.chain = defaultdict(list)
        self.start_states = []
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Break text into tokens (words and punctuation).
        
        I'm keeping punctuation as separate tokens so generated text
        has somewhat reasonable structure.
        """
        # Split on whitespace but keep punctuation separate
        tokens = re.findall(r'\w+|[.,!?;:\-—]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Learn transition probabilities from the input text.
        
        Args:
            text: Training corpus as a single string
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order-{self.order} chain")
        
        # Build the chain by sliding a window across tokens
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' tokens
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            self.chain[state].append(next_token)
            
            # Track potential starting states (beginning of sentences)
            if i == 0 or tokens[i - 1] in '.!?':
                self.start_states.append(state)
        
        # Fallback if we didn't find sentence boundaries
        if not self.start_states and self.chain:
            self.start_states = [list(self.chain.keys())[0]]
    
    def generate(self, length: int = 50, seed: Optional[str] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Approximate number of tokens to generate
            seed: Optional starting text to seed generation
            
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Chain not trained yet - call train() first")
        
        # Pick a starting state
        if seed:
            seed_tokens = self._tokenize(seed)
            if len(seed_tokens) >= self.order:
                current_state = tuple(seed_tokens[-self.order:])
            else:
                current_state = random.choice(self.start_states)
        else:
            current_state = random.choice(self.start_states)
        
        result = list(current_state)
        
        # Generate tokens one at a time
        for _ in range(length - self.order):
            if current_state not in self.chain:
                # Dead end - restart from a random state
                current_state = random.choice(list(self.chain.keys()))
                continue
            
            # Pick next token based on transition probabilities
            # (just sampling uniformly from observed transitions)
            next_token = random.choice(self.chain[current_state])
            result.append(next_token)
            
            # Slide the window forward
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        # Reconstruct text with proper spacing
        return self._detokenize(result)
    
    def _detokenize(self, tokens: List[str]) -> str:
        """
        Convert tokens back to readable text with proper spacing.
        """
        text = ""
        for i, token in enumerate(tokens):
            if i == 0:
                text = token
            elif token in '.,!?;:':
                # No space before punctuation
                text += token
            elif tokens[i - 1] in '—-':
                # No space after dashes
                text += token
            else:
                text += " " + token
        return text


if __name__ == "__main__":
    # Demo with some sample text - using public domain poetry
    sample_text = """
    The woods are lovely, dark and deep, but I have promises to keep,
    and miles to go before I sleep, and miles to go before I sleep.
    Two roads diverged in a yellow wood, and sorry I could not travel both
    and be one traveler, long I stood and looked down one as far as I could.
    I shall be telling this with a sigh somewhere ages and ages hence:
    Two roads diverged in a wood, and I took the one less traveled by,
    and that has made all the difference. Nature's first green is gold,
    her hardest hue to hold. Her early leaf's a flower but only so an hour.
    Then leaf subsides to leaf, so Eden sank to grief, so dawn goes down to day.
    Nothing gold can stay.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    print("Training on sample text (Robert Frost poems)...\n")
    
    # Try different orders to show the effect
    for order in [1, 2, 3]:
        print(f"--- Order {order} (using {order + 1}-grams) ---")
        chain = MarkovChain(order=order)
        chain.train(sample_text)
        
        generated = chain.generate(length=30)
        print(f"{generated}\n")
    
    # Demo with seeding
    print("--- Seeded generation (order 2, seed='the woods') ---")
    chain = MarkovChain(order=2)
    chain.train(sample_text)
    seeded = chain.generate(length=25, seed="the woods")
    print(f"{seeded}\n")
```