"""
Date: 2026-07-26
Built a threaded port scanner that checks common ports on a target host and identifies running services — wanted something quick for checking which services are up on my local network.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded port scanner.
Scans common ports on a target host to see what services might be running.
"""

import socket
import threading
from queue import Queue
from typing import List, Tuple
import time


# Common ports and their typical services
COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
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
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    9200: "Elasticsearch",
    27017: "MongoDB",
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target host.
    
    Uses a thread pool to scan multiple ports concurrently for speed.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
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
            # Create a TCP socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            # connect_ex returns 0 on success
            return result == 0
        except socket.error:
            return False
    
    def worker(self, queue: Queue):
        """
        Worker thread that pulls ports from queue and scans them.
        
        Args:
            queue: Queue containing port numbers to scan
        """
        while not queue.empty():
            port = queue.get()
            if self.scan_port(port):
                service = COMMON_PORTS.get(port, "Unknown")
                # Thread-safe append to results
                with self.lock:
                    self.open_ports.append((port, service))
                    print(f"[+] Port {port} is open - {service}")
            queue.task_done()
    
    def scan(self, ports: List[int]) -> List[Tuple[int, str]]:
        """
        Scan a list of ports on the target host.
        
        Args:
            ports: List of port numbers to scan
            
        Returns:
            List of tuples (port, service_name) for open ports
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(ports)} ports with {self.num_threads} threads...\n")
        
        # Put all ports in a queue for workers to process
        queue = Queue()
        for port in ports:
            queue.put(port)
        
        # Start worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        queue.join()
        
        return sorted(self.open_ports)


def resolve_hostname(target: str) -> str:
    """
    Resolve a hostname to an IP address.
    
    Args:
        target: Hostname or IP address
        
    Returns:
        IP address as string
    """
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {target}")


if __name__ == "__main__":
    # Demo: scan localhost for common services
    target_host = "localhost"
    
    print("=" * 60)
    print("Simple Port Scanner")
    print("=" * 60)
    
    try:
        # Resolve the target hostname
        ip_address = resolve_hostname(target_host)
        print(f"[*] Target: {target_host} ({ip_address})")
        
        # Create scanner instance
        # Using shorter timeout and fewer threads for demo since we're scanning localhost
        scanner = PortScanner(target=ip_address, timeout=0.5, num_threads=20)
        
        # Scan all common ports
        ports_to_scan = list(COMMON_PORTS.keys())
        
        start_time = time.time()
        open_ports = scanner.scan(ports_to_scan)
        elapsed = time.time() - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Scan complete in {elapsed:.2f} seconds")
        print(f"Found {len(open_ports)} open port(s):")
        
        if open_ports:
            for port, service in open_ports:
                print(f"  - {port:5d}/tcp  {service}")
        else:
            print("  No open ports found in the common ports list.")
        
        print("=" * 60)
        
    except ValueError as e:
        print(f"[!] Error: {e}")
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")