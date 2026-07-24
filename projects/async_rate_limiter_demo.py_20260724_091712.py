"""
Date: 2026-07-24
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns — lets you control request rates with configurable burst capacity.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Allows bursts up to bucket capacity, then enforces steady rate.
    Tokens refill at a constant rate over time.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens refilled per second (requests/sec sustained)
            capacity: Maximum tokens in bucket (max burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is where the magic happens - if we don't have enough tokens,
        we calculate exactly how long to wait before they're available.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_refill
                
                # Refill tokens based on time elapsed
                self.tokens = min(
                    self.capacity,
                    self.tokens + elapsed * self.rate
                )
                self.last_refill = now
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Not enough tokens - calculate sleep time
                # Need to wait until we have enough tokens refilled
                tokens_needed = tokens - self.tokens
                sleep_time = tokens_needed / self.rate
                
                # Release lock while sleeping so other tasks can check
                await asyncio.sleep(sleep_time)


async def make_request(
    request_id: int,
    limiter: TokenBucketRateLimiter,
    delay: Optional[float] = None
) -> None:
    """
    Simulate making a request with rate limiting.
    
    I added the delay parameter to simulate requests coming in
    at different times - makes the demo more realistic.
    """
    if delay:
        await asyncio.sleep(delay)
    
    start = time.time()
    await limiter.acquire()
    elapsed = time.time() - start
    
    print(f"Request {request_id:2d} | waited {elapsed:.3f}s | "
          f"completed at t={time.time() - demo_start:.3f}s")


async def burst_then_sustained_demo():
    """
    Demo showing burst handling followed by sustained rate limiting.
    
    This pattern is common in real APIs - you want to allow quick bursts
    but prevent sustained abuse.
    """
    print("=== Burst + Sustained Demo ===")
    print("Rate: 5 req/s, Capacity: 10 tokens\n")
    
    # 5 requests per second sustained, 10 token bucket
    limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    
    tasks = []
    
    # First 10 should go through immediately (burst)
    print("Sending 10 requests immediately (burst):")
    for i in range(10):
        tasks.append(make_request(i, limiter))
    
    # Then 10 more that will be rate limited
    print("\nSending 10 more requests (should be throttled):")
    for i in range(10, 20):
        tasks.append(make_request(i, limiter, delay=0.1))
    
    await asyncio.gather(*tasks)


async def producer_consumer_demo():
    """
    Producer-consumer pattern with rate-limited producer.
    
    The producer generates items quickly but rate limiter ensures
    they're "sent" at a controlled pace. Consumer processes freely.
    """
    print("\n\n=== Producer-Consumer with Rate Limiting ===")
    print("Producer rate: 3 items/s\n")
    
    limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    queue = asyncio.Queue(maxsize=10)
    
    async def producer():
        """Produce items at a rate-limited pace."""
        for i in range(15):
            await limiter.acquire()
            await queue.put(i)
            print(f"Produced item {i:2d} at t={time.time() - demo_start:.3f}s")
        
        await queue.put(None)  # Sentinel to stop consumer
    
    async def consumer():
        """Consume items as fast as they arrive."""
        while True:
            item = await queue.get()
            if item is None:
                break
            
            # Simulate some processing time
            await asyncio.sleep(0.05)
            print(f"  Consumed item {item:2d}")
    
    await asyncio.gather(
        producer(),
        consumer()
    )


async def main():
    """
    Run both demos to show different use cases.
    
    I wanted to show that rate limiting isn't just for external APIs -
    it's useful for any resource constraint scenario.
    """
    global demo_start
    demo_start = time.time()
    
    await burst_then_sustained_demo()
    await producer_consumer_demo()
    
    print(f"\n✓ All demos completed in {time.time() - demo_start:.2f}s")


if __name__ == "__main__":
    # Using asyncio.run() because it's the modern way and handles
    # event loop cleanup automatically
    asyncio.run(main())