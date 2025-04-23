import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.ColorTab.color_picker_hex import ColorPickerHex


class ColorTab(ctk.CTkFrame):
    def __init__(self, master, top_menu_bar, *args, **kwargs) -> None:
        super().__init__(master=master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self._color_picker_rgb = ColorPickerRGB(self)
        self._color_picker_rgb.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self._color_picker_hex = ColorPickerHex(self)
        self._color_picker_hex.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self._top_menu_bar = top_menu_bar
        self._command = ""
        self._color_picker_rgb.update_command(
            self._color_picker_rgb.rgb
        )  # setting default command

    @property
    def color_picker_rgb(self) -> ColorPickerRGB:
        return self._color_picker_rgb

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        self._command = value
