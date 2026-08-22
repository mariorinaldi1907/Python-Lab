"""
Date: 2026-08-22
Created a network scanner that pings hosts in a subnet and optionally checks common ports to see what's actually alive on my home network.
"""

#!/usr/bin/env python3
"""
Subnet Scanner - Find active hosts on a local network

I built this because I kept losing track of what devices were connected
to my home network. It does ICMP pings first (fast), then optionally
checks common ports to identify services.
"""

import socket
import subprocess
import platform
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import IPv4Network
import argparse


class SubnetScanner:
    """
    Scans a subnet for active hosts using ICMP and TCP probes.
    
    Uses threading to speed things up since network I/O is slow.
    ICMP requires elevated privileges on some systems, so we fall back
    to TCP if ping fails.
    """
    
    # Common ports I actually care about on my network
    COMMON_PORTS = {
        22: 'SSH',
        80: 'HTTP',
        443: 'HTTPS',
        3389: 'RDP',
        5000: 'Flask/Dev',
        8080: 'HTTP-Alt',
        9090: 'Prometheus'
    }
    
    def __init__(self, subnet, timeout=1.0, max_workers=50):
        """
        Args:
            subnet: CIDR notation like '192.168.1.0/24'
            timeout: seconds to wait per probe
            max_workers: how many threads to use for scanning
        """
        self.subnet = IPv4Network(subnet, strict=False)
        self.timeout = timeout
        self.max_workers = max_workers
        self.active_hosts = []
    
    def ping_host(self, ip):
        """
        Try to ping a host using the system's ping command.
        
        Returns True if host responds, False otherwise.
        This is faster than TCP but needs proper permissions.
        """
        # Different ping syntax for Windows vs Unix
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        # Quiet mode, single packet, short timeout
        command = ['ping', param, '1', '-W' if platform.system().lower() != 'windows' else '-w', '1', str(ip)]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=self.timeout + 0.5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def check_port(self, ip, port):
        """
        Try to connect to a specific TCP port.
        
        This is slower than ping but works without special privileges
        and tells us what services are running.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            return result == 0
        except socket.error:
            return False
    
    def scan_host(self, ip, check_ports=False):
        """
        Scan a single host - ping it, optionally check ports.
        
        Returns dict with host info if active, None otherwise.
        """
        ip_str = str(ip)
        
        # Try ICMP first - it's faster
        is_alive = self.ping_host(ip)
        
        # If ping failed, try a TCP connect to port 80 as fallback
        # (some hosts block ICMP but still run services)
        if not is_alive:
            is_alive = self.check_port(ip, 80)
        
        if not is_alive:
            return None
        
        host_info = {'ip': ip_str, 'ports': []}
        
        # Try to get hostname - sometimes useful
        try:
            hostname = socket.gethostbyaddr(ip_str)[0]
            host_info['hostname'] = hostname
        except socket.herror:
            host_info['hostname'] = 'unknown'
        
        # Check common ports if requested
        if check_ports:
            for port, service in self.COMMON_PORTS.items():
                if self.check_port(ip, port):
                    host_info['ports'].append({'port': port, 'service': service})
        
        return host_info
    
    def scan(self, check_ports=False):
        """
        Scan the entire subnet using thread pool for speed.
        
        Returns list of active hosts with their info.
        """
        print(f"[*] Scanning {self.subnet} ({self.subnet.num_addresses} addresses)")
        print(f"[*] Using {self.max_workers} workers, timeout={self.timeout}s")
        
        # Use thread pool to scan many hosts concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scan jobs
            future_to_ip = {
                executor.submit(self.scan_host, ip, check_ports): ip 
                for ip in self.subnet.hosts()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    if result:
                        self.active_hosts.append(result)
                        print(f"[+] Found: {result['ip']} ({result['hostname']})")
                except Exception as e:
                    print(f"[!] Error scanning {ip}: {e}", file=sys.stderr)
        
        return self.active_hosts


def main():
    """Demo the scanner on a local subnet"""
    parser = argparse.ArgumentParser(description='Scan a subnet for active hosts')
    parser.add_argument('subnet', nargs='?', default='192.168.1.0/24',
                       help='Subnet in CIDR notation (default: 192.168.1.0/24)')
    parser.add_argument('-p', '--ports', action='store_true',
                       help='Also check common ports (slower)')
    parser.add_argument('-t', '--timeout', type=float, default=1.0,
                       help='Timeout in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    scanner = SubnetScanner(args.subnet, timeout=args.timeout)
    active_hosts = scanner.scan(check_ports=args.ports)
    
    print(f"\n{'='*60}")
    print(f"Scan complete! Found {len(active_hosts)} active host(s)")
    print(f"{'='*60}\n")
    
    for host in active_hosts:
        print(f"IP: {host['ip']:15} | Hostname: {host['hostname']}")
        if host['ports']:
            for port_info in host['ports']:
                print(f"  └─ Port {port_info['port']}: {port_info['service']}")
            print()


if __name__ == "__main__":
    main()