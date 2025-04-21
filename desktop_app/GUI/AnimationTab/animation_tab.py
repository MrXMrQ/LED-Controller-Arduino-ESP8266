import customtkinter as ctk

from GUI.AnimationTab.animation_canvas import AnimationCanvas
from GUI.AnimationTab.animation_display import AnimationDisplay
from GUI.ColorTab.color_tab import ColorTab


class AnimationTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(self, master, color_tab: ColorTab, *args, **kwargs) -> None:
        super().__init__(master=master, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        buttons = [
            ("🌈 Rainbow Wave", self._on_click),
            ("💓 Pulsing Light", self._on_click),
            ("🚀 Chasing Light", self._on_click),
            ("⚡ Strobe", self._on_click),
            ("🌧️ Raindrop", self._on_click),
            ("🔥 Fireplace", self._on_click),
            ("1", self._on_click),
            ("2", self._on_click),
            ("3", self._on_click),
            ("4", self._on_click),
            ("5", self._on_click),
        ]

        self._animation_canvas = AnimationCanvas(self, buttons)
        self._animation_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self._animation_display = AnimationDisplay(self, color_tab.color_picker_rgb)
        self._animation_display.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def _on_click(self) -> None:
        print("Click!")
