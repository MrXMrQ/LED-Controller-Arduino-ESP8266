from ArduinoBackend.arduino import Arduino
from ArduinoBackend.ipScanner import IPScanner

import json
import os
from typing import List, Dict, Any, Optional, Union


class ArduinoManager:
    """
    Manages Arduino devices by tracking their information and status.
    Provides functionality to load, save, and update Arduino device data.
    """

    def __init__(self, filename="arduinos.json") -> None:
        """
        Initialize the ArduinoManager with the given storage filename.

        Args:
            filename: Path to the JSON file for storing Arduino data
        """
        self._filename = filename
        self._devices: List[Arduino] = []
        self._ip_scanner = IPScanner()

        # Load existing data or scan for new devices
        if os.path.exists(filename):
            self._load_from_file()
        else:
            scanned_devices = self._ip_scanner.get_devices()
            self._save_to_file(scanned_devices)

    def _load_from_file(self) -> None:
        """Load Arduino devices from the JSON file and update their IP addresses."""
        try:
            with open(self._filename, "r") as f:
                loaded_data = json.load(f)

            # Convert loaded data to Arduino objects
            loaded_devices = self._convert_from_dict(loaded_data)
            if loaded_devices:
                # Update IP addresses based on MAC addresses
                scanned_devices = self._ip_scanner.get_devices()
                self._update_device_information(loaded_devices, scanned_devices)
            else:
                self._save_to_file(self._ip_scanner.get_devices())
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading Arduino data: {e}")
            self._devices = []

    def _save_to_file(self, data: Union[List[Arduino], List[Dict[str, Any]]]) -> None:
        """
        Save Arduino data to the JSON file.

        Args:
            data: List of Arduino objects or dictionaries to save
        """
        try:
            # Convert data to dictionary format if needed
            save_data = data
            if data and isinstance(data[0], Arduino):
                save_data = self._convert_to_dict(data)

            with open(self._filename, "w") as f:
                json.dump(save_data, f, default=self._arduino_encoder, indent=4)

            # Update internal device list
            self._devices = (
                self._convert_from_dict(save_data)
                if save_data and isinstance(save_data[0], dict)
                else data
            )
        except IOError as e:
            print(f"Error saving Arduino data: {e}")

    def _arduino_encoder(self, obj) -> Dict[str, Any]:
        """
        JSON encoder for Arduino objects.

        Args:
            obj: Object to encode

        Returns:
            Dictionary representation of the Arduino

        Raises:
            TypeError: If object is not an Arduino
        """
        if isinstance(obj, Arduino):
            return obj.to_dict()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _update_device_information(
        self, loaded_devices: List[Arduino], scanned_devices: List[Arduino]
    ) -> None:
        """
        Update IP addresses of loaded devices based on MAC address matches with scanned devices.
        Merge loaded and scanned device lists, removing duplicates.

        Args:
            loaded_devices: List of Arduino objects loaded from file
            scanned_devices: List of Arduino objects from network scan
        """

        # Update IP addresses for existing devices
        for loaded_device in loaded_devices:
            for scanned_device in scanned_devices:
                if loaded_device == scanned_device:  # Equality checks MAC addresses
                    loaded_device.ip_address = scanned_device.ip_address

        # Merge both lists (removing duplicates by MAC address)
        all_devices = loaded_devices.copy()
        seen_macs = {device.mac_address for device in loaded_devices}

        for scanned_device in scanned_devices:
            if scanned_device.mac_address not in seen_macs:
                all_devices.append(scanned_device)
                seen_macs.add(scanned_device.mac_address)

        # Save the merged list
        self._save_to_file(all_devices)

    def _convert_to_dict(self, devices: List[Arduino]) -> List[Dict[str, Any]]:
        """
        Convert a list of Arduino objects to a list of dictionaries.

        Args:
            devices: List of Arduino objects

        Returns:
            List of dictionaries with Arduino data
        """
        return [device.to_dict() for device in devices]

    def _convert_from_dict(self, data: List[Dict[str, Any]]) -> List[Arduino]:
        """
        Convert a list of dictionaries to a list of Arduino objects.

        Args:
            data: List of dictionaries with Arduino data

        Returns:
            List of Arduino objects
        """
        if not data or not isinstance(data, list):
            return []

        arduino_list = []
        for item in data:
            if isinstance(item, dict):
                try:
                    arduino_list.append(
                        Arduino(
                            name=item.get("name", "Unknown"),
                            ip_address=item.get("ip_address", ""),
                            mac_address=item.get("mac_address", ""),
                            status=item.get("status", False),
                            last_command=item.get("last_command", ""),
                            single_led=item.get("single_led", ()),
                        )
                    )
                except Exception as e:
                    print(f"Error creating Arduino from data {item}: {e}")

        return arduino_list

    def add_device(self, device: Arduino) -> bool:
        """
        Add a new Arduino device if it's online and not already in the list.

        Args:
            device: Arduino object to add

        Returns:
            True if device was added, False otherwise
        """
        if not isinstance(device, Arduino):
            return False

        # Check if device is online
        if not device():
            return False

        # Check if device already exists
        if any(
            existing.mac_address == device.mac_address for existing in self._devices
        ):
            return False

        # Add the device and save
        updated_devices = self._devices.copy()
        updated_devices.append(device)
        self._save_to_file(updated_devices)
        return True

    def remove_device(self, mac_address: str) -> bool:
        """
        Remove an Arduino device by MAC address.

        Args:
            mac_address: MAC address of the device to remove

        Returns:
            True if device was removed, False if not found
        """
        updated_devices = [d for d in self._devices if d.mac_address != mac_address]

        if len(updated_devices) < len(self._devices):
            self._save_to_file(updated_devices)
            return True
        return False

    def rename_device(self, mac_address: str, new_name: str) -> bool:
        """
        Rename an Arduino device.

        Args:
            mac_address: MAC address of the device to rename
            new_name: New name for the device

        Returns:
            True if device was renamed, False if not found
        """
        for device in self._devices:
            if device.mac_address == mac_address:
                device.name = new_name
                self._save_to_file(self._devices)
                return True
        return False

    def refresh_devices(self) -> None:
        """
        Refresh device information by rescanning the network and updating existing devices.
        """
        scanned_devices = self._ip_scanner.get_devices()
        if self._devices:
            self._update_device_information(self._devices, scanned_devices)
        else:
            self._save_to_file(scanned_devices)

    def get_device(self, mac_address: str) -> Optional[Arduino]:
        """
        Get a device by MAC address.

        Args:
            mac_address: MAC address to search for

        Returns:
            Arduino object if found, None otherwise
        """
        for device in self._devices:
            if device.mac_address == mac_address:
                return device
        return None

    def get_online_devices(self) -> List[Arduino]:
        """
        Get a list of all devices that are currently online.

        Returns:
            List of online Arduino devices
        """
        return [device for device in self._devices if device()]

    @property
    def devices(self) -> List[Arduino]:
        """
        Get all managed Arduino devices.

        Returns:
            List of Arduino objects
        """
        return self._devices.copy()

    @devices.setter
    def devices(self, value) -> None:
        self._devices = value
