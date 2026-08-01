"""
Date: 2026-08-01
Created a concurrent port scanner using threading to check common ports quickly — learned a lot about socket timeouts and thread pooling.
"""

#!/usr/bin/env python3
"""
Simple multithreaded port scanner for checking open ports on a target host.
Uses Python's threading to speed up scanning without external dependencies.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
import sys


class PortScanner:
    """
    A concurrent port scanner that checks which ports are open on a target host.
    
    Uses a thread pool to scan multiple ports simultaneously, which is way faster
    than sequential scanning but doesn't overwhelm the system.
    """
    
    def __init__(self, target, timeout=1.0, num_threads=50):
        """
        Initialize the scanner with target host and scanning parameters.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds (default 1.0)
            num_threads: Number of concurrent threads (default 50)
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()  # Protect the open_ports list from race conditions
        
        # Try to resolve the hostname to an IP
        try:
            self.ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port and record if it's open.
        
        Args:
            port: Port number to scan
        """
        try:
            # Create a TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Try to connect - if successful, port is open
            result = sock.connect_ex((self.ip, port))
            
            if result == 0:
                # Thread-safe append to the results list
                with self.lock:
                    self.open_ports.append(port)
                    print(f"[+] Port {port} is OPEN")
            
            sock.close()
            
        except socket.error:
            # Connection failed, port is closed or filtered
            pass
    
    def worker(self, queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        Args:
            queue: Queue containing port numbers to scan
        """
        while True:
            port = queue.get()
            if port is None:
                break
            self.scan_port(port)
            queue.task_done()
    
    def scan(self, ports):
        """
        Scan a list of ports using multiple threads.
        
        Args:
            ports: List or range of port numbers to scan
            
        Returns:
            Sorted list of open ports
        """
        print(f"\n[*] Starting scan on {self.target} ({self.ip})")
        print(f"[*] Timeout: {self.timeout}s | Threads: {self.num_threads}")
        print(f"[*] Scanning {len(list(ports))} ports...\n")
        
        start_time = datetime.now()
        
        # Create a queue and fill it with port numbers
        queue = Queue()
        for port in ports:
            queue.put(port)
        
        # Start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all ports to be scanned
        queue.join()
        
        # Stop workers
        for _ in range(self.num_threads):
            queue.put(None)
        for thread in threads:
            thread.join()
        
        elapsed = datetime.now() - start_time
        
        print(f"\n[*] Scan completed in {elapsed.total_seconds():.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open ports\n")
        
        return sorted(self.open_ports)


def get_common_ports():
    """
    Return a list of commonly used ports to scan.
    
    I chose these based on the most frequently seen services in the wild.
    """
    return [
        20, 21,      # FTP
        22,          # SSH
        23,          # Telnet
        25,          # SMTP
        53,          # DNS
        80, 443,     # HTTP/HTTPS
        110, 143,    # POP3/IMAP
        445,         # SMB
        3306,        # MySQL
        3389,        # RDP
        5432,        # PostgreSQL
        5900,        # VNC
        8080, 8443   # Alt HTTP/HTTPS
    ]


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    target = "localhost"
    
    print("=" * 60)
    print("PORT SCANNER DEMO")
    print("=" * 60)
    
    try:
        scanner = PortScanner(target, timeout=0.5, num_threads=20)
        
        # Scan common ports
        common_ports = get_common_ports()
        open_ports = scanner.scan(common_ports)
        
        if open_ports:
            print("Open ports found:")
            for port in open_ports:
                print(f"  → {port}")
        else:
            print("No open ports found in the common ports list.")
        
        # Optionally scan a range (uncomment to try scanning ports 1-1024)
        # print("\n" + "=" * 60)
        # print("Scanning ports 1-100...")
        # print("=" * 60)
        # open_ports = scanner.scan(range(1, 101))
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        sys.exit(0)