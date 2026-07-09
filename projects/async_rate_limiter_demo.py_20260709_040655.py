"""
Date: 2026-07-09
Implemented a token bucket rate limiter with asyncio to understand how to throttle concurrent requests without blocking everything.
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    Tokens are added at a fixed rate. Each request consumes one token.
    If no tokens are available, requests wait until tokens are refilled.
    This prevents bursting beyond capacity while allowing steady flow.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 = 5 tokens/sec)
            capacity: Maximum tokens the bucket can hold
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """
        Refill tokens based on elapsed time since last refill.
        
        I'm using monotonic time here to avoid issues with system clock changes.
        The math is simple: tokens_to_add = time_elapsed * rate
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.rate
        
        if tokens_to_add > 0:
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
        
        This blocks until enough tokens are available. I added the lock
        to prevent race conditions when multiple coroutines try to acquire.
        """
        async with self._lock:
            while True:
                await self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long to wait for the next token
                # If we need more tokens, we wait until enough accumulate
                shortage = tokens - self.tokens
                wait_time = shortage / self.rate
                await asyncio.sleep(wait_time)


class APIClient:
    """
    Simulated API client that uses rate limiting.
    
    This mimics a real-world scenario where you're hitting an external API
    that has rate limits, and you want to avoid getting throttled or banned.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        """
        Initialize the API client with a rate limiter.
        
        Args:
            rate_limiter: TokenBucketRateLimiter instance to control request rate
        """
        self.rate_limiter = rate_limiter
        self.request_count = 0
        self.request_times = deque()
    
    async def make_request(self, request_id: int) -> dict:
        """
        Make a simulated API request with rate limiting.
        
        Args:
            request_id: Identifier for this request
            
        Returns:
            dict with request details and timing info
        """
        # Wait for rate limiter to allow the request
        await self.rate_limiter.acquire()
        
        # Record the request time
        request_time = time.monotonic()
        self.request_times.append(request_time)
        self.request_count += 1
        
        # Simulate API processing time (network latency, server processing, etc.)
        await asyncio.sleep(0.1)
        
        return {
            "request_id": request_id,
            "timestamp": request_time,
            "total_requests": self.request_count
        }


async def worker(worker_id: int, client: APIClient, num_requests: int):
    """
    Worker coroutine that makes multiple API requests.
    
    Args:
        worker_id: Identifier for this worker
        client: APIClient instance to use for requests
        num_requests: Number of requests this worker should make
    """
    print(f"Worker {worker_id} started, will make {num_requests} requests")
    
    for i in range(num_requests):
        result = await client.make_request(f"{worker_id}-{i}")
        print(f"  Worker {worker_id} completed request {i+1}/{num_requests} "
              f"(total: {result['total_requests']})")
    
    print(f"Worker {worker_id} finished!")


async def main():
    """
    Demo the rate limiter with concurrent workers.
    
    I'm setting up multiple workers that all try to make requests concurrently.
    The rate limiter ensures they don't exceed 3 requests per second total,
    even though each worker is trying to blast through their requests ASAP.
    """
    print("=== Async Rate Limiter Demo ===\n")
    
    # Configure rate limiter: 3 requests/second, capacity of 5 tokens
    # Capacity > rate allows for small bursts before throttling kicks in
    rate_limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    client = APIClient(rate_limiter)
    
    print(f"Rate limit: {rate_limiter.rate} requests/second")
    print(f"Bucket capacity: {rate_limiter.capacity} tokens\n")
    
    # Spawn 3 workers, each trying to make 4 requests
    # Total: 12 requests, should take ~4 seconds with 3 req/sec rate
    num_workers = 3
    requests_per_worker = 4
    
    start_time = time.monotonic()
    
    workers = [
        worker(i, client, requests_per_worker)
        for i in range(num_workers)
    ]
    
    await asyncio.gather(*workers)
    
    elapsed = time.monotonic() - start_time
    
    print(f"\n=== Summary ===")
    print(f"Total requests: {client.request_count}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Effective rate: {client.request_count / elapsed:.2f} requests/second")
    
    # Calculate actual request intervals to verify rate limiting worked
    if len(client.request_times) > 1:
        intervals = [
            client.request_times[i] - client.request_times[i-1]
            for i in range(1, len(client.request_times))
        ]
        avg_interval = sum(intervals) / len(intervals)
        print(f"Average interval between requests: {avg_interval:.3f} seconds")


if __name__ == "__main__":
    # Running this should show requests being throttled to ~3 per second
    # even though all workers are trying to go as fast as possible
    asyncio.run(main())