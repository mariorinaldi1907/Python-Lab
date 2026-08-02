"""
Date: 2026-08-02
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns — supports burst traffic and gradual refill.
"""

"""
Async Rate Limiter Demo using Token Bucket Algorithm

This demonstrates a practical concurrency pattern where multiple async tasks
compete for a limited resource (API calls, network requests, etc.) and are
rate-limited to avoid overwhelming a service.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Allows bursts up to bucket_size, then enforces rate_per_second.
    I chose token bucket over leaky bucket because it's more forgiving
    for bursty workloads while still enforcing average rate limits.
    """
    
    def __init__(self, rate_per_second: float, bucket_size: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate_per_second: How many tokens refill per second
            bucket_size: Maximum tokens that can accumulate (burst capacity)
        """
        self.rate_per_second = rate_per_second
        self.bucket_size = bucket_size
        self.tokens = bucket_size  # Start with full bucket
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called internally before checking if we can acquire a token.
        Using monotonic time to avoid issues with system clock changes.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate how many tokens should be added
        new_tokens = elapsed * self.rate_per_second
        self.tokens = min(self.bucket_size, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
        
        This will block until enough tokens are available. The lock ensures
        multiple coroutines don't race to grab the same tokens.
        """
        while True:
            async with self._lock:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long to wait for enough tokens
                needed = tokens - self.tokens
                wait_time = needed / self.rate_per_second
            
            # Sleep outside the lock so other tasks can check their status
            await asyncio.sleep(wait_time)


async def api_call(task_id: int, limiter: TokenBucketRateLimiter):
    """
    Simulate an API call that needs rate limiting.
    
    In real scenarios this might be hitting an external API with rate limits,
    or managing database connection pools, or limiting concurrent file I/O.
    """
    print(f"[{time.strftime('%H:%M:%S')}] Task {task_id}: Waiting for rate limit...")
    
    await limiter.acquire()
    
    print(f"[{time.strftime('%H:%M:%S')}] Task {task_id}: Acquired! Making API call...")
    
    # Simulate the actual API call taking some time
    await asyncio.sleep(0.5)
    
    print(f"[{time.strftime('%H:%M:%S')}] Task {task_id}: Completed!")


async def burst_test(limiter: TokenBucketRateLimiter):
    """
    Test the rate limiter with a burst of concurrent requests.
    
    This simulates what happens when you suddenly get a bunch of work to do
    and need to throttle it. The first few should go through quickly (burst),
    then subsequent ones should be rate-limited.
    """
    print("\n=== Burst Test: Launching 10 tasks at once ===\n")
    
    tasks = [api_call(i, limiter) for i in range(10)]
    await asyncio.gather(*tasks)


async def gradual_test(limiter: TokenBucketRateLimiter):
    """
    Test the rate limiter with gradually arriving requests.
    
    This is more like a steady-state scenario where requests trickle in
    over time. Should mostly flow through without much waiting.
    """
    print("\n=== Gradual Test: Tasks arriving over time ===\n")
    
    for i in range(5):
        asyncio.create_task(api_call(i + 100, limiter))
        await asyncio.sleep(0.8)  # New task every 0.8s
    
    # Wait a bit for all tasks to complete
    await asyncio.sleep(3)


async def main():
    """
    Run the demo showing both burst and gradual traffic patterns.
    
    I set up the rate limiter to allow 2 requests per second with a bucket
    size of 3. This means it can handle a burst of 3 immediate requests,
    then throttles to 2/sec after that.
    """
    print("Token Bucket Rate Limiter Demo")
    print("=" * 50)
    print("Config: 2 requests/sec, burst capacity of 3")
    print("=" * 50)
    
    limiter = TokenBucketRateLimiter(rate_per_second=2.0, bucket_size=3)
    
    await burst_test(limiter)
    
    # Give it a moment between tests
    await asyncio.sleep(2)
    
    await gradual_test(limiter)
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())