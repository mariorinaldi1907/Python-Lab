"""
Date: 2026-08-18
Built a text processor using the strategy pattern to swap between different text transformation algorithms at runtime — makes it easy to add new processing methods without changing existing code.
"""

"""
Text Processing with Strategy Pattern

I wanted a clean way to apply different text transformations without
a bunch of if/else statements. Strategy pattern felt perfect for this.
Each processing algorithm is its own class, and the context just delegates.
"""

from abc import ABC, abstractmethod
from typing import List
import re


class TextProcessingStrategy(ABC):
    """
    Abstract base for all text processing strategies.
    Any new processing algorithm just needs to implement process().
    """
    
    @abstractmethod
    def process(self, text: str) -> str:
        """Transform the input text according to the strategy's rules."""
        pass


class UpperCaseStrategy(TextProcessingStrategy):
    """Simple strategy that converts everything to uppercase."""
    
    def process(self, text: str) -> str:
        return text.upper()


class SlugifyStrategy(TextProcessingStrategy):
    """
    Converts text to URL-friendly slug format.
    Useful for generating clean URLs from article titles.
    """
    
    def process(self, text: str) -> str:
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and underscores with hyphens
        text = re.sub(r'[\s_]+', '-', text)
        # Remove all non-alphanumeric characters except hyphens
        text = re.sub(r'[^a-z0-9\-]', '', text)
        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)
        # Strip hyphens from start and end
        return text.strip('-')


class SentenceCaseStrategy(TextProcessingStrategy):
    """
    Capitalizes the first letter of each sentence.
    I'm defining sentences as ending with . ! or ?
    """
    
    def process(self, text: str) -> str:
        # Split by sentence terminators but keep them
        sentences = re.split(r'([.!?]\s*)', text)
        result = []
        
        for i, part in enumerate(sentences):
            if part and not re.match(r'[.!?]\s*', part):
                # Capitalize first letter of actual sentence content
                part = part.strip()
                if part:
                    part = part[0].upper() + part[1:].lower()
                result.append(part)
            else:
                result.append(part)
        
        return ''.join(result)


class WordCountStrategy(TextProcessingStrategy):
    """
    Returns word count statistics instead of transformed text.
    Bit of a stretch for "text processing" but shows flexibility.
    """
    
    def process(self, text: str) -> str:
        words = text.split()
        unique_words = set(word.lower().strip('.,!?;:') for word in words)
        
        return (f"Total words: {len(words)}, "
                f"Unique words: {len(unique_words)}, "
                f"Avg word length: {sum(len(w) for w in words) / len(words):.1f}")


class TextProcessor:
    """
    Context class that uses a strategy to process text.
    This is where the magic happens — you can swap strategies on the fly.
    """
    
    def __init__(self, strategy: TextProcessingStrategy = None):
        """
        Initialize with an optional default strategy.
        If none provided, you'll need to set one before processing.
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy: TextProcessingStrategy) -> None:
        """
        Change the processing strategy at runtime.
        This is the whole point of the pattern — no code changes needed.
        """
        self._strategy = strategy
    
    def process(self, text: str) -> str:
        """
        Delegate the actual processing to the current strategy.
        Raises ValueError if no strategy is set.
        """
        if self._strategy is None:
            raise ValueError("No processing strategy set!")
        return self._strategy.process(text)
    
    def batch_process(self, texts: List[str]) -> List[str]:
        """
        Process multiple texts with the current strategy.
        Added this because I often need to process batches.
        """
        return [self.process(text) for text in texts]


if __name__ == "__main__":
    # Demo time! Let's process some text in different ways
    sample_text = "Hello World! this is a TEST of the Strategy Pattern. does it work?"
    article_title = "My Journey Learning Python: Tips & Tricks!"
    
    print("=" * 60)
    print("TEXT PROCESSING STRATEGY PATTERN DEMO")
    print("=" * 60)
    
    # Create processor without initial strategy
    processor = TextProcessor()
    
    # Try different strategies on the same text
    print(f"\nOriginal text: {sample_text}\n")
    
    print("1. UPPERCASE STRATEGY:")
    processor.set_strategy(UpperCaseStrategy())
    print(f"   {processor.process(sample_text)}\n")
    
    print("2. SENTENCE CASE STRATEGY:")
    processor.set_strategy(SentenceCaseStrategy())
    print(f"   {processor.process(sample_text)}\n")
    
    print("3. WORD COUNT STRATEGY:")
    processor.set_strategy(WordCountStrategy())
    print(f"   {processor.process(sample_text)}\n")
    
    print("4. SLUGIFY STRATEGY (for URLs):")
    processor.set_strategy(SlugifyStrategy())
    print(f"   Original: {article_title}")
    print(f"   Slugified: {processor.process(article_title)}\n")
    
    # Batch processing demo
    print("5. BATCH PROCESSING:")
    batch = [
        "Python is Awesome",
        "Design Patterns are USEFUL",
        "Clean Code Matters"
    ]
    processor.set_strategy(SlugifyStrategy())
    results = processor.batch_process(batch)
    print("   Converting titles to URL slugs:")
    for original, slug in zip(batch, results):
        print(f"   {original:30} -> {slug}")
    
    print("\n" + "=" * 60)
    print("The beauty of this pattern: add new strategies without")
    print("touching existing code. Just implement the interface!")
    print("=" * 60)