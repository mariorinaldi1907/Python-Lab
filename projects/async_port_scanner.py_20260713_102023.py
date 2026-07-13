"""
Date: 2026-07-13
Created a concurrent port scanner to quickly check which services are running on a target host — helps me debug my homelab setup.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner to quickly identify open ports on a target host.
Uses threading to speed up the scanning process significantly.
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys


class PortScanner:
    """
    A multi-threaded port scanner that checks which ports are open on a target host.
    """

    def __init__(self, target, timeout=1.0, max_workers=100):
        """
        Initialize the scanner with target host and scanning parameters.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            max_workers: Number of concurrent threads (more = faster but more resource-intensive)
        """
        self.target = target
        self.timeout = timeout
        self.max_workers = max_workers
        self.open_ports = []
        self.lock = threading.Lock()  # Thread-safe list updates
        
        # Resolve the target hostname to IP address
        try:
            self.target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")

    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        
        Args:
            port: Port number to scan
            
        Returns:
            Tuple of (port, is_open, service_name)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Attempt connection - if successful, port is open
            result = sock.connect_ex((self.target_ip, port))
            if result == 0:
                # Try to get the service name for this port
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "unknown"
                return (port, True, service)
        except socket.error:
            pass
        finally:
            sock.close()
        
        return (port, False, None)

    def scan_range(self, start_port, end_port):
        """
        Scan a range of ports concurrently.
        
        Args:
            start_port: First port to scan (inclusive)
            end_port: Last port to scan (inclusive)
            
        Returns:
            List of tuples: (port, service_name) for open ports
        """
        print(f"[*] Starting scan of {self.target} ({self.target_ip})")
        print(f"[*] Scanning ports {start_port}-{end_port} with {self.max_workers} threads")
        
        start_time = datetime.now()
        
        # Use ThreadPoolExecutor for efficient concurrent scanning
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all port scan tasks
            future_to_port = {
                executor.submit(self.scan_port, port): port 
                for port in range(start_port, end_port + 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_port):
                port, is_open, service = future.result()
                if is_open:
                    with self.lock:
                        self.open_ports.append((port, service))
                        print(f"[+] Port {port} is OPEN - {service}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sort results by port number for clean output
        self.open_ports.sort(key=lambda x: x[0])
        
        print(f"\n[*] Scan completed in {duration:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open port(s)")
        
        return self.open_ports


def scan_common_ports(target):
    """
    Scan the most commonly used ports on a target.
    
    Args:
        target: Hostname or IP to scan
        
    Returns:
        List of open ports
    """
    # These are the most common ports I usually care about
    common_ports = [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        8080,  # HTTP Alternate
        8443,  # HTTPS Alternate
    ]
    
    scanner = PortScanner(target, timeout=0.5, max_workers=50)
    
    print(f"[*] Quick scan of common ports on {target}")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scanner.scan_port, port): port for port in common_ports}
        
        open_ports = []
        for future in as_completed(futures):
            port, is_open, service = future.result()
            if is_open:
                open_ports.append((port, service))
                print(f"[+] Port {port} is OPEN - {service}")
    
    return sorted(open_ports, key=lambda x: x[0])


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-threaded Port Scanner")
    print("=" * 60)
    
    # Demo 1: Scan common ports on localhost
    # This should find whatever services you have running locally
    print("\n--- Scanning common ports on localhost ---\n")
    try:
        open_ports = scan_common_ports("localhost")
        if open_ports:
            print(f"\nSummary: Found {len(open_ports)} open port(s) on localhost")
            for port, service in open_ports:
                print(f"  - {port}/{service}")
        else:
            print("\nNo common ports found open on localhost")
    except Exception as e:
        print(f"Error: {e}")
    
    # Demo 2: Full range scan on a smaller port range
    print("\n\n--- Scanning port range 1-100 on localhost ---\n")
    try:
        scanner = PortScanner("localhost", timeout=0.3, max_workers=50)
        scanner.scan_range(1, 100)
    except Exception as e:
        print(f"Error: {e}")