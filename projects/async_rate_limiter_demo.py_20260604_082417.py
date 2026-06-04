"""
Date: 2026-06-04
Implemented a token bucket rate limiter using asyncio to explore controlled concurrency — supports burst handling and demonstrates multiple workers competing for limited resources.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Allows bursts up to capacity, then refills at a steady rate.
    I went with this over a simple counter because it handles bursty
    workloads more realistically — like API rate limits do.
    """
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def _refill(self):
        """Add tokens based on elapsed time since last refill."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens. Waits if not enough tokens available.
        
        Returns True when tokens are acquired. This is async so other
        coroutines can run while we're waiting for refill.
        """
        while True:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            # Not enough tokens, wait a bit before checking again
            # Calculate how long until we'd have enough
            deficit = tokens - self.tokens
            wait_time = deficit / self.refill_rate
            await asyncio.sleep(wait_time)


class RateLimitedWorker:
    """
    Worker that processes tasks with rate limiting.
    
    This simulates something like making API calls where you have
    a rate limit to respect. Each worker competes for tokens from
    the shared bucket.
    """
    
    def __init__(self, worker_id: int, bucket: TokenBucket):
        self.worker_id = worker_id
        self.bucket = bucket
        self.tasks_completed = 0
    
    async def process_task(self, task_id: int):
        """
        Simulate processing a task that requires rate limiting.
        
        I'm using a small sleep to simulate actual work being done.
        """
        print(f"[Worker {self.worker_id}] Requesting token for task {task_id}...")
        await self.bucket.acquire(tokens=1)
        
        print(f"[Worker {self.worker_id}] Got token! Processing task {task_id}")
        await asyncio.sleep(0.1)  # Simulate work
        
        self.tasks_completed += 1
        print(f"[Worker {self.worker_id}] Completed task {task_id}")
    
    async def run(self, num_tasks: int):
        """Run a series of tasks through the rate limiter."""
        for i in range(num_tasks):
            await self.process_task(i)


async def demo_burst_handling(bucket: TokenBucket):
    """
    Demonstrate burst handling capability.
    
    Shows how the token bucket allows a burst of requests up to
    capacity, then enforces the steady refill rate.
    """
    print("\n=== Burst Handling Demo ===")
    print(f"Bucket: {bucket.capacity} tokens, {bucket.refill_rate} tokens/sec\n")
    
    start = time.time()
    
    # Try to process 5 tasks quickly (burst)
    for i in range(5):
        await bucket.acquire()
        elapsed = time.time() - start
        print(f"Task {i+1} acquired token at {elapsed:.2f}s")
    
    print("\nNotice: First 3 went fast (burst), then rate limiting kicked in\n")


async def demo_multiple_workers(num_workers: int, tasks_per_worker: int):
    """
    Demonstrate multiple workers competing for rate-limited resources.
    
    This is the realistic scenario — multiple coroutines all trying
    to use the same rate-limited resource (like an API).
    """
    print("\n=== Multiple Workers Demo ===")
    
    # Create a shared bucket: 3 tokens capacity, refills at 2 tokens/sec
    # This means sustained throughput of 2 requests/sec, but can burst to 3
    bucket = TokenBucket(capacity=3, refill_rate=2.0)
    
    print(f"Starting {num_workers} workers, {tasks_per_worker} tasks each")
    print(f"Rate limit: {bucket.refill_rate} requests/sec (burst: {bucket.capacity})\n")
    
    workers = [RateLimitedWorker(i, bucket) for i in range(num_workers)]
    
    start = time.time()
    
    # Run all workers concurrently
    await asyncio.gather(*[w.run(tasks_per_worker) for w in workers])
    
    elapsed = time.time() - start
    total_tasks = sum(w.tasks_completed for w in workers)
    
    print(f"\n=== Results ===")
    print(f"Total tasks: {total_tasks}")
    print(f"Time taken: {elapsed:.2f}s")
    print(f"Actual throughput: {total_tasks/elapsed:.2f} tasks/sec")
    print(f"(Expected ~{bucket.refill_rate:.2f} tasks/sec due to rate limit)")


async def main():
    """
    Run the demos.
    
    I structured this to show two aspects: burst handling and
    multi-worker concurrency. Both are important for understanding
    how rate limiters work in practice.
    """
    # First demo: show burst behavior
    burst_bucket = TokenBucket(capacity=3, refill_rate=1.0)
    await demo_burst_handling(burst_bucket)
    
    await asyncio.sleep(1)  # Pause between demos
    
    # Second demo: multiple workers competing
    await demo_multiple_workers(num_workers=3, tasks_per_worker=4)


if __name__ == "__main__":
    print("Async Rate Limiter Demo")
    print("Token bucket algorithm with asyncio\n")
    
    asyncio.run(main())