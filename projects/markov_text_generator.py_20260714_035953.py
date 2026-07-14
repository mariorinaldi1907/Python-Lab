"""
Date: 2026-07-14
Implemented a Markov chain text generator that builds n-gram probability models from input text and generates new semi-coherent output.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds a statistical model from input text and generates new text that
follows similar patterns. Uses n-grams (default trigrams) to capture
local context and create somewhat coherent output.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Optional


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The model stores transitions from n-1 words to the next word,
    building a probability distribution for each context.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous words to consider (2 = trigrams)
        """
        self.order = order
        # Maps (word1, word2, ...) -> Counter of possible next words
        self.transitions = defaultdict(Counter)
        self.start_states = []  # Possible sentence starts
        
    def train(self, text: str) -> None:
        """
        Build the Markov model from input text.
        
        Splits text into words and records transition frequencies.
        Treats newlines as sentence boundaries to get better starts.
        
        Args:
            text: Training text (multi-line strings work great)
        """
        # Split into sentences on newlines and periods
        sentences = re.split(r'[.\n]+', text)
        
        for sentence in sentences:
            # Tokenize: split on whitespace and filter empties
            words = [w.strip() for w in sentence.split() if w.strip()]
            
            if len(words) < self.order + 1:
                continue  # Skip sentences that are too short
            
            # Record this as a possible starting n-gram
            start_state = tuple(words[:self.order])
            self.start_states.append(start_state)
            
            # Build transitions for this sentence
            for i in range(len(words) - self.order):
                state = tuple(words[i:i + self.order])
                next_word = words[i + self.order]
                self.transitions[state][next_word] += 1
    
    def _pick_next_word(self, state: Tuple[str, ...]) -> Optional[str]:
        """
        Choose the next word based on current state.
        
        Uses weighted random selection based on observed frequencies.
        Returns None if we've never seen this state before.
        
        Args:
            state: Current n-gram context
            
        Returns:
            Next word, or None if state unknown
        """
        if state not in self.transitions:
            return None
        
        # Get possible next words and their counts
        candidates = self.transitions[state]
        words = list(candidates.keys())
        weights = list(candidates.values())
        
        # Weighted random choice
        return random.choices(words, weights=weights)[0]
    
    def generate(self, max_length: int = 100, seed: Optional[str] = None) -> str:
        """
        Generate new text from the trained model.
        
        Starts with a random (or seeded) n-gram and keeps picking
        next words until we hit max_length or get stuck.
        
        Args:
            max_length: Maximum number of words to generate
            seed: Optional starting phrase (uses first N words)
            
        Returns:
            Generated text string
        """
        if not self.start_states:
            return ""
        
        # Initialize with seed or random start
        if seed:
            seed_words = seed.split()[:self.order]
            if len(seed_words) == self.order:
                current_state = tuple(seed_words)
                result = list(seed_words)
            else:
                # Seed too short, fall back to random
                current_state = random.choice(self.start_states)
                result = list(current_state)
        else:
            current_state = random.choice(self.start_states)
            result = list(current_state)
        
        # Generate words one at a time
        for _ in range(max_length - self.order):
            next_word = self._pick_next_word(current_state)
            
            if next_word is None:
                break  # Dead end - no known transitions
            
            result.append(next_word)
            
            # Slide the window forward
            current_state = tuple(result[-self.order:])
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some sample text about programming
    # (Using triple quotes to preserve structure)
    sample_text = """
    Python is a high-level programming language. Python emphasizes code readability.
    Programming in Python is fun and productive. Python has a large standard library.
    The language supports multiple programming paradigms. Python is widely used in data science.
    Machine learning often uses Python as the primary language. Python developers love the simplicity.
    Code readability is a core principle of Python. The standard library includes many useful modules.
    Programming paradigms supported include object-oriented and functional programming.
    Data science projects benefit from Python libraries. The simplicity of Python attracts new developers.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Create and train a bigram model (order=1)
    print("Training bigram model (order=1)...")
    bigram_model = MarkovChain(order=1)
    bigram_model.train(sample_text)
    
    print("\nGenerated text (bigram, 30 words):")
    print(bigram_model.generate(max_length=30))
    
    # Create and train a trigram model (order=2)
    print("\n" + "="*50)
    print("\nTraining trigram model (order=2)...")
    trigram_model = MarkovChain(order=2)
    trigram_model.train(sample_text)
    
    print("\nGenerated text (trigram, 30 words):")
    print(trigram_model.generate(max_length=30))
    
    print("\nGenerated text with seed 'Python is':")
    print(trigram_model.generate(max_length=25, seed="Python is"))
    
    print("\n" + "="*50)
    print("\nNote: Longer training texts produce more coherent results!")
    print("Try feeding this script a book or article for better output.")