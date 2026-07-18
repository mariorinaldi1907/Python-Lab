"""
Date: 2026-07-18
Built a concurrent port scanner to check which services are running on my local network devices — learned some socket timeout edge cases the hard way.
"""

#!/usr/bin/env python3
"""
Simple Port Scanner
Scans a target host for open TCP ports using multithreading.
I wanted something lightweight that doesn't require nmap for quick checks.
"""

import socket
import threading
import time
from queue import Queue
from typing import List, Tuple


class PortScanner:
    """
    A multithreaded port scanner that checks which TCP ports are open on a host.
    
    Uses a thread pool pattern because scanning ports sequentially takes forever.
    Each thread grabs port numbers from a queue and attempts to connect.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds (lower = faster but less accurate)
            num_threads: Number of concurrent threads (too many can trigger rate limiting)
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        self.port_queue = Queue()
        
    def _resolve_target(self) -> str:
        """
        Resolve hostname to IP address.
        
        Returns:
            IP address as string
            
        Raises:
            socket.gaierror: If hostname cannot be resolved
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {self.target}")
    
    def _scan_port(self, port: int) -> bool:
        """
        Attempt to connect to a single port.
        
        Args:
            port: Port number to scan
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # AF_INET = IPv4, SOCK_STREAM = TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # connect_ex returns 0 on success, error code otherwise
            # Using this instead of connect() because it doesn't raise exceptions
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            return result == 0
        except socket.error:
            return False
    
    def _worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        This is the function that runs in each thread. It keeps pulling port
        numbers until the queue is empty, then exits.
        """
        while not self.port_queue.empty():
            port = self.port_queue.get()
            
            if self._scan_port(port):
                # Thread-safe append to shared list
                with self.lock:
                    self.open_ports.append(port)
            
            self.port_queue.task_done()
    
    def scan(self, start_port: int = 1, end_port: int = 1024) -> List[int]:
        """
        Scan a range of ports on the target host.
        
        Args:
            start_port: First port to scan (inclusive)
            end_port: Last port to scan (inclusive)
            
        Returns:
            Sorted list of open port numbers
        """
        # Clear results from any previous scan
        self.open_ports = []
        
        # Resolve hostname to IP
        ip = self._resolve_target()
        print(f"Scanning {self.target} ({ip})...")
        print(f"Port range: {start_port}-{end_port}")
        print(f"Threads: {self.num_threads}, Timeout: {self.timeout}s\n")
        
        # Fill the queue with all ports to scan
        for port in range(start_port, end_port + 1):
            self.port_queue.put(port)
        
        # Start timing
        start_time = time.time()
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True  # Dies when main thread exits
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        print(f"Scan completed in {elapsed:.2f} seconds")
        
        # Return sorted list of open ports
        return sorted(self.open_ports)


def get_service_name(port: int) -> str:
    """
    Try to get the common service name for a port number.
    
    Args:
        port: Port number
        
    Returns:
        Service name or "unknown" if not found
    """
    try:
        # This uses /etc/services on Unix systems
        return socket.getservbyport(port)
    except OSError:
        return "unknown"


if __name__ == "__main__":
    # Demo: scan common ports on localhost
    # In real use, you'd pass a target IP or hostname as a command line arg
    
    TARGET = "localhost"
    START_PORT = 1
    END_PORT = 1024
    
    scanner = PortScanner(target=TARGET, timeout=0.5, num_threads=100)
    
    try:
        open_ports = scanner.scan(start_port=START_PORT, end_port=END_PORT)
        
        if open_ports:
            print(f"\n✓ Found {len(open_ports)} open port(s):\n")
            for port in open_ports:
                service = get_service_name(port)
                print(f"  Port {port:5d} - {service}")
        else:
            print("\n✗ No open ports found in the specified range")
            
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")