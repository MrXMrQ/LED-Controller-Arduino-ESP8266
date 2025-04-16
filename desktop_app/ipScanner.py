import socket
import subprocess
import ipaddress
import platform
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Set, Optional
from arduino import Arduino


class IPScanner:
    """
    A class that efficiently scans the local network to detect Arduino devices
    by checking for specific HTTP endpoints.
    """

    def __init__(self, network_mask: str = "/24", exclude_ips: Set[str] = None) -> None:
        """
        Initializes the IPScanner with configurable network parameters.

        Args:
            network_mask: CIDR notation for the network mask (default: "/24")
            exclude_ips: Set of IP addresses to exclude from scanning (e.g., routers)
        """
        self.network_mask = network_mask
        self.exclude_ips = exclude_ips or {"192.168.2.1"}  # Default: exclude router
        self.local_ip = self._get_local_ip()
        self.devices: List[Arduino] = []
        self._scan_timestamp = 0

    def _get_local_ip(self) -> str:
        """
        Gets the local IP address by creating a temporary connection.

        Returns:
            The local IP address as a string
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            return local_ip
        except Exception as e:
            print(f"Error getting local IP: {e}")
            return "127.0.0.1"  # Fallback to localhost

    def _get_network_ips(self) -> List[str]:
        """
        Generates a list of all IP addresses in the local network.

        Returns:
            List of IP addresses to scan
        """
        try:
            ip_interface = ipaddress.IPv4Interface(
                f"{self.local_ip}{self.network_mask}"
            )
            network = ip_interface.network
            return [
                str(ip) for ip in network.hosts() if str(ip) not in self.exclude_ips
            ]
        except ValueError as e:
            print(f"Error creating network range: {e}")
            return []

    def _ping_device(self, ip: str) -> Tuple[str, bool]:
        """
        Pings a device to check if it's online.

        Args:
            ip: IP address to ping

        Returns:
            Tuple of (ip_address, is_reachable)
        """
        ping_command = (
            "ping -n 1 -w 1" if platform.system() == "Windows" else "ping -c 1 -W 1"
        )

        try:
            result = subprocess.run(
                f"{ping_command} {ip}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=1,  # Add timeout to prevent hanging
            )
            return ip, result.returncode == 0
        except subprocess.TimeoutExpired:
            return ip, False
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return ip, False

    def _check_arduino_http(self, ip: str) -> Optional[Arduino]:
        """
        Checks if the device at the given IP is an Arduino by verifying
        HTTP endpoints and retrieving the MAC address.

        Args:
            ip: IP address to check

        Returns:
            Arduino object if detected, None otherwise
        """
        # Get MAC address and check if endpoint exists
        mac_address = "Unknown"
        try:
            response = requests.get(f"http://{ip}/mac", timeout=1)
            if response.status_code == 200:
                mac_address = response.text.strip()
            else:
                return None
        except requests.RequestException:
            return None

        # Create and return Arduino object
        return Arduino("Arduino", ip, mac_address, True, "", ())

    def scan_network(
        self, max_workers: int = 50, rescan: bool = False
    ) -> List[Arduino]:
        """
        Scans the network for Arduino devices using parallel processing for efficiency.

        Args:
            max_workers: Maximum number of threads to use for scanning
            rescan: Force a new scan even if a recent scan was performed

        Returns:
            List of Arduino devices found on the network
        """
        # Check if we need to rescan
        current_time = time.time()
        if not rescan and self.devices and (current_time - self._scan_timestamp) < 60:
            return self.devices

        # Get IPs to scan
        ips_to_scan = self._get_network_ips()
        if not ips_to_scan:
            return []

        # First pass: Find all responsive IPs with ping (faster elimination)
        responsive_ips = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(self._ping_device, ip): ip for ip in ips_to_scan
            }
            for future in as_completed(future_to_ip):
                ip, is_reachable = future.result()
                if is_reachable:
                    responsive_ips.append(ip)

        # Second pass: Check responsive IPs for Arduino endpoints
        arduino_devices = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {
                executor.submit(self._check_arduino_http, ip): ip
                for ip in responsive_ips
            }
            for future in as_completed(future_to_ip):
                arduino = future.result()
                if arduino:
                    arduino_devices.append(arduino)

        # Update instance variables
        self.devices = arduino_devices
        self._scan_timestamp = current_time

        return arduino_devices

    def get_devices(self) -> List[Arduino]:
        """
        Returns the Arduino devices found during the most recent scan,
        or performs a new scan if no devices are available.

        Returns:
            List of Arduino devices
        """
        if not self.devices:
            return self.scan_network()
        return self.devices

    def find_device_by_mac(self, mac_address: str) -> Optional[Arduino]:
        """
        Finds a device by its MAC address from the last scan results.

        Args:
            mac_address: MAC address to search for

        Returns:
            Arduino object if found, None otherwise
        """
        for device in self.devices:
            if device.mac_address.lower() == mac_address.lower():
                return device
        return None
