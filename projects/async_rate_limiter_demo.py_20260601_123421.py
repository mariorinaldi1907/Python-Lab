"""
Date: 2026-06-01
Implemented a token bucket rate limiter using asyncio to demonstrate controlled concurrency with bursting — useful for API calls or resource throttling.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter that allows bursts up to capacity.
    
    Tokens refill at a constant rate. Each operation consumes one token.
    If no tokens available, the caller waits until one becomes available.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 means 5 operations/sec)
            capacity: Maximum tokens that can accumulate (allows bursts)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)  # Start with full bucket
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time since last update."""
        now = time.monotonic()
        elapsed = now - self.last_update
        # Add tokens proportional to time elapsed
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
    
    async def acquire(self) -> None:
        """
        Acquire a token, waiting if necessary.
        
        This method will block until a token becomes available.
        """
        async with self._lock:
            while True:
                self._refill()
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate how long to wait for next token
                deficit = 1.0 - self.tokens
                wait_time = deficit / self.rate
                
                # Release lock while waiting so other coroutines can check
                await asyncio.sleep(wait_time)


class RateLimitedWorker:
    """
    Worker that processes tasks with rate limiting.
    
    Simulates an API client or resource-intensive worker that needs throttling.
    """
    
    def __init__(self, worker_id: int, rate_limiter: TokenBucketRateLimiter):
        """
        Initialize worker.
        
        Args:
            worker_id: Unique identifier for this worker
            rate_limiter: Shared rate limiter instance
        """
        self.worker_id = worker_id
        self.rate_limiter = rate_limiter
        self.completed_tasks = 0
    
    async def process_task(self, task_id: int) -> None:
        """
        Process a single task with rate limiting.
        
        Args:
            task_id: Task identifier
        """
        # Wait for rate limiter permission
        await self.rate_limiter.acquire()
        
        # Simulate work (e.g., API call)
        print(f"[{time.strftime('%H:%M:%S')}] Worker {self.worker_id} processing task {task_id}")
        await asyncio.sleep(0.1)  # Simulate actual work
        
        self.completed_tasks += 1
    
    async def run(self, num_tasks: int) -> None:
        """
        Run multiple tasks through the rate limiter.
        
        Args:
            num_tasks: Number of tasks to process
        """
        tasks = [self.process_task(i) for i in range(num_tasks)]
        await asyncio.gather(*tasks)
        print(f"Worker {self.worker_id} completed {self.completed_tasks} tasks")


async def demonstrate_rate_limiting():
    """
    Demonstrate the rate limiter with multiple concurrent workers.
    
    Shows how the token bucket allows bursts but maintains average rate.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    # Create rate limiter: 3 operations/sec, burst capacity of 5
    # This means we can do 5 ops instantly, then throttle to 3/sec
    rate_limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    
    print("Rate limiter configured:")
    print(f"  - Rate: {rate_limiter.rate} operations/second")
    print(f"  - Burst capacity: {rate_limiter.capacity} tokens")
    print(f"  - Workers: 3")
    print(f"  - Tasks per worker: 4\n")
    
    print("Starting workers (watch the timestamps)...\n")
    start_time = time.monotonic()
    
    # Create multiple workers sharing the same rate limiter
    # This simulates multiple API clients sharing a rate limit
    workers = [
        RateLimitedWorker(worker_id=i, rate_limiter=rate_limiter)
        for i in range(3)
    ]
    
    # Each worker tries to process 4 tasks
    # Total: 12 tasks, but rate limited to ~3/sec after initial burst
    await asyncio.gather(*[worker.run(num_tasks=4) for worker in workers])
    
    elapsed = time.monotonic() - start_time
    print(f"\n=== Summary ===")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Total tasks: 12")
    print(f"Effective rate: {12 / elapsed:.2f} tasks/second")
    print("\nNotice how the first 5 tasks execute quickly (burst),")
    print("then the rest are throttled to ~3 per second.")


if __name__ == "__main__":
    # Run the demo
    # You'll see the first few tasks execute immediately (using burst capacity)
    # Then subsequent tasks are rate-limited to the configured rate
    asyncio.run(demonstrate_rate_limiting())