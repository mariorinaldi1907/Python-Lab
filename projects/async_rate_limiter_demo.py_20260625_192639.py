"""
Date: 2026-06-25
Implemented a token bucket rate limiter using asyncio to demonstrate how to throttle concurrent API calls or requests in a clean, reusable way.
"""

"""
Async rate limiter demo using the token bucket algorithm.

I built this to show how you can elegantly throttle concurrent operations
without blocking everything. The token bucket refills at a steady rate but
allows bursts up to the bucket capacity — super useful for API clients.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Tokens refill at a steady rate. Each operation consumes one token.
    If no tokens available, the operation waits until one is available.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens per second to add to the bucket
            capacity: Maximum number of tokens the bucket can hold
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Refill tokens based on elapsed time
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                await asyncio.sleep(wait_time)


async def simulated_api_call(worker_id: int, call_num: int, limiter: TokenBucketRateLimiter) -> None:
    """
    Simulate an API call that respects rate limiting.
    
    Args:
        worker_id: ID of the worker making the call
        call_num: The call number for this worker
        limiter: Rate limiter to use
    """
    await limiter.acquire()
    
    # Simulate the actual API work
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] Worker {worker_id} - Call #{call_num} started")
    
    # Simulate network delay
    await asyncio.sleep(0.1)
    
    print(f"[{timestamp}] Worker {worker_id} - Call #{call_num} completed")


async def worker(worker_id: int, num_calls: int, limiter: TokenBucketRateLimiter) -> None:
    """
    Worker that makes multiple API calls.
    
    Args:
        worker_id: Unique identifier for this worker
        num_calls: Number of calls this worker should make
        limiter: Rate limiter instance
    """
    print(f"Worker {worker_id} starting with {num_calls} calls to make")
    
    tasks = []
    for i in range(num_calls):
        task = simulated_api_call(worker_id, i + 1, limiter)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    print(f"Worker {worker_id} finished all calls")


async def demo_burst_then_steady():
    """
    Demonstrate burst handling followed by steady-state rate limiting.
    
    The rate limiter allows 5 tokens max (burst capacity) but refills
    at 2 tokens/second. We'll fire off 10 requests immediately and see
    how they get throttled.
    """
    print("=" * 60)
    print("DEMO: Burst traffic followed by steady state")
    print("Rate: 2 requests/second, Capacity: 5 tokens")
    print("=" * 60)
    
    limiter = TokenBucketRateLimiter(rate=2.0, capacity=5)
    
    # Create 3 workers that each want to make several calls
    # Total of 10 calls trying to go through at once
    workers = [
        worker(1, 4, limiter),
        worker(2, 3, limiter),
        worker(3, 3, limiter),
    ]
    
    start = time.monotonic()
    await asyncio.gather(*workers)
    elapsed = time.monotonic() - start
    
    print(f"\nTotal time: {elapsed:.2f} seconds")
    print(f"Expected ~2.5 seconds for 10 calls at 2/sec after initial burst of 5")


async def demo_concurrent_limited():
    """
    Show how multiple concurrent workers are all constrained by the same limiter.
    """
    print("\n" + "=" * 60)
    print("DEMO: Multiple concurrent workers sharing a rate limiter")
    print("Rate: 3 requests/second, Capacity: 3 tokens")
    print("=" * 60)
    
    limiter = TokenBucketRateLimiter(rate=3.0, capacity=3)
    
    # 5 workers each making 2 calls = 10 total calls at 3/sec
    workers = [worker(i + 1, 2, limiter) for i in range(5)]
    
    start = time.monotonic()
    await asyncio.gather(*workers)
    elapsed = time.monotonic() - start
    
    print(f"\nTotal time: {elapsed:.2f} seconds")
    print(f"Expected ~2.3 seconds for 10 calls at 3/sec with initial burst of 3")


async def main():
    """Run all demonstrations."""
    print("\nToken Bucket Rate Limiter Demo")
    print("This shows how the algorithm handles burst traffic gracefully\n")
    
    await demo_burst_then_steady()
    await asyncio.sleep(0.5)  # Brief pause between demos
    await demo_concurrent_limited()
    
    print("\n" + "=" * 60)
    print("Demo complete! The rate limiter kept everything under control.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())