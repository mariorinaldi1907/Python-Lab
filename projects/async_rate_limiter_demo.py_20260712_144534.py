"""
Date: 2026-07-12
Implemented a token bucket rate limiter using asyncio to explore how to handle bursty API calls without overwhelming downstream services.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Allows burst traffic up to capacity, then enforces a steady rate.
    Tokens refill at a constant rate — if you're out of tokens, you wait.
    """
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize bucket at full capacity."""
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
    
    def _refill(self):
        """Add tokens based on time elapsed since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        
        # Don't exceed capacity — tokens don't accumulate forever
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Returns the time spent waiting (useful for metrics).
        """
        start = time.monotonic()
        
        while True:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return time.monotonic() - start
            
            # Calculate how long to wait for enough tokens
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.refill_rate
            
            # Sleep a bit and try again — asyncio keeps other tasks running
            await asyncio.sleep(wait_time)


class RateLimitedWorker:
    """
    Simulates a worker that makes rate-limited API calls.
    
    In a real scenario, this could be hitting an external API that
    has strict rate limits (e.g., 10 requests per second).
    """
    
    def __init__(self, worker_id: int, bucket: TokenBucket):
        """Initialize with a unique ID and shared rate limiter."""
        self.worker_id = worker_id
        self.bucket = bucket
        self.requests_made = 0
    
    async def make_request(self, request_num: int):
        """Simulate making a single API request with rate limiting."""
        wait_time = await self.bucket.acquire()
        
        # Simulate the actual API call taking some time
        await asyncio.sleep(0.1)
        
        self.requests_made += 1
        print(f"[Worker {self.worker_id}] Request #{request_num} completed "
              f"(waited {wait_time:.3f}s for token)")
    
    async def run(self, num_requests: int):
        """Execute a batch of requests, respecting rate limits."""
        print(f"[Worker {self.worker_id}] Starting {num_requests} requests...")
        
        tasks = []
        for i in range(num_requests):
            tasks.append(self.make_request(i + 1))
        
        await asyncio.gather(*tasks)
        print(f"[Worker {self.worker_id}] Completed all {self.requests_made} requests")


async def demonstrate_rate_limiting():
    """
    Run a demo showing multiple workers sharing a rate limiter.
    
    We set up a bucket that allows bursts of 5 requests but only
    refills at 2 requests/second. Watch how the first few are instant
    (burst capacity) then subsequent ones queue up waiting for tokens.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    print("Config: 5 token capacity, 2 tokens/second refill rate")
    print("Running 3 workers, each making 4 requests (12 total)\n")
    
    # Shared bucket across all workers — this enforces global rate limit
    bucket = TokenBucket(capacity=5, refill_rate=2.0)
    
    # Spin up multiple workers that all compete for tokens
    workers = [
        RateLimitedWorker(worker_id=1, bucket=bucket),
        RateLimitedWorker(worker_id=2, bucket=bucket),
        RateLimitedWorker(worker_id=3, bucket=bucket),
    ]
    
    start_time = time.monotonic()
    
    # Launch all workers concurrently
    await asyncio.gather(*[worker.run(4) for worker in workers])
    
    elapsed = time.monotonic() - start_time
    total_requests = sum(w.requests_made for w in workers)
    
    print(f"\n=== Summary ===")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Effective rate: {total_requests / elapsed:.2f} requests/second")
    print(f"\nExpected ~2 req/s after initial burst — pretty close!")


def main():
    """Entry point — just kick off the async demo."""
    asyncio.run(demonstrate_rate_limiting())


if __name__ == "__main__":
    main()