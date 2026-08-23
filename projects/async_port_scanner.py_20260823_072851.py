"""
Date: 2026-08-23
Created a multithreaded port scanner that can quickly check common ports or custom ranges — helps me audit my local network and dev servers.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner using threading to check multiple ports simultaneously.
I built this to quickly audit what's running on my dev machines and containers.
"""

import socket
import threading
from datetime import datetime
from queue import Queue
import argparse
import sys


# Common ports that I usually want to check on servers
COMMON_PORTS = {
    20: "FTP Data",
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
    8000: "HTTP Alt",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt",
    27017: "MongoDB",
}


class PortScanner:
    """
    Multithreaded port scanner that checks which ports are open on a target host.
    Uses a queue to distribute work across threads for faster scanning.
    """
    
    def __init__(self, target, ports, num_threads=50, timeout=1.0):
        """
        Initialize the scanner with target and configuration.
        
        Args:
            target: Hostname or IP address to scan
            ports: List of port numbers to check
            num_threads: Number of concurrent scanning threads
            timeout: Socket connection timeout in seconds
        """
        self.target = target
        self.ports = ports
        self.num_threads = num_threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        self.port_queue = Queue()
        
    def _resolve_target(self):
        """
        Resolve hostname to IP address.
        Returns the IP or raises an exception if resolution fails.
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {self.target}")
    
    def _scan_port(self, port):
        """
        Attempt to connect to a single port.
        If successful, the port is open and we record it.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.ip, port))
            
            if result == 0:
                # Port is open, try to grab the service banner if available
                service = COMMON_PORTS.get(port, "Unknown")
                with self.lock:
                    self.open_ports.append((port, service))
            
            sock.close()
            
        except socket.error:
            # Connection failed, port is closed or filtered
            pass
    
    def _worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        Keeps running until the queue is empty.
        """
        while not self.port_queue.empty():
            port = self.port_queue.get()
            self._scan_port(port)
            self.port_queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        Returns a sorted list of (port, service) tuples for open ports.
        """
        print(f"[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.num_threads} threads")
        
        # Resolve the target to an IP
        self.ip = self._resolve_target()
        print(f"[*] Resolved {self.target} to {self.ip}")
        
        start_time = datetime.now()
        
        # Fill the queue with ports to scan
        for port in self.ports:
            self.port_queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sort results by port number
        self.open_ports.sort(key=lambda x: x[0])
        
        print(f"\n[*] Scan completed in {duration:.2f} seconds")
        return self.open_ports


def print_results(target, open_ports):
    """
    Pretty print the scan results showing open ports and their services.
    """
    print(f"\n{'='*60}")
    print(f"Scan Results for {target}")
    print(f"{'='*60}")
    
    if not open_ports:
        print("No open ports found.")
    else:
        print(f"Found {len(open_ports)} open port(s):\n")
        print(f"{'PORT':<10} {'SERVICE':<20}")
        print("-" * 30)
        for port, service in open_ports:
            print(f"{port:<10} {service:<20}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Multithreaded port scanner for network reconnaissance"
    )
    parser.add_argument(
        "target",
        help="Target hostname or IP address"
    )
    parser.add_argument(
        "-p", "--ports",
        help="Port range (e.g., 1-1024) or 'common' for common ports",
        default="common"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=50,
        help="Number of threads to use (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Determine which ports to scan
    if args.ports.lower() == "common":
        ports = list(COMMON_PORTS.keys())
    elif "-" in args.ports:
        # Parse range like "1-1024"
        start, end = map(int, args.ports.split("-"))
        ports = list(range(start, end + 1))
    else:
        # Single port
        ports = [int(args.ports)]
    
    try:
        scanner = PortScanner(
            target=args.target,
            ports=ports,
            num_threads=args.threads,
            timeout=1.0
        )
        
        open_ports = scanner.scan()
        print_results(args.target, open_ports)
        
    except ValueError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)