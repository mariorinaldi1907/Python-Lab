"""
Date: 2026-08-31
Wrote a multi-threaded port scanner that checks common services on a target host, because I got tired of waiting for nmap when I just want quick results.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner for quick service discovery.
Uses threading to speed up scanning of common ports.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
import argparse


# Common ports I actually care about when debugging
COMMON_PORTS = {
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
    8443: "HTTPS-Alt",
    27017: "MongoDB",
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target host.
    """
    
    def __init__(self, target, ports, timeout=1.0, threads=100):
        """
        Initialize the scanner with target and configuration.
        
        Args:
            target: Hostname or IP address to scan
            ports: List of port numbers to check
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            threads: Number of concurrent threads (more = faster but resource intensive)
        """
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()
        
    def _resolve_target(self):
        """
        Resolve hostname to IP address.
        Returns the IP or raises socket.gaierror if invalid.
        """
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {self.target}")
    
    def _scan_port(self, port):
        """
        Attempt to connect to a single port.
        Adds to open_ports list if connection succeeds.
        """
        try:
            # Create a socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            # connect_ex returns 0 on success
            if result == 0:
                with self.lock:
                    service = COMMON_PORTS.get(port, "Unknown")
                    self.open_ports.append((port, service))
        except socket.error:
            # Port is closed or unreachable
            pass
    
    def _worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        Runs until the queue is empty.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
            self._scan_port(port)
            self.queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        Returns a sorted list of (port, service) tuples for open ports.
        """
        # Resolve the target first
        ip = self._resolve_target()
        print(f"Scanning {self.target} ({ip})...")
        print(f"Using {self.threads} threads with {self.timeout}s timeout\n")
        
        start_time = datetime.now()
        
        # Add all ports to the queue
        for port in self.ports:
            self.queue.put(port)
        
        # Create and start worker threads
        workers = []
        for _ in range(min(self.threads, len(self.ports))):
            t = threading.Thread(target=self._worker)
            t.start()
            workers.append(t)
        
        # Wait for all tasks to complete
        self.queue.join()
        
        # Stop workers
        for _ in workers:
            self.queue.put(None)
        for t in workers:
            t.join()
        
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        
        # Sort results by port number
        self.open_ports.sort()
        
        print(f"Scan completed in {elapsed:.2f} seconds")
        print(f"Found {len(self.open_ports)} open port(s)\n")
        
        return self.open_ports


def print_results(open_ports):
    """
    Pretty print the scan results.
    """
    if not open_ports:
        print("No open ports found.")
        return
    
    print("PORT      SERVICE")
    print("-" * 30)
    for port, service in open_ports:
        print(f"{port:<9} {service}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Concurrent port scanner for quick service discovery"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="localhost",
        help="Target hostname or IP (default: localhost)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all common ports instead of just localhost demo"
    )
    
    args = parser.parse_args()
    
    # For demo purposes, scan a smaller range on localhost
    # In real usage, you'd scan the common ports or a custom range
    if args.target == "localhost" and not args.all:
        print("=== Demo Mode: Scanning localhost common ports ===\n")
        ports_to_scan = list(COMMON_PORTS.keys())
    else:
        ports_to_scan = list(COMMON_PORTS.keys())
    
    scanner = PortScanner(
        target=args.target,
        ports=ports_to_scan,
        timeout=0.5,
        threads=50
    )
    
    try:
        results = scanner.scan()
        print_results(results)
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")