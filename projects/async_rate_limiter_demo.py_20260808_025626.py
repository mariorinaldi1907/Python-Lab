"""
Date: 2026-08-08
Implemented a token bucket rate limiter using asyncio to experiment with concurrency control — useful pattern for API calls and resource throttling.
"""

"""
Async Rate Limiter Demo using Token Bucket Algorithm

This demonstrates a token bucket rate limiter that I can reuse for API clients.
The bucket refills at a steady rate but allows bursts up to the bucket capacity.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Rate limiter using the token bucket algorithm.
    
    Tokens are added at a fixed rate. Each operation consumes one token.
    If no tokens available, operations wait until tokens refill.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 10 = 10 requests/sec)
            capacity: Maximum tokens in bucket (allows bursts)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Refill tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add based on elapsed time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Not enough tokens - calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Release lock while waiting so other coroutines can check
                # We'll recheck after waiting in case another task consumed tokens
                await asyncio.sleep(wait_time)


async def api_call(limiter: TokenBucketRateLimiter, call_id: int, delay: float = 0.1):
    """
    Simulated API call that respects rate limiting.
    
    Args:
        limiter: The rate limiter instance
        call_id: ID for this call (for logging)
        delay: Simulated processing time
    """
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Call {call_id:2d} - Requesting token...")
    
    await limiter.acquire()
    
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Call {call_id:2d} - ✓ Token acquired, executing...")
    
    # Simulate actual work
    await asyncio.sleep(delay)
    
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Call {call_id:2d} - Complete")


async def burst_then_steady_demo():
    """
    Demo showing burst capability followed by steady-state rate limiting.
    
    Creates a rate limiter that allows 5 req/sec with capacity for 10.
    Sends an initial burst of 15 requests to show how it handles both
    the burst (uses full capacity) and then enforces the rate limit.
    """
    print("=" * 60)
    print("DEMO: Burst then Steady State")
    print("Rate: 5 requests/sec, Capacity: 10 tokens")
    print("Sending 15 rapid requests...")
    print("=" * 60)
    
    # 5 requests per second, but can burst up to 10
    limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    
    # Fire off 15 concurrent requests
    tasks = [api_call(limiter, i, delay=0.05) for i in range(1, 16)]
    
    start = time.monotonic()
    await asyncio.gather(*tasks)
    elapsed = time.monotonic() - start
    
    print("=" * 60)
    print(f"All 15 calls completed in {elapsed:.2f} seconds")
    print("First 10 should be fast (burst), remaining 5 rate-limited")
    print("=" * 60)


async def producer_consumer_with_rate_limit():
    """
    Bonus: Producer-consumer pattern with rate-limited consumers.
    
    Shows how rate limiting integrates with other async patterns.
    Producer generates work items, consumers process them with rate limiting.
    """
    print("\n" + "=" * 60)
    print("BONUS DEMO: Rate-Limited Producer-Consumer")
    print("=" * 60)
    
    queue = asyncio.Queue(maxsize=5)
    limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    
    async def producer():
        """Produce work items."""
        for i in range(8):
            await queue.put(i)
            print(f"📦 Producer: Added item {i} to queue")
            await asyncio.sleep(0.2)  # Simulate work discovery
        await queue.put(None)  # Sentinel to stop consumer
    
    async def consumer():
        """Consume work items with rate limiting."""
        while True:
            item = await queue.get()
            if item is None:
                break
            
            await limiter.acquire()
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 🔧 Consumer: Processing item {item}")
            await asyncio.sleep(0.1)
    
    await asyncio.gather(producer(), consumer())
    print("=" * 60)


if __name__ == "__main__":
    print("\n🚀 Async Rate Limiter Demo - Token Bucket Algorithm\n")
    
    # Run the main demo
    asyncio.run(burst_then_steady_demo())
    
    # Run bonus demo
    asyncio.run(producer_consumer_with_rate_limit())
    
    print("\n✨ All demos complete!\n")