"""
Date: 2026-06-01
Implemented a token bucket rate limiter using asyncio to demonstrate how to throttle concurrent requests without blocking — useful for API integrations.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens are added at a fixed rate. Each request consumes one token.
    If no tokens are available, the request waits until one becomes available.
    This prevents bursts from overwhelming downstream services.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 means 5 requests/sec)
            capacity: Maximum tokens that can accumulate (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire a token, waiting if necessary.
        
        This refills tokens based on elapsed time, then waits until
        at least one token is available. I chose monotonic time to avoid
        issues with system clock adjustments.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                
                # Refill tokens based on time elapsed
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate how long until next token is available
                # This prevents busy-waiting and is more efficient
                sleep_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)


class AsyncWorker:
    """
    Simulated worker that makes async "API calls" with rate limiting.
    
    Each worker processes items from a queue and respects the rate limiter,
    demonstrating how multiple concurrent tasks can share a limited resource.
    """
    
    def __init__(self, worker_id: int, rate_limiter: TokenBucketRateLimiter, queue: asyncio.Queue):
        """
        Initialize a worker.
        
        Args:
            worker_id: Unique identifier for logging
            rate_limiter: Shared rate limiter instance
            queue: Queue to pull work items from
        """
        self.worker_id = worker_id
        self.rate_limiter = rate_limiter
        self.queue = queue
        self.processed = 0
    
    async def process_item(self, item: str) -> None:
        """
        Simulate processing an item with an API call.
        
        This is where the rate limiting happens — we acquire a token before
        "calling the API" to ensure we don't exceed our rate limit.
        """
        await self.rate_limiter.acquire()
        
        # Simulate API call with random latency
        await asyncio.sleep(0.1)
        
        self.processed += 1
        print(f"[Worker {self.worker_id}] Processed: {item} (total: {self.processed})")
    
    async def run(self) -> None:
        """
        Main worker loop — pulls items from queue until None is received.
        """
        while True:
            item = await self.queue.get()
            
            if item is None:
                # Sentinel value to signal shutdown
                self.queue.task_done()
                break
            
            try:
                await self.process_item(item)
            finally:
                self.queue.task_done()
        
        print(f"[Worker {self.worker_id}] Shutting down after processing {self.processed} items")


async def producer(queue: asyncio.Queue, num_items: int) -> None:
    """
    Producer that adds work items to the queue.
    
    In a real scenario, this might be reading from a database, file,
    or listening to a message queue. Here I'm just generating numbered tasks.
    """
    print(f"[Producer] Adding {num_items} items to queue...")
    
    for i in range(num_items):
        item = f"task-{i+1:03d}"
        await queue.put(item)
        await asyncio.sleep(0.01)  # Small delay to simulate realistic production
    
    print("[Producer] Finished adding items")


async def main():
    """
    Demo of the rate limiter with multiple concurrent workers.
    
    I'm setting up 3 workers sharing a rate limiter that allows 5 requests/sec.
    This demonstrates how the token bucket prevents all workers from overwhelming
    a downstream service, even though they're all trying to work concurrently.
    """
    # Configuration
    RATE_LIMIT = 5.0  # requests per second
    BURST_CAPACITY = 8  # allow small bursts
    NUM_WORKERS = 3
    NUM_ITEMS = 20
    
    print(f"=== Async Rate Limiter Demo ===")
    print(f"Rate limit: {RATE_LIMIT} req/sec, Burst: {BURST_CAPACITY}")
    print(f"Workers: {NUM_WORKERS}, Items: {NUM_ITEMS}\n")
    
    # Shared queue and rate limiter
    queue = asyncio.Queue()
    rate_limiter = TokenBucketRateLimiter(rate=RATE_LIMIT, capacity=BURST_CAPACITY)
    
    # Start producer
    producer_task = asyncio.create_task(producer(queue, NUM_ITEMS))
    
    # Start workers
    workers = [
        AsyncWorker(worker_id=i+1, rate_limiter=rate_limiter, queue=queue)
        for i in range(NUM_WORKERS)
    ]
    worker_tasks = [asyncio.create_task(worker.run()) for worker in workers]
    
    # Wait for producer to finish
    await producer_task
    
    # Wait for queue to be fully processed
    await queue.join()
    
    # Send shutdown signal to workers
    for _ in range(NUM_WORKERS):
        await queue.put(None)
    
    # Wait for all workers to shut down
    await asyncio.gather(*worker_tasks)
    
    total_processed = sum(w.processed for w in workers)
    print(f"\n=== Summary ===")
    print(f"Total processed: {total_processed}/{NUM_ITEMS}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.2f} seconds")