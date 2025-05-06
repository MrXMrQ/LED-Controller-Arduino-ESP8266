import socket
import ipaddress
import concurrent.futures
import time
import requests

from ArduinoBackend.arduino import Arduino


class NetworkScanner:
    def __init__(self, timeout=0.5, max_workers=100) -> None:
        self._timeout = timeout
        self._max_workers = max_workers
        self._http_devices = []

    def _get_network_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connect to a public DNS server to determine local IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()

            # Default to /24 subnet mask which is common for home networks
            return f"{'.'.join(ip.split('.')[:3])}.0/24"
        except Exception:
            s.close()
            # Fallback to localhost if no connection
            return "127.0.0.1/24"

    def _check_port(self, ip, port) -> str | None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self._timeout)

        try:
            result = sock.connect_ex((str(ip), port))
            if result == 0:
                return str(ip)
        except:
            pass
        finally:
            sock.close()

        return None

    def scan_network(self, network=None, port=80) -> list:
        """
        Scan the network for devices with the specified port open.

        Args:
            network (str, optional): Network in CIDR notation (e.g., '192.168.1.0/24')
            port (int, optional): Port to scan for

        Returns:
            list: List of dictionaries containing device information
        """
        start_time = time.time()

        if network is None:
            network = self._get_network_ip()

        # Clear previous results
        self._http_devices = []

        ip_network = ipaddress.IPv4Network(network, strict=False)
        total_hosts = ip_network.num_addresses - 2

        print(f"Scanning {total_hosts} hosts on {network} for port {port}...")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as executor:
            ip_list = list(ip_network.hosts())
            future_to_ip = {
                executor.submit(self._check_port, ip, port): ip for ip in ip_list
            }

            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future.result()

                if ip:
                    response = requests.get(f"http://{ip}/mac")

                    if (
                        response.status_code not in (200, 201, 202, 203, 204)
                        or "html" in response.text
                    ):
                        continue

                    mac = response.text

                    a = Arduino(
                        name=mac,
                        ip_address=str(ip),
                        mac_address=mac.upper(),
                        status=True,
                    )

                    self._http_devices.append(a)

        scan_time = time.time() - start_time
        print(f"Scan completed in {scan_time:.2f} seconds")
        print(f"Found {len(self._http_devices)} devices with port {port} open")

        return self._http_devices

    def __str__(self) -> None:
        string = ""
        for arduino in self._http_devices:
            string += f"{str(arduino)}\n"

        return string

    @property
    def http_devices(self) -> list:
        return self._http_devices


# scanner = NetworkScanner(timeout=0.3, max_workers=150)
# devices = scanner.scan_network()
