"""
Date: 2026-06-20
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns and demonstrate how to throttle API calls or worker tasks.
"""

"""
Async Rate Limiter Demo - Token Bucket Pattern

I built this to understand rate limiting better, especially for scenarios where
you need to make a bunch of API calls but don't want to hammer the server.
The token bucket algorithm is nice because it allows bursts while still
maintaining an average rate limit.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import List


@dataclass
class RateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Tokens refill at a constant rate up to max_tokens. Each operation
    consumes one token. If no tokens available, the operation waits.
    """
    rate: float  # tokens per second
    max_tokens: int  # bucket capacity
    
    def __post_init__(self):
        """Initialize the token bucket."""
        self.tokens = self.max_tokens
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire a token, waiting if necessary.
        
        This refills tokens based on elapsed time, then consumes one.
        If no tokens are available, we wait until one is ready.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_refill
                
                # Refill tokens based on time elapsed
                self.tokens = min(
                    self.max_tokens,
                    self.tokens + elapsed * self.rate
                )
                self.last_refill = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate how long until next token is available
                wait_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)


class APIWorker:
    """
    Simulates a worker making rate-limited API calls.
    
    I wanted to show a realistic use case where multiple workers share
    a rate limiter to avoid overwhelming an external service.
    """
    
    def __init__(self, worker_id: int, limiter: RateLimiter):
        """Initialize worker with an ID and shared rate limiter."""
        self.worker_id = worker_id
        self.limiter = limiter
        self.calls_made = 0
    
    async def make_api_call(self, request_id: int):
        """
        Simulate an API call with rate limiting.
        
        The actual "work" here is trivial, but in real life this would be
        an HTTP request or database query that you want to throttle.
        """
        await self.limiter.acquire()
        
        start_time = time.monotonic()
        # Simulate API call taking some time
        await asyncio.sleep(0.1)
        
        self.calls_made += 1
        print(
            f"[Worker {self.worker_id}] Request {request_id} completed "
            f"at {start_time:.2f}s (total calls: {self.calls_made})"
        )
    
    async def run_batch(self, num_requests: int):
        """Execute a batch of requests with rate limiting."""
        tasks = [
            self.make_api_call(i) 
            for i in range(num_requests)
        ]
        await asyncio.gather(*tasks)


async def demo_rate_limiter():
    """
    Demonstrate the rate limiter with multiple concurrent workers.
    
    This creates a scenario where 3 workers each try to make 5 requests.
    Without rate limiting, all 15 would fire immediately. With the limiter
    set to 5 tokens/sec with a burst of 3, you'll see the throttling in action.
    """
    print("=== Async Rate Limiter Demo ===\n")
    print("Creating rate limiter: 5 requests/sec, burst capacity of 3")
    print("Spawning 3 workers, each making 5 requests\n")
    
    # Rate limiter allows 5 requests per second with a burst of 3
    limiter = RateLimiter(rate=5.0, max_tokens=3)
    
    # Create workers that share the rate limiter
    workers = [
        APIWorker(worker_id=i, limiter=limiter)
        for i in range(3)
    ]
    
    start = time.monotonic()
    
    # Run all workers concurrently
    await asyncio.gather(*[
        worker.run_batch(num_requests=5)
        for worker in workers
    ])
    
    elapsed = time.monotonic() - start
    total_calls = sum(w.calls_made for w in workers)
    
    print(f"\n=== Summary ===")
    print(f"Total requests: {total_calls}")
    print(f"Time elapsed: {elapsed:.2f}s")
    print(f"Effective rate: {total_calls / elapsed:.2f} requests/sec")
    print(f"\nExpected ~5 req/sec (rate limit), got {total_calls / elapsed:.2f}")


if __name__ == "__main__":
    # Run the async demo
    # You should see the first 3 requests fire immediately (burst),
    # then the rest throttled at ~5 per second
    asyncio.run(demo_rate_limiter())