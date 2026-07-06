"""
Date: 2026-07-06
Implemented a token bucket rate limiter using asyncio to explore concurrency patterns and how to throttle API-like requests without blocking.
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiterConfig:
    """Configuration for the token bucket rate limiter."""
    max_tokens: int
    refill_rate: float  # tokens per second
    refill_interval: float = 0.1  # how often to check and refill


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter that allows bursts up to max_tokens.
    
    The bucket refills at a constant rate. Each operation consumes one token.
    If no tokens are available, the caller waits until tokens are refilled.
    This pattern is great for APIs that allow short bursts but need overall throttling.
    """
    
    def __init__(self, config: RateLimiterConfig):
        self.max_tokens = config.max_tokens
        self.refill_rate = config.refill_rate
        self.refill_interval = config.refill_interval
        self.tokens = float(config.max_tokens)
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
        self._refill_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background refill task."""
        self._refill_task = asyncio.create_task(self._refill_loop())
    
    async def stop(self):
        """Stop the background refill task."""
        if self._refill_task:
            self._refill_task.cancel()
            try:
                await self._refill_task
            except asyncio.CancelledError:
                pass
    
    async def _refill_loop(self):
        """Background task that periodically refills tokens."""
        while True:
            try:
                await asyncio.sleep(self.refill_interval)
                async with self._lock:
                    now = time.time()
                    elapsed = now - self.last_refill
                    # Calculate how many tokens to add based on elapsed time
                    tokens_to_add = elapsed * self.refill_rate
                    self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
                    self.last_refill = now
            except asyncio.CancelledError:
                break
    
    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens from the bucket, waiting if necessary.
        
        This is the key method - it blocks until enough tokens are available.
        I'm using a simple spin-wait here since the refill is frequent.
        """
        while True:
            async with self._lock:
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
            # Not enough tokens, wait a bit before checking again
            await asyncio.sleep(0.05)


class APISimulator:
    """
    Simulates an API client that makes requests with rate limiting.
    
    In real life, this would be hitting actual endpoints, but here I'm just
    simulating network delays and printing requests.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter, client_id: str):
        self.rate_limiter = rate_limiter
        self.client_id = client_id
        self.requests_made = 0
    
    async def make_request(self, request_id: int):
        """Simulate making an API request with rate limiting."""
        # Wait for permission from the rate limiter
        await self.rate_limiter.acquire()
        
        # Simulate the actual request
        start_time = time.time()
        await asyncio.sleep(0.1)  # Simulate network delay
        duration = time.time() - start_time
        
        self.requests_made += 1
        print(f"[{self.client_id}] Request #{request_id} completed in {duration:.2f}s "
              f"(total: {self.requests_made})")


async def simulate_bursty_traffic(api: APISimulator, burst_size: int):
    """
    Simulate a burst of requests - this tests how the rate limiter handles spikes.
    
    In practice, bursts happen all the time: a user refreshes repeatedly,
    a batch job kicks off, etc. The token bucket handles this nicely.
    """
    tasks = []
    for i in range(burst_size):
        task = asyncio.create_task(api.make_request(i + 1))
        tasks.append(task)
    
    await asyncio.gather(*tasks)


async def main():
    """
    Demo the rate limiter with simulated API traffic.
    
    I'm configuring it to allow 5 tokens max (burst capacity) and refill
    at 2 tokens/second. This means sustained throughput is 2 req/s,
    but we can handle bursts of up to 5 requests if the bucket is full.
    """
    print("=== Token Bucket Rate Limiter Demo ===\n")
    
    config = RateLimiterConfig(
        max_tokens=5,
        refill_rate=2.0,  # 2 tokens per second
        refill_interval=0.1
    )
    
    rate_limiter = TokenBucketRateLimiter(config)
    await rate_limiter.start()
    
    api = APISimulator(rate_limiter, "Client-A")
    
    print(f"Config: {config.max_tokens} max tokens, {config.refill_rate} tokens/sec refill rate\n")
    
    # First burst: should go through quickly (bucket is full)
    print("Sending initial burst of 5 requests (bucket is full)...")
    await simulate_bursty_traffic(api, 5)
    print()
    
    # Second burst immediately after: will be rate limited
    print("Sending another burst of 5 requests (bucket is empty now)...")
    await simulate_bursty_traffic(api, 5)
    print()
    
    # Wait for bucket to refill partially
    print("Waiting 2 seconds for bucket to refill...")
    await asyncio.sleep(2)
    print()
    
    # Third burst: should have ~4 tokens available
    print("Sending final burst of 5 requests (bucket partially refilled)...")
    await simulate_bursty_traffic(api, 5)
    
    await rate_limiter.stop()
    print(f"\nTotal requests made: {api.requests_made}")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())