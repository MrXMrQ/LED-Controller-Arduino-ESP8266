import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.ColorTab.color_picker_hex import ColorPickerHex


class ColorTab(ctk.CTkFrame):
    _BUTTON_STYLE = {
        "corner_radius": 7,
        "height": 50,
        "fg_color": "#8387C4",
        "hover_color": "#8378C4",
        "text_color": "white",
        "font": ("Inter", 16, "bold"),
        "border_width": 4,
        "border_color": "#2D315A",
    }

    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master=master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self._color_picker = ColorPickerRGB(self, ColorTab._BUTTON_STYLE)
        self._color_picker.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self._color_picker_hex = ColorPickerHex(self, ColorTab._BUTTON_STYLE)
        self._color_picker_hex.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
