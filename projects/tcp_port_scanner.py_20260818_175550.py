"""
Date: 2026-08-18
Made a port scanner that checks common ports across a range, identifies services when possible, and uses threading to speed things up without hammering the network too hard.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner - scans a host for open ports and tries to identify services.
I wanted something quick to check what's running on my local dev machines
without installing nmap every time I set up a new environment.
"""

import socket
import threading
import queue
import time
from typing import List, Tuple, Optional


# Common ports and their typical services - helps with quick identification
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


class PortScanner:
    """
    Multithreaded TCP port scanner with configurable timeout and thread count.
    Uses a queue-based approach to distribute work across threads efficiently.
    """
    
    def __init__(self, host: str, timeout: float = 1.0, num_threads: int = 10):
        """
        Initialize the port scanner.
        
        Args:
            host: Target hostname or IP address
            timeout: Socket connection timeout in seconds
            num_threads: Number of worker threads to use
        """
        self.host = host
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, port: int) -> Tuple[int, bool, Optional[str]]:
        """
        Attempt to connect to a single port and identify the service.
        
        Args:
            port: Port number to scan
            
        Returns:
            Tuple of (port, is_open, service_name)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            result = sock.connect_ex((self.host, port))
            if result == 0:
                # Port is open, try to grab a banner for service detection
                service = self._identify_service(sock, port)
                return (port, True, service)
            return (port, False, None)
        except socket.error:
            return (port, False, None)
        finally:
            sock.close()
    
    def _identify_service(self, sock: socket.socket, port: int) -> str:
        """
        Try to identify the service running on an open port.
        First checks common ports dict, then attempts banner grabbing.
        
        Args:
            sock: Connected socket
            port: Port number
            
        Returns:
            Service name or description
        """
        # Check if it's a well-known port
        if port in COMMON_PORTS:
            return COMMON_PORTS[port]
        
        # Try basic banner grabbing - some services announce themselves
        try:
            sock.settimeout(0.5)
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                return banner[:50]  # Truncate long banners
        except:
            pass
        
        return "Unknown"
    
    def worker(self, port_queue: queue.Queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        This is where the actual scanning happens in each thread.
        
        Args:
            port_queue: Queue containing port numbers to scan
        """
        while True:
            try:
                port = port_queue.get_nowait()
            except queue.Empty:
                break
            
            port_num, is_open, service = self.scan_port(port)
            
            if is_open:
                with self.lock:
                    self.open_ports.append((port_num, service))
            
            port_queue.task_done()
    
    def scan_range(self, start_port: int, end_port: int) -> List[Tuple[int, str]]:
        """
        Scan a range of ports using multiple threads.
        
        Args:
            start_port: Starting port number (inclusive)
            end_port: Ending port number (inclusive)
            
        Returns:
            List of tuples (port, service) for all open ports
        """
        print(f"Scanning {self.host} from port {start_port} to {end_port}...")
        print(f"Using {self.num_threads} threads with {self.timeout}s timeout\n")
        
        # Create queue and populate with ports to scan
        port_queue = queue.Queue()
        for port in range(start_port, end_port + 1):
            port_queue.put(port)
        
        start_time = time.time()
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker, args=(port_queue,))
            t.start()
            threads.append(t)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        
        print(f"\nScan completed in {elapsed:.2f} seconds")
        print(f"Found {len(self.open_ports)} open port(s)\n")
        
        return self.open_ports


def main():
    """
    Demo the port scanner on localhost.
    Scans common ports to see what services are running locally.
    """
    print("=" * 60)
    print("TCP Port Scanner - Mario's Network Tool")
    print("=" * 60 + "\n")
    
    # Scan localhost on common service ports
    # Using a smaller range and fewer threads for the demo to be quick
    scanner = PortScanner(
        host="127.0.0.1",
        timeout=0.5,  # Fast timeout since it's localhost
        num_threads=20
    )
    
    # Scan well-known ports (1-1024) - adjust range as needed
    open_ports = scanner.scan_range(1, 1024)
    
    if open_ports:
        print("Open Ports:")
        print("-" * 60)
        for port, service in open_ports:
            print(f"  Port {port:5d} → {service}")
    else:
        print("No open ports found in the scanned range.")
    
    print("\n" + "=" * 60)
    print("Tip: Try scanning other hosts or different port ranges!")
    print("Example: scanner.scan_range(8000, 9000) for dev servers")
    print("=" * 60)


if __name__ == "__main__":
    main()