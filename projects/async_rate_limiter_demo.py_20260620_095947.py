"""
Date: 2026-06-20
Implemented a token bucket rate limiter with asyncio to explore controlled concurrency — useful for API clients that need strict rate limiting.
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
    

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Each request consumes one token. Tokens are refilled at a constant rate.
    If no tokens are available, requests must wait until tokens are refilled.
    This prevents burst traffic from overwhelming downstream services.
    """
    
    def __init__(self, config: RateLimiterConfig):
        """Initialize the rate limiter with given configuration."""
        self.max_tokens = config.max_tokens
        self.refill_rate = config.refill_rate
        self.tokens = float(config.max_tokens)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        
    async def _refill_tokens(self):
        """
        Refill tokens based on time elapsed since last refill.
        
        This is called before each acquire attempt to ensure tokens
        are up to date with the current time.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate new tokens based on elapsed time
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
        
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire the specified number of tokens, waiting if necessary.
        
        Returns the time (in seconds) that was waited.
        """
        async with self._lock:
            await self._refill_tokens()
            
            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate
                
                await asyncio.sleep(wait_time)
                await self._refill_tokens()
                
                self.tokens -= tokens
                return wait_time
            else:
                self.tokens -= tokens
                return 0.0


class APIClient:
    """
    Simulated API client that uses rate limiting.
    
    In a real scenario, this would make actual HTTP requests,
    but here we just simulate the work with sleeps.
    """
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        """Initialize client with a rate limiter."""
        self.rate_limiter = rate_limiter
        self.request_log = deque()
        
    async def fetch_data(self, request_id: int) -> dict:
        """
        Simulate fetching data from an API endpoint.
        
        This method respects the rate limiter before making requests.
        """
        wait_time = await self.rate_limiter.acquire()
        
        timestamp = time.time()
        
        # Simulate actual API call with random processing time
        await asyncio.sleep(0.1)
        
        result = {
            'request_id': request_id,
            'timestamp': timestamp,
            'wait_time': wait_time,
            'status': 'success'
        }
        
        self.request_log.append(result)
        return result


async def run_concurrent_requests(num_requests: int, rate_limiter: TokenBucketRateLimiter):
    """
    Fire off multiple concurrent requests and watch the rate limiter in action.
    
    All requests are started simultaneously, but the rate limiter ensures
    they're processed at a controlled rate.
    """
    client = APIClient(rate_limiter)
    
    print(f"\n🚀 Starting {num_requests} concurrent requests...")
    print(f"Rate limit: {rate_limiter.refill_rate} requests/sec (burst: {rate_limiter.max_tokens})\n")
    
    start_time = time.time()
    
    # Launch all requests concurrently
    tasks = [client.fetch_data(i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Print results with timing info
    print("Request Results:")
    print("-" * 70)
    for result in results:
        wait_msg = f"(waited {result['wait_time']:.2f}s)" if result['wait_time'] > 0 else "(no wait)"
        print(f"Request #{result['request_id']:2d}: completed at {result['timestamp']:.2f} {wait_msg}")
    
    print("-" * 70)
    print(f"\n📊 Statistics:")
    print(f"   Total requests: {num_requests}")
    print(f"   Total time: {total_duration:.2f}s")
    print(f"   Actual rate: {num_requests / total_duration:.2f} requests/sec")
    print(f"   Average wait: {sum(r['wait_time'] for r in results) / num_requests:.2f}s")


async def main():
    """
    Demo the rate limiter with different configurations.
    
    I wanted to see how the token bucket handles burst traffic versus
    sustained load, so this runs a couple different scenarios.
    """
    # Scenario 1: Tight rate limit (2 req/sec, burst of 3)
    print("\n" + "="*70)
    print("SCENARIO 1: Tight limit - 2 req/sec with burst capacity of 3")
    print("="*70)
    
    config1 = RateLimiterConfig(max_tokens=3, refill_rate=2.0)
    limiter1 = TokenBucketRateLimiter(config1)
    await run_concurrent_requests(10, limiter1)
    
    # Give it a moment before next scenario
    await asyncio.sleep(1)
    
    # Scenario 2: More generous limit (5 req/sec, burst of 10)
    print("\n" + "="*70)
    print("SCENARIO 2: Generous limit - 5 req/sec with burst capacity of 10")
    print("="*70)
    
    config2 = RateLimiterConfig(max_tokens=10, refill_rate=5.0)
    limiter2 = TokenBucketRateLimiter(config2)
    await run_concurrent_requests(15, limiter2)


if __name__ == "__main__":
    asyncio.run(main())