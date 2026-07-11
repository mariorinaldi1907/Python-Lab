"""
Date: 2026-07-11
Implemented a token bucket rate limiter using asyncio to understand how to control API request rates in concurrent environments.
"""

"""
Async Rate Limiter Demo using Token Bucket Algorithm

This script demonstrates a token bucket rate limiter that controls
how fast concurrent tasks can execute. I built this to understand
rate limiting patterns for API clients and background workers.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling execution rate.
    
    Tokens refill at a steady rate up to a max capacity (burst).
    Each operation consumes one token. If no tokens available, waits.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens per second to add to bucket
            capacity: Maximum tokens the bucket can hold (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on time elapsed since last refill.
        
        This is the core of the token bucket - we calculate how many
        tokens should have been added based on elapsed time.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add: rate * time_elapsed
        tokens_to_add = elapsed * self.rate
        
        # Don't exceed capacity (this enforces burst limit)
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            Time spent waiting in seconds
        """
        async with self._lock:
            await self._refill()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
                
                await asyncio.sleep(wait_time)
                
                # After waiting, refill and consume
                await self._refill()
                self.tokens -= tokens
                
                return wait_time
            else:
                # We have enough tokens, consume immediately
                self.tokens -= tokens
                return 0.0


class APIWorker:
    """
    Simulates an async worker making API calls with rate limiting.
    
    I wanted to show a realistic use case - imagine hitting an API
    that only allows N requests per second.
    """
    
    def __init__(self, worker_id: int, rate_limiter: TokenBucketRateLimiter):
        """
        Initialize the worker.
        
        Args:
            worker_id: Unique identifier for this worker
            rate_limiter: Shared rate limiter instance
        """
        self.worker_id = worker_id
        self.rate_limiter = rate_limiter
        self.requests_made = 0
        self.total_wait_time = 0.0
    
    async def make_request(self, request_num: int):
        """
        Simulate making an API request with rate limiting.
        
        Args:
            request_num: The request number for logging
        """
        # Acquire token before making request
        wait_time = await self.rate_limiter.acquire()
        self.total_wait_time += wait_time
        
        # Simulate API call taking some time
        await asyncio.sleep(0.05)
        
        self.requests_made += 1
        
        status = "waited" if wait_time > 0 else "immediate"
        print(f"Worker {self.worker_id} | Request #{request_num} | "
              f"{status} ({wait_time:.3f}s)")
    
    async def run(self, num_requests: int):
        """
        Run the worker for a specified number of requests.
        
        Args:
            num_requests: How many requests this worker should make
        """
        for i in range(num_requests):
            await self.make_request(i + 1)
        
        print(f"\nWorker {self.worker_id} finished: "
              f"{self.requests_made} requests, "
              f"total wait time: {self.total_wait_time:.2f}s")


async def demo_rate_limiter():
    """
    Demonstrate the rate limiter with multiple concurrent workers.
    
    This shows how the rate limiter handles burst traffic and then
    throttles to maintain the target rate across all workers.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    # Create rate limiter: 5 requests/sec, burst capacity of 10
    # This means we can handle 10 requests immediately, then throttle to 5/sec
    rate_limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    
    print(f"Rate limit: {rate_limiter.rate} req/sec")
    print(f"Burst capacity: {rate_limiter.capacity} tokens")
    print(f"Starting {3} workers, each making {8} requests\n")
    
    # Create multiple workers sharing the same rate limiter
    workers = [
        APIWorker(worker_id=i, rate_limiter=rate_limiter)
        for i in range(3)
    ]
    
    # Run all workers concurrently
    start_time = time.monotonic()
    
    await asyncio.gather(
        *[worker.run(num_requests=8) for worker in workers]
    )
    
    end_time = time.monotonic()
    total_time = end_time - start_time
    
    total_requests = sum(w.requests_made for w in workers)
    effective_rate = total_requests / total_time
    
    print(f"\n=== Summary ===")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Effective rate: {effective_rate:.2f} req/sec")
    print(f"Target rate: {rate_limiter.rate} req/sec")


if __name__ == "__main__":
    # Run the demo
    # You'll see the first ~10 requests go through quickly (burst),
    # then the rate limiter kicks in and throttles to 5 req/sec
    asyncio.run(demo_rate_limiter())