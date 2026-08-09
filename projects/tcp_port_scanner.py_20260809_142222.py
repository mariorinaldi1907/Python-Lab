"""
Date: 2026-08-09
Wrote a concurrent port scanner that checks common services and prints results in real-time — helps me quickly audit which ports are open on my local network devices.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded TCP port scanner.
Scans a target host for open ports and identifies common services.
"""

import socket
import threading
import time
from queue import Queue
from typing import List, Tuple


# Common ports and their typical services
COMMON_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
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


class PortScanner:
    """
    Multi-threaded TCP port scanner with configurable timeout and thread count.
    """
    
    def __init__(self, target: str, timeout: float = 1.0, num_threads: int = 50):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            timeout: Socket connection timeout in seconds
            num_threads: Number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
        # Resolve hostname to IP once at the beginning
        try:
            self.ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def scan_port(self, port: int) -> bool:
        """
        Attempt to connect to a single port.
        
        Args:
            port: Port number to scan
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            # Create a TCP socket and set timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Try to connect - if successful, port is open
            result = sock.connect_ex((self.ip, port))
            sock.close()
            
            return result == 0
        except socket.error:
            return False
    
    def worker(self, port_queue: Queue):
        """
        Worker thread that pulls ports from queue and scans them.
        
        Args:
            port_queue: Queue containing port numbers to scan
        """
        while not port_queue.empty():
            port = port_queue.get()
            
            if self.scan_port(port):
                # Thread-safe append to results list
                with self.lock:
                    self.open_ports.append(port)
                    service = COMMON_PORTS.get(port, "Unknown")
                    print(f"[+] Port {port:5d} is open    ({service})")
            
            port_queue.task_done()
    
    def scan_range(self, start_port: int = 1, end_port: int = 1024) -> List[int]:
        """
        Scan a range of ports using multiple threads.
        
        Args:
            start_port: First port in range (inclusive)
            end_port: Last port in range (inclusive)
            
        Returns:
            Sorted list of open port numbers
        """
        print(f"\n[*] Starting scan on {self.target} ({self.ip})")
        print(f"[*] Scanning ports {start_port}-{end_port} with {self.num_threads} threads\n")
        
        start_time = time.time()
        
        # Create queue and populate with port numbers
        port_queue = Queue()
        for port in range(start_port, end_port + 1):
            port_queue.put(port)
        
        # Spawn worker threads
        threads = []
        for _ in range(min(self.num_threads, port_queue.qsize())):
            thread = threading.Thread(target=self.worker, args=(port_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        
        print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open port(s)\n")
        
        return sorted(self.open_ports)
    
    def scan_common_ports(self) -> List[int]:
        """
        Scan only the common service ports defined in COMMON_PORTS.
        
        Returns:
            Sorted list of open port numbers
        """
        return self.scan_range(
            start_port=min(COMMON_PORTS.keys()),
            end_port=max(COMMON_PORTS.keys())
        )


def main():
    """
    Demo the port scanner on localhost.
    This will check which services are running on your local machine.
    """
    print("=" * 60)
    print("TCP Port Scanner Demo")
    print("=" * 60)
    
    # Scan localhost for common ports
    # I'm using a shorter timeout and fewer threads for localhost since it's fast
    scanner = PortScanner(target="localhost", timeout=0.5, num_threads=20)
    
    # Scan well-known ports (1-1024)
    open_ports = scanner.scan_range(start_port=1, end_port=1024)
    
    if open_ports:
        print("Summary of Open Ports:")
        print("-" * 40)
        for port in open_ports:
            service = COMMON_PORTS.get(port, "Unknown Service")
            print(f"  {port:5d}  -  {service}")
    else:
        print("No open ports found in the scanned range.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()