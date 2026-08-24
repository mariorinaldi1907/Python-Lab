"""
Date: 2026-08-24
Created a concurrent port scanner that checks common ports and attempts to grab service banners — helps me quickly audit my local network.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded port scanner with service detection.
Scans a target host for open ports and attempts to identify running services.
"""

import socket
import threading
import queue
import time
from typing import List, Tuple, Optional


class PortScanner:
    """
    Multi-threaded port scanner that checks for open ports and tries to identify services.
    """
    
    # Common ports I usually care about when checking my servers
    COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 5900, 8080, 8443]
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 10):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket timeout in seconds (keep it low for faster scans)
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.results = []
        self.lock = threading.Lock()
        
    def _scan_port(self, port: int) -> Optional[Tuple[int, str]]:
        """
        Attempt to connect to a single port and grab service banner if possible.
        
        Args:
            port: Port number to scan
            
        Returns:
            Tuple of (port, service_info) if open, None otherwise
        """
        try:
            # Create a socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to grab a banner
                service_info = self._grab_banner(sock, port)
                sock.close()
                return (port, service_info)
            
            sock.close()
            return None
            
        except socket.error:
            return None
    
    def _grab_banner(self, sock: socket.socket, port: int) -> str:
        """
        Attempt to grab a service banner from an open port.
        
        Args:
            sock: Connected socket
            port: Port number (used for service name lookup)
            
        Returns:
            Service information string
        """
        try:
            # Try to get the service name from the port number
            service_name = socket.getservbyport(port)
        except OSError:
            service_name = "unknown"
        
        # Try to receive a banner (some services send data immediately)
        try:
            sock.settimeout(0.5)  # Short timeout for banner grab
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                return f"{service_name}: {banner[:50]}"  # Limit banner length
        except socket.timeout:
            pass
        except Exception:
            pass
        
        return service_name
    
    def _worker(self, port_queue: queue.Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        
        Args:
            port_queue: Thread-safe queue containing ports to scan
        """
        while True:
            try:
                port = port_queue.get_nowait()
            except queue.Empty:
                break
            
            result = self._scan_port(port)
            
            if result:
                with self.lock:
                    self.results.append(result)
            
            port_queue.task_done()
    
    def scan(self, ports: Optional[List[int]] = None) -> List[Tuple[int, str]]:
        """
        Scan the target for open ports using multiple threads.
        
        Args:
            ports: List of ports to scan (defaults to COMMON_PORTS)
            
        Returns:
            List of tuples containing (port, service_info) for open ports
        """
        if ports is None:
            ports = self.COMMON_PORTS
        
        # Create a queue and populate it with ports
        port_queue = queue.Queue()
        for port in ports:
            port_queue.put(port)
        
        # Create and start worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self._worker, args=(port_queue,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Sort results by port number for cleaner output
        self.results.sort(key=lambda x: x[0])
        return self.results


def print_banner():
    """Print a simple banner for the tool."""
    print("=" * 60)
    print("  Simple Port Scanner with Service Detection")
    print("  Mario's Network Utilities")
    print("=" * 60)
    print()


if __name__ == "__main__":
    print_banner()
    
    # Scan localhost as a demo — safe and always available
    target_host = "127.0.0.1"
    
    print(f"[*] Scanning target: {target_host}")
    print(f"[*] Checking common ports...")
    print()
    
    # Initialize scanner with reasonable defaults
    scanner = PortScanner(target=target_host, timeout=0.5, num_threads=20)
    
    start_time = time.time()
    open_ports = scanner.scan()
    elapsed_time = time.time() - start_time
    
    # Display results
    if open_ports:
        print(f"[+] Found {len(open_ports)} open port(s):\n")
        print(f"{'PORT':<10} {'SERVICE'}")
        print("-" * 60)
        
        for port, service in open_ports:
            print(f"{port:<10} {service}")
    else:
        print("[-] No open ports found (or host is down)")
    
    print()
    print(f"[*] Scan completed in {elapsed_time:.2f} seconds")
    print()
    print("Note: This scans localhost by default. To scan other hosts,")
    print("      modify the target_host variable or extend this script")
    print("      to accept command-line arguments.")