"""
Date: 2026-07-12
Implemented a token bucket rate limiter using asyncio to throttle concurrent requests — useful pattern I keep needing for API integrations.
"""

"""
Async rate limiter using the token bucket algorithm.

This demonstrates a concurrency pattern I've needed multiple times when working
with external APIs that have strict rate limits. The token bucket refills at a
steady rate, and each request consumes a token before proceeding.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Rate limiter based on the token bucket algorithm.
    
    Tokens are added at a fixed rate (refill_rate per second).
    Each operation consumes one token. If no tokens are available,
    the caller waits until a token becomes available.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the rate limiter.
        
        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called internally before consuming tokens. The bucket
        never exceeds its capacity.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate how many tokens to add based on time elapsed
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> None:
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
                
                # Calculate how long we need to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Release lock during sleep so other tasks can check
                await asyncio.sleep(wait_time)


async def simulate_api_call(call_id: int, limiter: TokenBucketRateLimiter) -> None:
    """
    Simulate an API call that respects rate limiting.
    
    Args:
        call_id: Identifier for this call
        limiter: Rate limiter to use
    """
    start_time = time.monotonic()
    
    print(f"[{start_time:.2f}] Task {call_id}: Requesting token...")
    
    # Wait for rate limiter to allow this request
    await limiter.acquire()
    
    acquired_time = time.monotonic()
    wait_time = acquired_time - start_time
    
    print(f"[{acquired_time:.2f}] Task {call_id}: Token acquired (waited {wait_time:.2f}s), making API call...")
    
    # Simulate the actual API call taking some time
    await asyncio.sleep(0.5)
    
    complete_time = time.monotonic()
    print(f"[{complete_time:.2f}] Task {call_id}: Complete!")


async def burst_test(limiter: TokenBucketRateLimiter, num_requests: int) -> None:
    """
    Test the rate limiter with a burst of concurrent requests.
    
    Args:
        limiter: Rate limiter instance
        num_requests: Number of concurrent requests to make
    """
    print(f"\n{'='*60}")
    print(f"Starting burst test with {num_requests} requests")
    print(f"Rate limiter: {limiter.capacity} tokens, {limiter.refill_rate} tokens/sec")
    print(f"{'='*60}\n")
    
    start = time.monotonic()
    
    # Fire off all requests at once
    tasks = [simulate_api_call(i, limiter) for i in range(num_requests)]
    await asyncio.gather(*tasks)
    
    elapsed = time.monotonic() - start
    print(f"\n{'='*60}")
    print(f"All {num_requests} requests completed in {elapsed:.2f} seconds")
    print(f"{'='*60}\n")


async def main():
    """
    Run demonstrations of the rate limiter.
    
    This shows two scenarios:
    1. A small burst that fits within the bucket capacity
    2. A larger burst that requires waiting for token refills
    """
    # Scenario 1: Small burst (all requests can proceed immediately)
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2.0)
    await burst_test(limiter, num_requests=5)
    
    # Give some time between tests
    await asyncio.sleep(1)
    
    # Scenario 2: Larger burst (some requests must wait)
    # With capacity=3 and refill_rate=2, the 4th+ requests will be throttled
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=2.0)
    await burst_test(limiter, num_requests=8)


if __name__ == "__main__":
    # I'm using asyncio.run() which handles the event loop setup/teardown
    # much cleaner than the old get_event_loop() pattern
    print("Token Bucket Rate Limiter Demo")
    print("This shows how requests are throttled when exceeding limits\n")
    
    asyncio.run(main())