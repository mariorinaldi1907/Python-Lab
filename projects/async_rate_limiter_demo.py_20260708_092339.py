"""
Date: 2026-07-08
Implemented a token bucket rate limiter using asyncio to explore practical concurrency patterns for API throttling scenarios.
"""

"""
Async Rate Limiter Demo

A practical demonstration of the token bucket algorithm for rate limiting.
I wanted to explore how to properly throttle async operations without blocking
the entire event loop. This came up when I was thinking about how to handle
API rate limits in a real project.

The token bucket refills at a constant rate, and each operation consumes tokens.
If no tokens are available, the operation waits until tokens are replenished.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens are added at a fixed rate (refill_rate per second).
    Each operation consumes tokens. If bucket is empty, operations wait.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the rate limiter.
        
        Args:
            capacity: Maximum number of tokens the bucket can hold
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        I'm using monotonic time here to avoid issues with system clock changes.
        The refill calculation is straightforward: tokens_per_second * elapsed_seconds.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate new tokens, but don't exceed capacity
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the core method. If we don't have enough tokens, we calculate
        exactly how long to wait before we'll have them, then sleep for that duration.
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate wait time needed for tokens to refill
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Release lock during sleep so other tasks can progress
                await asyncio.sleep(wait_time)


async def simulate_api_call(call_id: int, limiter: TokenBucketRateLimiter) -> None:
    """
    Simulate an API call that respects rate limits.
    
    In a real scenario, this would be an actual HTTP request or database query.
    The rate limiter ensures we don't overwhelm the service.
    """
    start_time = time.monotonic()
    
    print(f"[{start_time:.2f}] Task {call_id}: Requesting token...")
    await limiter.acquire()
    
    acquire_time = time.monotonic()
    print(f"[{acquire_time:.2f}] Task {call_id}: Token acquired (waited {acquire_time - start_time:.2f}s), making API call")
    
    # Simulate actual work (API call taking some time)
    await asyncio.sleep(0.1)
    
    end_time = time.monotonic()
    print(f"[{end_time:.2f}] Task {call_id}: Completed")


async def burst_scenario():
    """
    Demonstrate burst handling with rate limiting.
    
    This simulates what happens when you suddenly get a bunch of requests.
    The rate limiter will process the first few immediately (up to capacity),
    then throttle the rest according to the refill rate.
    """
    print("=== Burst Scenario ===")
    print("Creating rate limiter: 3 tokens capacity, 1 token/second refill\n")
    
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
    
    # Fire off 8 tasks all at once
    tasks = [simulate_api_call(i, limiter) for i in range(8)]
    await asyncio.gather(*tasks)
    
    print("\n✓ All tasks completed!")


async def steady_scenario():
    """
    Demonstrate steady traffic with rate limiting.
    
    This shows how the rate limiter handles requests that come in at regular intervals.
    You'll see that requests within the limit proceed immediately.
    """
    print("\n\n=== Steady Traffic Scenario ===")
    print("Creating rate limiter: 5 tokens capacity, 2 tokens/second refill\n")
    
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
    
    # Send requests with small delays between them
    for i in range(6):
        asyncio.create_task(simulate_api_call(i, limiter))
        await asyncio.sleep(0.3)  # Stagger the requests a bit
    
    # Wait for all to complete
    await asyncio.sleep(3)
    print("\n✓ Steady traffic handled!")


async def main():
    """
    Run both demo scenarios.
    
    I wanted to show two different use cases: handling sudden bursts
    (like when a cron job triggers multiple processes) and steady traffic
    (like regular user requests).
    """
    start = time.monotonic()
    
    await burst_scenario()
    await steady_scenario()
    
    duration = time.monotonic() - start
    print(f"\n\nTotal demo duration: {duration:.2f}s")


if __name__ == "__main__":
    # Run the async demo
    # This pattern is pretty standard for asyncio programs
    asyncio.run(main())