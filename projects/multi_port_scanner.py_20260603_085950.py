"""
Date: 2026-06-03
Wrote a concurrent port scanner with configurable threading because I got tired of waiting for nmap when I just need to check if a few services are up.
"""

#!/usr/bin/env python3
"""
Multi-threaded port scanner with common service detection.
Scans a target host across a range of ports to check what's open.
"""

import socket
import threading
import time
from queue import Queue
from typing import List, Tuple, Optional


class PortScanner:
    """
    Threaded port scanner that checks multiple ports concurrently.
    Uses a queue-based approach so we don't spawn thousands of threads.
    """
    
    # Common services I actually care about checking
    COMMON_PORTS = {
        20: "FTP-DATA",
        21: "FTP",
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
        8080: "HTTP-Alt",
        27017: "MongoDB"
    }
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the scanner.
        
        Args:
            target: Hostname or IP to scan
            timeout: Socket connection timeout in seconds
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports: List[Tuple[int, Optional[str]]] = []
        self.lock = threading.Lock()
        
    def _scan_port(self, port: int) -> bool:
        """
        Attempt to connect to a single port.
        Returns True if the port is open, False otherwise.
        """
        try:
            # Create a socket with a timeout so we don't wait forever
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            # connect_ex returns 0 if connection succeeded
            return result == 0
            
        except socket.gaierror:
            # DNS resolution failed
            return False
        except socket.error:
            return False
    
    def _worker(self, port_queue: Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        This is where the actual scanning happens in parallel.
        """
        while not port_queue.empty():
            port = port_queue.get()
            
            if self._scan_port(port):
                service = self.COMMON_PORTS.get(port, "Unknown")
                
                # Thread-safe append to results
                with self.lock:
                    self.open_ports.append((port, service))
                    
            port_queue.task_done()
    
    def scan(self, start_port: int = 1, end_port: int = 1024) -> List[Tuple[int, Optional[str]]]:
        """
        Scan a range of ports using multiple threads.
        
        Args:
            start_port: First port to scan (inclusive)
            end_port: Last port to scan (inclusive)
            
        Returns:
            List of tuples (port, service_name) for open ports
        """
        # Clear previous results
        self.open_ports = []
        
        # Build the queue of ports to scan
        port_queue = Queue()
        for port in range(start_port, end_port + 1):
            port_queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(min(self.num_threads, port_queue.qsize())):
            thread = threading.Thread(target=self._worker, args=(port_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        return self.open_ports


def resolve_target(target: str) -> str:
    """
    Resolve a hostname to an IP address.
    If it's already an IP, just return it.
    """
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {target}")


if __name__ == "__main__":
    # Demo: scan localhost for common services
    target = "localhost"
    
    print(f"Starting port scan on {target}...")
    print("=" * 60)
    
    try:
        # Resolve the target first
        ip = resolve_target(target)
        print(f"Target IP: {ip}")
        print()
        
        # Create scanner with reasonable defaults
        # Lower timeout for localhost since it should be fast
        scanner = PortScanner(target=ip, timeout=0.5, num_threads=100)
        
        # Scan common ports (1-1024) - the well-known port range
        start_time = time.time()
        open_ports = scanner.scan(start_port=1, end_port=1024)
        elapsed = time.time() - start_time
        
        # Display results
        if open_ports:
            print(f"Found {len(open_ports)} open port(s):\n")
            for port, service in open_ports:
                print(f"  Port {port:5d} - {service}")
        else:
            print("No open ports found in the scanned range.")
        
        print()
        print(f"Scan completed in {elapsed:.2f} seconds")
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")