import ast
import customtkinter as ctk

from ArduinoBackend.arduino import Arduino
from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.SingleLEDControllTab.single_led_display import SingleLEDDisplay


class SingleLEDControllTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(self, master, top_menu_bar, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)
        self._command = ""

        self._color_picker_rgb = ColorPickerRGB(self)
        self._color_picker_rgb.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=SingleLEDControllTab._PADX,
            pady=SingleLEDControllTab._PADY,
        )

        self._options_menu = top_menu_bar.options_menu

        self._single_led_display = SingleLEDDisplay(
            self, self._options_menu, self._color_picker_rgb
        )
        self._single_led_display.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=SingleLEDControllTab._PADX,
            pady=SingleLEDControllTab._PADY,
        )

    def change_single_led_color(self, value: str) -> None:
        if self._single_led_display.led is None:
            return

        self._single_led_display.led.configure(True, fg_color=value)
        self._single_led_display.update_dict(
            self._single_led_display.led, self._single_led_display.key
        )

    @property
    def single_led_display(self) -> SingleLEDDisplay:
        return self._single_led_display

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value) -> str:
        pass

    def update_command(self, value: dict) -> None:
        keys = list(value.keys())
        values = list(value.values())
        ziped_list = tuple((x, *y) for x, y in zip(keys, values))

        self._command = f"singleLED?singleLED={ziped_list}"

    def _save_arduino_single_led_setting(self, value, arduino: Arduino) -> None:
        if not self._options_menu.get() in self._options_menu.device_map:
            return

        arduino.single_led = ast.literal_eval(value.replace("singleLED?singleLED=", ""))

        self._options_menu.arduino_manager.update_arduino(
            arduino, arduino.single_led, "single_led"
        )
