"""
Date: 2026-07-25
Created a quick port scanner to check what's running on my local network — uses threading to speed things up without overwhelming the target.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner
A simple multi-threaded port scanner for checking open ports on a target host.
I built this to quickly scan my local services without installing nmap.
"""

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    Multi-threaded TCP port scanner that checks for open ports on a target host.
    Uses a queue-based approach to distribute work across threads efficiently.
    """
    
    def __init__(self, target, ports, threads=10, timeout=1.0):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            ports: List of port numbers to check
            threads: Number of worker threads (default 10)
            timeout: Socket timeout in seconds (default 1.0)
        """
        self.target = target
        self.ports = ports
        self.num_threads = threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        self.port_queue = Queue()
        
    def resolve_target(self):
        """
        Resolve the target hostname to an IP address.
        Returns the IP as a string, or None if resolution fails.
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            return None
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port on the target.
        If successful, the port is considered open.
        
        Args:
            port: Port number to scan
        
        Returns:
            True if port is open, False otherwise
        """
        try:
            # Create a new socket for each connection attempt
            # Using SOCK_STREAM for TCP connections
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Attempt connection - if it succeeds, port is open
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            return result == 0
        except socket.error:
            return False
    
    def worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        Continues until the queue is empty.
        """
        while not self.port_queue.empty():
            port = self.port_queue.get()
            
            if self.scan_port(port):
                # Thread-safe append to the open_ports list
                with self.lock:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is open")
            
            self.port_queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        Returns a sorted list of open ports.
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.num_threads} threads")
        print(f"[*] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Populate the queue with all ports to scan
        for port in self.ports:
            self.port_queue.put(port)
        
        # Create and start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all tasks to complete
        self.port_queue.join()
        
        # Ensure all threads have finished
        for thread in threads:
            thread.join()
        
        print(f"\n[*] Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return sorted(self.open_ports)


def parse_port_range(port_string):
    """
    Parse a port range string into a list of port numbers.
    Supports formats like '80', '80-100', '22,80,443'.
    
    Args:
        port_string: String representation of ports
    
    Returns:
        List of integer port numbers
    """
    ports = []
    
    for part in port_string.split(','):
        if '-' in part:
            # Handle range like '80-100'
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            # Handle single port
            ports.append(int(part))
    
    return ports


if __name__ == "__main__":
    # Demo: scan common ports on localhost
    print("=" * 60)
    print("TCP Port Scanner Demo")
    print("=" * 60)
    
    # Scan common service ports on localhost
    target = "127.0.0.1"
    
    # Common ports: SSH, HTTP, HTTPS, MySQL, PostgreSQL, etc.
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 5432, 8080, 8443]
    
    scanner = PortScanner(target, common_ports, threads=20, timeout=0.5)
    
    # Resolve target first
    ip = scanner.resolve_target()
    if not ip:
        print(f"[!] Could not resolve target: {target}")
    else:
        print(f"[*] Target resolved to: {ip}")
        
        # Run the scan
        open_ports = scanner.scan()
        
        # Display results
        print("\n" + "=" * 60)
        print("SCAN RESULTS")
        print("=" * 60)
        
        if open_ports:
            print(f"\n[+] Found {len(open_ports)} open port(s):")
            for port in open_ports:
                print(f"    - Port {port}")
        else:
            print("\n[-] No open ports found in the scanned range")
        
        print("\n" + "=" * 60)