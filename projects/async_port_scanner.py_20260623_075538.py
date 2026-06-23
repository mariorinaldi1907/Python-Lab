"""
Date: 2026-06-23
Created a concurrent port scanner that checks multiple ports at once — helps me quickly identify what's running on local services during development.
"""

#!/usr/bin/env python3
"""
Async Port Scanner
Scans a range of ports on a target host to check which ones are open.
Uses threading to speed things up without external dependencies.
"""

import socket
import threading
import time
from queue import Queue
from typing import List, Tuple


class PortScanner:
    """
    A multithreaded port scanner that checks which ports are open on a host.
    
    I wanted something lightweight that doesn't need nmap installed, just for
    quick checks when I'm testing local services or debugging network stuff.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds
            num_threads: Number of concurrent threads to use
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
        # Try to resolve the hostname to IP right away
        try:
            self.ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def _scan_port(self, port: int) -> bool:
        """
        Check if a single port is open.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # AF_INET is IPv4, SOCK_STREAM is TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # connect_ex returns 0 if connection succeeded
            result = sock.connect_ex((self.ip, port))
            sock.close()
            
            return result == 0
        except socket.error:
            return False
    
    def _worker(self, port_queue: Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        Args:
            port_queue: Queue containing port numbers to scan
        """
        while not port_queue.empty():
            port = port_queue.get()
            
            if self._scan_port(port):
                # Thread-safe append to the results list
                with self.lock:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is open")
            
            port_queue.task_done()
    
    def scan(self, start_port: int = 1, end_port: int = 1024) -> List[int]:
        """
        Scan a range of ports on the target host.
        
        Args:
            start_port: First port in range to scan
            end_port: Last port in range to scan (inclusive)
            
        Returns:
            Sorted list of open port numbers
        """
        print(f"\n[*] Starting scan on {self.target} ({self.ip})")
        print(f"[*] Scanning ports {start_port}-{end_port} with {self.num_threads} threads\n")
        
        # Reset results from any previous scans
        self.open_ports = []
        
        # Create a queue and fill it with port numbers
        port_queue = Queue()
        for port in range(start_port, end_port + 1):
            port_queue.put(port)
        
        # Start timing
        start_time = time.time()
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker, args=(port_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        
        # Sort the results for cleaner output
        self.open_ports.sort()
        
        print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open ports")
        
        return self.open_ports
    
    def get_service_name(self, port: int) -> str:
        """
        Try to get the service name for a port using socket.getservbyport().
        
        Args:
            port: Port number to look up
            
        Returns:
            Service name or "unknown" if not found
        """
        try:
            return socket.getservbyport(port)
        except OSError:
            return "unknown"


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    print("=" * 60)
    print("Port Scanner Demo")
    print("=" * 60)
    
    try:
        # Scan localhost - useful for checking what I have running locally
        scanner = PortScanner("localhost", timeout=0.5, num_threads=100)
        
        # Check common ports - web servers, databases, etc.
        open_ports = scanner.scan(start_port=1, end_port=9000)
        
        if open_ports:
            print("\n" + "=" * 60)
            print("Open Ports Summary:")
            print("=" * 60)
            for port in open_ports:
                service = scanner.get_service_name(port)
                print(f"  Port {port:5d}  ->  {service}")
        else:
            print("\nNo open ports found in the scanned range.")
            
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")