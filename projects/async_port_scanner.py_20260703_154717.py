"""
Date: 2026-07-03
Created a multithreaded port scanner that can check common ports or custom ranges — learned a lot about socket timeouts and thread pools.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner using threading to speed up network discovery.
Scans target host for open ports and identifies common services.
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import argparse


# Common ports to scan with their typical services
COMMON_PORTS = {
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
    8080: 'HTTP-Alt',
    8443: 'HTTPS-Alt'
}


class PortScanner:
    """
    Multithreaded port scanner that checks if ports are open on a target host.
    Uses a thread pool to scan multiple ports concurrently for speed.
    """
    
    def __init__(self, target, timeout=1.0, max_workers=100):
        """
        Initialize the scanner with target host and scanning parameters.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket timeout in seconds (lower = faster but less accurate)
            max_workers: Maximum number of concurrent threads
        """
        self.target = target
        self.timeout = timeout
        self.max_workers = max_workers
        self.open_ports = []
        self.lock = threading.Lock()  # For thread-safe list updates
        
    def resolve_target(self):
        """
        Resolve hostname to IP address.
        Returns the IP or raises exception if resolution fails.
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {self.target}")
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        Returns tuple (port, is_open, service_name) where is_open is boolean.
        
        Using connect_ex instead of connect because it returns error codes
        rather than raising exceptions, which is cleaner for port scanning.
        """
        service = COMMON_PORTS.get(port, 'Unknown')
        
        try:
            # Create a new socket for this connection attempt
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # connect_ex returns 0 if connection succeeds, error code otherwise
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                return (port, True, service)
            else:
                return (port, False, service)
                
        except socket.error:
            return (port, False, service)
    
    def scan_ports(self, ports):
        """
        Scan multiple ports concurrently using a thread pool.
        Updates self.open_ports with results.
        
        Args:
            ports: Iterable of port numbers to scan
        """
        print(f"[*] Starting scan of {self.target}")
        print(f"[*] Scanning {len(ports)} ports with {self.max_workers} threads")
        print(f"[*] Timeout set to {self.timeout}s per port\n")
        
        start_time = datetime.now()
        
        # Use ThreadPoolExecutor for clean concurrent execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all port scan jobs
            future_to_port = {executor.submit(self.scan_port, port): port 
                            for port in ports}
            
            # Process results as they complete
            for future in as_completed(future_to_port):
                port, is_open, service = future.result()
                
                if is_open:
                    with self.lock:
                        self.open_ports.append((port, service))
                    print(f"[+] Port {port:5d} OPEN  - {service}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[*] Scan completed in {duration:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open ports")
        
        return self.open_ports


def main():
    """
    Demo that scans localhost for common ports.
    In real usage you'd scan a remote host, but localhost is safe for testing.
    """
    parser = argparse.ArgumentParser(
        description='Concurrent port scanner for network reconnaissance'
    )
    parser.add_argument(
        '--target', 
        default='127.0.0.1',
        help='Target host to scan (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--ports',
        default='common',
        help='Ports to scan: "common" or range like "1-1000" (default: common)'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=0.5,
        help='Connection timeout in seconds (default: 0.5)'
    )
    
    args = parser.parse_args()
    
    # Determine which ports to scan
    if args.ports == 'common':
        ports_to_scan = list(COMMON_PORTS.keys())
    else:
        # Parse range like "1-1000"
        try:
            start, end = map(int, args.ports.split('-'))
            ports_to_scan = range(start, end + 1)
        except ValueError:
            print("[!] Invalid port range. Use format: 1-1000")
            return
    
    try:
        scanner = PortScanner(
            target=args.target,
            timeout=args.timeout,
            max_workers=100
        )
        
        # Resolve hostname first
        ip = scanner.resolve_target()
        print(f"[*] Resolved {args.target} to {ip}\n")
        
        # Run the scan
        open_ports = scanner.scan_ports(ports_to_scan)
        
        # Summary
        if open_ports:
            print("\n" + "="*50)
            print("OPEN PORTS SUMMARY:")
            print("="*50)
            for port, service in sorted(open_ports):
                print(f"  {port:5d}/tcp  {service}")
        else:
            print("\n[*] No open ports found")
            
    except ValueError as e:
        print(f"[!] Error: {e}")
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")


if __name__ == "__main__":
    main()