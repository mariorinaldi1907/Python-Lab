"""
Date: 2026-07-09
Created a simple subnet scanner to discover active hosts and open ports on my local network using pure Python stdlib.
"""

#!/usr/bin/env python3
"""
Subnet Scanner - Discover active hosts and check common ports on a network.

I built this to help me quickly map out devices on my home network without
installing nmap or other external tools. Just uses stdlib sockets and threading
to speed things up a bit.
"""

import socket
import threading
import ipaddress
import time
from typing import List, Tuple


class SubnetScanner:
    """
    Scans a subnet for active hosts and checks for common open ports.
    
    Uses multithreading to speed up the scanning process since network I/O
    is slow. I tried to keep the timeout values reasonable so it doesn't
    hang forever on dead hosts.
    """
    
    # Common ports I usually want to check - web servers, SSH, etc.
    COMMON_PORTS = [21, 22, 23, 80, 443, 3306, 3389, 5432, 8080, 8443]
    
    def __init__(self, subnet: str, timeout: float = 0.5):
        """
        Initialize the scanner with a subnet in CIDR notation.
        
        Args:
            subnet: Network address in CIDR format (e.g., '192.168.1.0/24')
            timeout: Socket timeout in seconds (I use 0.5s for local networks)
        """
        self.subnet = ipaddress.ip_network(subnet, strict=False)
        self.timeout = timeout
        self.active_hosts = []
        self.results = {}
        self.lock = threading.Lock()
    
    def check_host(self, ip: str) -> bool:
        """
        Check if a host is reachable by attempting a socket connection.
        
        I'm using port 80 as a quick check since ping requires raw sockets
        which need root privileges. This isn't perfect but works for most cases.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if host responds, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Try to connect to port 80 - most devices have something there
            result = sock.connect_ex((ip, 80))
            sock.close()
            # connect_ex returns 0 on success, but we also consider refused
            # connections as "active" since the host is responding
            return result in [0, 10061, 111]  # Success or connection refused
        except (socket.timeout, socket.error):
            return False
    
    def scan_port(self, ip: str, port: int) -> bool:
        """
        Check if a specific port is open on a host.
        
        Args:
            ip: IP address to scan
            port: Port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except (socket.timeout, socket.error):
            return False
    
    def scan_host_ports(self, ip: str) -> List[int]:
        """
        Scan common ports on a specific host.
        
        Args:
            ip: IP address to scan
            
        Returns:
            List of open port numbers
        """
        open_ports = []
        for port in self.COMMON_PORTS:
            if self.scan_port(ip, port):
                open_ports.append(port)
        return open_ports
    
    def worker(self, ip: str):
        """
        Worker thread that checks a host and scans its ports.
        
        This gets called by each thread to process one IP address.
        Uses a lock when updating shared data structures.
        
        Args:
            ip: IP address to process
        """
        if self.check_host(ip):
            open_ports = self.scan_host_ports(ip)
            
            with self.lock:
                self.active_hosts.append(ip)
                self.results[ip] = {
                    'hostname': self._get_hostname(ip),
                    'open_ports': open_ports
                }
    
    def _get_hostname(self, ip: str) -> str:
        """
        Try to resolve the hostname for an IP address.
        
        Args:
            ip: IP address to resolve
            
        Returns:
            Hostname if found, otherwise returns the IP
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return ip
    
    def scan(self, max_threads: int = 50) -> dict:
        """
        Scan the entire subnet for active hosts and open ports.
        
        I use threading here because scanning sequentially takes forever.
        50 threads seems like a good balance between speed and not hammering
        the network too hard.
        
        Args:
            max_threads: Maximum number of concurrent threads
            
        Returns:
            Dictionary mapping IP addresses to their scan results
        """
        threads = []
        
        # Convert network hosts to list so we can iterate
        hosts = list(self.subnet.hosts())
        
        print(f"Scanning {len(hosts)} hosts in {self.subnet}...")
        start_time = time.time()
        
        for ip in hosts:
            ip_str = str(ip)
            thread = threading.Thread(target=self.worker, args=(ip_str,))
            thread.start()
            threads.append(thread)
            
            # Limit concurrent threads to avoid overwhelming the network
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time
        print(f"Scan completed in {elapsed:.2f} seconds")
        
        return self.results


if __name__ == "__main__":
    # Demo: Scan a small local subnet (adjust to match your network)
    # Using a /29 subnet (6 hosts) for the demo so it runs quickly
    
    print("=== Subnet Scanner Demo ===\n")
    
    # You'd normally use something like '192.168.1.0/24' for your home network
    # Using 127.0.0.0/29 here so the demo works without a real network
    scanner = SubnetScanner("127.0.0.0/29", timeout=0.3)
    results = scanner.scan(max_threads=10)
    
    print(f"\nFound {len(results)} active host(s):\n")
    
    if results:
        for ip, info in sorted(results.items()):
            print(f"Host: {ip}")
            print(f"  Hostname: {info['hostname']}")
            if info['open_ports']:
                print(f"  Open ports: {', '.join(map(str, info['open_ports']))}")
            else:
                print(f"  Open ports: None detected")
            print()
    else:
        print("No active hosts found in this subnet.")
        print("\nTip: Try scanning your actual local network, e.g., '192.168.1.0/24'")