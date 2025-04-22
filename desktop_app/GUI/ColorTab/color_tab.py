import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.ColorTab.color_picker_hex import ColorPickerHex


class ColorTab(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master=master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self._color_picker_rgb = ColorPickerRGB(self)
        self._color_picker_rgb.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self._color_picker_hex = ColorPickerHex(self)
        self._color_picker_hex.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    @property
    def color_picker_rgb(self) -> ColorPickerRGB:
        return self._color_picker_rgb
