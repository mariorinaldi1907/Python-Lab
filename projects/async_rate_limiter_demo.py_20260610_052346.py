"""
Date: 2026-06-10
Implemented a token bucket rate limiter using asyncio to demonstrate controlled concurrency with realistic API call simulation.
"""

"""
Async rate limiter using token bucket algorithm.

I wanted to explore rate limiting patterns after hitting API limits too many times
in production. The token bucket is nice because it allows bursts while still
enforcing long-term rate limits.
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiterConfig:
    """Configuration for the rate limiter."""
    rate: float  # tokens per second
    capacity: int  # max burst size


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Refills at a constant rate but allows bursts up to capacity.
    This is way better than a simple counter because you can handle
    spiky traffic patterns without rejecting requests unnecessarily.
    """
    
    def __init__(self, config: RateLimiterConfig):
        self.rate = config.rate
        self.capacity = config.capacity
        self.tokens = float(config.capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        
        # Don't exceed capacity - that's the whole point of the bucket
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from the bucket.
        
        Returns True if tokens were available, False otherwise.
        I'm not blocking here - caller decides whether to retry.
        """
        async with self._lock:
            await self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def wait_for_token(self, tokens: int = 1):
        """
        Block until we can acquire the requested tokens.
        
        This is the "nice" version that handles retries for you.
        In production you'd want a timeout here.
        """
        while True:
            if await self.acquire(tokens):
                return
            # Sleep for the minimum time needed to get a token
            await asyncio.sleep(1.0 / self.rate)


class APIClient:
    """
    Mock API client that respects rate limits.
    
    Simulates making requests to an external API that has rate limits.
    In reality this would be httpx or aiohttp calls.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        self.rate_limiter = rate_limiter
        self.request_count = 0
        self.start_time = None
    
    async def make_request(self, worker_id: int, request_id: int) -> dict:
        """
        Simulate an API request with rate limiting.
        
        Waits for rate limiter, then "calls" the API (just sleeps).
        """
        if self.start_time is None:
            self.start_time = time.monotonic()
        
        # Wait for rate limiter to allow this request
        await self.rate_limiter.wait_for_token()
        
        # Simulate API call latency
        await asyncio.sleep(0.1)
        
        self.request_count += 1
        elapsed = time.monotonic() - self.start_time
        
        return {
            'worker_id': worker_id,
            'request_id': request_id,
            'total_requests': self.request_count,
            'elapsed': elapsed,
            'rate': self.request_count / elapsed if elapsed > 0 else 0
        }


async def worker(worker_id: int, num_requests: int, client: APIClient, results: list):
    """
    Worker that makes multiple API requests.
    
    Each worker competes for rate limiter tokens. This simulates
    having multiple parts of your app all hitting the same external API.
    """
    print(f"[Worker {worker_id}] Starting with {num_requests} requests to make")
    
    for i in range(num_requests):
        result = await client.make_request(worker_id, i)
        results.append(result)
        
        # Print every 5th request to avoid spam
        if i % 5 == 0 or i == num_requests - 1:
            print(f"[Worker {worker_id}] Request {i+1}/{num_requests} | "
                  f"Total: {result['total_requests']} | "
                  f"Rate: {result['rate']:.2f} req/s")
    
    print(f"[Worker {worker_id}] Completed all requests")


async def main():
    """
    Demo the rate limiter with multiple concurrent workers.
    
    I'm using 3 workers making 20 requests each, rate limited to 10 req/s.
    Should see the rate hover around 10 req/s even though we have multiple
    workers competing for tokens.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    # Configure rate limiter: 10 requests/sec, burst up to 15
    config = RateLimiterConfig(rate=10.0, capacity=15)
    rate_limiter = TokenBucketRateLimiter(config)
    
    print(f"Config: {config.rate} req/s, burst capacity: {config.capacity}\n")
    
    # Create shared API client
    client = APIClient(rate_limiter)
    results = []
    
    # Spawn multiple workers that will compete for rate limiter tokens
    workers_count = 3
    requests_per_worker = 20
    
    start = time.monotonic()
    
    worker_tasks = [
        worker(i, requests_per_worker, client, results)
        for i in range(workers_count)
    ]
    
    await asyncio.gather(*worker_tasks)
    
    elapsed = time.monotonic() - start
    total_requests = len(results)
    
    print(f"\n=== Summary ===")
    print(f"Total requests: {total_requests}")
    print(f"Time elapsed: {elapsed:.2f}s")
    print(f"Average rate: {total_requests / elapsed:.2f} req/s")
    print(f"Expected ~{config.rate} req/s (after initial burst)")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())