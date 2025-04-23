import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.Menus import options_menu
from GUI.Menus.options_menu import OptionsMenu
from GUI.SingleLEDControllTab.single_led_display import SingleLEDDisplay


class SingleLEDControllTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(self, master, options_menu: OptionsMenu, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)
        self._command = "SingleLEDControllTab"

        self._color_picker_rgb = ColorPickerRGB(self)
        self._color_picker_rgb.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=SingleLEDControllTab._PADX,
            pady=SingleLEDControllTab._PADY,
        )

        self._single_led_display = SingleLEDDisplay(
            self, options_menu, self._color_picker_rgb
        )
        self._single_led_display.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=SingleLEDControllTab._PADX,
            pady=SingleLEDControllTab._PADY,
        )

    def change_led_color(self, value: str) -> None:
        if self._single_led_display.led is None:
            return

        self._single_led_display.led.configure(True, fg_color=value)

    @property
    def single_led_display(self) -> SingleLEDDisplay:
        return self._single_led_display

    @property
    def command(self) -> str:
        return self._command
