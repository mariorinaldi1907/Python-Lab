"""
Date: 2026-06-16
Created a concurrent port scanner because I got tired of waiting for nmap when I just want to check a handful of common ports quickly.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner using threading.
I wanted something faster than sequential scanning but didn't want to deal
with async/await complexity for something this simple.
"""

import socket
import threading
import time
from queue import Queue
from typing import List, Tuple


class PortScanner:
    """
    Multi-threaded port scanner that checks which ports are open on a target host.
    
    Uses a thread pool approach because spinning up thousands of threads is a bad idea,
    and this keeps memory usage reasonable even when scanning large port ranges.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the scanner with target and performance params.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds (lower = faster but less accurate)
            num_threads: Number of concurrent scanning threads (sweet spot is usually 50-100)
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
    def _resolve_target(self) -> str:
        """
        Resolve hostname to IP address.
        
        Returns:
            IP address as string
            
        Raises:
            socket.gaierror: If hostname cannot be resolved
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            raise ValueError(f"Unable to resolve hostname: {self.target}")
    
    def _scan_port(self, port: int) -> bool:
        """
        Attempt to connect to a single port.
        
        Args:
            port: Port number to scan
            
        Returns:
            True if port is open, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Try to connect - if it works, port is open
            result = sock.connect_ex((self.target, port))
            return result == 0
        except socket.error:
            return False
        finally:
            sock.close()
    
    def _worker(self, queue: Queue):
        """
        Worker thread that pulls ports from queue and scans them.
        
        This is the function each thread runs - it keeps pulling port numbers
        from the shared queue until there's nothing left to scan.
        
        Args:
            queue: Thread-safe queue containing port numbers to scan
        """
        while not queue.empty():
            try:
                port = queue.get_nowait()
            except:
                # Queue is empty, we're done
                break
                
            if self._scan_port(port):
                # Thread-safe append to results
                with self.lock:
                    self.open_ports.append(port)
                    
            queue.task_done()
    
    def scan(self, ports: List[int]) -> List[int]:
        """
        Scan a list of ports and return which ones are open.
        
        Args:
            ports: List of port numbers to scan
            
        Returns:
            Sorted list of open port numbers
        """
        # Resolve hostname first so we don't do it on every connection
        try:
            ip = self._resolve_target()
            print(f"Scanning {self.target} ({ip})...")
        except ValueError as e:
            print(f"Error: {e}")
            return []
        
        # Reset results from any previous scan
        self.open_ports = []
        
        # Fill the work queue
        queue = Queue()
        for port in ports:
            queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self._worker, args=(queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all work to complete
        for thread in threads:
            thread.join()
        
        # Return sorted results
        return sorted(self.open_ports)


def get_common_ports() -> List[int]:
    """
    Return a list of commonly used ports worth checking.
    
    I picked these based on what I actually see in use - web servers, databases,
    SSH, etc. Could expand this but these cover 90% of what I care about.
    """
    return [
        20, 21,      # FTP
        22,          # SSH
        23,          # Telnet
        25,          # SMTP
        53,          # DNS
        80, 443,     # HTTP/HTTPS
        110, 143,    # POP3/IMAP
        3306,        # MySQL
        3389,        # RDP
        5432,        # PostgreSQL
        5900,        # VNC
        6379,        # Redis
        8080, 8443,  # Alt HTTP/HTTPS
        27017,       # MongoDB
    ]


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    print("=== Port Scanner Demo ===\n")
    
    target = "localhost"
    scanner = PortScanner(target, timeout=0.5, num_threads=50)
    
    print("Scanning common ports on localhost...")
    start_time = time.time()
    
    common_ports = get_common_ports()
    open_ports = scanner.scan(common_ports)
    
    elapsed = time.time() - start_time
    
    print(f"\nScan completed in {elapsed:.2f} seconds")
    print(f"Scanned {len(common_ports)} ports\n")
    
    if open_ports:
        print(f"Found {len(open_ports)} open port(s):")
        for port in open_ports:
            print(f"  → Port {port} is OPEN")
    else:
        print("No open ports found among common ports.")
    
    # Also demonstrate scanning a custom range
    print("\n" + "="*40)
    print("\nScanning custom range (8000-8010)...")
    
    custom_range = list(range(8000, 8011))
    open_custom = scanner.scan(custom_range)
    
    if open_custom:
        print(f"Open ports in range: {open_custom}")
    else:
        print("No open ports in this range.")