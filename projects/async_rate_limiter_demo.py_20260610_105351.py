"""
Date: 2026-06-10
Implemented a token bucket rate limiter with asyncio to throttle concurrent API calls — wanted to see how the refill mechanism works in practice.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Tokens refill at a constant rate, and each request consumes one token.
    If no tokens are available, requests wait until tokens are replenished.
    This smooths out bursts while allowing sustained throughput.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Number of tokens added per second
            capacity: Maximum tokens that can be stored (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        This is called before each acquire attempt to ensure tokens
        are current. Uses monotonic time to avoid clock adjustments.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate how many tokens to add based on elapsed time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            Time spent waiting for tokens
        """
        async with self._lock:
            await self._refill()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
                await asyncio.sleep(wait_time)
                await self._refill()
            
            # Now we definitely have enough tokens
            self.tokens -= tokens
            return 0 if self.tokens >= tokens else wait_time


async def simulate_api_call(call_id: int, delay: float = 0.1) -> dict:
    """
    Simulate an API call that takes some time to complete.
    
    Args:
        call_id: Identifier for this call
        delay: Simulated network latency
        
    Returns:
        Fake API response with call details
    """
    await asyncio.sleep(delay)
    return {
        "id": call_id,
        "status": "success",
        "timestamp": time.time()
    }


async def worker(
    worker_id: int,
    rate_limiter: TokenBucketRateLimiter,
    num_requests: int
):
    """
    Worker coroutine that makes rate-limited API calls.
    
    Each worker tries to make multiple requests but must respect
    the shared rate limiter. This demonstrates how multiple coroutines
    can coordinate through a single rate limiter instance.
    
    Args:
        worker_id: Identifier for this worker
        rate_limiter: Shared rate limiter instance
        num_requests: Number of requests this worker should make
    """
    print(f"[Worker {worker_id}] Starting with {num_requests} requests to make")
    
    for i in range(num_requests):
        # Acquire permission from rate limiter
        start = time.monotonic()
        await rate_limiter.acquire()
        wait_time = time.monotonic() - start
        
        # Make the actual API call
        result = await simulate_api_call(i)
        
        status = "⏱️  waited" if wait_time > 0.01 else "✓ immediate"
        print(
            f"[Worker {worker_id}] Request {i+1}/{num_requests} - {status} "
            f"({wait_time:.3f}s wait) - Response: {result['status']}"
        )
    
    print(f"[Worker {worker_id}] ✅ Completed all requests")


async def demo_rate_limiter():
    """
    Demonstrate the rate limiter with multiple concurrent workers.
    
    We spin up several workers that all try to make requests at once.
    The rate limiter ensures they don't exceed the configured rate,
    even though they're all running concurrently.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    # Allow 3 requests per second, with burst capacity of 5
    # This means we can handle a burst of 5 immediate requests,
    # then sustained rate of 3/sec after that
    rate_limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    
    print(f"Rate limiter config: {rate_limiter.rate} req/sec, "
          f"burst capacity: {rate_limiter.capacity}\n")
    
    # Create 3 workers that will each make 4 requests
    # Total: 12 requests competing for rate-limited access
    workers = [
        worker(worker_id=i, rate_limiter=rate_limiter, num_requests=4)
        for i in range(3)
    ]
    
    start_time = time.monotonic()
    await asyncio.gather(*workers)
    total_time = time.monotonic() - start_time
    
    print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")
    print(f"📊 Effective rate: {12 / total_time:.2f} requests/second")
    print("\nNote: First 5 requests should be immediate (burst), rest throttled.")


if __name__ == "__main__":
    # Run the demo
    # You should see the first few requests go through immediately
    # (up to the burst capacity), then subsequent requests get
    # rate limited to maintain the configured rate
    asyncio.run(demo_rate_limiter())