import ast
import platform
import subprocess
from typing import Dict, Any, Union

# Import requests properly
import requests


class Arduino:
    count = 0

    def __init__(
        self,
        name: str,
        ip_address: str,
        mac_address: str,
        status: bool,
        last_command: str = "ledOn?r=255&g=156&b=100",
        single_led: tuple = (),
    ) -> None:
        self._name = name
        self._ip_address = ip_address
        self._mac_address = mac_address
        self._online = status
        self._last_command = last_command
        self._single_led = single_led

        Arduino.count += 1

    def __str__(self) -> str:
        return f"{self._name}, {self._single_led}"

    def __eq__(self, value) -> bool:
        if not isinstance(value, Arduino):
            return False

        if self._mac_address == value._mac_address:
            return True

        return False

    def __hash__(self):
        return hash(self._mac_address)

    def __call__(self) -> bool:
        ping_command = (
            "ping -n 1 -w 1" if platform.system() == "Windows" else "ping -c 1 -W 1"
        )

        response = subprocess.run(
            f"{ping_command} {self._ip_address}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        url = f"http://{self._ip_address}{'/mac'}"
        try:
            response = requests.get(url, timeout=0.1)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        return False

    def get_short_mac(self) -> str:
        if not self.mac_address or self.mac_address == "Unknown":
            return "Unknown"

        return self.mac_address[-6:].upper()

    def to_dict(self) -> Dict[str, Any]:
        status = self()
        return {
            "name": self._name,
            "ip_address": self._ip_address,
            "mac_address": self._mac_address,
            "status": status,
            "last_command": self._last_command,
            "single_led": self._single_led,
        }

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def ip_address(self) -> str:
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value: str) -> None:
        self._ip_address = value

    @property
    def mac_address(self) -> str:
        return self._mac_address

    @property
    def status(self) -> bool:
        return self._online

    @property
    def last_command(self) -> str:
        return self._last_command

    @last_command.setter
    def last_command(self, value: str) -> None:
        self._last_command = value

    @property
    def single_led(self) -> tuple:
        return self._single_led

    @single_led.setter
    def single_led(self, value) -> None:
        self._single_led = value
