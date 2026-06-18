"""
Date: 2026-06-18
Created an asyncio-based rate limiter using the token bucket algorithm to explore concurrent request handling with configurable limits.
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiterStats:
    """Track stats for the rate limiter's behavior."""
    total_requests: int = 0
    allowed_requests: int = 0
    throttled_requests: int = 0
    total_wait_time: float = 0.0


class TokenBucketRateLimiter:
    """
    Rate limiter using the token bucket algorithm.
    
    Tokens are added at a fixed rate. Each request consumes one token.
    If no tokens are available, the request waits until a token is generated.
    This allows for burst traffic up to the bucket capacity while maintaining
    an average rate over time.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (max sustained request rate)
            capacity: Maximum tokens in bucket (allows bursts up to this size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)  # Start with a full bucket
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
        self.stats = RateLimiterStats()
    
    async def _refill_tokens(self):
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_update
        # Add tokens proportional to time passed, capped at capacity
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to consume (default 1)
            
        Returns:
            Time spent waiting in seconds
        """
        async with self._lock:
            self.stats.total_requests += 1
            await self._refill_tokens()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
                self.stats.throttled_requests += 1
                self.stats.total_wait_time += wait_time
                await asyncio.sleep(wait_time)
                await self._refill_tokens()
            
            self.tokens -= tokens
            self.stats.allowed_requests += 1
            return self.stats.total_wait_time


async def api_request(request_id: int, limiter: TokenBucketRateLimiter):
    """
    Simulate an API request that respects rate limits.
    
    In a real scenario, this would make an HTTP call or similar.
    Here we just demonstrate the rate limiting behavior.
    """
    start = time.monotonic()
    wait_time = await limiter.acquire()
    duration = time.monotonic() - start
    
    # Simulate the actual work (e.g., network call)
    await asyncio.sleep(0.05)
    
    print(f"Request {request_id:3d} | waited: {duration:6.3f}s | completed")


async def burst_traffic_simulator(limiter: TokenBucketRateLimiter):
    """
    Simulate bursty traffic to demonstrate rate limiting.
    
    Sends an initial burst of requests, then spreads out more requests over time.
    This shows how the token bucket handles both bursts and sustained load.
    """
    tasks = []
    
    # Initial burst of 10 requests at once
    print("\n=== Sending burst of 10 requests ===")
    for i in range(10):
        tasks.append(asyncio.create_task(api_request(i, limiter)))
    
    await asyncio.sleep(0.5)
    
    # Then a more gradual stream
    print("\n=== Sending gradual stream of 15 requests ===")
    for i in range(10, 25):
        tasks.append(asyncio.create_task(api_request(i, limiter)))
        await asyncio.sleep(0.2)  # Slight delay between submissions
    
    # Wait for all requests to complete
    await asyncio.gather(*tasks)


async def main():
    """
    Demo the rate limiter with realistic traffic patterns.
    
    Using a rate of 5 req/sec with capacity of 5 means:
    - We can handle bursts up to 5 requests instantly
    - After that, we're limited to 5 requests per second average
    """
    print("Token Bucket Rate Limiter Demo")
    print("=" * 50)
    print("Config: 5 requests/sec, burst capacity of 5 tokens")
    print("=" * 50)
    
    limiter = TokenBucketRateLimiter(rate=5.0, capacity=5)
    
    start_time = time.monotonic()
    await burst_traffic_simulator(limiter)
    total_time = time.monotonic() - start_time
    
    # Print summary statistics
    stats = limiter.stats
    print("\n" + "=" * 50)
    print("STATISTICS")
    print("=" * 50)
    print(f"Total requests:      {stats.total_requests}")
    print(f"Allowed immediately: {stats.allowed_requests - stats.throttled_requests}")
    print(f"Throttled requests:  {stats.throttled_requests}")
    print(f"Total wait time:     {stats.total_wait_time:.2f}s")
    print(f"Total duration:      {total_time:.2f}s")
    print(f"Effective rate:      {stats.total_requests / total_time:.2f} req/sec")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())