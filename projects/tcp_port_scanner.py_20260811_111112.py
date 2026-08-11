"""
Date: 2026-08-11
Created a TCP port scanner that uses threading to check common ports and attempts to grab service banners, useful for checking what's running on my local machines.
"""

#!/usr/bin/env python3
"""
Simple TCP port scanner with banner grabbing capabilities.
Scans common ports on a target host and attempts to identify services.
"""

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    A multithreaded TCP port scanner that attempts to identify services
    by grabbing banners from open ports.
    """
    
    def __init__(self, target, ports, threads=50, timeout=1.0):
        """
        Initialize the port scanner.
        
        Args:
            target: IP address or hostname to scan
            ports: List of ports to check
            threads: Number of concurrent threads to use
            timeout: Socket timeout in seconds
        """
        self.target = target
        self.ports = ports
        self.threads = threads
        self.timeout = timeout
        self.queue = Queue()
        self.open_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, port):
        """
        Attempt to connect to a single port and grab banner if possible.
        
        Args:
            port: Port number to scan
            
        Returns:
            Dictionary with port info if open, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to grab banner
                banner = None
                try:
                    # Send a simple HTTP request for common web ports
                    if port in [80, 8080, 8000, 443]:
                        sock.send(b"GET / HTTP/1.1\r\nHost: scanner\r\n\r\n")
                    
                    # Try to receive banner (some services send without prompt)
                    sock.settimeout(0.5)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                except:
                    # If banner grab fails, that's fine — we still know it's open
                    pass
                
                sock.close()
                return {'port': port, 'banner': banner}
            
            sock.close()
            return None
            
        except socket.gaierror:
            # Hostname couldn't be resolved
            return None
        except socket.error:
            # Connection error
            return None
    
    def worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        This is the function that each thread executes.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
                
            result = self.scan_port(port)
            
            if result:
                with self.lock:
                    self.open_ports.append(result)
                    # Print immediately when found for better UX
                    banner_info = f" - {result['banner'][:50]}" if result['banner'] else ""
                    print(f"[+] Port {result['port']}/tcp is open{banner_info}")
            
            self.queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        
        Returns:
            List of dictionaries containing open port information
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.threads} threads")
        print(f"[*] Scan started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Create and start worker threads
        thread_list = []
        for _ in range(self.threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            thread_list.append(thread)
        
        # Add all ports to the queue
        for port in self.ports:
            self.queue.put(port)
        
        # Wait for all tasks to complete
        self.queue.join()
        
        # Stop workers
        for _ in range(self.threads):
            self.queue.put(None)
        for thread in thread_list:
            thread.join()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x['port'])
        
        print(f"\n[*] Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Found {len(self.open_ports)} open ports\n")
        
        return self.open_ports


def get_common_ports():
    """
    Return a list of commonly used ports to scan.
    I chose these based on what I typically see in use.
    """
    return [
        20, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
        1723, 3306, 3389, 5900, 8080, 8443, 8888
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TCP Port Scanner with banner grabbing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python tcp_port_scanner.py 192.168.1.1 --ports 1-1024"
    )
    
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('--ports', help='Port range (e.g., 1-1024) or "common"', default='common')
    parser.add_argument('--threads', type=int, default=50, help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=float, default=1.0, help='Socket timeout in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Parse port specification
    if args.ports.lower() == 'common':
        ports = get_common_ports()
    elif '-' in args.ports:
        # Handle range like "1-1024"
        start, end = map(int, args.ports.split('-'))
        ports = list(range(start, end + 1))
    else:
        # Single port or comma-separated list
        ports = [int(p.strip()) for p in args.ports.split(',')]
    
    # Run the scan
    scanner = PortScanner(args.target, ports, threads=args.threads, timeout=args.timeout)
    open_ports = scanner.scan()
    
    # Summary output
    if open_ports:
        print("Open Ports Summary:")
        print("-" * 60)
        for result in open_ports:
            banner = result['banner'][:60] if result['banner'] else "No banner"
            print(f"Port {result['port']:5d}/tcp    {banner}")
    else:
        print("No open ports found.")