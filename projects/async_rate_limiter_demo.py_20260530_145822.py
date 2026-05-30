"""
Date: 2026-05-30
Created a token bucket rate limiter using asyncio to demonstrate controlled concurrency and rate limiting for async tasks.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling async task execution.
    
    Allows bursts up to max_tokens, then throttles to refill_rate tokens/sec.
    This is basically how AWS API throttling works — you get a burst budget
    that refills over time.
    """
    
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Initialize the rate limiter.
        
        Args:
            max_tokens: Maximum tokens in the bucket (burst capacity)
            refill_rate: Tokens added per second
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Refill tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Add tokens proportional to time elapsed
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True when tokens are acquired
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                # Calculate how long to wait for enough tokens
                # This is why I like token bucket over simple delays —
                # it handles varying request sizes intelligently
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                await asyncio.sleep(wait_time)


async def api_call(limiter: TokenBucketRateLimiter, task_id: int, cost: int = 1):
    """
    Simulate an API call with rate limiting.
    
    Args:
        limiter: The rate limiter to use
        task_id: Identifier for this task
        cost: Token cost for this operation (simulates heavy vs light calls)
    """
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Task {task_id} waiting for {cost} token(s)...")
    
    await limiter.acquire(cost)
    
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Task {task_id} executing (cost: {cost})")
    
    # Simulate actual work
    await asyncio.sleep(0.1)
    
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Task {task_id} completed")


async def burst_test(limiter: TokenBucketRateLimiter):
    """
    Test the rate limiter with a burst of requests.
    
    This simulates what happens when you suddenly get a spike of traffic.
    The first few requests burn through the token bucket, then subsequent
    ones have to wait for refills.
    """
    print("\n=== BURST TEST ===")
    print("Sending 10 requests as fast as possible...")
    print("(Bucket: 5 tokens max, refills at 2 tokens/sec)\n")
    
    tasks = [api_call(limiter, i) for i in range(10)]
    await asyncio.gather(*tasks)


async def variable_cost_test():
    """
    Test with different token costs per request.
    
    This demonstrates how you might handle different API endpoints that
    have different rate limit costs (like GraphQL complexity scoring).
    """
    print("\n\n=== VARIABLE COST TEST ===")
    print("Different requests have different token costs...")
    print("(Bucket: 10 tokens max, refills at 3 tokens/sec)\n")
    
    limiter = TokenBucketRateLimiter(max_tokens=10, refill_rate=3.0)
    
    tasks = [
        api_call(limiter, 1, cost=1),  # Light request
        api_call(limiter, 2, cost=5),  # Heavy request
        api_call(limiter, 3, cost=2),  # Medium request
        api_call(limiter, 4, cost=1),  # Light request
        api_call(limiter, 5, cost=3),  # Medium request
    ]
    
    await asyncio.gather(*tasks)


async def sustained_load_test():
    """
    Test sustained load to show steady-state behavior.
    
    After the initial burst capacity is exhausted, requests should process
    at exactly the refill rate.
    """
    print("\n\n=== SUSTAINED LOAD TEST ===")
    print("Steady stream of requests (should stabilize at refill rate)...")
    print("(Bucket: 3 tokens max, refills at 1 token/sec)\n")
    
    limiter = TokenBucketRateLimiter(max_tokens=3, refill_rate=1.0)
    
    # Send requests with small delays between them
    for i in range(8):
        asyncio.create_task(api_call(limiter, i))
        await asyncio.sleep(0.2)  # Small delay, but faster than refill rate
    
    # Wait for all tasks to complete
    await asyncio.sleep(10)


async def main():
    """Run all the demo tests."""
    print("Token Bucket Rate Limiter Demo")
    print("=" * 50)
    
    # Test 1: Basic burst handling
    limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=2.0)
    await burst_test(limiter)
    
    # Test 2: Variable cost requests
    await variable_cost_test()
    
    # Test 3: Sustained load
    await sustained_load_test()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    # I'm using asyncio.run() here because it properly handles cleanup
    # and is the recommended way since Python 3.7
    asyncio.run(main())