"""
Date: 2026-07-02
Implemented a token bucket rate limiter using asyncio to control API request rates while exploring coroutines and queue-based task distribution.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens are added at a fixed rate, and each request consumes one token.
    If no tokens are available, the request waits until one becomes available.
    This prevents bursting while still allowing some flexibility.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (requests per second)
            capacity: Maximum number of tokens that can accumulate
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire a token, blocking if necessary until one is available.
        
        This is the main method workers call before making a request.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Add tokens based on elapsed time, capped at capacity
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate how long to wait for the next token
                # This avoids busy-waiting and is more efficient
                sleep_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)


class WorkQueue:
    """
    Producer-consumer work queue with rate limiting.
    
    Producers add tasks to the queue, and consumers process them
    while respecting the rate limiter's constraints.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        """
        Initialize work queue with a rate limiter.
        
        Args:
            rate_limiter: TokenBucketRateLimiter instance to control processing rate
        """
        self.queue = asyncio.Queue()
        self.rate_limiter = rate_limiter
        self.processed_count = 0
    
    async def produce(self, task_id: int) -> None:
        """
        Add a task to the queue (producer side).
        
        Args:
            task_id: Unique identifier for the task
        """
        await self.queue.put(task_id)
        print(f"[Producer] Queued task {task_id}")
    
    async def consume(self, worker_id: int) -> None:
        """
        Process tasks from the queue with rate limiting (consumer side).
        
        Each consumer is a long-running coroutine that pulls tasks
        from the queue and processes them while respecting rate limits.
        
        Args:
            worker_id: Unique identifier for this consumer worker
        """
        while True:
            task_id = await self.queue.get()
            
            if task_id is None:  # Sentinel value to stop the worker
                self.queue.task_done()
                print(f"[Consumer {worker_id}] Shutting down")
                break
            
            # Acquire token before processing - this is where rate limiting happens
            await self.rate_limiter.acquire()
            
            # Simulate API call or expensive operation
            await asyncio.sleep(0.1)
            
            self.processed_count += 1
            print(f"[Consumer {worker_id}] Processed task {task_id} (total: {self.processed_count})")
            
            self.queue.task_done()


async def demo():
    """
    Demonstrate the rate limiter with a producer-consumer pattern.
    
    Creates multiple producers generating tasks and multiple consumers
    processing them under rate limit constraints. This simulates a
    real-world scenario like API request throttling.
    """
    print("=== Async Rate Limiter Demo ===\n")
    print("Rate limit: 5 requests/second")
    print("Burst capacity: 10 tokens")
    print("Tasks: 30 total\n")
    
    # Allow 5 requests per second with burst capacity of 10
    rate_limiter = TokenBucketRateLimiter(rate=5.0, capacity=10)
    work_queue = WorkQueue(rate_limiter)
    
    # Start consumer workers
    num_workers = 3
    consumers = [
        asyncio.create_task(work_queue.consume(worker_id))
        for worker_id in range(num_workers)
    ]
    
    # Produce tasks rapidly to demonstrate rate limiting
    start_time = time.monotonic()
    num_tasks = 30
    
    for task_id in range(num_tasks):
        await work_queue.produce(task_id)
        await asyncio.sleep(0.05)  # Produce faster than we can consume
    
    # Wait for all tasks to be processed
    await work_queue.queue.join()
    elapsed = time.monotonic() - start_time
    
    # Send sentinel values to stop workers
    for _ in range(num_workers):
        await work_queue.queue.put(None)
    
    # Wait for workers to finish
    await asyncio.gather(*consumers)
    
    print(f"\n=== Summary ===")
    print(f"Total tasks processed: {work_queue.processed_count}")
    print(f"Time elapsed: {elapsed:.2f}s")
    print(f"Effective rate: {work_queue.processed_count / elapsed:.2f} tasks/second")
    print(f"Expected rate: ~5 tasks/second (rate limit working!)")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(demo())