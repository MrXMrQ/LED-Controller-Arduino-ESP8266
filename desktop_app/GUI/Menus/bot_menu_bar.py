import requests
import customtkinter as ctk

from ArduinoBackend.arduino import Arduino
from ArduinoBackend.arduino_manager import ArduinoManager

from GUI.CSButton.cs_button import CSButton
from GUI.Menus.options_menu import OptionsMenu


class BotMenuBar(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(
            master,
            border_color="black",
            border_width=4,
            corner_radius=15,
            height=30,
            *args,
            **kwargs,
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._options_menu = OptionsMenu(self, ArduinoManager())
        self._options_menu.grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        self._master = master

        led_on_btn = CSButton(
            self, "🔆", command=self._led_on, font=("Segoe UI Emoji", 30)
        )
        led_on_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        led_off_btn = CSButton(
            self, "🔅", command=self._led_off, font=("Segoe UI Emoji", 30)
        )
        led_off_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        post_button_btn = CSButton(self, "Post", command=self._post)
        post_button_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    def _get_arduino(self) -> Arduino:
        if not self._options_menu.get() in self._options_menu.device_map:
            print("No Arduino Selected")
            return None

        return self._options_menu.device_map[self._options_menu.get()]

    def _led_on(self) -> None:
        arduino = self._get_arduino()

        if arduino is None:
            return

        self._request(f"http://{arduino.ip_address}/{arduino.last_command}")

    def _led_off(self) -> None:
        arduino = self._get_arduino()

        if arduino is None:
            return

        self._request(f"http://{arduino.ip_address}/ledOff")

    def _post(self) -> None:
        arduino = self._get_arduino()

        if arduino is None:
            return

        if not hasattr(self._master.top_menu_bar.active_tab, "command"):
            self._request(f"http://{arduino.ip_address}/{arduino.last_command}")
            return

        url: str = (
            f"http://{arduino.ip_address}/{self._master.top_menu_bar.active_tab.command}"
        )

        if url.replace(f"http://{arduino.ip_address}/", "") == "":
            self._request(f"http://{arduino.ip_address}/{arduino.last_command}")
            return

        if hasattr(
            self._master.top_menu_bar.active_tab, "_save_arduino_single_led_setting"
        ):
            self._master.top_menu_bar.active_tab._save_arduino_single_led_setting(
                url.replace(f"http://{arduino.ip_address}/", ""), arduino
            )

        self._save_last_command(arduino, url)
        self._request(url)

    def _save_last_command(self, arduino: Arduino, new_command) -> None:
        if not self._options_menu.get() in self._options_menu.device_map:
            return

        arduino.last_command = new_command.replace(f"http://{arduino.ip_address}/", "")

        self._options_menu.arduino_manager.update_arduino(
            arduino, arduino.last_command, "last_command"
        )

    def _request(self, url: str) -> None:
        print(url)

        try:
            response = requests.post(url)

            if response.status_code in (200, 201, 202, 203, 204):
                return

            print(f"FAIL: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"connection failure: {e}")

    @property
    def options_menu(self) -> OptionsMenu:
        return self._options_menu
