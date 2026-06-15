"""
Date: 2026-06-15
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns — handles burst traffic and graceful degradation.
"""

"""
Async rate limiter using the token bucket algorithm.

I wanted to play around with asyncio and understand how rate limiting works
under the hood. The token bucket is a classic pattern: tokens refill at a
steady rate, and each request consumes one token. If no tokens are available,
the request waits or gets rejected.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens refill at a constant rate (tokens_per_second). Each operation
    consumes a token. If the bucket is empty, operations either wait for
    a token or fail immediately based on the wait parameter.
    """
    
    def __init__(self, tokens_per_second: float, bucket_capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            tokens_per_second: Rate at which tokens are added to the bucket
            bucket_capacity: Maximum number of tokens the bucket can hold
        """
        self.tokens_per_second = tokens_per_second
        self.bucket_capacity = bucket_capacity
        self.tokens = bucket_capacity  # Start with a full bucket
        self.last_refill_time = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill_tokens(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called internally before each acquire attempt to update
        the token count based on how much time has passed.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        
        # Calculate how many tokens to add based on elapsed time
        tokens_to_add = elapsed * self.tokens_per_second
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now
    
    async def acquire(self, wait: bool = True) -> bool:
        """
        Attempt to acquire a token from the bucket.
        
        Args:
            wait: If True, wait for a token to become available.
                  If False, return immediately if no tokens available.
        
        Returns:
            True if token was acquired, False if not (only when wait=False)
        """
        async with self._lock:
            await self._refill_tokens()
            
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            
            if not wait:
                return False
            
            # Calculate how long to wait for the next token
            wait_time = (1.0 - self.tokens) / self.tokens_per_second
        
        # Release lock while waiting to allow other operations
        await asyncio.sleep(wait_time)
        
        # Try again after waiting
        return await self.acquire(wait=False)


async def simulate_request(request_id: int, limiter: TokenBucketRateLimiter, wait: bool = True):
    """
    Simulate a single API request with rate limiting.
    
    Args:
        request_id: Unique identifier for this request
        limiter: The rate limiter instance to use
        wait: Whether to wait for rate limit or fail fast
    """
    start_time = time.monotonic()
    acquired = await limiter.acquire(wait=wait)
    elapsed = time.monotonic() - start_time
    
    if acquired:
        print(f"[Request {request_id:2d}] ✓ Allowed after {elapsed:.3f}s")
        # Simulate doing some work
        await asyncio.sleep(0.1)
    else:
        print(f"[Request {request_id:2d}] ✗ Rejected (rate limit exceeded)")


async def demo_burst_traffic():
    """
    Demonstrate rate limiter handling a burst of concurrent requests.
    
    This creates a burst of 15 requests against a rate limiter configured
    for 5 requests per second with a bucket capacity of 3 (allowing short bursts).
    """
    print("=" * 60)
    print("DEMO: Burst Traffic Handling")
    print("Rate limit: 5 req/s, Bucket capacity: 3 tokens")
    print("Simulating 15 concurrent requests...")
    print("=" * 60)
    
    # 5 requests per second, but allow bursts of up to 3
    limiter = TokenBucketRateLimiter(tokens_per_second=5.0, bucket_capacity=3)
    
    # Create 15 concurrent requests
    tasks = [simulate_request(i, limiter, wait=True) for i in range(15)]
    await asyncio.gather(*tasks)


async def demo_fail_fast():
    """
    Demonstrate rate limiter with fail-fast behavior (no waiting).
    
    Some requests will be rejected immediately if tokens aren't available.
    """
    print("\n" + "=" * 60)
    print("DEMO: Fail-Fast Mode")
    print("Rate limit: 3 req/s, Bucket capacity: 2 tokens")
    print("Simulating 8 requests with no waiting...")
    print("=" * 60)
    
    limiter = TokenBucketRateLimiter(tokens_per_second=3.0, bucket_capacity=2)
    
    # Fire off requests without waiting for rate limit
    tasks = [simulate_request(i, limiter, wait=False) for i in range(8)]
    await asyncio.gather(*tasks)


async def main():
    """
    Run all rate limiter demonstrations.
    
    I included two scenarios: one where requests wait for tokens (typical API client),
    and one where they fail fast (useful for high-throughput services that need to
    shed load quickly).
    """
    await demo_burst_traffic()
    await demo_fail_fast()
    
    print("\n" + "=" * 60)
    print("Rate limiter demos complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())