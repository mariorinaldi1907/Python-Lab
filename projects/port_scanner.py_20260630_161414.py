"""
Date: 2026-06-30
Wrote a multi-threaded port scanner because I got tired of waiting for nmap when I just want to check a few common ports on my local network.
"""

#!/usr/bin/env python3
"""
Port scanner with threading support and service name resolution.
Uses socket to probe ports and determines if they're open/closed.
"""

import socket
import threading
import argparse
import time
from queue import Queue
from typing import List, Tuple


class PortScanner:
    """
    Multi-threaded port scanner that probes TCP ports on a target host.
    
    Uses a thread pool pattern to scan multiple ports concurrently,
    which significantly speeds things up compared to sequential scanning.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 10):
        """
        Initialize the scanner with target host and threading config.
        
        Args:
            target: IP address or hostname to scan
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()  # Protect the open_ports list
        
    def get_service_name(self, port: int) -> str:
        """
        Try to resolve the service name for a given port.
        
        Uses socket.getservbyport which looks up /etc/services.
        Returns "unknown" if the port isn't in the services database.
        """
        try:
            return socket.getservbyport(port, 'tcp')
        except OSError:
            return "unknown"
    
    def scan_port(self, port: int) -> Tuple[int, bool, str]:
        """
        Attempt to connect to a single port on the target.
        
        Returns a tuple of (port_number, is_open, service_name).
        The connection attempt itself tells us if the port is open.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # connect_ex returns 0 on success, error code otherwise
            result = sock.connect_ex((self.target, port))
            is_open = (result == 0)
            service = self.get_service_name(port) if is_open else ""
            return (port, is_open, service)
        except socket.gaierror:
            # DNS resolution failed
            return (port, False, "")
        except socket.error:
            # Some other socket error occurred
            return (port, False, "")
        finally:
            sock.close()
    
    def worker(self, queue: Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        This is the function each thread runs. It keeps pulling from
        the queue until there's nothing left to scan.
        """
        while not queue.empty():
            port = queue.get()
            port_num, is_open, service = self.scan_port(port)
            
            if is_open:
                with self.lock:
                    self.open_ports.append((port_num, service))
            
            queue.task_done()
    
    def scan(self, ports: List[int]) -> List[Tuple[int, str]]:
        """
        Scan a list of ports using multiple threads.
        
        Creates a queue with all ports, spawns worker threads,
        and waits for completion. Returns sorted list of open ports.
        """
        queue = Queue()
        
        # Load all ports into the queue
        for port in ports:
            queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all tasks to complete
        queue.join()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        return self.open_ports


def parse_port_range(port_str: str) -> List[int]:
    """
    Parse port specifications like "80,443,8000-8010".
    
    Supports individual ports (80), ranges (1000-2000),
    and comma-separated combinations of both.
    """
    ports = []
    parts = port_str.split(',')
    
    for part in parts:
        if '-' in part:
            # Handle range like "8000-8010"
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            # Single port
            ports.append(int(part))
    
    return ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan TCP ports on a target host"
    )
    parser.add_argument(
        "target",
        help="Target IP address or hostname"
    )
    parser.add_argument(
        "-p", "--ports",
        default="20-25,80,443,3000,3306,5432,6379,8000-8080,27017",
        help="Ports to scan (e.g., '80,443,8000-8010')"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout in seconds"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=50,
        help="Number of worker threads"
    )
    
    args = parser.parse_args()
    
    print(f"Starting scan of {args.target}...")
    print(f"Timeout: {args.timeout}s | Workers: {args.workers}")
    
    ports = parse_port_range(args.ports)
    print(f"Scanning {len(ports)} ports...\n")
    
    start_time = time.time()
    
    scanner = PortScanner(
        target=args.target,
        timeout=args.timeout,
        num_threads=args.workers
    )
    
    open_ports = scanner.scan(ports)
    
    elapsed = time.time() - start_time
    
    print(f"Scan completed in {elapsed:.2f} seconds\n")
    
    if open_ports:
        print(f"Found {len(open_ports)} open port(s):\n")
        print(f"{'PORT':<10} {'SERVICE':<20}")
        print("-" * 30)
        for port, service in open_ports:
            service_str = service if service != "unknown" else ""
            print(f"{port:<10} {service_str:<20}")
    else:
        print("No open ports found.")