import customtkinter as ctk

from ArduinoBackend.arduino import Arduino
from ArduinoBackend.arduinoManager import ArduinoManager
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
        self._last_command = ""

        led_on_btn = CSButton(
            self, "🔆", command=self._led_on, font=("Segoe UI Emoji", 30)
        )
        led_on_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        led_off_btn = CSButton(
            self, "🔅", command=self._led_off, font=("Segoe UI Emoji", 30)
        )
        led_off_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        post_button_btn = CSButton(self, "Post", command=self._post)
        post_button_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    def _led_on(self) -> None:
        print("LED on")

    def _led_off(self) -> None:
        print("led off")

    def _post(self) -> None:
        if not hasattr(self._master.top_menu_bar.active_tab, "command"):
            print(self._last_command)
            return

        if not self._options_menu.get() in self._options_menu.device_map:
            print("No Arduino Selected")
            return

        arduino: Arduino = self._options_menu.device_map[self._options_menu.get()]

        url: str = (
            f"http://{arduino.ip_address}/{self._master.top_menu_bar.active_tab.command}"
        )

        if url.replace(f"http://{arduino.ip_address}/", "") == "":
            print(self._last_command)
            return

        if hasattr(
            self._master.top_menu_bar.active_tab, "_save_arduino_single_led_setting"
        ):
            self._master.top_menu_bar.active_tab._save_arduino_single_led_setting(
                url.replace(f"http://{arduino.ip_address}/", ""), arduino
            )

        print(url)
        self._last_command = url

    @property
    def options_menu(self) -> OptionsMenu:
        return self._options_menu
