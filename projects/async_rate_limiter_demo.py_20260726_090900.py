"""
Date: 2026-07-26
Implemented a token bucket rate limiter with asyncio to explore controlled concurrency — useful for respecting API rate limits in real projects.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiterConfig:
    """Configuration for the token bucket rate limiter."""
    max_tokens: int
    refill_rate: float  # tokens per second
    

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    The bucket starts full and drains as requests are made. It refills
    at a constant rate. If the bucket is empty, requests must wait.
    This is the algorithm I use in production for API rate limiting.
    """
    
    def __init__(self, config: RateLimiterConfig):
        """Initialize the rate limiter with given configuration."""
        self.max_tokens = config.max_tokens
        self.refill_rate = config.refill_rate
        self.tokens = float(config.max_tokens)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Refill tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        # Calculate how many tokens to add based on time passed
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is where the magic happens — if we don't have enough tokens,
        we calculate how long to wait and sleep. The lock ensures thread safety.
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Not enough tokens, calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Release lock while sleeping so other coroutines can check
                await asyncio.sleep(wait_time)


class MockAPIClient:
    """
    Simulates an API client that respects rate limits.
    
    I built this to test the rate limiter with realistic scenarios
    where multiple coroutines are competing for API quota.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter, name: str):
        """Initialize API client with a rate limiter."""
        self.rate_limiter = rate_limiter
        self.name = name
        self.request_count = 0
    
    async def make_request(self, request_id: int) -> dict:
        """
        Make a rate-limited API request.
        
        In real life, this would be an HTTP call. Here we just simulate
        the delay and show that rate limiting is working.
        """
        await self.rate_limiter.acquire()
        
        start_time = time.time()
        # Simulate API call taking some time
        await asyncio.sleep(0.1)
        
        self.request_count += 1
        return {
            'client': self.name,
            'request_id': request_id,
            'timestamp': start_time,
            'total_requests': self.request_count
        }


async def worker(client: MockAPIClient, num_requests: int, worker_id: int):
    """
    Worker coroutine that makes multiple API requests.
    
    This simulates real-world scenarios where you have multiple async
    tasks all trying to use the same rate-limited resource.
    """
    print(f"[Worker {worker_id}] Starting with {num_requests} requests to make")
    
    for i in range(num_requests):
        result = await client.make_request(i)
        print(f"[Worker {worker_id}] Request {i+1}/{num_requests} completed - "
              f"Total by {result['client']}: {result['total_requests']}")
    
    print(f"[Worker {worker_id}] Finished all requests")


async def demonstrate_rate_limiting():
    """
    Main demo showing the rate limiter in action.
    
    I set up a scenario with 5 requests/sec limit and spawn multiple
    workers that all share the same rate limiter. Watch how they coordinate!
    """
    print("=" * 70)
    print("Token Bucket Rate Limiter Demo")
    print("=" * 70)
    print("\nConfiguration:")
    print("  - Max tokens: 5")
    print("  - Refill rate: 5 tokens/second")
    print("  - Workers: 3")
    print("  - Requests per worker: 4")
    print("\nExpected behavior: ~12 requests over ~2.4 seconds")
    print("=" * 70)
    print()
    
    # Configure rate limiter: 5 requests per second
    config = RateLimiterConfig(max_tokens=5, refill_rate=5.0)
    rate_limiter = TokenBucketRateLimiter(config)
    
    # Create API client (shared rate limiter)
    api_client = MockAPIClient(rate_limiter, "SharedClient")
    
    # Spawn multiple workers competing for rate limit
    start_time = time.time()
    
    workers = [
        worker(api_client, num_requests=4, worker_id=i)
        for i in range(3)
    ]
    
    await asyncio.gather(*workers)
    
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print(f"Demo completed in {elapsed:.2f} seconds")
    print(f"Total requests made: {api_client.request_count}")
    print(f"Effective rate: {api_client.request_count / elapsed:.2f} requests/sec")
    print("=" * 70)


if __name__ == "__main__":
    # Run the demo — this is what I'd actually use to verify it works
    asyncio.run(demonstrate_rate_limiting())