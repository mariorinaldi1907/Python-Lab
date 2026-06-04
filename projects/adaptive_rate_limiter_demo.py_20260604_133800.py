"""
Date: 2026-06-04
Created a token bucket rate limiter using threading to demo how I'd throttle API calls in production — refills tokens over time and tracks success/denied rates.
"""

#!/usr/bin/env python3
"""
Adaptive Rate Limiter Demo using Token Bucket Algorithm

This demonstrates a token bucket pattern for rate limiting with threading.
I built this to simulate how I'd handle API rate limits in real projects —
tokens refill over time, and requests either succeed or get throttled.
"""

import threading
import time
import random
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimitStats:
    """Track statistics for rate limiting performance."""
    
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    
    def success_rate(self) -> float:
        """Calculate the percentage of allowed requests."""
        if self.total_requests == 0:
            return 0.0
        return (self.allowed_requests / self.total_requests) * 100


class TokenBucket:
    """
    Thread-safe token bucket rate limiter.
    
    Tokens refill at a constant rate. Each request consumes one token.
    If no tokens are available, the request is denied (non-blocking).
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the token bucket.
        
        Args:
            capacity: Maximum number of tokens the bucket can hold
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def _refill(self):
        """Refill tokens based on elapsed time — called internally before consumption."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens proportional to time passed
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def try_consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were available and consumed, False otherwise
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_available_tokens(self) -> float:
        """Get current number of available tokens (thread-safe)."""
        with self.lock:
            self._refill()
            return self.tokens


class RequestSimulator:
    """
    Simulates multiple clients making requests to a rate-limited service.
    
    This is what I'd use to test rate limiting behavior under load.
    """
    
    def __init__(self, rate_limiter: TokenBucket, num_clients: int):
        """
        Initialize the simulator.
        
        Args:
            rate_limiter: The TokenBucket instance to test
            num_clients: Number of concurrent client threads
        """
        self.rate_limiter = rate_limiter
        self.num_clients = num_clients
        self.stats = RateLimitStats()
        self.stats_lock = threading.Lock()
        self.running = True
        
    def simulate_client(self, client_id: int):
        """
        Simulate a single client making random requests.
        
        Each client makes requests at random intervals, mimicking real usage patterns.
        """
        while self.running:
            # Random sleep to simulate variable request patterns
            time.sleep(random.uniform(0.05, 0.3))
            
            allowed = self.rate_limiter.try_consume()
            
            with self.stats_lock:
                self.stats.total_requests += 1
                if allowed:
                    self.stats.allowed_requests += 1
                else:
                    self.stats.denied_requests += 1
            
            # Only print occasional updates to avoid spam
            if self.stats.total_requests % 20 == 0:
                status = "✓ ALLOWED" if allowed else "✗ DENIED"
                tokens = self.rate_limiter.get_available_tokens()
                print(f"Client {client_id}: {status} | Tokens: {tokens:.2f}")
    
    def run(self, duration: float):
        """
        Run the simulation for a specified duration.
        
        Args:
            duration: How long to run the simulation in seconds
        """
        threads = []
        
        print(f"\n🚀 Starting simulation with {self.num_clients} clients...")
        print(f"Rate limit: {self.rate_limiter.refill_rate} requests/sec\n")
        
        # Spawn client threads
        for i in range(self.num_clients):
            thread = threading.Thread(target=self.simulate_client, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Let it run for the specified duration
        time.sleep(duration)
        self.running = False
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=1)
        
        self._print_summary()
    
    def _print_summary(self):
        """Print final statistics after simulation completes."""
        print("\n" + "=" * 50)
        print("📊 SIMULATION RESULTS")
        print("=" * 50)
        print(f"Total Requests:   {self.stats.total_requests}")
        print(f"Allowed:          {self.stats.allowed_requests} ({self.stats.success_rate():.1f}%)")
        print(f"Denied (Throttled): {self.stats.denied_requests}")
        print(f"Final Token Count: {self.rate_limiter.get_available_tokens():.2f}")
        print("=" * 50)


if __name__ == "__main__":
    # Configuration — tuned these to show interesting throttling behavior
    BUCKET_CAPACITY = 10  # Max burst size
    REFILL_RATE = 5.0     # 5 tokens/second = 5 requests/sec sustained
    NUM_CLIENTS = 4       # Concurrent clients hammering the limiter
    DURATION = 8          # Run for 8 seconds
    
    print("🪣 Token Bucket Rate Limiter Demo")
    print(f"Bucket capacity: {BUCKET_CAPACITY} tokens")
    print(f"Refill rate: {REFILL_RATE} tokens/second")
    
    # Create the rate limiter
    limiter = TokenBucket(capacity=BUCKET_CAPACITY, refill_rate=REFILL_RATE)
    
    # Run simulation
    simulator = RequestSimulator(limiter, NUM_CLIENTS)
    simulator.run(DURATION)
    
    print("\n💡 Notice how requests get throttled when tokens run out,")
    print("   but the system recovers as tokens refill over time.")