"""
Date: 2026-06-28
Made a concurrent port scanner that checks for open TCP ports and identifies common services, useful for quick network audits on my local machines.
"""

#!/usr/bin/env python3
"""
Simple TCP port scanner with multi-threading support.
Scans a target host for open ports and tries to identify common services.
"""

import socket
import threading
import sys
from queue import Queue
from datetime import datetime


# Common port to service mapping for quick identification
COMMON_PORTS = {
    20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
    25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
    143: 'IMAP', 443: 'HTTPS', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
    8080: 'HTTP-Alt', 27017: 'MongoDB'
}


class PortScanner:
    """
    Multi-threaded TCP port scanner.
    
    Uses a thread pool to scan ports concurrently, which is way faster
    than sequential scanning but still uses stdlib only.
    """
    
    def __init__(self, target, timeout=1.0, num_threads=100):
        """
        Initialize the port scanner.
        
        Args:
            target: IP address or hostname to scan
            timeout: Socket timeout in seconds (lower = faster but less reliable)
            num_threads: Number of concurrent threads to use
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        self.port_queue = Queue()
        
    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        
        Returns True if port is open, False otherwise.
        Uses the socket connection attempt as the test — if it connects, it's open.
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
        
        This is the function each thread runs — they grab ports from the shared
        queue until it's empty, which distributes the work automatically.
        """
        while not self.port_queue.empty():
            port = self.port_queue.get()
            if self.scan_port(port):
                service = COMMON_PORTS.get(port, 'Unknown')
                with self.lock:
                    self.open_ports.append((port, service))
                    print(f"[+] Port {port:5d} - OPEN - {service}")
            self.port_queue.task_done()
    
    def scan(self, start_port=1, end_port=1024):
        """
        Scan a range of ports using multiple threads.
        
        Args:
            start_port: First port to scan (inclusive)
            end_port: Last port to scan (inclusive)
        
        I chose 1-1024 as the default because those are the well-known ports,
        but you can scan any range you want.
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning ports {start_port} to {end_port}")
        print(f"[*] Using {self.num_threads} threads\n")
        
        start_time = datetime.now()
        
        # Fill the queue with all ports to scan
        for port in range(start_port, end_port + 1):
            self.port_queue.put(port)
        
        # Create and start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return duration
    
    def print_summary(self, duration):
        """Print a summary of the scan results."""
        print(f"\n{'='*50}")
        print(f"Scan completed in {duration:.2f} seconds")
        print(f"Found {len(self.open_ports)} open port(s)")
        
        if self.open_ports:
            print(f"\nOpen ports on {self.target}:")
            self.open_ports.sort()
            for port, service in self.open_ports:
                print(f"  {port:5d}/tcp - {service}")
        else:
            print(f"\nNo open ports found on {self.target}")
        print(f"{'='*50}\n")


def resolve_target(hostname):
    """
    Resolve a hostname to an IP address.
    
    Just a helper to handle both IPs and hostnames cleanly.
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{hostname}'")
        sys.exit(1)


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    # In real use, you'd probably want to add argparse for CLI args
    
    print("TCP Port Scanner Demo")
    print("=" * 50)
    
    target_host = "127.0.0.1"  # Scan localhost
    target_ip = resolve_target(target_host)
    
    # Create scanner with sensible defaults
    # I'm using a 0.5s timeout because localhost is fast
    scanner = PortScanner(target_ip, timeout=0.5, num_threads=50)
    
    # Scan well-known ports (1-1024)
    # On localhost you'll usually see at least a few services running
    duration = scanner.scan(start_port=1, end_port=1024)
    
    # Print nice summary
    scanner.print_summary(duration)
    
    print("TIP: Try running 'python -m http.server 8000' in another")
    print("     terminal, then run this scanner again to see port 8000 open!")