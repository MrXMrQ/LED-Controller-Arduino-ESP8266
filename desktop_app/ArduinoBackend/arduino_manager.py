import os
import json

from ArduinoBackend.network_scanner import NetworkScanner
from ArduinoBackend.arduino import Arduino


class ArduinoManager:
    def __init__(self, filename: str = "arduino.json") -> None:
        self._filename = filename
        self._network_scanner = NetworkScanner(timeout=0.3, max_workers=100)
        self._data: list[Arduino] = []

        if os.path.exists(filename):
            self.load_and_upate_from_file()
        else:
            self._create_file()

    def _create_file(self) -> None:
        self._data = [arduino for arduino in self._network_scanner.scan_network()]

        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(
                self._convert_data_to_dict(self._data), f, ensure_ascii=False, indent=4
            )

    def load_and_upate_from_file(self) -> list:
        self._data = []

        with open(self._filename, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        loaded_data = self._convert_data_from_dict(loaded_data)
        scanned_data = self._network_scanner.scan_network()

        for scanned in scanned_data:
            found = False
            for loaded in loaded_data:
                if scanned == loaded:
                    loaded.status = scanned.status
                    loaded.ip_address = scanned.ip_address
                    self._data.append(loaded)
                    found = True
                    break
            if not found:
                self._data.append(scanned)

        for loaded in loaded_data:
            if loaded not in self._data:
                loaded.status = False
                self._data.append(loaded)

        self._save_to_file(self._data)

    def _save_to_file(self, data: list[Arduino]) -> None:
        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(self._convert_data_to_dict(data), f, ensure_ascii=False, indent=4)
            self._data = data

    def _convert_data_to_dict(self, list_to_convert: list[Arduino]) -> list[dict]:
        return [arduino.to_dict() for arduino in list_to_convert]

    def _convert_data_from_dict(self, list_to_convert: list[dict]) -> None:
        if not list_to_convert:
            return []

        arduino_list = []
        for item in list_to_convert:
            try:
                arduino_list.append(
                    Arduino(
                        name=item.get("name"),
                        ip_address=item.get("ip_address"),
                        mac_address=item.get("mac_address"),
                        status=item.get("status"),
                        last_command=item.get("last_command"),
                        single_led=item.get("single_led"),
                    )
                )
            except Exception as e:
                print(f"Error creating Arduino from data {item}: {e}")

        return arduino_list

    def update_arduino(self, arduino_to_update, value: str, attribut: str) -> None:
        for arduino in self._data:
            if arduino == arduino_to_update:
                arduino.__setattr__(attribut, value)

        self._save_to_file(self._data)

    @property
    def data(self) -> list[Arduino]:
        return self._data
