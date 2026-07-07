"""
Date: 2026-07-07
Implemented a token bucket rate limiter using asyncio to demonstrate controlled concurrency — useful pattern I keep needing for API clients.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter - refills tokens at a steady rate.
    
    The idea: you have a bucket that holds tokens. Each operation costs one token.
    Tokens refill at a constant rate. If bucket is empty, you wait.
    This smooths out bursts while allowing occasional spikes within capacity.
    """
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the bucket.
        
        Args:
            capacity: Max tokens the bucket can hold
            refill_rate: How many tokens we add per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity  # start full
        self.last_refill = time.monotonic()

    def _refill(self):
        """Add tokens based on time elapsed since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        # Calculate how many tokens to add based on elapsed time
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the core rate limiting logic - if we don't have enough tokens,
        we calculate how long to wait for them to refill.
        """
        while True:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return
            
            # Not enough tokens - calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            await asyncio.sleep(wait_time)


class RateLimitedWorker:
    """
    Worker that processes tasks with rate limiting.
    
    I wanted to simulate something like an API client that needs to respect
    rate limits - e.g., "no more than 5 requests per second".
    """
    
    def __init__(self, worker_id: int, rate_limiter: TokenBucket):
        """
        Create a worker.
        
        Args:
            worker_id: Identifier for logging
            rate_limiter: Shared rate limiter across all workers
        """
        self.worker_id = worker_id
        self.rate_limiter = rate_limiter
        self.tasks_completed = 0

    async def process_task(self, task_id: int) -> None:
        """
        Process a single task with rate limiting.
        
        In a real scenario, this might be an HTTP request, database query, etc.
        The rate limiter ensures we don't hammer the resource too hard.
        """
        # Acquire token before proceeding - this is where rate limiting happens
        await self.rate_limiter.acquire()
        
        start_time = time.time()
        print(f"[Worker {self.worker_id}] Starting task {task_id} at {start_time:.2f}s")
        
        # Simulate some work (like an API call)
        await asyncio.sleep(0.1)
        
        self.tasks_completed += 1
        elapsed = time.time() - start_time
        print(f"[Worker {self.worker_id}] Completed task {task_id} in {elapsed:.2f}s")

    async def run(self, num_tasks: int) -> None:
        """Run multiple tasks sequentially."""
        for task_id in range(num_tasks):
            await self.process_task(task_id)


async def main():
    """
    Demo the rate limiter with multiple concurrent workers.
    
    Setup: 3 workers, each trying to do 4 tasks = 12 total tasks
    Rate limit: 5 tokens per second, bucket capacity of 10
    
    Watch how the tasks get spread out over time due to rate limiting.
    Without the limiter, all 12 tasks would start nearly instantly.
    """
    print("=== Async Rate Limiter Demo ===")
    print("Rate limit: 5 tasks/second (bucket capacity: 10)")
    print("Workers: 3, Tasks per worker: 4\n")
    
    # Shared rate limiter - this is the key to coordinated rate limiting
    # All workers share the same bucket, so they collectively respect the limit
    rate_limiter = TokenBucket(capacity=10, refill_rate=5.0)
    
    # Create workers
    workers = [
        RateLimitedWorker(worker_id=i, rate_limiter=rate_limiter)
        for i in range(3)
    ]
    
    # Start all workers concurrently
    start_time = time.time()
    await asyncio.gather(*[worker.run(num_tasks=4) for worker in workers])
    total_time = time.time() - start_time
    
    # Stats
    print("\n=== Results ===")
    total_tasks = sum(w.tasks_completed for w in workers)
    print(f"Total tasks completed: {total_tasks}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average rate: {total_tasks / total_time:.2f} tasks/second")
    print("\nNotice how tasks are spread out to respect the 5 tasks/second limit!")
    print("The first 10 start quickly (bucket capacity), then throttling kicks in.")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())