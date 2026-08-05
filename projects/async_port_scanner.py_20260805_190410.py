"""
Date: 2026-08-05
Created a multi-threaded port scanner that checks common service ports and tries to identify what's running on them using banner grabbing.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner that checks common services on a target host.
Uses threading to scan multiple ports simultaneously for speed.
"""

import socket
import threading
from queue import Queue
from datetime import datetime
from typing import Dict, List, Tuple


class PortScanner:
    """
    Multi-threaded port scanner that identifies open ports and attempts
    to determine what service is running on each.
    """
    
    # Common ports I want to check - mostly focused on web/database/admin services
    COMMON_PORTS = {
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
        8443: "HTTPS-Alt",
        27017: "MongoDB",
    }
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 10):
        """
        Initialize the port scanner.
        
        Args:
            target: IP address or hostname to scan
            timeout: Socket timeout in seconds (kept low for speed)
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports: Dict[int, str] = {}
        self.lock = threading.Lock()
        
    def scan_port(self, port: int) -> Tuple[bool, str]:
        """
        Attempt to connect to a single port and grab its banner if possible.
        
        Args:
            port: Port number to scan
            
        Returns:
            Tuple of (is_open, service_info)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to grab a banner
                service_info = self.COMMON_PORTS.get(port, "Unknown")
                try:
                    # Send a simple probe and see if we get a banner back
                    sock.send(b"\r\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        # Truncate long banners to keep output clean
                        service_info = f"{service_info} - {banner[:50]}"
                except:
                    # Banner grabbing failed, just use the known service name
                    pass
                
                sock.close()
                return True, service_info
            else:
                sock.close()
                return False, ""
                
        except socket.gaierror:
            # Hostname couldn't be resolved
            return False, ""
        except socket.error:
            # Connection error
            return False, ""
    
    def worker(self, queue: Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        Args:
            queue: Queue containing port numbers to scan
        """
        while True:
            port = queue.get()
            if port is None:
                break
                
            is_open, service_info = self.scan_port(port)
            
            if is_open:
                # Thread-safe update of open ports dictionary
                with self.lock:
                    self.open_ports[port] = service_info
                    
            queue.task_done()
    
    def scan(self, ports: List[int] = None) -> Dict[int, str]:
        """
        Scan the target host for open ports using multiple threads.
        
        Args:
            ports: List of ports to scan. If None, scans COMMON_PORTS.
            
        Returns:
            Dictionary mapping open port numbers to service information
        """
        if ports is None:
            ports = list(self.COMMON_PORTS.keys())
        
        # Create a queue and populate it with ports to scan
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
        
        return self.open_ports


def resolve_target(target: str) -> str:
    """
    Resolve a hostname to an IP address.
    
    Args:
        target: Hostname or IP address
        
    Returns:
        IP address as string
    """
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {target}")


if __name__ == "__main__":
    # Demo: scan localhost for common services
    print("=== Port Scanner Demo ===\n")
    
    target = "localhost"
    print(f"Target: {target}")
    
    # Resolve the target to an IP
    try:
        ip = resolve_target(target)
        print(f"Resolved to: {ip}")
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    
    # Create scanner and run it
    scanner = PortScanner(target, timeout=0.5, num_threads=20)
    
    start_time = datetime.now()
    print(f"\nStarting scan at {start_time.strftime('%H:%M:%S')}")
    print(f"Scanning {len(scanner.COMMON_PORTS)} common ports...\n")
    
    open_ports = scanner.scan()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Display results
    if open_ports:
        print(f"Found {len(open_ports)} open port(s):\n")
        for port in sorted(open_ports.keys()):
            print(f"  Port {port:5d} - {open_ports[port]}")
    else:
        print("No open ports found in the common ports list.")
    
    print(f"\nScan completed in {duration:.2f} seconds")