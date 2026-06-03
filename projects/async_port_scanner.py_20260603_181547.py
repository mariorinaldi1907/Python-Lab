"""
Date: 2026-06-03
Created a multi-threaded port scanner that can check common ports on any host — helps me debug network issues on my homelab.
"""

#!/usr/bin/env python3
"""
Async Port Scanner
==================
A simple multi-threaded port scanner that checks which ports are open on a target host.
I got tired of waiting for nmap to install on every new machine, so I built this.
"""

import socket
import threading
import argparse
import time
from queue import Queue
from typing import List, Tuple


# Common ports that I usually care about when debugging services
COMMON_PORTS = {
    20: 'FTP-DATA',
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    143: 'IMAP',
    443: 'HTTPS',
    445: 'SMB',
    3306: 'MySQL',
    3389: 'RDP',
    5432: 'PostgreSQL',
    5900: 'VNC',
    6379: 'Redis',
    8080: 'HTTP-Alt',
    8443: 'HTTPS-Alt',
    9200: 'Elasticsearch',
    27017: 'MongoDB',
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target host.
    Uses a queue-based worker pool to scan multiple ports concurrently.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, threads: int = 50):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds (lower = faster but less reliable)
            threads: Number of worker threads (more = faster but may hit system limits)
        """
        self.target = target
        self.timeout = timeout
        self.threads = threads
        self.open_ports: List[Tuple[int, str]] = []
        self.lock = threading.Lock()
        
    def scan_port(self, port: int) -> bool:
        """
        Attempt to connect to a single port.
        
        Args:
            port: Port number to scan
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # Create a socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            return result == 0  # 0 means connection succeeded
        except socket.error:
            return False
    
    def worker(self, queue: Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        Args:
            queue: Thread-safe queue containing port numbers to scan
        """
        while True:
            port = queue.get()
            if port is None:  # Poison pill to stop worker
                break
                
            if self.scan_port(port):
                service = COMMON_PORTS.get(port, 'Unknown')
                with self.lock:  # Thread-safe access to shared list
                    self.open_ports.append((port, service))
                    print(f"[+] Port {port} ({service}) is open")
            
            queue.task_done()
    
    def scan(self, ports: List[int]) -> List[Tuple[int, str]]:
        """
        Scan a list of ports using multiple worker threads.
        
        Args:
            ports: List of port numbers to scan
            
        Returns:
            List of tuples (port, service_name) for open ports
        """
        queue = Queue()
        
        # Start worker threads
        workers = []
        for _ in range(self.threads):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.daemon = True
            thread.start()
            workers.append(thread)
        
        # Add all ports to the queue
        for port in ports:
            queue.put(port)
        
        # Wait for all tasks to complete
        queue.join()
        
        # Stop workers with poison pills
        for _ in range(self.threads):
            queue.put(None)
        
        for worker in workers:
            worker.join()
        
        return sorted(self.open_ports, key=lambda x: x[0])


def main():
    """
    Demo the port scanner with command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Scan ports on a target host to find open services'
    )
    parser.add_argument('target', help='Target hostname or IP address')
    parser.add_argument(
        '-p', '--ports',
        help='Port range (e.g., "1-100" or "80,443,8080")',
        default='common'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=1.0,
        help='Connection timeout in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=50,
        help='Number of threads (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Parse port specification
    if args.ports == 'common':
        ports = list(COMMON_PORTS.keys())
    elif '-' in args.ports:
        start, end = map(int, args.ports.split('-'))
        ports = list(range(start, end + 1))
    else:
        ports = [int(p) for p in args.ports.split(',')]
    
    print(f"[*] Starting scan on {args.target}")
    print(f"[*] Scanning {len(ports)} ports with {args.threads} threads")
    print(f"[*] Timeout: {args.timeout}s\n")
    
    start_time = time.time()
    
    scanner = PortScanner(args.target, timeout=args.timeout, threads=args.threads)
    open_ports = scanner.scan(ports)
    
    elapsed = time.time() - start_time
    
    print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
    print(f"[*] Found {len(open_ports)} open ports:")
    
    if open_ports:
        for port, service in open_ports:
            print(f"    {port:5d} - {service}")
    else:
        print("    (none)")


if __name__ == "__main__":
    main()