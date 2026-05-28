"""
Date: 2026-05-28
Wrote a multi-threaded port scanner to check which services are running on my local network — uses socket connections with configurable timeout and thread pooling.
"""

#!/usr/bin/env python3
"""
Local Port Scanner
A simple multi-threaded port scanner that checks which ports are open on a target host.
I built this because I got tired of waiting for nmap when I just wanted to quickly check
what services were running on my raspberry pi or local servers.
"""

import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import argparse


# Common ports and their typical services - helps identify what's probably running
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


def scan_port(host, port, timeout=1.0):
    """
    Attempt to connect to a single port on the target host.
    
    Returns a tuple: (port, is_open, service_name)
    I'm using a short timeout because I don't want to wait around for closed ports,
    but you might need to increase it for slower networks.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        
        # connect_ex returns 0 if connection succeeded
        if result == 0:
            service = COMMON_PORTS.get(port, "Unknown")
            return (port, True, service)
        else:
            return (port, False, None)
    except socket.gaierror:
        # Couldn't resolve hostname
        return (port, False, None)
    except socket.error:
        # Connection failed for some other reason
        return (port, False, None)


def scan_port_range(host, start_port, end_port, timeout=1.0, max_workers=100):
    """
    Scan a range of ports on the target host using a thread pool.
    
    The thread pool is important here - scanning ports sequentially would take forever.
    I cap it at 100 workers by default to avoid hammering the network too hard,
    but you can adjust based on your needs.
    """
    open_ports = []
    
    print(f"\n[*] Starting scan on {host}")
    print(f"[*] Scanning ports {start_port}-{end_port}")
    print(f"[*] Timeout: {timeout}s, Workers: {max_workers}")
    print("-" * 60)
    
    start_time = datetime.now()
    
    # Using ThreadPoolExecutor because socket operations are I/O bound
    # For CPU-bound work I'd use ProcessPoolExecutor instead
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all port scan tasks
        future_to_port = {
            executor.submit(scan_port, host, port, timeout): port
            for port in range(start_port, end_port + 1)
        }
        
        # Process results as they complete (not in order)
        for future in as_completed(future_to_port):
            port, is_open, service = future.result()
            
            if is_open:
                open_ports.append((port, service))
                # Print immediately when we find an open port - more satisfying
                print(f"[+] Port {port:5d} OPEN    {service}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 60)
    print(f"[*] Scan completed in {duration:.2f} seconds")
    print(f"[*] Found {len(open_ports)} open port(s)")
    
    return open_ports


def resolve_host(host):
    """
    Resolve hostname to IP address.
    
    This catches common issues early before we start scanning.
    """
    try:
        ip = socket.gethostbyname(host)
        print(f"[*] Resolved {host} to {ip}")
        return ip
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {host}")
        sys.exit(1)


def main():
    """
    Main entry point with argument parsing.
    
    I wanted this to be usable both as a script and importable,
    so I kept the CLI logic separate from the scanning logic.
    """
    parser = argparse.ArgumentParser(
        description="Scan ports on a target host to see what's open",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 192.168.1.1 -p 1-1000          # Scan first 1000 ports
  %(prog)s localhost -p 80,443,8080       # Scan specific ports
  %(prog)s example.com -p 1-65535 -t 2.0  # Full scan with 2s timeout
        """
    )
    
    parser.add_argument("host", help="Target hostname or IP address")
    parser.add_argument(
        "-p", "--ports",
        default="1-1024",
        help="Port range (e.g., 1-1024) or comma-separated list (e.g., 22,80,443)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout in seconds (default: 1.0)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=100,
        help="Number of concurrent threads (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Resolve the hostname first
    ip = resolve_host(args.host)
    
    # Parse port specification
    if "-" in args.ports:
        # Range like "1-1024"
        start, end = map(int, args.ports.split("-"))
    elif "," in args.ports:
        # Comma-separated like "22,80,443"
        port_list = list(map(int, args.ports.split(",")))
        start = min(port_list)
        end = max(port_list)
        # This is a bit hacky but works for the demo
        # In production I'd refactor to handle arbitrary port lists better
    else:
        # Single port
        start = end = int(args.ports)
    
    # Run the scan
    open_ports = scan_port_range(ip, start, end, args.timeout, args.workers)
    
    if not open_ports:
        print("\n[!] No open ports found")
    
    return open_ports


if __name__ == "__main__":
    # Demo mode - scan localhost for common services
    # This is what runs when you just execute the script directly
    
    print("=" * 60)
    print("LOCAL PORT SCANNER - Demo Mode")
    print("=" * 60)
    
    # If arguments provided, use them; otherwise run demo
    if len(sys.argv) > 1:
        main()
    else:
        print("\n[*] No arguments provided - running demo scan on localhost")
        print("[*] Usage: python local_port_scanner.py <host> -p <ports>")
        print()
        
        # Scan common ports on localhost as a demo
        demo_ports = [22, 80, 443, 3000, 5432, 8080, 8443]
        start_port = min(demo_ports)
        end_port = max(demo_ports)
        
        open_ports = scan_port_range(
            "127.0.0.1",
            start_port,
            end_port,
            timeout=0.5,
            max_workers=50
        )
        
        if open_ports:
            print("\n[*] You have these services running locally:")
            for port, service in open_ports:
                print(f"    - Port {port}: {service}")