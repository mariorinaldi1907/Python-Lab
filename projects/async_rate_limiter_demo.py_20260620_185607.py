"""
Date: 2026-06-20
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns and see how burst traffic gets smoothed out over time.
"""

#!/usr/bin/env python3
"""
Async rate limiter demo using the token bucket algorithm.

I wanted to understand how rate limiting actually works under the hood,
so I built this token bucket implementation. It's useful for API clients
or any situation where you need to throttle requests while still allowing
short bursts.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Tokens refill at a constant rate. Each operation consumes one token.
    If no tokens are available, the caller waits until refill happens.
    This allows bursts up to max_tokens while maintaining average rate.
    """
    rate: float  # tokens per second
    max_tokens: int  # bucket capacity
    tokens: float  # current token count
    last_refill: float  # timestamp of last refill
    
    def __init__(self, rate: float, max_tokens: Optional[int] = None):
        """
        Initialize the token bucket.
        
        Args:
            rate: How many tokens per second to add
            max_tokens: Maximum bucket capacity (defaults to rate if not specified)
        """
        self.rate = rate
        self.max_tokens = max_tokens or int(rate)
        self.tokens = float(self.max_tokens)  # start with full bucket
        self.last_refill = time.monotonic()
    
    def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called before each consume attempt to ensure the bucket
        reflects the current state. Tokens never exceed max_tokens.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate how many tokens to add based on elapsed time
        new_tokens = elapsed * self.rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
    
    async def consume(self, tokens: int = 1) -> float:
        """
        Consume tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            Time spent waiting in seconds
        """
        wait_time = 0.0
        
        while True:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return wait_time
            
            # Not enough tokens, calculate how long to wait
            tokens_needed = tokens - self.tokens
            sleep_duration = tokens_needed / self.rate
            
            await asyncio.sleep(sleep_duration)
            wait_time += sleep_duration


async def api_worker(worker_id: int, rate_limiter: TokenBucket, num_requests: int):
    """
    Simulates a worker making API requests through a rate limiter.
    
    Args:
        worker_id: Identifier for this worker (for logging)
        rate_limiter: Shared rate limiter instance
        num_requests: How many requests this worker should make
    """
    for i in range(num_requests):
        start = time.monotonic()
        wait_time = await rate_limiter.consume()
        
        # Simulate the actual API call taking some time
        await asyncio.sleep(0.05)
        
        elapsed = time.monotonic() - start
        
        print(
            f"Worker {worker_id} | Request {i+1}/{num_requests} | "
            f"Waited: {wait_time:.3f}s | Total: {elapsed:.3f}s"
        )


async def demonstrate_rate_limiting():
    """
    Run a demo showing how the token bucket smooths out burst traffic.
    
    We'll spin up multiple workers that all try to make requests at once.
    The rate limiter will queue them up and release them at the configured rate.
    """
    print("=" * 70)
    print("Token Bucket Rate Limiter Demo")
    print("=" * 70)
    print("\nConfiguration:")
    print("  - Rate: 5 requests/second")
    print("  - Bucket size: 10 tokens (allows initial burst)")
    print("  - Workers: 3")
    print("  - Requests per worker: 8")
    print("\nStarting workers (they'll all try to send requests immediately)...\n")
    
    # Create a rate limiter: 5 requests per second, burst up to 10
    limiter = TokenBucket(rate=5.0, max_tokens=10)
    
    # Spawn multiple workers that all try to send requests at once
    workers = [
        api_worker(worker_id=1, rate_limiter=limiter, num_requests=8),
        api_worker(worker_id=2, rate_limiter=limiter, num_requests=8),
        api_worker(worker_id=3, rate_limiter=limiter, num_requests=8),
    ]
    
    start_time = time.monotonic()
    await asyncio.gather(*workers)
    total_time = time.monotonic() - start_time
    
    print(f"\n{'=' * 70}")
    print(f"All workers completed in {total_time:.2f} seconds")
    print(f"Total requests: 24")
    print(f"Effective rate: {24 / total_time:.2f} requests/second")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(demonstrate_rate_limiting())