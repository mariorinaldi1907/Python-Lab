"""
Date: 2026-06-29
Created a token bucket rate limiter using asyncio to demonstrate controlled concurrency — handles bursts gracefully and shows real-world API call simulation.
"""

"""
Async Rate Limiter Demo using Token Bucket Algorithm

I wanted to explore rate limiting patterns for API calls, so I built this
token bucket implementation. The idea is simple: tokens refill at a steady
rate, and each request consumes a token. If you're out of tokens, you wait.

This handles bursts naturally (up to bucket capacity) while maintaining
average rate limits over time.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Tokens are added at a constant rate (refill_rate per second).
    Each operation consumes one token. If no tokens available, the caller waits.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the rate limiter.
        
        Args:
            capacity: Maximum number of tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)  # Start with full bucket
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called internally before each acquire attempt to ensure
        tokens are up-to-date without needing a background task.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Add tokens based on time elapsed
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
            
        Returns:
            Time spent waiting in seconds
        """
        async with self._lock:
            await self._refill()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                deficit = tokens - self.tokens
                wait_time = deficit / self.refill_rate
                await asyncio.sleep(wait_time)
                
                # Refill again after waiting
                await self._refill()
            else:
                wait_time = 0.0
            
            # Consume the tokens
            self.tokens -= tokens
            return wait_time


async def simulate_api_call(api_id: int, limiter: TokenBucketRateLimiter):
    """
    Simulate making an API call with rate limiting.
    
    Args:
        api_id: Identifier for this API call
        limiter: The rate limiter to use
    """
    request_time = time.monotonic()
    print(f"[{api_id:02d}] Requesting at t={request_time:.2f}s")
    
    # Acquire a token (this may block if rate limit exceeded)
    wait_time = await limiter.acquire()
    
    if wait_time > 0:
        print(f"[{api_id:02d}] Had to wait {wait_time:.2f}s for rate limit")
    
    # Simulate the actual API call taking some time
    await asyncio.sleep(0.1)
    
    completion_time = time.monotonic()
    print(f"[{api_id:02d}] Completed at t={completion_time:.2f}s")


async def burst_then_steady_demo():
    """
    Demo showing burst behavior followed by steady-state rate limiting.
    
    First 5 requests should burst through (bucket capacity = 5).
    Subsequent requests get rate limited to 2 per second.
    """
    print("=" * 60)
    print("DEMO: Burst then Steady State")
    print("Rate limit: 2 requests/sec, burst capacity: 5")
    print("=" * 60)
    
    # Allow 2 requests per second, with burst capacity of 5
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
    
    # Fire off 10 requests as fast as possible
    tasks = [simulate_api_call(i, limiter) for i in range(10)]
    await asyncio.gather(*tasks)


async def parallel_workers_demo():
    """
    Demo showing multiple workers sharing a rate limiter.
    
    This simulates a real scenario where you have multiple async tasks
    all trying to call an API that has rate limits.
    """
    print("\n" + "=" * 60)
    print("DEMO: Parallel Workers Sharing Rate Limiter")
    print("Rate limit: 3 requests/sec, burst capacity: 3")
    print("=" * 60)
    
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=3.0)
    
    async def worker(worker_id: int, num_requests: int):
        """Each worker makes multiple requests through the shared limiter."""
        for req in range(num_requests):
            call_id = f"W{worker_id}-R{req}"
            await simulate_api_call(call_id, limiter)
            # Small delay between requests from same worker
            await asyncio.sleep(0.2)
    
    # 3 workers, each making 3 requests
    workers = [worker(i, 3) for i in range(3)]
    await asyncio.gather(*workers)


async def main():
    """Run all demos sequentially."""
    start = time.monotonic()
    
    await burst_then_steady_demo()
    await parallel_workers_demo()
    
    elapsed = time.monotonic() - start
    print(f"\n{'=' * 60}")
    print(f"All demos completed in {elapsed:.2f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    # Run the async demos
    asyncio.run(main())