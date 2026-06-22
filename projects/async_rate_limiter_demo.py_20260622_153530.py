"""
Date: 2026-06-22
Created an async rate limiter using the token bucket algorithm to explore concurrency patterns and see how asyncio handles real-world API throttling scenarios.
"""

"""
Async Rate Limiter Demo using Token Bucket Algorithm

I wanted to understand rate limiting better since I keep hitting API limits
in my side projects. The token bucket is elegant — it allows bursts while
still enforcing average rates. This implementation uses asyncio to simulate
multiple concurrent workers trying to access a rate-limited resource.
"""

import asyncio
import time
from typing import Optional


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Tokens refill at a constant rate. Each request consumes one token.
    If no tokens are available, the request waits until a token is refilled.
    This allows bursts (up to bucket_size) while maintaining average rate.
    """
    
    def __init__(self, rate: float, bucket_size: int):
        """
        Initialize the token bucket.
        
        Args:
            rate: Tokens refilled per second (e.g., 5.0 means 5 requests/sec)
            bucket_size: Maximum tokens that can accumulate (burst capacity)
        """
        self.rate = rate
        self.bucket_size = bucket_size
        self.tokens = bucket_size  # Start with a full bucket
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time.
        
        Called internally before consuming tokens. The math here is straightforward:
        tokens_to_add = elapsed_seconds * tokens_per_second
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.rate
        
        # Cap at bucket_size to prevent infinite accumulation
        self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
            
        Returns:
            The time spent waiting in seconds
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return 0.0
                
                # Not enough tokens, calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                # Release lock while waiting to let other coroutines proceed
                # (though in this case we're actually blocking)
                await asyncio.sleep(wait_time)


async def worker(worker_id: int, limiter: TokenBucket, num_requests: int):
    """
    Simulates a worker making rate-limited requests.
    
    Each worker tries to make num_requests calls through the rate limiter.
    This helps demonstrate how multiple concurrent workers share the rate limit.
    """
    for i in range(num_requests):
        start = time.monotonic()
        await limiter.acquire()
        wait_time = time.monotonic() - start
        
        # Simulate some work after acquiring permission
        await asyncio.sleep(0.05)
        
        print(f"Worker {worker_id} | Request {i+1}/{num_requests} | "
              f"Waited: {wait_time:.3f}s")


async def demonstrate_burst_handling(limiter: TokenBucket):
    """
    Shows how the token bucket handles burst traffic.
    
    Sends several requests rapidly to demonstrate burst capacity,
    then shows how rate limiting kicks in after bucket depletes.
    """
    print("\n=== Burst Handling Demo ===")
    print("Sending 5 rapid requests (bucket can handle initial burst)...\n")
    
    for i in range(5):
        start = time.monotonic()
        await limiter.acquire()
        wait_time = time.monotonic() - start
        print(f"Burst request {i+1} | Waited: {wait_time:.3f}s")
    
    print("\nBucket depleted. Next requests will be rate-limited...\n")
    
    for i in range(3):
        start = time.monotonic()
        await limiter.acquire()
        wait_time = time.monotonic() - start
        print(f"Rate-limited request {i+1} | Waited: {wait_time:.3f}s")


async def main():
    """
    Main demo orchestrating different rate limiting scenarios.
    
    I wanted to show both concurrent workers sharing a limit and
    how burst traffic gets handled. Real-world use cases include
    API clients, web scrapers, or any system that needs to respect
    external rate limits.
    """
    print("╔════════════════════════════════════════════╗")
    print("║   Async Rate Limiter with Token Bucket    ║")
    print("╚════════════════════════════════════════════╝\n")
    
    # Config: 2 requests per second, burst capacity of 3
    rate_limit = 2.0
    burst_capacity = 3
    
    print(f"Rate: {rate_limit} requests/sec")
    print(f"Burst capacity: {burst_capacity} tokens\n")
    
    # Demo 1: Multiple concurrent workers
    print("=== Concurrent Workers Demo ===")
    print("3 workers, each making 3 requests\n")
    
    limiter = TokenBucket(rate=rate_limit, bucket_size=burst_capacity)
    
    workers = [
        worker(worker_id=1, limiter=limiter, num_requests=3),
        worker(worker_id=2, limiter=limiter, num_requests=3),
        worker(worker_id=3, limiter=limiter, num_requests=3),
    ]
    
    await asyncio.gather(*workers)
    
    # Demo 2: Burst handling
    # Wait a bit to let the bucket refill
    print("\nWaiting 2 seconds for bucket to refill...")
    await asyncio.sleep(2)
    
    limiter_burst = TokenBucket(rate=rate_limit, bucket_size=burst_capacity)
    await demonstrate_burst_handling(limiter_burst)
    
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    # Python 3.7+ has asyncio.run() which handles event loop creation/cleanup
    asyncio.run(main())