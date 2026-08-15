"""
Date: 2026-08-15
Wrote a concurrent port scanner with banner grabbing to check what services are running on open ports — helpful for my homelab debugging.
"""

#!/usr/bin/env python3
"""
A threaded port scanner with banner grabbing.
I got tired of waiting for nmap every time I wanted to check my homelab,
so I built this lighter alternative using Python's threading and sockets.
"""

import socket
import threading
import argparse
import sys
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    Concurrent port scanner that can grab service banners.
    Uses a thread pool to speed things up without hammering the target.
    """
    
    def __init__(self, target, ports, timeout=1.0, num_threads=50, grab_banner=False):
        """
        Initialize the scanner with target and configuration.
        
        Args:
            target: IP address or hostname to scan
            ports: List of ports to check
            timeout: Socket timeout in seconds
            num_threads: Number of worker threads (don't go crazy with this)
            grab_banner: Whether to attempt banner grabbing on open ports
        """
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.num_threads = num_threads
        self.grab_banner = grab_banner
        self.queue = Queue()
        self.open_ports = []
        self.lock = threading.Lock()
        
        # Try to resolve hostname early so we don't spam DNS
        try:
            self.target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")
    
    def scan_port(self, port):
        """
        Attempt to connect to a single port.
        Returns True if open, False otherwise.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target_ip, port))
            
            banner = None
            if result == 0 and self.grab_banner:
                # Port is open, try to grab banner
                banner = self._grab_banner(sock)
            
            sock.close()
            
            if result == 0:
                with self.lock:
                    self.open_ports.append((port, banner))
                return True
            return False
        except Exception:
            # Socket errors just mean port is closed or filtered
            return False
    
    def _grab_banner(self, sock):
        """
        Try to grab service banner from an open socket.
        Some services announce themselves, which is helpful for identification.
        """
        try:
            sock.settimeout(0.5)
            # Some services send banner immediately, others need a prompt
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if not banner:
                # Try sending a generic probe for HTTP-like services
                sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return banner if banner else None
        except:
            return None
    
    def worker(self):
        """
        Worker thread that pulls ports from queue and scans them.
        This is where the actual work happens concurrently.
        """
        while True:
            port = self.queue.get()
            if port is None:
                break
            self.scan_port(port)
            self.queue.task_done()
    
    def scan(self):
        """
        Start the scan with configured number of threads.
        Returns list of (port, banner) tuples for open ports.
        """
        print(f"[*] Starting scan of {self.target} ({self.target_ip})")
        print(f"[*] Scanning {len(self.ports)} ports with {self.num_threads} threads")
        start_time = datetime.now()
        
        # Fire up worker threads
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Queue up all ports to scan
        for port in self.ports:
            self.queue.put(port)
        
        # Wait for all scans to complete
        self.queue.join()
        
        # Stop workers
        for _ in range(self.num_threads):
            self.queue.put(None)
        for t in threads:
            t.join()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n[*] Scan completed in {elapsed:.2f} seconds")
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x[0])
        return self.open_ports


def parse_port_range(port_spec):
    """
    Parse port specification like '80,443,8000-8010' into a list.
    Supports individual ports and ranges.
    """
    ports = []
    for part in port_spec.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fast port scanner with banner grabbing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s localhost -p 80,443,8000-8010
  %(prog)s 192.168.1.1 -p 1-1000 -t 100 --banner
        """
    )
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('-p', '--ports', default='1-1000',
                       help='Ports to scan (e.g., 80,443,8000-9000)')
    parser.add_argument('-t', '--threads', type=int, default=50,
                       help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=float, default=1.0,
                       help='Socket timeout in seconds (default: 1.0)')
    parser.add_argument('--banner', action='store_true',
                       help='Attempt to grab service banners')
    
    args = parser.parse_args()
    
    try:
        ports = parse_port_range(args.ports)
        scanner = PortScanner(
            target=args.target,
            ports=ports,
            timeout=args.timeout,
            num_threads=args.threads,
            grab_banner=args.banner
        )
        
        open_ports = scanner.scan()
        
        if open_ports:
            print(f"\n[+] Found {len(open_ports)} open ports:\n")
            for port, banner in open_ports:
                if banner:
                    # Truncate long banners for readability
                    banner_display = banner[:100] + '...' if len(banner) > 100 else banner
                    print(f"  {port}/tcp\t{banner_display}")
                else:
                    print(f"  {port}/tcp\topen")
        else:
            print("\n[-] No open ports found")
    
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)