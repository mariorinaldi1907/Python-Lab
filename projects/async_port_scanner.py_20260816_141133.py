"""
Date: 2026-08-16
Created a multi-threaded port scanner that can check ranges of ports on a target host, with timeout handling and service name resolution for common ports.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner using Python's threading and socket libraries.
Scans a range of ports on a target host and identifies open ports with their services.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
import argparse


class PortScanner:
    """
    Multi-threaded port scanner that checks which ports are open on a target host.
    Uses a worker pool pattern to scan multiple ports concurrently.
    """
    
    # Common ports and their typical services - helps identify what's running
    COMMON_PORTS = {
        20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
        25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
        143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
        3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 8080: 'HTTP-Proxy',
        8443: 'HTTPS-Alt', 27017: 'MongoDB'
    }
    
    def __init__(self, target, port_range, num_threads=100, timeout=1.0):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            port_range: Tuple of (start_port, end_port)
            num_threads: Number of concurrent scanner threads
            timeout: Socket connection timeout in seconds
        """
        self.target = target
        self.port_range = port_range
        self.num_threads = num_threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()  # Protect shared list from race conditions
        self.queue = Queue()
        
    def resolve_target(self):
        """
        Resolve hostname to IP address.
        Returns the IP or raises an exception if resolution fails.
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {self.target}")
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        If successful, the port is open and we record it.
        
        Args:
            port: Port number to scan
        """
        try:
            # Create a new socket for this connection attempt
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Attempt connection - if it succeeds, port is open
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Thread-safe append to results
                with self.lock:
                    service = self.COMMON_PORTS.get(port, 'Unknown')
                    self.open_ports.append((port, service))
                    
            sock.close()
            
        except socket.error:
            # Connection failed or timeout - port is closed/filtered
            pass
    
    def worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        Runs until the queue is empty.
        """
        while not self.queue.empty():
            port = self.queue.get()
            self.scan_port(port)
            self.queue.task_done()
    
    def scan(self):
        """
        Main scan method - sets up the queue, spawns workers, and waits for completion.
        Returns a sorted list of (port, service) tuples for open ports.
        """
        # First, make sure we can resolve the target
        ip = self.resolve_target()
        print(f"Starting scan on {self.target} ({ip})")
        print(f"Scanning ports {self.port_range[0]}-{self.port_range[1]} with {self.num_threads} threads\n")
        
        start_time = datetime.now()
        
        # Fill the queue with all ports to scan
        for port in range(self.port_range[0], self.port_range[1] + 1):
            self.queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True  # Die when main thread dies
            thread.start()
            threads.append(thread)
        
        # Wait for all tasks to complete
        self.queue.join()
        
        # Calculate scan duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sort results by port number for clean output
        self.open_ports.sort(key=lambda x: x[0])
        
        print(f"\nScan completed in {duration:.2f} seconds")
        print(f"Found {len(self.open_ports)} open port(s)\n")
        
        return self.open_ports


def main():
    """
    Demo the port scanner by scanning common ports on localhost.
    In practice, you'd use argparse for real CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description='Scan network ports on a target host',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('target', nargs='?', default='localhost',
                        help='Target hostname or IP (default: localhost)')
    parser.add_argument('-p', '--ports', default='1-1024',
                        help='Port range to scan, e.g. "1-1024" (default: 1-1024)')
    parser.add_argument('-t', '--threads', type=int, default=100,
                        help='Number of threads (default: 100)')
    
    args = parser.parse_args()
    
    # Parse port range
    try:
        start_port, end_port = map(int, args.ports.split('-'))
        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
            raise ValueError("Ports must be between 1 and 65535")
        if start_port > end_port:
            raise ValueError("Start port must be less than end port")
    except ValueError as e:
        print(f"Invalid port range: {e}")
        return
    
    # Run the scan
    scanner = PortScanner(
        target=args.target,
        port_range=(start_port, end_port),
        num_threads=args.threads,
        timeout=0.5  # Half second timeout keeps things moving
    )
    
    try:
        open_ports = scanner.scan()
        
        if open_ports:
            print("Open Ports:")
            print("-" * 40)
            for port, service in open_ports:
                print(f"  {port:5d}/tcp    {service}")
        else:
            print("No open ports found in the specified range.")
            
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")


if __name__ == "__main__":
    main()