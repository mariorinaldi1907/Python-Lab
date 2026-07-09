"""
Date: 2026-07-09
Created a Markov chain text generator that learns from input text and generates semi-coherent sentences by analyzing word transition probabilities.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Generates pseudo-random text based on statistical patterns from input text.
I wanted to build something that could actually produce readable-ish output,
so I added logic to track sentence boundaries and capitalize properly.
"""

import random
import re
from collections import defaultdict, Counter


class MarkovChain:
    """
    A Markov chain text generator that learns transition probabilities
    between words and generates new text based on those patterns.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous words to consider for the next word.
                   Higher order = more coherent but less creative.
        """
        self.order = order
        # Using defaultdict of Counters makes probability calculation cleaner
        self.chain = defaultdict(Counter)
        self.start_words = []  # Track words that begin sentences
        
    def train(self, text):
        """
        Build the Markov chain from input text.
        
        Args:
            text: String of training text
        """
        # Split into sentences to preserve natural boundaries
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) < self.order + 1:
                continue
                
            # Track sentence-starting words for better generation
            if words:
                self.start_words.append(tuple(words[:self.order]))
            
            # Build transition probabilities
            for i in range(len(words) - self.order):
                # The "state" is the current sequence of words
                state = tuple(words[i:i + self.order])
                # The "next word" is what follows this state
                next_word = words[i + self.order]
                self.chain[state][next_word] += 1
    
    def _choose_next_word(self, state):
        """
        Select the next word based on weighted probabilities.
        
        Args:
            state: Tuple of the current word sequence
            
        Returns:
            Next word string, or None if state not found
        """
        if state not in self.chain:
            return None
        
        # Counter makes this easy - we can sample based on frequencies
        possible_words = self.chain[state]
        words = list(possible_words.keys())
        weights = list(possible_words.values())
        
        return random.choices(words, weights=weights)[0]
    
    def generate(self, max_words=50, start_with=None):
        """
        Generate new text using the trained Markov chain.
        
        Args:
            max_words: Maximum number of words to generate
            start_with: Optional starting phrase (string). If None, picks randomly.
            
        Returns:
            Generated text string
        """
        if not self.chain:
            return ""
        
        # Initialize with starting state
        if start_with:
            current = tuple(start_with.split()[:self.order])
        elif self.start_words:
            current = random.choice(self.start_words)
        else:
            current = random.choice(list(self.chain.keys()))
        
        result = list(current)
        
        # Generate words until we hit max_words or get stuck
        for _ in range(max_words - self.order):
            next_word = self._choose_next_word(current)
            
            if next_word is None:
                # Dead end - try to find a valid continuation
                if self.start_words:
                    current = random.choice(self.start_words)
                    result.append(".")  # Add sentence break
                    result.extend(current)
                else:
                    break
            else:
                result.append(next_word)
                # Slide the window forward
                current = tuple(result[-self.order:])
        
        # Capitalize first letter and add period if missing
        text = " ".join(result)
        if text:
            text = text[0].upper() + text[1:]
            if not text.endswith(('.', '!', '?')):
                text += '.'
        
        return text


if __name__ == "__main__":
    # Demo with some classic text - I'm using a public domain excerpt
    sample_text = """
    To be or not to be that is the question. Whether tis nobler in the mind to suffer
    the slings and arrows of outrageous fortune. Or to take arms against a sea of troubles
    and by opposing end them. To die to sleep no more. And by a sleep to say we end
    the heartache and the thousand natural shocks that flesh is heir to. Tis a consummation
    devoutly to be wished. To die to sleep. To sleep perchance to dream. Ay there's the rub.
    For in that sleep of death what dreams may come when we have shuffled off this mortal coil
    must give us pause. There's the respect that makes calamity of so long life.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on Shakespeare's 'To be or not to be' soliloquy...\n")
    
    # Try different order values to show the effect
    for order in [1, 2, 3]:
        print(f"--- Order {order} (considers {order} previous word(s)) ---")
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        # Generate a few examples
        for i in range(3):
            generated = markov.generate(max_words=30)
            print(f"{i+1}. {generated}")
        print()
    
    # Show custom starting phrase
    print("--- Starting with 'to be' ---")
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    generated = markov.generate(max_words=25, start_with="to be")
    print(generated)