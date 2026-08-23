"""
Date: 2026-08-23
Wrote a port scanner that checks common services across a target host, using threading to speed things up and attempting to grab service banners when possible.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner - Mario's Network Utilities
Scans a target host for open TCP ports and attempts to grab service banners.
Uses threading to make it reasonably fast without hammering the network too hard.
"""

import socket
import threading
import argparse
from queue import Queue
from typing import List, Tuple, Optional


# Common ports I usually check - could expand this list but these are the big ones
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


class PortScanner:
    """
    Handles the actual port scanning with configurable threading.
    I wanted this to be fast but not overwhelm my own network or trigger rate limits.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 10):
        """
        Initialize the scanner with target host and performance settings.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, port: int) -> Optional[Tuple[int, str, str]]:
        """
        Attempt to connect to a single port and grab banner if possible.
        
        Returns tuple of (port, service_name, banner) if open, None if closed.
        Banner grabbing doesn't always work but it's worth trying.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                service_name = COMMON_PORTS.get(port, "unknown")
                banner = ""
                
                # Try to grab a banner - some services send data immediately
                try:
                    sock.send(b'\r\n')  # Some services need a nudge
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                except:
                    # Many services won't respond to random data, that's fine
                    pass
                
                sock.close()
                return (port, service_name, banner)
            
            sock.close()
            return None
            
        except socket.gaierror:
            # Couldn't resolve hostname
            return None
        except socket.error:
            # Connection error, port likely closed or filtered
            return None
    
    def worker(self, port_queue: Queue):
        """
        Worker thread that pulls ports from queue and scans them.
        Using a queue pattern here makes it easy to distribute work.
        """
        while not port_queue.empty():
            port = port_queue.get()
            result = self.scan_port(port)
            
            if result:
                with self.lock:
                    self.open_ports.append(result)
            
            port_queue.task_done()
    
    def scan(self, ports: List[int]) -> List[Tuple[int, str, str]]:
        """
        Scan multiple ports using thread pool.
        
        Args:
            ports: List of port numbers to scan
            
        Returns:
            List of tuples (port, service, banner) for open ports
        """
        port_queue = Queue()
        for port in ports:
            port_queue.put(port)
        
        # Spin up worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self.worker, args=(port_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all scanning to complete
        for thread in threads:
            thread.join()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        return self.open_ports


def resolve_target(target: str) -> str:
    """
    Resolve hostname to IP address for display purposes.
    Keeps the original target for actual scanning.
    """
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return "Unable to resolve"


def print_results(target: str, open_ports: List[Tuple[int, str, str]]):
    """
    Pretty print the scan results.
    I like having clear output that shows what was found.
    """
    print(f"\n{'='*70}")
    print(f"Scan Results for: {target}")
    print(f"{'='*70}\n")
    
    if not open_ports:
        print("No open ports found in the scanned range.")
        return
    
    print(f"Found {len(open_ports)} open port(s):\n")
    print(f"{'PORT':<8} {'SERVICE':<20} {'BANNER':<40}")
    print(f"{'-'*70}")
    
    for port, service, banner in open_ports:
        # Truncate long banners so output stays readable
        banner_display = banner[:37] + "..." if len(banner) > 40 else banner
        print(f"{port:<8} {service:<20} {banner_display:<40}")


if __name__ == "__main__":
    # Demo: scan localhost for common services
    # In real use, you'd pass target via command line args
    
    print("Mario's TCP Port Scanner")
    print("Scanning localhost for common services...\n")
    
    target_host = "localhost"
    
    # Resolve and display target info
    ip_address = resolve_target(target_host)
    print(f"Target: {target_host} ({ip_address})")
    print(f"Scanning {len(COMMON_PORTS)} common ports with 10 threads...")
    
    # Create scanner and run it
    scanner = PortScanner(target_host, timeout=0.5, num_threads=10)
    ports_to_scan = list(COMMON_PORTS.keys())
    
    results = scanner.scan(ports_to_scan)
    print_results(target_host, results)
    
    # Quick example of scanning a custom range
    print("\n" + "="*70)
    print("Bonus: Scanning localhost ports 8000-8010...")
    print("="*70)
    
    custom_scanner = PortScanner(target_host, timeout=0.3, num_threads=5)
    custom_results = custom_scanner.scan(list(range(8000, 8011)))
    
    if custom_results:
        print(f"\nFound {len(custom_results)} open port(s) in range 8000-8010:")
        for port, service, banner in custom_results:
            print(f"  Port {port}: {service}")
    else:
        print("\nNo open ports found in range 8000-8010")