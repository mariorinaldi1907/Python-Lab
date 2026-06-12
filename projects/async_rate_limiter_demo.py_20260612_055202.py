"""
Date: 2026-06-12
Created an asyncio-based rate limiter using the token bucket pattern to demonstrate controlled concurrency and backpressure handling in async code.
"""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Tokens are added at a constant rate, and each operation consumes one token.
    If no tokens available, the caller waits until one becomes available.
    This approach smooths out bursts while maintaining average throughput.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Tokens added per second (e.g., 5.0 means 5 requests/sec)
            capacity: Maximum tokens the bucket can hold
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill_tokens(self):
        """
        Refill tokens based on elapsed time since last update.
        This is where the 'constant rate' magic happens.
        """
        now = time.monotonic()
        elapsed = now - self.last_update
        
        # Calculate how many tokens to add based on time passed
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default 1)
            
        Returns:
            Time spent waiting in seconds
        """
        async with self._lock:
            await self._refill_tokens()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                
                await asyncio.sleep(wait_time)
                await self._refill_tokens()
            
            self.tokens -= tokens
            return 0 if self.tokens >= 0 else abs(self.tokens) / self.rate


class APIClient:
    """
    Simulated API client that uses rate limiting.
    
    In real life, I'd use this pattern when hitting external APIs
    that have strict rate limits (looking at you, Twitter API).
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter, name: str = "API"):
        """
        Initialize the API client.
        
        Args:
            rate_limiter: Rate limiter instance to control request frequency
            name: Name for logging purposes
        """
        self.rate_limiter = rate_limiter
        self.name = name
        self.request_count = 0
    
    async def make_request(self, request_id: int) -> dict:
        """
        Simulate making an API request with rate limiting.
        
        Args:
            request_id: Unique identifier for this request
            
        Returns:
            Dict with request metadata
        """
        start_time = time.monotonic()
        
        # Acquire token before making request
        await self.rate_limiter.acquire()
        
        # Simulate API call taking some time
        await asyncio.sleep(0.1)
        
        self.request_count += 1
        elapsed = time.monotonic() - start_time
        
        return {
            "id": request_id,
            "client": self.name,
            "elapsed": elapsed,
            "total_requests": self.request_count
        }


async def worker(client: APIClient, worker_id: int, num_requests: int):
    """
    Worker coroutine that makes multiple API requests.
    
    This simulates concurrent clients all trying to hit the same API.
    The rate limiter ensures they don't overwhelm the endpoint.
    """
    print(f"[Worker {worker_id}] Starting with {num_requests} requests")
    
    for i in range(num_requests):
        result = await client.make_request(i)
        print(f"[Worker {worker_id}] Request {i+1}/{num_requests} "
              f"completed in {result['elapsed']:.3f}s")
    
    print(f"[Worker {worker_id}] Finished all requests")


async def demonstrate_rate_limiting():
    """
    Main demo showing rate limiter in action with concurrent workers.
    
    I'm creating multiple workers that all try to make requests simultaneously.
    Without rate limiting, they'd all fire at once. With it, you'll see them
    queue up and get served at the controlled rate.
    """
    print("=== Rate Limiter Demo ===\n")
    
    # Create rate limiter: 3 requests per second, bucket capacity of 5
    # This means bursts up to 5 are allowed, but sustained rate is 3/sec
    rate_limiter = TokenBucketRateLimiter(rate=3.0, capacity=5)
    
    # Create a shared API client
    api_client = APIClient(rate_limiter, name="DemoAPI")
    
    print(f"Rate limit: {rate_limiter.rate} req/sec")
    print(f"Bucket capacity: {rate_limiter.capacity} tokens")
    print(f"Launching 3 workers with 4 requests each (12 total)\n")
    
    start_time = time.monotonic()
    
    # Spawn multiple workers that will compete for rate-limited resources
    workers = [
        worker(api_client, worker_id=1, num_requests=4),
        worker(api_client, worker_id=2, num_requests=4),
        worker(api_client, worker_id=3, num_requests=4),
    ]
    
    await asyncio.gather(*workers)
    
    total_time = time.monotonic() - start_time
    
    print(f"\n=== Summary ===")
    print(f"Total time: {total_time:.2f}s")
    print(f"Total requests: {api_client.request_count}")
    print(f"Actual rate: {api_client.request_count / total_time:.2f} req/sec")
    print(f"Expected rate: ~{rate_limiter.rate:.2f} req/sec (after initial burst)")


if __name__ == "__main__":
    # Run the async demo
    # You should see requests initially burst (up to capacity),
    # then settle into the steady rate of 3 req/sec
    asyncio.run(demonstrate_rate_limiting())