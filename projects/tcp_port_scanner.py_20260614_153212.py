"""
Date: 2026-06-14
Wrote a concurrent port scanner that checks common ports and tries to identify services by their banners — wanted something faster than nmap for quick checks on my local network.
"""

#!/usr/bin/env python3
"""
TCP Port Scanner with Service Detection

A simple multi-threaded port scanner that checks common ports
and attempts basic service fingerprinting via banner grabbing.
Mario - 2024
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
import time


# Common ports I actually want to check regularly
COMMON_PORTS = {
    20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
    25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
    143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
    3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
    8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 27017: 'MongoDB'
}


def scan_port(host: str, port: int, timeout: float = 1.0) -> Tuple[int, bool, Optional[str]]:
    """
    Attempt to connect to a single port and grab banner if possible.
    
    Returns a tuple of (port, is_open, banner).
    The banner grabbing is pretty naive but works for most text-based protocols.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            # Port is open, try to grab a banner
            banner = None
            try:
                # Some services send data immediately (like SSH)
                sock.settimeout(0.5)
                data = sock.recv(1024)
                banner = data.decode('utf-8', errors='ignore').strip()
            except socket.timeout:
                # No immediate banner, try sending HTTP request for web servers
                if port in [80, 443, 8080, 8443]:
                    try:
                        sock.send(b'GET / HTTP/1.0\r\n\r\n')
                        data = sock.recv(1024)
                        banner = data.decode('utf-8', errors='ignore').strip()[:100]
                    except:
                        pass
            except:
                pass
            
            return (port, True, banner)
        else:
            return (port, False, None)
    except socket.error:
        return (port, False, None)
    finally:
        sock.close()


def scan_host(host: str, ports: List[int], max_workers: int = 50, timeout: float = 1.0) -> List[dict]:
    """
    Scan multiple ports on a host using a thread pool.
    
    max_workers controls concurrency — 50 seems like a sweet spot
    where it's fast but doesn't overwhelm the target or my machine.
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all port scans
        future_to_port = {
            executor.submit(scan_port, host, port, timeout): port 
            for port in ports
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_port):
            port, is_open, banner = future.result()
            if is_open:
                service = COMMON_PORTS.get(port, 'unknown')
                results.append({
                    'port': port,
                    'service': service,
                    'banner': banner
                })
    
    # Sort by port number for cleaner output
    return sorted(results, key=lambda x: x['port'])


def resolve_hostname(host: str) -> Optional[str]:
    """
    Resolve hostname to IP address.
    
    Returns None if resolution fails — helps catch typos early.
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def print_scan_results(host: str, results: List[dict], elapsed: float):
    """
    Pretty-print the scan results.
    
    I wanted something readable for quick terminal checks.
    """
    print(f"\n{'='*70}")
    print(f"Scan Results for {host}")
    print(f"{'='*70}")
    print(f"Scanned in {elapsed:.2f} seconds")
    print(f"Found {len(results)} open port(s)\n")
    
    if results:
        print(f"{'PORT':<8} {'SERVICE':<15} {'BANNER'}")
        print(f"{'-'*70}")
        for result in results:
            port = result['port']
            service = result['service']
            banner = result['banner'] if result['banner'] else '(no banner)'
            # Truncate long banners to keep output clean
            if len(banner) > 45:
                banner = banner[:42] + '...'
            print(f"{port:<8} {service:<15} {banner}")
    else:
        print("No open ports found in the scanned range.")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Demo: scan localhost for common ports
    target = "localhost"
    
    print(f"Starting port scan on {target}...")
    print(f"Checking {len(COMMON_PORTS)} common ports with multi-threading")
    
    # Resolve hostname first
    ip = resolve_hostname(target)
    if not ip:
        print(f"Error: Could not resolve hostname '{target}'")
        exit(1)
    
    print(f"Resolved {target} -> {ip}\n")
    
    # Run the scan
    start_time = time.time()
    open_ports = scan_host(ip, list(COMMON_PORTS.keys()), max_workers=50, timeout=1.0)
    elapsed = time.time() - start_time
    
    # Display results
    print_scan_results(target, open_ports, elapsed)
    
    # Quick tip for usage
    print("Tip: Edit COMMON_PORTS dict or pass custom port list to scan_host()")
    print("     to scan different ports. Adjust max_workers for speed/stealth tradeoff.")