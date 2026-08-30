"""
Date: 2026-08-30
Implemented a token bucket rate limiter using asyncio to demonstrate how concurrent tasks can share bandwidth while staying under a rate cap.
"""

"""
Async rate limiter using the token bucket algorithm.

I wanted to explore how to properly throttle concurrent workers in Python
without letting anyone hog all the bandwidth. The token bucket is nice because
it allows bursts up to the bucket capacity while maintaining an average rate.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Rate limiter implementing the token bucket algorithm.
    
    Tokens are added at a fixed rate. Each operation consumes one token.
    If no tokens are available, the caller waits until one becomes available.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens per second to add to the bucket
            capacity: Maximum tokens the bucket can hold (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the main method workers call before doing rate-limited work.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Add tokens based on time elapsed since last update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long we need to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Release the lock while waiting so other tasks can proceed
                self._lock.release()
                await asyncio.sleep(wait_time)
                await self._lock.acquire()


async def api_worker(worker_id: int, limiter: TokenBucketRateLimiter, num_requests: int):
    """
    Simulate a worker making API calls with rate limiting.
    
    This represents a real-world scenario where you have multiple coroutines
    hitting an API that has rate limits, and you want to coordinate them.
    """
    print(f"[Worker {worker_id}] Starting with {num_requests} requests to make")
    
    for i in range(num_requests):
        await limiter.acquire()
        
        # Simulate doing actual work (API call, processing, etc)
        request_time = time.time()
        print(f"[Worker {worker_id}] Request {i+1}/{num_requests} at {request_time:.2f}")
        
        # Simulate the API call taking some time
        await asyncio.sleep(0.05)
    
    print(f"[Worker {worker_id}] Completed all requests")


async def demo_basic_rate_limiting():
    """
    Demo showing multiple workers sharing a rate limit.
    
    I set it to 5 requests/second with burst capacity of 10.
    You'll see the first bunch fire quickly (burst), then they settle into
    the steady rate as the bucket empties.
    """
    print("=== Basic Rate Limiting Demo ===")
    print("Rate: 5 requests/sec, Capacity: 10 tokens\n")
    
    # Create a rate limiter: 5 requests per second, burst up to 10
    limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    
    # Spawn 3 workers, each wanting to make 5 requests
    workers = [
        api_worker(worker_id=1, limiter=limiter, num_requests=5),
        api_worker(worker_id=2, limiter=limiter, num_requests=5),
        api_worker(worker_id=3, limiter=limiter, num_requests=5),
    ]
    
    start_time = time.time()
    await asyncio.gather(*workers)
    elapsed = time.time() - start_time
    
    print(f"\nCompleted 15 total requests in {elapsed:.2f} seconds")
    print(f"Effective rate: {15/elapsed:.2f} requests/sec")


async def demo_burst_behavior():
    """
    Demo showing how burst capacity works.
    
    If you wait a bit before starting requests, the bucket fills up and
    you can do a quick burst before throttling kicks in.
    """
    print("\n\n=== Burst Behavior Demo ===")
    print("Waiting 2 seconds to fill bucket, then bursting...\n")
    
    limiter = TokenBucketRateLimiter(rate=3.0, capacity=8)
    
    # Wait for bucket to fill
    await asyncio.sleep(2.0)
    
    # Now do a bunch of requests quickly
    print("Starting burst of 12 requests:")
    
    for i in range(12):
        await limiter.acquire()
        print(f"Request {i+1} at {time.time():.2f}")
    
    print("\nNotice: first 8 fire immediately (burst capacity),")
    print("then remaining 4 are throttled at 3 req/sec")


async def main():
    """
    Run all the demos.
    
    This shows different aspects of how the rate limiter behaves.
    """
    await demo_basic_rate_limiting()
    await demo_burst_behavior()


if __name__ == "__main__":
    # asyncio.run() is the clean way to run async code in Python 3.7+
    asyncio.run(main())