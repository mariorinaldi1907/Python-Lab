"""
Date: 2026-07-18
Created a port scanner that checks which ports are open on a target host using multithreading to speed things up — helps me audit my local dev environment.
"""

#!/usr/bin/env python3
"""
Simple port scanner using Python's socket library.
Scans a range of ports on a given host to check which ones are open.
Uses threading to make it reasonably fast.
"""

import socket
import threading
import time
from queue import Queue


class PortScanner:
    """
    A simple multithreaded port scanner that checks which ports are open on a target host.
    """
    
    def __init__(self, target, port_range=(1, 1024), timeout=0.5, num_threads=50):
        """
        Initialize the port scanner.
        
        Args:
            target: IP address or hostname to scan
            port_range: Tuple of (start_port, end_port) to scan
            timeout: Socket connection timeout in seconds
            num_threads: Number of worker threads to use
        """
        self.target = target
        self.port_range = port_range
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()
    
    def _resolve_target(self):
        """
        Resolve the target hostname to an IP address.
        
        Returns:
            IP address as string, or None if resolution fails
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            return None
    
    def _scan_port(self, port):
        """
        Attempt to connect to a specific port on the target.
        
        Args:
            port: Port number to scan
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # Create a socket with IPv4 and TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Try to connect - if successful, port is open
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            return result == 0
        except Exception:
            # Any exception means we couldn't connect
            return False
    
    def _worker(self):
        """
        Worker thread that processes ports from the queue.
        Each worker pulls port numbers and scans them until the queue is empty.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
            
            if self._scan_port(port):
                # Thread-safe append to the results list
                with self.lock:
                    self.open_ports.append(port)
            
            self.queue.task_done()
    
    def scan(self):
        """
        Run the port scan using multiple threads.
        
        Returns:
            List of open ports (sorted)
        """
        print(f"Scanning {self.target} from port {self.port_range[0]} to {self.port_range[1]}...")
        
        # Verify we can resolve the target
        ip = self._resolve_target()
        if ip is None:
            print(f"Error: Could not resolve {self.target}")
            return []
        
        if ip != self.target:
            print(f"Resolved {self.target} to {ip}")
        
        start_time = time.time()
        
        # Start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            threads.append(thread)
        
        # Queue up all ports to scan
        for port in range(self.port_range[0], self.port_range[1] + 1):
            self.queue.put(port)
        
        # Wait for all tasks to complete
        self.queue.join()
        
        # Stop workers
        for _ in range(self.num_threads):
            self.queue.put(None)
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        print(f"\nScan completed in {elapsed:.2f} seconds")
        
        # Return sorted list of open ports
        self.open_ports.sort()
        return self.open_ports


def get_service_name(port):
    """
    Try to get the common service name for a given port number.
    
    Args:
        port: Port number
        
    Returns:
        Service name if known, otherwise "unknown"
    """
    try:
        return socket.getservbyport(port)
    except OSError:
        return "unknown"


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    print("=" * 60)
    print("Port Scanner Demo - Scanning localhost")
    print("=" * 60)
    
    scanner = PortScanner(
        target="localhost",
        port_range=(1, 1024),  # Scan well-known ports
        timeout=0.3,
        num_threads=100
    )
    
    open_ports = scanner.scan()
    
    if open_ports:
        print(f"\nFound {len(open_ports)} open port(s):\n")
        for port in open_ports:
            service = get_service_name(port)
            print(f"  Port {port:5d} - {service}")
    else:
        print("\nNo open ports found in the specified range.")
    
    print("\n" + "=" * 60)