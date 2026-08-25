"""
Date: 2026-08-25
Made a multi-threaded port scanner that probes common ports and attempts basic service fingerprinting by analyzing response banners.
"""

#!/usr/bin/env python3
"""
A simple port scanner with basic service detection.
Scans a target host for open ports and tries to identify running services.
"""

import socket
import threading
import argparse
from datetime import datetime
from queue import Queue

# Common ports to scan if no range is specified
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]

# Simple service signatures - checks banner responses
SERVICE_SIGNATURES = {
    'SSH': [b'SSH'],
    'HTTP': [b'HTTP/', b'<html', b'<HTML'],
    'FTP': [b'220', b'FTP'],
    'SMTP': [b'220', b'SMTP'],
    'MySQL': [b'mysql', b'MariaDB'],
    'PostgreSQL': [b'PostgreSQL'],
}


class PortScanner:
    """
    Multi-threaded port scanner that checks which ports are open
    and attempts to identify the service running on each port.
    """
    
    def __init__(self, target, ports, timeout=1.0, threads=50):
        """
        Initialize the port scanner.
        
        Args:
            target: Target hostname or IP address
            ports: List of ports to scan
            timeout: Socket timeout in seconds
            threads: Number of worker threads to use
        """
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()
        
    def resolve_target(self):
        """
        Resolve the target hostname to an IP address.
        
        Returns:
            IP address as string, or None if resolution fails
        """
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            return None
    
    def grab_banner(self, port):
        """
        Attempt to grab a service banner from the port.
        Sends a generic probe and reads the response.
        
        Args:
            port: Port number to probe
            
        Returns:
            Banner string or None if no banner received
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target, port))
            
            # Try sending a generic probe - some services respond without input
            try:
                sock.send(b'HELLO\r\n')
            except:
                pass
            
            # Try to receive banner
            banner = sock.recv(1024)
            sock.close()
            return banner.decode('utf-8', errors='ignore').strip()
        except:
            return None
    
    def identify_service(self, banner):
        """
        Attempt to identify service from banner response.
        
        Args:
            banner: Banner bytes received from service
            
        Returns:
            Service name or 'Unknown'
        """
        if not banner:
            return 'Unknown'
        
        banner_bytes = banner.encode('utf-8', errors='ignore')
        
        for service, signatures in SERVICE_SIGNATURES.items():
            for sig in signatures:
                if sig in banner_bytes:
                    return service
        
        return 'Unknown'
    
    def scan_port(self, port):
        """
        Scan a single port to check if it's open.
        If open, attempt to grab banner and identify service.
        
        Args:
            port: Port number to scan
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                # Port is open - try to identify service
                banner = self.grab_banner(port)
                service = self.identify_service(banner) if banner else 'Unknown'
                
                with self.lock:
                    self.open_ports.append({
                        'port': port,
                        'service': service,
                        'banner': banner[:50] if banner else None  # Truncate long banners
                    })
        except Exception as e:
            # Connection errors are expected for closed ports
            pass
    
    def worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
            self.scan_port(port)
            self.queue.task_done()
    
    def scan(self):
        """
        Execute the port scan using multiple threads.
        
        Returns:
            List of dictionaries containing open port information
        """
        # Start worker threads
        workers = []
        for _ in range(min(self.threads, len(self.ports))):
            t = threading.Thread(target=self.worker)
            t.start()
            workers.append(t)
        
        # Queue all ports to scan
        for port in self.ports:
            self.queue.put(port)
        
        # Wait for all scans to complete
        self.queue.join()
        
        # Stop workers
        for _ in workers:
            self.queue.put(None)
        for t in workers:
            t.join()
        
        # Sort results by port number
        self.open_ports.sort(key=lambda x: x['port'])
        return self.open_ports


if __name__ == "__main__":
    print("=" * 60)
    print("Simple Port Scanner with Service Detection")
    print("=" * 60)
    
    # Demo: scan localhost common ports
    target = "localhost"
    print(f"\nTarget: {target}")
    
    scanner = PortScanner(target, COMMON_PORTS, timeout=0.5, threads=20)
    
    # Resolve target
    ip = scanner.resolve_target()
    if not ip:
        print(f"Error: Could not resolve {target}")
        exit(1)
    
    print(f"Resolved IP: {ip}")
    print(f"Scanning {len(COMMON_PORTS)} common ports...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run the scan
    start = datetime.now()
    results = scanner.scan()
    elapsed = (datetime.now() - start).total_seconds()
    
    # Display results
    if results:
        print(f"Found {len(results)} open port(s):\n")
        print(f"{'PORT':<8} {'SERVICE':<15} {'BANNER'}")
        print("-" * 60)
        for r in results:
            banner = r['banner'] if r['banner'] else '-'
            print(f"{r['port']:<8} {r['service']:<15} {banner}")
    else:
        print("No open ports found.")
    
    print(f"\nScan completed in {elapsed:.2f} seconds")