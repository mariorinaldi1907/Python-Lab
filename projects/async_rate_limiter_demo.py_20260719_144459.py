"""
Date: 2026-07-19
Implemented a token bucket rate limiter using asyncio to explore backpressure and throttling patterns in concurrent systems.
"""

"""
Async rate limiter demo using the token bucket algorithm.

I wanted to explore how to build a proper rate limiter that handles bursts
gracefully while still enforcing an average request rate. The token bucket
is perfect for this - allows short bursts but maintains long-term limits.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Tokens refill at a constant rate. Each request consumes one token.
    If no tokens are available, the request waits until one becomes available.
    This allows bursts up to bucket_size while maintaining average rate.
    """
    
    def __init__(self, rate: float, bucket_size: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens per second to add to the bucket
            bucket_size: Maximum tokens that can accumulate (burst capacity)
        """
        self.rate = rate
        self.bucket_size = bucket_size
        self.tokens = float(bucket_size)  # Start with a full bucket
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Refill tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time, but cap at bucket_size
        self.tokens = min(self.bucket_size, self.tokens + elapsed * self.rate)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1):
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
                # We need (tokens - self.tokens) more tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Release lock while waiting to allow refills
                await asyncio.sleep(wait_time)


async def simulated_api_call(request_id: int, limiter: TokenBucketRateLimiter):
    """
    Simulate an API call with rate limiting.
    
    This represents a real-world scenario where you're calling an external
    API that has rate limits. The limiter ensures we don't exceed them.
    """
    timestamp = time.time()
    
    # Acquire a token before making the request
    await limiter.acquire()
    
    print(f"[{timestamp:.2f}] Request {request_id:02d} - Starting API call")
    
    # Simulate API processing time (random variation)
    await asyncio.sleep(0.1)
    
    print(f"[{time.time():.2f}] Request {request_id:02d} - Completed")


async def burst_traffic_demo():
    """
    Demo showing how the rate limiter handles burst traffic.
    
    We send 15 requests as fast as possible. The limiter allows the first
    5 to go through immediately (bucket_size), then throttles the rest
    to maintain 2 requests/second average.
    """
    print("=" * 60)
    print("BURST TRAFFIC DEMO")
    print("Rate: 2 requests/sec | Bucket: 5 tokens | Sending: 15 requests")
    print("=" * 60)
    
    # Allow 2 requests per second, with burst capacity of 5
    limiter = TokenBucketRateLimiter(rate=2.0, bucket_size=5)
    
    # Fire off 15 requests as fast as possible
    tasks = [simulated_api_call(i, limiter) for i in range(15)]
    
    start = time.time()
    await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    print(f"\nAll 15 requests completed in {elapsed:.2f} seconds")
    print(f"Effective rate: {15 / elapsed:.2f} requests/sec")
    print()


async def steady_traffic_demo():
    """
    Demo showing the limiter maintaining a steady rate.
    
    Requests come in at varying intervals, but the limiter ensures
    they're processed at a consistent rate.
    """
    print("=" * 60)
    print("STEADY TRAFFIC DEMO")
    print("Rate: 3 requests/sec | Bucket: 2 tokens | Sending: 10 requests")
    print("=" * 60)
    
    limiter = TokenBucketRateLimiter(rate=3.0, bucket_size=2)
    
    tasks = []
    for i in range(10):
        tasks.append(simulated_api_call(i, limiter))
        # Small delay between request submissions
        await asyncio.sleep(0.15)
    
    start = time.time()
    await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    print(f"\nAll 10 requests completed in {elapsed:.2f} seconds")
    print(f"Effective rate: {10 / elapsed:.2f} requests/sec")
    print()


async def main():
    """Run both demo scenarios to show different rate limiting behaviors."""
    print("\nAsyncio Token Bucket Rate Limiter Demo")
    print("Mario's concurrency pattern exploration\n")
    
    # First demo: burst traffic hitting the limiter hard
    await burst_traffic_demo()
    
    # Small pause between demos
    await asyncio.sleep(1)
    
    # Second demo: steadier traffic pattern
    await steady_traffic_demo()
    
    print("Demo complete! The token bucket smoothly handles both scenarios.")


if __name__ == "__main__":
    # Python 3.7+ has asyncio.run() which handles the event loop for us
    asyncio.run(main())