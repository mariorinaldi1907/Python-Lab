"""
Date: 2026-06-20
Wrote a multi-threaded port scanner that checks which ports are open on a target and tries to grab service banners — way faster than sequential scanning.
"""

#!/usr/bin/env python3
"""
Concurrent port scanner with banner grabbing capability.
Scans a target host for open ports and attempts to identify running services.
"""

import socket
import threading
import argparse
import sys
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    Multi-threaded port scanner that checks for open ports and grabs service banners.
    """
    
    def __init__(self, target, ports, num_threads=50, timeout=1.0):
        """
        Initialize the port scanner.
        
        Args:
            target: Hostname or IP address to scan
            ports: List of ports to scan
            num_threads: Number of concurrent threads to use
            timeout: Socket connection timeout in seconds
        """
        self.target = target
        self.ports = ports
        self.num_threads = num_threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()
        
    def resolve_target(self):
        """
        Resolve hostname to IP address.
        
        Returns:
            IP address as string, or None if resolution fails
        """
        try:
            ip = socket.gethostbyname(self.target)
            return ip
        except socket.gaierror:
            return None
    
    def grab_banner(self, port):
        """
        Attempt to grab a service banner from an open port.
        
        Args:
            port: Port number to connect to
            
        Returns:
            Banner string if available, otherwise generic service name
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target, port))
            
            # Send a generic probe to trigger a response
            try:
                sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
            except:
                pass
            
            # Try to receive banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            # Return first line of banner if it exists
            if banner:
                return banner.split('\n')[0][:60]  # Limit length
            
        except:
            pass
        
        # Fallback to common port services if banner grab fails
        common_services = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL',
            6379: 'Redis',
            8080: 'HTTP-Proxy',
        }
        return common_services.get(port, 'Unknown')
    
    def scan_port(self, port):
        """
        Scan a single port to check if it's open.
        
        Args:
            port: Port number to scan
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                # Port is open, grab banner
                banner = self.grab_banner(port)
                
                with self.lock:
                    self.open_ports.append((port, banner))
                    print(f"[+] Port {port:5d} open - {banner}")
                    
        except socket.error:
            pass
    
    def worker(self):
        """
        Worker thread that pulls ports from queue and scans them.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
            self.scan_port(port)
            self.queue.task_done()
    
    def scan(self):
        """
        Start the port scanning process with multiple threads.
        
        Returns:
            List of tuples (port, banner) for open ports
        """
        print(f"\n[*] Starting scan on {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.num_threads} threads")
        print(f"[*] Timeout: {self.timeout}s\n")
        
        start_time = datetime.now()
        
        # Start worker threads
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)
        
        # Add ports to queue
        for port in self.ports:
            self.queue.put(port)
        
        # Wait for all tasks to complete
        self.queue.join()
        
        # Stop workers
        for _ in range(self.num_threads):
            self.queue.put(None)
        for thread in threads:
            thread.join()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[*] Scan completed in {duration:.2f} seconds")
        print(f"[*] Found {len(self.open_ports)} open ports\n")
        
        return sorted(self.open_ports)


def parse_port_range(port_string):
    """
    Parse port specification into list of port numbers.
    Supports: single port (80), range (20-25), comma-separated (80,443,8080)
    
    Args:
        port_string: String specifying ports
        
    Returns:
        List of port numbers
    """
    ports = []
    parts = port_string.split(',')
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    
    return ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Multi-threaded port scanner with banner grabbing'
    )
    parser.add_argument('target', help='Target hostname or IP address')
    parser.add_argument(
        '-p', '--ports',
        default='20-25,80,443,3306,5432,8080',
        help='Ports to scan (e.g., "80,443" or "20-100")'
    )
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=50,
        help='Number of threads (default: 50)'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=1.0,
        help='Connection timeout in seconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Parse ports
    try:
        ports = parse_port_range(args.ports)
    except ValueError:
        print("[!] Invalid port specification")
        sys.exit(1)
    
    # Create scanner and resolve target
    scanner = PortScanner(args.target, ports, args.threads, args.timeout)
    
    ip = scanner.resolve_target()
    if not ip:
        print(f"[!] Could not resolve hostname: {args.target}")
        sys.exit(1)
    
    print(f"[*] Resolved {args.target} to {ip}")
    
    # Run the scan
    open_ports = scanner.scan()
    
    # Print summary
    if open_ports:
        print("Open ports summary:")
        for port, banner in open_ports:
            print(f"  {port:5d}/tcp - {banner}")
    else:
        print("No open ports found.")