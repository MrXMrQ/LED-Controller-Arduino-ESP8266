import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton
from GUI.OptionsMenu.options_menu import OptionsMenu
from GUI.window import ArduinoManager


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

        led_on_btn = CSButton(self, "🔆", command=self._led_on)
        led_on_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        led_off_btn = CSButton(self, "🔅", command=self._led_off)
        led_off_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        post_button_btn = CSButton(self, "Post", command=self._post)
        post_button_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    def _led_on(self) -> None:
        print("LED on")

    def _led_off(self) -> None:
        print("led off")

    def _post(self) -> None:
        print("POST")

    @property
    def options_menu(self) -> OptionsMenu:
        return self._options_menu
