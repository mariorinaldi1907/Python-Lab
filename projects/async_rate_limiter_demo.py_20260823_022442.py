"""
Date: 2026-08-23
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns and throttling multiple concurrent tasks.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    A token bucket rate limiter for async tasks.
    
    Tokens replenish at a steady rate (rate per second). Tasks consume tokens
    when they run. If no tokens are available, tasks wait until replenishment.
    This allows bursts up to capacity while maintaining average throughput.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 means 5 requests/sec)
            capacity: Maximum tokens in bucket (allows bursts)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity  # Start with a full bucket
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last update.
        
        This is where the "leaky bucket" math happens — we add tokens
        proportional to time passed, capped at capacity.
        """
        now = time.monotonic()
        elapsed = now - self.last_update
        
        # Calculate new tokens based on elapsed time
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            The wait time in seconds (0 if no wait needed)
        """
        async with self._lock:
            await self._refill()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate
                
                # Actually wait for the tokens to replenish
                await asyncio.sleep(wait_time)
                await self._refill()
            
            # Consume the tokens
            self.tokens -= tokens
            return 0 if self.tokens >= 0 else abs(self.tokens) / self.rate


async def api_request(request_id: int, limiter: TokenBucketRateLimiter, cost: int = 1):
    """
    Simulate an API request with rate limiting.
    
    Each request must acquire tokens before proceeding. This mimics
    a real-world scenario where you're calling an external API with limits.
    """
    start = time.monotonic()
    
    print(f"[Request {request_id}] Waiting for rate limiter...")
    await limiter.acquire(tokens=cost)
    
    # Simulate actual API work
    await asyncio.sleep(0.1)
    
    elapsed = time.monotonic() - start
    print(f"[Request {request_id}] Completed in {elapsed:.2f}s (cost: {cost} tokens)")


async def producer(queue: asyncio.Queue, num_tasks: int):
    """
    Producer: generates tasks and puts them in the queue.
    
    In a real scenario, this might be reading from a file,
    receiving webhooks, or pulling from a database.
    """
    print(f"\n[Producer] Starting to generate {num_tasks} tasks...")
    
    for i in range(num_tasks):
        # Some tasks cost more tokens (e.g., expensive operations)
        cost = 2 if i % 5 == 0 else 1
        await queue.put((i, cost))
        await asyncio.sleep(0.05)  # Simulate tasks arriving over time
    
    print("[Producer] All tasks generated, signaling completion")
    await queue.put(None)  # Sentinel value to signal completion


async def consumer(
    consumer_id: int,
    queue: asyncio.Queue,
    limiter: TokenBucketRateLimiter
):
    """
    Consumer: processes tasks from the queue with rate limiting.
    
    Multiple consumers can run concurrently, all sharing the same
    rate limiter to respect global throughput constraints.
    """
    print(f"[Consumer {consumer_id}] Starting up")
    
    while True:
        item = await queue.get()
        
        if item is None:
            # Put sentinel back for other consumers
            await queue.put(None)
            break
        
        request_id, cost = item
        await api_request(f"{consumer_id}-{request_id}", limiter, cost)
        queue.task_done()
    
    print(f"[Consumer {consumer_id}] Shutting down")


async def main():
    """
    Demo the rate limiter with a producer-consumer pattern.
    
    I'm setting up a scenario where tasks arrive faster than we can
    process them (due to rate limiting), showing how the limiter
    smooths out the traffic.
    """
    print("=== Async Rate Limiter Demo ===")
    print("Simulating API calls with 3 requests/sec limit, burst capacity of 5\n")
    
    # Rate limiter: 3 tokens/sec, max 5 tokens (allows small bursts)
    limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    
    # Shared queue for work items
    queue = asyncio.Queue()
    
    # Start timing
    start_time = time.monotonic()
    
    # Kick off producer and multiple consumers
    producers = [asyncio.create_task(producer(queue, num_tasks=15))]
    consumers = [
        asyncio.create_task(consumer(i, queue, limiter))
        for i in range(3)
    ]
    
    # Wait for all tasks to complete
    await asyncio.gather(*producers)
    await queue.join()
    
    # Consumers will exit when they see the sentinel
    await asyncio.gather(*consumers)
    
    elapsed = time.monotonic() - start_time
    print(f"\n=== Demo completed in {elapsed:.2f}s ===")
    print("Notice how requests were throttled to respect the rate limit!")


if __name__ == "__main__":
    # Running the async demo — watch how the rate limiter
    # controls the flow even with multiple concurrent consumers
    asyncio.run(main())