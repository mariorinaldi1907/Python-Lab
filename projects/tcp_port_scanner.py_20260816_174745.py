"""
Date: 2026-08-16
Created a port scanner that uses threading to check multiple ports simultaneously and attempts to grab service banners for identification.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner with Banner Grabbing
Scans a target host for open TCP ports and attempts to identify services.
"""

import socket
import sys
import threading
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    Multithreaded TCP port scanner with banner grabbing capabilities.
    """
    
    def __init__(self, target, ports, threads=50, timeout=1.0):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            ports: List of ports to scan
            threads: Number of concurrent threads (default: 50)
            timeout: Socket timeout in seconds (default: 1.0)
        """
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        
        # Queue to hold ports that need scanning
        self.queue = Queue()
        for port in self.ports:
            self.queue.put(port)
        
        # Limit threads to avoid overwhelming the system
        self.num_threads = min(threads, len(ports))
    
    def resolve_target(self):
        """
        Resolve hostname to IP address.
        
        Returns:
            IP address as string, or None if resolution fails
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            return None
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port and grab banner if possible.
        
        Args:
            port: Port number to scan
            
        Returns:
            Dictionary with port info if open, None otherwise
        """
        try:
            # Create a socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to grab banner
                banner = self.grab_banner(sock)
                sock.close()
                return {
                    'port': port,
                    'banner': banner
                }
            else:
                sock.close()
                return None
                
        except socket.error:
            return None
    
    def grab_banner(self, sock):
        """
        Attempt to receive service banner from an open socket.
        
        Args:
            sock: Connected socket object
            
        Returns:
            Banner string or None
        """
        try:
            # Some services send banner immediately
            sock.settimeout(0.5)
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return banner if banner else None
        except:
            # If that fails, try sending a generic request
            try:
                sock.send(b'\r\n')
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                return banner if banner else None
            except:
                return None
    
    def worker(self):
        """
        Worker thread that pulls ports from queue and scans them.
        """
        while not self.queue.empty():
            port = self.queue.get()
            result = self.scan_port(port)
            
            if result:
                with self.lock:
                    self.open_ports.append(result)
            
            self.queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        
        Returns:
            List of dictionaries containing open port information
        """
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Sort results by port number
        self.open_ports.sort(key=lambda x: x['port'])
        return self.open_ports


def get_common_ports():
    """
    Return a list of commonly used ports.
    
    Returns:
        List of integer port numbers
    """
    # These are the most common services I usually check
    return [
        20, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
        143, 443, 445, 993, 995, 1723, 3306, 3389, 5900,
        8080, 8443
    ]


if __name__ == "__main__":
    print("=" * 60)
    print("TCP Port Scanner with Banner Grabbing")
    print("=" * 60)
    
    # Scan localhost as a safe demo
    target = "localhost"
    
    print(f"\nTarget: {target}")
    
    scanner = PortScanner(target, get_common_ports(), threads=50, timeout=0.5)
    
    # Resolve target
    ip = scanner.resolve_target()
    if not ip:
        print(f"Error: Could not resolve {target}")
        sys.exit(1)
    
    print(f"Resolved to: {ip}")
    print(f"Scanning {len(scanner.ports)} common ports...")
    print(f"Using {scanner.num_threads} threads\n")
    
    start_time = datetime.now()
    
    # Perform scan
    open_ports = scanner.scan()
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    # Display results
    print(f"\nScan completed in {elapsed:.2f} seconds")
    print(f"Found {len(open_ports)} open port(s):\n")
    
    if open_ports:
        for result in open_ports:
            port = result['port']
            banner = result['banner']
            
            print(f"  Port {port}/tcp - OPEN")
            if banner:
                # Truncate long banners for readability
                banner_preview = banner[:80] + "..." if len(banner) > 80 else banner
                print(f"    Banner: {banner_preview}")
    else:
        print("  No open ports found on common port list.")
    
    print("\n" + "=" * 60)