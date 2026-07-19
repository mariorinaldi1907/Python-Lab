"""
Date: 2026-07-19
Created a port scanner that checks common ports on any host, grabs service banners when possible, and uses threading to speed things up without hammering the target.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner with Banner Grabbing
Scans a target host for open TCP ports and attempts to grab service banners.
Uses threading to improve scan speed while being respectful of the target.
"""

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime


class PortScanner:
    """
    Multi-threaded TCP port scanner with banner grabbing capability.
    
    The threading approach here lets us scan multiple ports concurrently
    without waiting for each timeout sequentially. I've capped the threads
    to avoid being too aggressive on the target network.
    """
    
    def __init__(self, target, timeout=1.0, max_threads=50):
        """
        Initialize the port scanner.
        
        Args:
            target: IP address or hostname to scan
            timeout: Socket timeout in seconds
            max_threads: Maximum number of concurrent scanning threads
        """
        self.target = target
        self.timeout = timeout
        self.max_threads = max_threads
        self.open_ports = []
        self.lock = threading.Lock()
        
    def scan_port(self, port):
        """
        Scan a single port and attempt banner grabbing.
        
        Args:
            port: Port number to scan
            
        Returns:
            dict with port info if open, None if closed
        """
        try:
            # Create a socket and attempt connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                # Port is open, try to grab a banner
                banner = self._grab_banner(sock, port)
                
                with self.lock:
                    port_info = {
                        'port': port,
                        'state': 'open',
                        'banner': banner
                    }
                    self.open_ports.append(port_info)
                    return port_info
            
            sock.close()
            
        except socket.gaierror:
            # Hostname resolution failed
            return None
        except socket.error:
            # Connection error, port is likely closed or filtered
            return None
        
        return None
    
    def _grab_banner(self, sock, port):
        """
        Attempt to grab service banner from an open port.
        
        Some services send a banner immediately upon connection,
        others need a prompt. I'm sending a generic HTTP request
        for common web ports and just listening otherwise.
        
        Args:
            sock: Connected socket object
            port: Port number (used to determine protocol)
            
        Returns:
            Banner string or 'No banner' if nothing received
        """
        try:
            # For HTTP/HTTPS ports, send a request to trigger response
            if port in [80, 443, 8080, 8443]:
                sock.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
            
            # Try to receive data
            sock.settimeout(0.5)  # Shorter timeout for banner grab
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return banner[:100] if banner else 'No banner'
            
        except:
            return 'No banner'
        finally:
            sock.close()
    
    def worker(self, port_queue):
        """
        Worker thread that pulls ports from queue and scans them.
        
        Args:
            port_queue: Queue containing port numbers to scan
        """
        while not port_queue.empty():
            port = port_queue.get()
            self.scan_port(port)
            port_queue.task_done()
    
    def scan(self, ports):
        """
        Scan multiple ports using thread pool.
        
        Args:
            ports: List of port numbers to scan
            
        Returns:
            List of open port dictionaries
        """
        # Create queue and populate with ports
        port_queue = Queue()
        for port in ports:
            port_queue.put(port)
        
        # Start worker threads
        threads = []
        num_threads = min(self.max_threads, len(ports))
        
        for _ in range(num_threads):
            thread = threading.Thread(target=self.worker, args=(port_queue,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        port_queue.join()
        
        # Sort results by port number for cleaner output
        self.open_ports.sort(key=lambda x: x['port'])
        return self.open_ports


def get_common_ports():
    """
    Return a list of commonly used ports to scan.
    
    I picked these based on typical services you'd find on servers.
    Could expand this list, but these cover most of the interesting stuff.
    """
    return [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        445,   # SMB
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        6379,  # Redis
        8080,  # HTTP-alt
        8443,  # HTTPS-alt
        27017, # MongoDB
    ]


if __name__ == "__main__":
    # Demo: scan localhost for common open ports
    print("=" * 60)
    print("TCP Port Scanner Demo")
    print("=" * 60)
    
    target = "127.0.0.1"  # Scanning localhost to avoid any network issues
    ports = get_common_ports()
    
    print(f"\nTarget: {target}")
    print(f"Scanning {len(ports)} common ports...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    scanner = PortScanner(target, timeout=0.5, max_threads=20)
    start_time = datetime.now()
    
    open_ports = scanner.scan(ports)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"Scan completed in {duration:.2f} seconds\n")
    print("=" * 60)
    print("Results:")
    print("=" * 60)
    
    if open_ports:
        for port_info in open_ports:
            print(f"\nPort {port_info['port']}: {port_info['state'].upper()}")
            if port_info['banner'] != 'No banner':
                # Truncate long banners for display
                banner_preview = port_info['banner'][:80]
                print(f"  Banner: {banner_preview}")
    else:
        print("\nNo open ports found on target.")
        print("(This is expected on localhost unless you have services running)")
    
    print("\n" + "=" * 60)
    print(f"Total open ports: {len(open_ports)}")
    print("=" * 60)