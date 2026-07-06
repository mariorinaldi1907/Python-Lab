"""
Date: 2026-07-06
Wrote a port scanner to check which services are running on my local network — useful for debugging my homelab setup.
"""

#!/usr/bin/env python3
"""
Simple multi-threaded port scanner for checking open ports on local machines.
I built this because I kept forgetting which services were running where on my homelab.
"""

import socket
import threading
from datetime import datetime
from queue import Queue


# Common ports I actually care about on my network
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
    9090: "Prometheus",
}


class PortScanner:
    """
    Multi-threaded port scanner that checks if ports are open on a target host.
    Uses a queue to distribute work across threads for faster scanning.
    """

    def __init__(self, target, ports, num_threads=50, timeout=1.0):
        """
        Initialize the port scanner.

        Args:
            target: IP address or hostname to scan
            ports: List of ports to check
            num_threads: Number of worker threads (more = faster but noisier)
            timeout: Socket timeout in seconds (lower = faster but less reliable)
        """
        self.target = target
        self.ports = ports
        self.num_threads = num_threads
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()
        self.queue = Queue()

    def _scan_port(self, port):
        """
        Attempt to connect to a single port.
        Returns True if connection succeeds (port is open), False otherwise.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            # connect_ex returns 0 on success
            return result == 0
        except socket.gaierror:
            # Couldn't resolve hostname
            return False
        except socket.error:
            # Generic socket error
            return False

    def _worker(self):
        """
        Worker thread that pulls ports from the queue and scans them.
        This is where the actual threading magic happens.
        """
        while True:
            port = self.queue.get()
            if port is None:
                # Poison pill to shut down the thread
                break

            if self._scan_port(port):
                with self.lock:
                    self.open_ports.append(port)

            self.queue.task_done()

    def scan(self):
        """
        Start the scan using multiple worker threads.
        Returns a sorted list of open ports.
        """
        # Spin up worker threads
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            threads.append(t)

        # Queue up all the ports to scan
        for port in self.ports:
            self.queue.put(port)

        # Wait for all tasks to complete
        self.queue.join()

        # Send poison pills to shut down workers
        for _ in range(self.num_threads):
            self.queue.put(None)

        # Wait for threads to finish
        for t in threads:
            t.join()

        return sorted(self.open_ports)


def get_service_name(port):
    """
    Return the common service name for a port, or 'Unknown' if not recognized.
    """
    return COMMON_PORTS.get(port, "Unknown")


def scan_host(target, port_range=None, common_only=True, num_threads=50):
    """
    Scan a host for open ports and display results.

    Args:
        target: IP or hostname to scan
        port_range: Tuple of (start, end) ports, or None to use common ports
        common_only: If True, only scan common service ports
        num_threads: Number of scanning threads
    """
    print(f"\n[*] Starting scan on {target}")
    print(f"[*] Scan started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # Decide which ports to scan
    if common_only and port_range is None:
        ports_to_scan = list(COMMON_PORTS.keys())
        print(f"[*] Scanning {len(ports_to_scan)} common ports...")
    elif port_range:
        ports_to_scan = range(port_range[0], port_range[1] + 1)
        print(f"[*] Scanning ports {port_range[0]}-{port_range[1]}...")
    else:
        ports_to_scan = range(1, 1025)  # Well-known ports
        print(f"[*] Scanning ports 1-1024...")

    # Run the scan
    scanner = PortScanner(target, ports_to_scan, num_threads=num_threads)
    open_ports = scanner.scan()

    print("-" * 60)
    if open_ports:
        print(f"[+] Found {len(open_ports)} open port(s):\n")
        for port in open_ports:
            service = get_service_name(port)
            print(f"    Port {port:5d} : {service}")
    else:
        print("[-] No open ports found")

    print(f"\n[*] Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # Demo: scan localhost for common services
    # This is what I use to check what's running after I spin up Docker containers
    print("=" * 60)
    print("Local Port Scanner - checking what's listening on localhost")
    print("=" * 60)

    scan_host("127.0.0.1", common_only=True, num_threads=20)

    # Uncomment to scan a specific range (e.g., for a web server)
    # print("\n" + "=" * 60)
    # scan_host("127.0.0.1", port_range=(8000, 8100), num_threads=20)