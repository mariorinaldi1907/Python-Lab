"""
Date: 2026-06-09
Created a multi-threaded port scanner because I was tired of waiting forever for nmap when I just wanted to check a few common ports on my local network.
"""

#!/usr/bin/env python3
"""
Async Port Scanner - checks which ports are open on a target host.
Uses threading to speed things up because scanning ports one-by-one is painfully slow.
"""

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime


# Common ports I actually care about when debugging stuff
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
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    27017: "MongoDB",
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target.
    Uses a thread pool to scan multiple ports concurrently.
    """
    
    def __init__(self, target, timeout=1.0, num_threads=50):
        """
        Initialize the scanner with a target host.
        
        Args:
            target: hostname or IP address to scan
            timeout: socket timeout in seconds (lower = faster but more false negatives)
            num_threads: number of worker threads (more = faster but heavier on resources)
        """
        self.target = target
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
        # Try to resolve the hostname to IP first so we don't do it repeatedly
        try:
            self.target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def scan_port(self, port):
        """
        Check if a single port is open using TCP connect scan.
        This is the "polite" way - completes the handshake instead of SYN scan.
        
        Args:
            port: port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target_ip, port))
            sock.close()
            
            # connect_ex returns 0 if connection succeeded
            return result == 0
        except socket.error:
            return False
    
    def worker(self, port_queue):
        """
        Worker thread that pulls ports from queue and scans them.
        This is where the actual threading magic happens.
        
        Args:
            port_queue: Queue object containing ports to scan
        """
        while not port_queue.empty():
            port = port_queue.get()
            if self.scan_port(port):
                # Use lock because multiple threads might write to the list
                with self.lock:
                    self.open_ports.append(port)
            port_queue.task_done()
    
    def scan(self, ports):
        """
        Scan a list of ports using thread pool.
        
        Args:
            ports: iterable of port numbers to scan
            
        Returns:
            list of open ports sorted numerically
        """
        # Reset results in case someone calls scan() multiple times
        self.open_ports = []
        
        # Queue up all the ports we need to check
        port_queue = Queue()
        for port in ports:
            port_queue.put(port)
        
        # Spin up worker threads
        threads = []
        for _ in range(min(self.num_threads, len(ports))):
            thread = threading.Thread(target=self.worker, args=(port_queue,))
            thread.daemon = True  # so they die when main thread exits
            thread.start()
            threads.append(thread)
        
        # Wait for all ports to be scanned
        port_queue.join()
        
        return sorted(self.open_ports)


def main():
    """
    CLI interface for the port scanner.
    Demonstrates scanning both common ports and custom ranges.
    """
    parser = argparse.ArgumentParser(
        description="Fast multi-threaded port scanner for checking open ports"
    )
    parser.add_argument("target", help="hostname or IP address to scan")
    parser.add_argument(
        "-p", "--ports",
        help="port range (e.g., '1-1000' or '80,443,8080')",
        default=None
    )
    parser.add_argument(
        "-c", "--common",
        action="store_true",
        help="scan only common ports (faster)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="connection timeout in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=50,
        help="number of threads (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Figure out which ports to scan based on arguments
    if args.common:
        ports_to_scan = list(COMMON_PORTS.keys())
    elif args.ports:
        # Parse port specification
        ports_to_scan = []
        for part in args.ports.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports_to_scan.extend(range(start, end + 1))
            else:
                ports_to_scan.append(int(part))
    else:
        # Default: scan common ports
        ports_to_scan = list(COMMON_PORTS.keys())
    
    print(f"[*] Starting scan on {args.target}")
    print(f"[*] Scanning {len(ports_to_scan)} ports with {args.threads} threads")
    print(f"[*] Timeout set to {args.timeout}s\n")
    
    start_time = datetime.now()
    
    try:
        scanner = PortScanner(args.target, timeout=args.timeout, num_threads=args.threads)
        open_ports = scanner.scan(ports_to_scan)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n[+] Scan complete in {elapsed:.2f} seconds")
        print(f"[+] Found {len(open_ports)} open port(s):\n")
        
        if open_ports:
            for port in open_ports:
                service = COMMON_PORTS.get(port, "unknown")
                print(f"    Port {port:5d} : {service}")
        else:
            print("    No open ports found")
            
    except ValueError as e:
        print(f"[!] Error: {e}")
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")


if __name__ == "__main__":
    # Quick demo if run without arguments
    import sys
    
    if len(sys.argv) == 1:
        print("Demo: Scanning localhost for common ports\n")
        sys.argv = ["port_scanner.py", "localhost", "--common", "--timeout", "0.5"]
    
    main()