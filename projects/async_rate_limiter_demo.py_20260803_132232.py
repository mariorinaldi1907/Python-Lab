"""
Date: 2026-08-03
Implemented a token bucket rate limiter using asyncio to understand how APIs throttle requests — includes both time-based and burst control.
"""

"""
Async rate limiter using the token bucket algorithm.

This was fun to build — I wanted to understand how rate limiting actually works
under the hood. The token bucket is elegant: tokens refill at a steady rate,
and each request consumes a token. If you're out of tokens, you wait.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Rate limiter using the token bucket algorithm.
    
    Allows bursts up to max_tokens, then enforces a steady rate of refill_rate tokens/sec.
    This is how most real APIs (Stripe, GitHub, etc.) do rate limiting.
    """
    
    def __init__(self, refill_rate: float, max_tokens: int):
        """
        Initialize the rate limiter.
        
        Args:
            refill_rate: Tokens added per second (e.g., 2.0 = 2 requests/sec)
            max_tokens: Maximum burst capacity (bucket size)
        """
        self.refill_rate = refill_rate
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is the core of the algorithm — we calculate how many tokens
        should have been added since the last check, then cap at max_tokens.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add based on time passed
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to consume (default 1)
            
        Returns:
            Wait time in seconds (0 if no wait was needed)
        """
        async with self._lock:
            await self._refill()
            
            if self.tokens >= tokens:
                # Fast path: we have enough tokens
                self.tokens -= tokens
                return 0.0
            
            # Need to wait for tokens to refill
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            
            await asyncio.sleep(wait_time)
            
            # After waiting, refill and consume
            await self._refill()
            self.tokens -= tokens
            
            return wait_time


async def api_request(request_id: int, rate_limiter: TokenBucketRateLimiter):
    """
    Simulate an API request that respects rate limiting.
    
    In a real scenario, this would be hitting an external API.
    The rate limiter ensures we don't exceed our allowed request rate.
    """
    start = time.time()
    wait_time = await rate_limiter.acquire()
    
    # Simulate actual work (e.g., HTTP request)
    await asyncio.sleep(0.1)
    
    elapsed = time.time() - start
    
    if wait_time > 0:
        print(f"Request {request_id:2d}: waited {wait_time:.2f}s, "
              f"completed in {elapsed:.2f}s total")
    else:
        print(f"Request {request_id:2d}: no wait needed, "
              f"completed in {elapsed:.2f}s")


async def producer_consumer_demo():
    """
    Demo showing producer-consumer pattern with rate limiting.
    
    The producer generates requests as fast as possible, but the rate limiter
    ensures they're processed at a controlled rate. This prevents overwhelming
    downstream services.
    """
    print("=== Rate Limiter Demo ===")
    print("Config: 3 requests/sec, burst capacity of 5")
    print("Sending 10 requests as fast as possible...\n")
    
    # Allow 3 requests per second, with a burst of up to 5
    limiter = TokenBucketRateLimiter(refill_rate=3.0, max_tokens=5)
    
    start_time = time.time()
    
    # Fire off 10 requests concurrently
    tasks = [api_request(i, limiter) for i in range(10)]
    await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    print(f"\n✓ All requests completed in {total_time:.2f}s")
    print(f"  (Expected ~2.7s: 5 burst immediately, then 5 more at 3/sec)")


async def burst_test():
    """
    Show how the bucket handles burst traffic vs steady state.
    
    This demonstrates the key advantage of token bucket: you can burst
    when tokens are available, but sustained traffic is rate-limited.
    """
    print("\n\n=== Burst Behavior Test ===")
    print("First 3 requests should be instant (burst)...")
    
    limiter = TokenBucketRateLimiter(refill_rate=2.0, max_tokens=3)
    
    # Initial burst — should all go through immediately
    for i in range(3):
        wait = await limiter.acquire()
        print(f"  Request {i+1}: waited {wait:.2f}s")
    
    print("\nNow bucket is empty. Next requests wait for refill:")
    
    # These need to wait for tokens to refill
    for i in range(3):
        wait = await limiter.acquire()
        print(f"  Request {i+4}: waited {wait:.2f}s")


if __name__ == "__main__":
    # I'm using asyncio.run() here because it's the modern way to run async code.
    # It handles event loop creation/cleanup automatically.
    asyncio.run(producer_consumer_demo())
    asyncio.run(burst_test())