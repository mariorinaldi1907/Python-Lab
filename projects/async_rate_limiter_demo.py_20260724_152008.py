"""
Date: 2026-07-24
Implemented a token bucket rate limiter using asyncio to explore how to throttle concurrent tasks without blocking everything — includes a realistic API request simulator.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens refill at a constant rate. Each operation consumes one token.
    If no tokens available, the caller waits until one becomes available.
    This prevents bursting beyond the specified rate while allowing some flexibility.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens per second to add to the bucket
            capacity: Maximum tokens the bucket can hold (allows bursting)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire a token, waiting if necessary.
        
        This refills tokens based on elapsed time, then waits if we're empty.
        The algorithm ensures smooth rate limiting without hard blocking.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_refill
                
                # Refill tokens based on time elapsed
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_refill = now
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                
                # Calculate how long to wait for the next token
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)


class AsyncProducerConsumer:
    """
    Producer-consumer pattern with rate limiting.
    
    Producers generate tasks and put them in a queue. Consumers process tasks
    from the queue with rate limiting to simulate real-world API constraints.
    """
    
    def __init__(self, rate_limit: float, max_queue_size: int = 50):
        """
        Initialize the producer-consumer system.
        
        Args:
            rate_limit: Maximum requests per second for consumers
            max_queue_size: Queue capacity (creates backpressure when full)
        """
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.rate_limiter = TokenBucketRateLimiter(rate=rate_limit, capacity=10)
        self.results = deque(maxlen=100)
        self.running = True
    
    async def producer(self, producer_id: int, num_items: int, delay: float):
        """
        Produce items at a specified rate.
        
        Args:
            producer_id: Identifier for this producer
            num_items: Total items to produce
            delay: Seconds between productions
        """
        for i in range(num_items):
            if not self.running:
                break
            
            item = f"P{producer_id}-Item{i}"
            await self.queue.put(item)
            print(f"[Producer {producer_id}] Produced: {item} (queue size: {self.queue.qsize()})")
            
            await asyncio.sleep(delay)
        
        print(f"[Producer {producer_id}] Finished producing")
    
    async def consumer(self, consumer_id: int):
        """
        Consume items from the queue with rate limiting.
        
        This simulates making API requests that must respect rate limits.
        Each item processing is throttled by the rate limiter.
        """
        while self.running:
            try:
                # Wait for an item with timeout so we can check self.running
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Rate limit the processing (simulate API call throttling)
                await self.rate_limiter.acquire()
                
                # Simulate some processing time
                await asyncio.sleep(0.1)
                
                result = f"{item} -> processed by C{consumer_id}"
                self.results.append(result)
                print(f"[Consumer {consumer_id}] Processed: {result}")
                
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # No item available, check if we should continue
                if self.queue.empty() and not self.running:
                    break
                continue
        
        print(f"[Consumer {consumer_id}] Shutting down")
    
    async def run(self, num_producers: int, num_consumers: int, items_per_producer: int):
        """
        Run the producer-consumer demo.
        
        Args:
            num_producers: Number of producer coroutines
            num_consumers: Number of consumer coroutines
            items_per_producer: Items each producer will create
        """
        # Start producers (they produce quickly to demonstrate backpressure)
        producers = [
            asyncio.create_task(self.producer(i, items_per_producer, delay=0.05))
            for i in range(num_producers)
        ]
        
        # Start consumers (they're rate-limited to show throttling)
        consumers = [
            asyncio.create_task(self.consumer(i))
            for i in range(num_consumers)
        ]
        
        # Wait for all producers to finish
        await asyncio.gather(*producers)
        
        # Wait for queue to be processed
        await self.queue.join()
        
        # Signal consumers to stop
        self.running = False
        
        # Wait for consumers to finish
        await asyncio.gather(*consumers, return_exceptions=True)
        
        print(f"\n{'='*60}")
        print(f"Demo complete! Processed {len(self.results)} items total")
        print(f"{'='*60}")


async def main():
    """
    Demo the rate-limited producer-consumer pattern.
    
    This simulates a realistic scenario: multiple data sources producing items
    faster than we can process them (due to API rate limits), demonstrating
    how the queue provides backpressure and the rate limiter smooths output.
    """
    print("Starting async rate-limited producer-consumer demo...")
    print("=" * 60)
    print("Scenario: 2 fast producers, 2 rate-limited consumers (5 req/sec)")
    print("=" * 60)
    
    system = AsyncProducerConsumer(rate_limit=5.0, max_queue_size=10)
    
    await system.run(
        num_producers=2,
        num_consumers=2,
        items_per_producer=8
    )


if __name__ == "__main__":
    asyncio.run(main())