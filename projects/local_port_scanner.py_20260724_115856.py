"""
Date: 2026-07-24
Wrote a multithreaded port scanner to quickly find open ports on local machines — helps me see what services I have exposed during dev work.
"""

#!/usr/bin/env python3
"""
Local Port Scanner
A simple multithreaded port scanner to check which ports are open on a target host.
I built this to quickly audit what services are running on my local dev machines.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
import argparse


class PortScanner:
    """
    Handles concurrent port scanning with configurable thread count.
    Uses a queue to distribute work across threads efficiently.
    """
    
    def __init__(self, target, ports, threads=50, timeout=1.0):
        """
        Initialize the scanner with target and configuration.
        
        Args:
            target: hostname or IP address to scan
            ports: list of port numbers to check
            threads: number of concurrent scanning threads
            timeout: socket timeout in seconds
        """
        self.target = target
        self.ports = ports
        self.threads = threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()
        
    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        Returns True if port is open, False otherwise.
        
        Why socket.AF_INET? Because I'm scanning IPv4 addresses.
        SOCK_STREAM gives us TCP, which is what most services use.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            return result == 0
        except socket.error:
            return False
    
    def worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        This runs continuously until the queue is empty.
        """
        while not self.queue.empty():
            port = self.queue.get()
            if self.scan_port(port):
                # Using a lock here because multiple threads write to open_ports
                with self.lock:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is open")
            self.queue.task_done()
    
    def run(self):
        """
        Execute the scan by spawning worker threads.
        Returns a sorted list of open ports.
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.threads} threads")
        start_time = datetime.now()
        
        # Fill the queue with all ports to scan
        for port in self.ports:
            self.queue.put(port)
        
        # Spawn and start worker threads
        thread_list = []
        for _ in range(self.threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            thread_list.append(thread)
        
        # Wait for all threads to complete
        for thread in thread_list:
            thread.join()
        
        elapsed = datetime.now() - start_time
        print(f"\n[*] Scan completed in {elapsed.total_seconds():.2f} seconds")
        
        return sorted(self.open_ports)


def get_service_name(port):
    """
    Try to get the common service name for a port number.
    Falls back to 'unknown' if the port isn't in the services database.
    """
    try:
        return socket.getservbyport(port)
    except OSError:
        return "unknown"


def parse_port_range(port_string):
    """
    Parse a port specification like '80,443,8000-8010' into a list of integers.
    
    Args:
        port_string: comma-separated ports and ranges (e.g., '22,80,443,8000-8100')
    
    Returns:
        List of port numbers
    """
    ports = []
    for part in port_string.split(','):
        if '-' in part:
            # Handle range like '8000-8010'
            start, end = part.split('-')
            ports.extend(range(int(start), int(end) + 1))
        else:
            # Single port
            ports.append(int(part))
    return ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan ports on a target host to find open services"
    )
    parser.add_argument(
        "target",
        nargs='?',
        default="localhost",
        help="Target hostname or IP (default: localhost)"
    )
    parser.add_argument(
        "-p", "--ports",
        default="20-1024",
        help="Ports to scan: single, comma-separated, or ranges (default: 20-1024)"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=50,
        help="Number of concurrent threads (default: 50)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Socket timeout in seconds (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    # Resolve the target to an IP
    try:
        target_ip = socket.gethostbyname(args.target)
        print(f"[*] Resolving {args.target} -> {target_ip}")
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {args.target}")
        exit(1)
    
    # Parse the port specification
    ports = parse_port_range(args.ports)
    
    # Run the scan
    scanner = PortScanner(target_ip, ports, args.threads, args.timeout)
    open_ports = scanner.run()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Scan Report for {args.target} ({target_ip})")
    print(f"{'='*50}")
    
    if open_ports:
        print(f"\nFound {len(open_ports)} open port(s):\n")
        for port in open_ports:
            service = get_service_name(port)
            print(f"  {port:5d}/tcp    {service}")
    else:
        print("\nNo open ports found in the specified range.")
    
    print()