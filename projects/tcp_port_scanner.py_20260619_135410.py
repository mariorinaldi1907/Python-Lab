"""
Date: 2026-06-19
Created a concurrent port scanner that probes common services and handles connection timeouts gracefully — useful for quick network audits on my home lab.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded TCP port scanner with common service detection.
Scans a target host for open ports and attempts to identify running services.
"""

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime


# Common ports and their typical services - helps with quick identification
COMMON_SERVICES = {
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
    8080: "HTTP-Proxy",
    27017: "MongoDB"
}


class PortScanner:
    """
    Multi-threaded port scanner that checks which TCP ports are open on a target.
    Uses a queue-based approach so threads can grab work dynamically.
    """
    
    def __init__(self, target, timeout=1.0, num_threads=50):
        """
        Initialize the scanner with target host and configuration.
        
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
        
        # Resolve hostname to IP for cleaner output
        try:
            self.target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port on the target.
        Returns True if the port is open, False otherwise.
        """
        try:
            # AF_INET = IPv4, SOCK_STREAM = TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((self.target_ip, port))
            sock.close()
            
            # connect_ex returns 0 on success, error code otherwise
            return result == 0
        except socket.error:
            return False
    
    def get_service_name(self, port):
        """
        Try to identify the service running on a port.
        First checks our common services dict, then falls back to system lookup.
        """
        if port in COMMON_SERVICES:
            return COMMON_SERVICES[port]
        
        # Try to get service name from the system's services file
        try:
            return socket.getservbyport(port, 'tcp')
        except OSError:
            return "unknown"
    
    def worker(self, queue):
        """
        Worker thread that pulls ports from the queue and scans them.
        This is the function each thread runs in a loop.
        """
        while True:
            port = queue.get()
            if port is None:
                break
            
            if self.scan_port(port):
                service = self.get_service_name(port)
                # Thread-safe append to results list
                with self.lock:
                    self.open_ports.append((port, service))
                    print(f"  [+] Port {port:5d} - {service}")
            
            queue.task_done()
    
    def scan_range(self, start_port, end_port):
        """
        Scan a range of ports using multiple threads.
        Displays results as they're found for better interactivity.
        """
        print(f"\n[*] Starting scan on {self.target} ({self.target_ip})")
        print(f"[*] Scanning ports {start_port}-{end_port} with {self.num_threads} threads")
        print(f"[*] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Queue holds all ports to be scanned
        queue = Queue()
        
        # Spawn worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Fill the queue with all ports to scan
        for port in range(start_port, end_port + 1):
            queue.put(port)
        
        # Wait for all ports to be processed
        queue.join()
        
        # Signal threads to exit by sending None
        for _ in range(self.num_threads):
            queue.put(None)
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        return self.open_ports


def main():
    """
    Demo the port scanner with command-line arguments or defaults.
    Scans common ports on localhost by default.
    """
    parser = argparse.ArgumentParser(
        description="Scan TCP ports on a target host",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("target", nargs="?", default="localhost", 
                       help="Target hostname or IP (default: localhost)")
    parser.add_argument("-s", "--start", type=int, default=1,
                       help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024,
                       help="End port (default: 1024)")
    parser.add_argument("-t", "--threads", type=int, default=50,
                       help="Number of threads (default: 50)")
    parser.add_argument("--timeout", type=float, default=1.0,
                       help="Connection timeout in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    try:
        scanner = PortScanner(
            target=args.target,
            timeout=args.timeout,
            num_threads=args.threads
        )
        
        start_time = datetime.now()
        open_ports = scanner.scan_range(args.start, args.end)
        end_time = datetime.now()
        
        # Summary output
        print(f"\n{'='*60}")
        print(f"[*] Scan completed in {(end_time - start_time).total_seconds():.2f} seconds")
        print(f"[*] Found {len(open_ports)} open port(s)")
        
        if open_ports:
            print(f"\n{'PORT':<10} {'SERVICE':<20}")
            print(f"{'-'*30}")
            for port, service in sorted(open_ports):
                print(f"{port:<10} {service:<20}")
        
        print(f"{'='*60}\n")
        
    except ValueError as e:
        print(f"[!] Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())