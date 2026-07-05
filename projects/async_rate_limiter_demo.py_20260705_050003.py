"""
Date: 2026-07-05
Implemented a token bucket rate limiter using asyncio to demo how to throttle concurrent operations without blocking the event loop.
"""

"""
Async Rate Limiter using Token Bucket Algorithm

This demonstrates how to build a simple but effective rate limiter that can
throttle async operations. I use this pattern a lot when hitting external APIs
that have rate limits — better to handle it gracefully than get 429'd.

The token bucket refills at a steady rate, and tasks consume tokens before
proceeding. If no tokens available, they wait until the bucket refills.
"""

import asyncio
import time
from typing import Optional


class AsyncTokenBucket:
    """
    Token bucket rate limiter for async operations.
    
    Tokens refill at a constant rate (refill_rate per second).
    Each operation consumes one token. If bucket is empty, callers wait.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the token bucket.
        
        Args:
            capacity: Max tokens the bucket can hold
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the main method tasks call before doing rate-limited work.
        """
        while True:
            async with self._lock:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long until we have enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
            
            # Sleep outside the lock so other tasks can check too
            await asyncio.sleep(wait_time)
    
    async def _refill(self) -> None:
        """
        Refill tokens based on elapsed time since last refill.
        
        Called internally before each acquire attempt. This is where the
        "steady drip" of new tokens happens.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Add tokens based on time passed
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now


async def api_call(call_id: int, limiter: AsyncTokenBucket, delay: float = 0.1) -> str:
    """
    Simulate an API call that needs rate limiting.
    
    In real life this would be an aiohttp request or similar.
    """
    # Wait for rate limiter to allow us through
    await limiter.acquire()
    
    start = time.monotonic()
    print(f"[{start:.2f}] API call #{call_id} started")
    
    # Simulate actual work
    await asyncio.sleep(delay)
    
    end = time.monotonic()
    print(f"[{end:.2f}] API call #{call_id} completed")
    
    return f"Result from call {call_id}"


async def producer_consumer_demo():
    """
    Demo showing rate limiter in a producer-consumer style pattern.
    
    Producer generates tasks quickly, but rate limiter ensures we don't
    actually hit the "API" too fast. This is realistic — often you have
    a queue of work but need to throttle execution.
    """
    print("=== Rate Limiter Demo ===")
    print("Creating token bucket: 3 tokens capacity, 2 tokens/sec refill rate")
    print("This means max 2 requests per second sustained, with burst of 3\n")
    
    # Allow bursts of 3, but sustained rate of 2 per second
    limiter = AsyncTokenBucket(capacity=3, refill_rate=2.0)
    
    # Create a bunch of tasks all at once (the "producer" part)
    tasks = []
    num_calls = 8
    
    print(f"Launching {num_calls} API calls simultaneously...\n")
    
    for i in range(num_calls):
        task = asyncio.create_task(api_call(i, limiter))
        tasks.append(task)
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    print("\n=== All calls completed ===")
    print(f"Total results: {len(results)}")
    print("\nNotice how the first 3 went through immediately (burst capacity),")
    print("then the rest throttled to ~2 per second (refill rate)")


async def main():
    """
    Main entry point for the demo.
    
    I could've added more patterns here (like multiple producers with
    different priorities) but wanted to keep it focused on the core
    rate limiting concept.
    """
    await producer_consumer_demo()


if __name__ == "__main__":
    # Run the async demo
    # On Windows you might need to use asyncio.set_event_loop_policy()
    # if you get weird errors, but works fine on Linux/Mac
    asyncio.run(main())