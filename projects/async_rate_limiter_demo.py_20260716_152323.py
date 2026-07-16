"""
Date: 2026-07-16
Implemented a token bucket rate limiter using asyncio to control concurrent API request patterns — useful for avoiding API throttling.
"""

#!/usr/bin/env python3
"""
Async rate limiter demo using the token bucket algorithm.

I wanted to build something practical that I'd actually use when hitting APIs.
The token bucket lets you handle bursts while maintaining an average rate limit.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Tokens are added at a constant rate. Each request consumes one token.
    If no tokens are available, the request waits until one is added.
    This allows bursts up to bucket_size while maintaining average rate.
    """
    
    def __init__(self, rate: float, bucket_size: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 = 5 requests/sec)
            bucket_size: Max tokens that can accumulate (burst capacity)
        """
        self.rate = rate
        self.bucket_size = bucket_size
        self.tokens = bucket_size  # Start with a full bucket
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _add_tokens(self):
        """
        Add tokens based on time elapsed since last update.
        
        This is called before each acquire attempt to refill the bucket
        based on how much time has passed.
        """
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Add tokens proportional to elapsed time
        self.tokens = min(
            self.bucket_size,
            self.tokens + elapsed * self.rate
        )
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        async with self._lock:
            while True:
                await self._add_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Not enough tokens, calculate how long to wait
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
                
                # Release lock while waiting to allow other coroutines to check
                await asyncio.sleep(wait_time)


async def api_request(request_id: int, limiter: TokenBucketRateLimiter, delay: float = 0.1):
    """
    Simulate an API request with rate limiting.
    
    Args:
        request_id: Identifier for this request
        limiter: Rate limiter instance to use
        delay: Simulated processing time for the request
    """
    timestamp = time.time()
    print(f"[{timestamp:.2f}] Request {request_id:2d}: Waiting for rate limiter...")
    
    await limiter.acquire()
    
    acquired_time = time.time()
    wait_duration = acquired_time - timestamp
    print(f"[{acquired_time:.2f}] Request {request_id:2d}: Acquired token (waited {wait_duration:.2f}s), executing...")
    
    # Simulate the actual API call
    await asyncio.sleep(delay)
    
    complete_time = time.time()
    print(f"[{complete_time:.2f}] Request {request_id:2d}: Complete")


async def burst_then_steady_demo():
    """
    Demo scenario: burst of requests followed by steady stream.
    
    This shows how the token bucket handles both burst traffic
    (using accumulated tokens) and sustained traffic (rate-limited).
    """
    print("=" * 70)
    print("DEMO: Burst then steady traffic")
    print("Rate limit: 2 requests/second, Bucket size: 5")
    print("=" * 70)
    
    # 2 requests per second, but can burst up to 5
    limiter = TokenBucketRateLimiter(rate=2.0, bucket_size=5)
    
    tasks = []
    
    # Initial burst of 8 requests
    print("\n>>> Sending burst of 8 requests...")
    for i in range(8):
        tasks.append(asyncio.create_task(api_request(i, limiter)))
    
    # Wait a bit, then send more requests
    await asyncio.sleep(2.0)
    print("\n>>> Sending 4 more requests after 2-second pause...")
    for i in range(8, 12):
        tasks.append(asyncio.create_task(api_request(i, limiter)))
    
    # Wait for all requests to complete
    await asyncio.gather(*tasks)
    
    print("\n" + "=" * 70)
    print("All requests completed!")
    print("=" * 70)


async def main():
    """
    Run the rate limiter demo.
    
    In real usage, I'd probably make this a context manager and
    integrate it with aiohttp or httpx for actual API calls.
    """
    start_time = time.time()
    
    await burst_then_steady_demo()
    
    elapsed = time.time() - start_time
    print(f"\nTotal demo time: {elapsed:.2f} seconds")
    print("\nNotice how the first 5 requests go through immediately (burst capacity),")
    print("then subsequent requests are rate-limited to ~2 per second.")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())