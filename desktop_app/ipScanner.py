import socket
import subprocess
import ipaddress
import platform
import requests
from concurrent.futures import ThreadPoolExecutor


class IPScanner:
    """
    A class that scans the local network to detect devices that are reachable
    and have a specific HTTP path.
    """

    def __init__(self) -> None:
        """
        Initializes the IPScanner class by obtaining the local IP address
        and scanning the local network for reachable devices.

        This method retrieves the local machine's IP address and uses it to
        initiate a scan of the local network. The devices that are reachable
        and responsive to HTTP requests on a specific path are collected.
        """

        self.local_ip = self.get_local_ip()
        self.devices = self.scan_network(self.local_ip)

    def get_local_ip(self) -> str:
        """
        Retrieves the local IP address of the machine by establishing a socket
        connection to a remote server (Google's public DNS).

        The method uses the socket library to create a UDP connection to the server
        at '8.8.8.8' (Google DNS) to determine the local IP address that can be
        used for network scanning.

        Returns:
            str: The local IP address of the machine.
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip

    def scan_network(self, local_ip) -> list:
        """
        Scans the local network to identify all reachable devices.

        The method determines the network range based on the local IP address,
        performs a ping scan to find devices that are responsive, and then checks
        if these devices are accessible via an HTTP request to a specific path.

        Args:
            local_ip (str): The local IP address used to determine the network range.

        Returns:
            list: A list of IP addresses of reachable devices that respond to HTTP requests
                  on a specific path.
        """

        ip_obj = ipaddress.IPv4Interface(local_ip + "/24")
        network = ip_obj.network

        ping_command = (
            "ping -n 1 -w 1" if platform.system() == "Windows" else "ping -c 1 -W 1"
        )

        reachable_devices = []

        ips_to_scan = [str(ip) for ip in network.hosts()]

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(
                lambda ip: self.ping_device(ip, ping_command), ips_to_scan
            )

        for ip_str, is_reachable in results:
            if is_reachable:
                if self.check_http(ip_str, "/esp8266"):
                    reachable_devices.append(ip_str)

        reachable_devices.remove("192.168.2.1")

        return reachable_devices

    def ping_device(self, ip_str, ping_command):
        """
        Pings a device with the given IP address and returns whether it is reachable.

        The method uses the `subprocess` module to run the system ping command
        and checks the return code to determine if the device responded.

        Args:
            ip_str (str): The IP address of the device to ping.
            ping_command (str): The command used to ping the device (depends on the OS).

        Returns:
            tuple: A tuple containing the IP address and a boolean indicating whether
                   the device is reachable (True if reachable, False otherwise).
        """

        response = subprocess.run(
            f"{ping_command} {ip_str}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return ip_str, response.returncode == 0

    def check_http(self, ip_str: str, path: str) -> bool:
        """
        Checks if the device at the specified IP address is responding to an HTTP request
        at a specific path (e.g., /esp8266).

        This method sends a GET request to the device and checks if it responds with
        an HTTP status code 200 (OK).

        Args:
            ip_str (str): The IP address of the device to check.
            path (str): The path to request from the device.

        Returns:
            bool: True if the device responds with a 200 OK status code, False otherwise.
        """

        url = f"http://{ip_str}{path}"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        return False

    def get_devices(self) -> list:
        return self.devices
