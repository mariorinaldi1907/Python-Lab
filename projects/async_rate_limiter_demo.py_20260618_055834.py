"""
Date: 2026-06-18
Implemented a token bucket rate limiter using asyncio to see how to throttle concurrent API calls properly — something I wish I had when I was hammering external APIs last month.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import List
import random


@dataclass
class RateLimiterConfig:
    """Configuration for the token bucket rate limiter."""
    max_tokens: int  # Maximum tokens in the bucket
    refill_rate: float  # Tokens added per second
    

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request throughput.
    
    This is basically how most real-world rate limiters work — you have a bucket
    that fills up with tokens over time, and each request consumes a token.
    If the bucket is empty, requests have to wait.
    """
    
    def __init__(self, config: RateLimiterConfig):
        self.max_tokens = config.max_tokens
        self.refill_rate = config.refill_rate
        self.tokens = float(config.max_tokens)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def _refill(self):
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        # Add tokens proportional to time elapsed
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the core method — consumers call this before doing work.
        If there aren't enough tokens, we calculate how long to wait.
        """
        async with self._lock:
            await self._refill()
            
            while self.tokens < tokens:
                # Calculate how long we need to wait for enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Release lock while waiting so other tasks can check too
                self._lock.release()
                await asyncio.sleep(wait_time)
                self._lock = asyncio.Lock()
                async with self._lock:
                    await self._refill()
            
            self.tokens -= tokens


class APIClient:
    """
    Simulated API client that respects rate limits.
    
    In real life, this would be calling external APIs, but here
    we just simulate network delay and response handling.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        self.rate_limiter = rate_limiter
        self.request_count = 0
    
    async def make_request(self, request_id: int) -> dict:
        """
        Make a single API request with rate limiting.
        
        The rate limiter ensures we don't overwhelm the "API".
        """
        # Wait for permission to make the request
        await self.rate_limiter.acquire()
        
        # Simulate network latency
        delay = random.uniform(0.1, 0.3)
        await asyncio.sleep(delay)
        
        self.request_count += 1
        timestamp = time.strftime("%H:%M:%S")
        
        return {
            "request_id": request_id,
            "timestamp": timestamp,
            "latency_ms": int(delay * 1000)
        }


async def consumer_task(client: APIClient, task_id: int, num_requests: int):
    """
    Simulate a consumer making multiple API requests.
    
    Each consumer independently tries to make requests, but they all
    share the same rate limiter — this is the key to throttling.
    """
    print(f"[Consumer {task_id}] Starting, will make {num_requests} requests")
    
    for i in range(num_requests):
        try:
            result = await client.make_request(request_id=i)
            print(f"[Consumer {task_id}] Request {i+1}/{num_requests} completed at "
                  f"{result['timestamp']} (latency: {result['latency_ms']}ms)")
        except Exception as e:
            print(f"[Consumer {task_id}] Request {i+1} failed: {e}")
    
    print(f"[Consumer {task_id}] Finished all requests")


async def main():
    """
    Demo the rate limiter with multiple concurrent consumers.
    
    We create 5 consumers that each try to make 3 requests, but the rate
    limiter only allows 5 requests per second with a burst of 3.
    Watch how the requests get throttled!
    """
    print("=" * 60)
    print("Async Token Bucket Rate Limiter Demo")
    print("=" * 60)
    
    # Configure rate limiter: 3 tokens max, refills at 5 tokens/sec
    # This means we can burst 3 requests immediately, then sustain 5 req/sec
    config = RateLimiterConfig(max_tokens=3, refill_rate=5.0)
    rate_limiter = TokenBucketRateLimiter(config)
    
    print(f"\nRate Limiter Config:")
    print(f"  - Max burst: {config.max_tokens} requests")
    print(f"  - Sustained rate: {config.refill_rate} requests/second")
    print(f"\nSpawning 5 consumers, each making 3 requests...")
    print(f"(Watch how they get throttled!)\n")
    
    # Create shared API client
    client = APIClient(rate_limiter)
    
    # Spawn multiple consumers
    start_time = time.monotonic()
    consumers = [
        consumer_task(client, task_id=i, num_requests=3)
        for i in range(5)
    ]
    
    # Wait for all consumers to finish
    await asyncio.gather(*consumers)
    
    elapsed = time.monotonic() - start_time
    
    print(f"\n" + "=" * 60)
    print(f"Demo Complete!")
    print(f"  - Total requests: {client.request_count}")
    print(f"  - Total time: {elapsed:.2f} seconds")
    print(f"  - Effective rate: {client.request_count / elapsed:.2f} req/sec")
    print(f"  - Target rate: {config.refill_rate} req/sec")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())