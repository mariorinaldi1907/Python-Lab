"""
Date: 2026-06-28
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns — demonstrates controlled throughput with multiple producers competing for limited resources.
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiterStats:
    """Track statistics for rate limiter performance."""
    total_requests: int = 0
    allowed_requests: int = 0
    throttled_requests: int = 0
    total_wait_time: float = 0.0


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens are added at a constant rate. Each request consumes one token.
    If no tokens available, the request waits until one becomes available.
    This is more flexible than a simple fixed-window counter because it allows
    bursts up to the bucket capacity while maintaining average rate over time.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (requests per second allowed)
            capacity: Maximum tokens that can accumulate (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
        self.stats = RateLimiterStats()
    
    async def _refill_tokens(self):
        """Refill tokens based on elapsed time since last update."""
        now = time.monotonic()
        elapsed = now - self.last_update
        # Add tokens proportional to time elapsed
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Returns the time spent waiting (useful for stats).
        """
        wait_start = time.monotonic()
        
        async with self.lock:
            self.stats.total_requests += 1
            
            while self.tokens < tokens:
                # Calculate how long we need to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                self.stats.throttled_requests += 1
                
                # Release lock while waiting to allow other tasks to check
                await asyncio.sleep(wait_time)
                await self._refill_tokens()
            
            # Consume tokens
            await self._refill_tokens()
            self.tokens -= tokens
            self.stats.allowed_requests += 1
        
        wait_duration = time.monotonic() - wait_start
        self.stats.total_wait_time += wait_duration
        return wait_duration


async def api_call_simulator(call_id: int, limiter: TokenBucketRateLimiter, delay: float = 0.1):
    """
    Simulate an API call that needs rate limiting.
    
    Args:
        call_id: Unique identifier for this call
        limiter: Rate limiter to use
        delay: Simulated API processing time
    """
    print(f"[Task {call_id}] Requesting token...")
    wait_time = await limiter.acquire()
    
    if wait_time > 0.01:  # Only log significant waits
        print(f"[Task {call_id}] Waited {wait_time:.3f}s for token")
    
    print(f"[Task {call_id}] Token acquired! Making API call...")
    await asyncio.sleep(delay)  # Simulate actual API call
    print(f"[Task {call_id}] API call completed")


async def producer(
    name: str,
    task_queue: asyncio.Queue,
    num_tasks: int,
    delay: float
):
    """
    Producer that generates tasks at a certain rate.
    
    Args:
        name: Producer identifier
        task_queue: Queue to put tasks into
        num_tasks: Number of tasks to produce
        delay: Delay between producing tasks
    """
    for i in range(num_tasks):
        task_id = f"{name}-{i}"
        await task_queue.put(task_id)
        print(f"[{name}] Produced task: {task_id}")
        await asyncio.sleep(delay)
    print(f"[{name}] Finished producing {num_tasks} tasks")


async def consumer(
    name: str,
    task_queue: asyncio.Queue,
    limiter: TokenBucketRateLimiter,
    stop_event: asyncio.Event
):
    """
    Consumer that processes tasks from queue with rate limiting.
    
    Args:
        name: Consumer identifier
        task_queue: Queue to consume tasks from
        limiter: Rate limiter for controlling throughput
        stop_event: Signal to stop consuming
    """
    while not stop_event.is_set() or not task_queue.empty():
        try:
            # Wait for task with timeout so we can check stop_event
            task_id = await asyncio.wait_for(task_queue.get(), timeout=0.5)
            print(f"[{name}] Processing: {task_id}")
            await limiter.acquire()
            # Simulate work
            await asyncio.sleep(0.05)
            print(f"[{name}] Completed: {task_id}")
        except asyncio.TimeoutError:
            continue
    print(f"[{name}] Stopped consuming")


async def main():
    """
    Demo the rate limiter with producer-consumer pattern.
    
    Multiple producers generate tasks faster than allowed rate.
    Multiple consumers process tasks, all sharing a rate limiter.
    """
    print("=== Async Rate Limiter Demo ===\n")
    
    # Allow 5 requests per second, burst up to 10
    limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    task_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    
    print(f"Rate limiter config: {limiter.rate} req/s, capacity: {limiter.capacity}\n")
    
    # Create producers that generate tasks quickly
    producers = [
        producer("Producer-1", task_queue, num_tasks=8, delay=0.1),
        producer("Producer-2", task_queue, num_tasks=8, delay=0.15),
    ]
    
    # Create consumers that share the rate limiter
    consumers = [
        consumer("Consumer-A", task_queue, limiter, stop_event),
        consumer("Consumer-B", task_queue, limiter, stop_event),
    ]
    
    # Run producers and consumers concurrently
    await asyncio.gather(*producers)
    print("\n[Main] All producers finished, waiting for consumers...\n")
    
    # Wait a bit for queue to drain
    await asyncio.sleep(1.0)
    stop_event.set()
    await asyncio.gather(*consumers)
    
    # Print statistics
    print("\n=== Rate Limiter Statistics ===")
    print(f"Total requests: {limiter.stats.total_requests}")
    print(f"Allowed immediately: {limiter.stats.allowed_requests}")
    print(f"Throttled (waited): {limiter.stats.throttled_requests}")
    print(f"Total wait time: {limiter.stats.total_wait_time:.3f}s")
    if limiter.stats.total_requests > 0:
        avg_wait = limiter.stats.total_wait_time / limiter.stats.total_requests
        print(f"Average wait per request: {avg_wait:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())