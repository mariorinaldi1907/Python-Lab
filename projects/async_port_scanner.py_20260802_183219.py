"""
Date: 2026-08-02
Created a concurrent port scanner that checks multiple ports simultaneously and identifies common services running on open ports.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded port scanner with service detection.
I built this to quickly check what's running on my local network devices.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
import sys


# Common ports and their typical services
# I only included the most common ones I actually care about
COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    27017: "MongoDB",
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target host.
    Uses a thread pool to scan multiple ports concurrently for speed.
    """
    
    def __init__(self, target, timeout=1.0, num_threads=50):
        """
        Initialize the scanner with target and performance settings.
        
        Args:
            target: IP address or hostname to scan
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()  # Protect shared open_ports list
        
    def _resolve_target(self):
        """
        Resolve hostname to IP address.
        Returns the IP or None if resolution fails.
        """
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            return None
    
    def _scan_port(self, port):
        """
        Attempt to connect to a single port.
        If successful, adds it to the open_ports list.
        
        Args:
            port: Port number to scan
        """
        try:
            # Create a new socket for each connection attempt
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Try to connect - if it succeeds, port is open
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, grab the service name if we know it
                service = COMMON_SERVICES.get(port, "Unknown")
                with self.lock:
                    self.open_ports.append((port, service))
            
            sock.close()
            
        except socket.error:
            # Connection failed, port is closed or filtered
            pass
    
    def _worker(self, queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        Runs until the queue is empty.
        
        Args:
            queue: Queue containing port numbers to scan
        """
        while not queue.empty():
            port = queue.get()
            self._scan_port(port)
            queue.task_done()
    
    def scan(self, port_range):
        """
        Scan a range of ports using multiple threads.
        
        Args:
            port_range: Tuple of (start_port, end_port) inclusive
            
        Returns:
            List of tuples (port, service) for open ports, sorted by port number
        """
        start_port, end_port = port_range
        
        # Verify the target is reachable
        ip = self._resolve_target()
        if not ip:
            print(f"Error: Could not resolve {self.target}")
            return []
        
        print(f"Scanning {self.target} ({ip}) from port {start_port} to {end_port}...")
        print(f"Using {self.num_threads} threads with {self.timeout}s timeout\n")
        
        start_time = datetime.now()
        
        # Create a queue and populate it with ports to scan
        port_queue = Queue()
        for port in range(start_port, end_port + 1):
            port_queue.put(port)
        
        # Spin up worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker, args=(port_queue,))
            thread.daemon = True  # Dies when main thread exits
            thread.start()
            threads.append(thread)
        
        # Wait for all scanning to complete
        port_queue.join()
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        
        print(f"\nScan completed in {elapsed:.2f} seconds")
        print(f"Found {len(self.open_ports)} open port(s)\n")
        
        return self.open_ports


def print_results(open_ports):
    """
    Pretty print the scan results.
    
    Args:
        open_ports: List of (port, service) tuples
    """
    if not open_ports:
        print("No open ports found.")
        return
    
    print("PORT     SERVICE")
    print("-" * 25)
    for port, service in open_ports:
        print(f"{port:<8} {service}")


if __name__ == "__main__":
    # Demo: scan common ports on localhost
    # In real usage, you'd pass target as a command-line arg
    
    target = "127.0.0.1"  # Localhost
    
    # Quick scan of well-known ports (1-1024)
    # For a full scan, use (1, 65535) but it takes a while
    scanner = PortScanner(target, timeout=0.5, num_threads=100)
    results = scanner.scan((1, 1024))
    
    print_results(results)
    
    print("\n" + "="*50)
    print("TIP: Change 'target' variable to scan other hosts")
    print("Example: target = '192.168.1.1' for your router")
    print("="*50)