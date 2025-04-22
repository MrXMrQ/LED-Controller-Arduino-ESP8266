import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton

from GUI.ColorTab.color_tab import ColorTab
from GUI.AnimationTab.animation_tab import AnimationTab
from GUI.DeviceTab.device_tab import DeviceTab
from GUI.window import ArduinoManager


class TopMenuBar(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self, master, tab: ctk.CTkFrame, device_map: dict, *args, **kwargs
    ) -> None:
        super().__init__(
            master,
            border_color="black",
            border_width=4,
            corner_radius=15,
            height=30,
            *args,
            **kwargs,
        )

        self._tab = tab
        self._device_map = device_map

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._device_tab = DeviceTab(self._tab, self._device_map)
        self._color_tab = ColorTab(self._tab)
        self._animation_tab = AnimationTab(self._tab, self._color_tab)

        button_data = [
            ("Devices", lambda: self._load(self._device_tab)),
            ("Color", lambda: self._load(self._color_tab)),
            ("Animation", lambda: self._load(self._animation_tab)),
            ("LED", lambda: print("click")),
        ]
        count = 0

        for text, command in button_data:
            CSButton(self, text, command).grid(
                row=0,
                column=count,
                sticky="ew",
                padx=TopMenuBar._PADX,
                pady=TopMenuBar._PADY,
            )
            count += 1

        self._load(self._device_tab)

    def _load(self, tab: ctk.CTkFrame) -> None:
        for child in self._tab.winfo_children():
            child.pack_forget()

        if isinstance(tab, AnimationTab):
            tab.animation_display.update_color_display()

        if isinstance(tab, DeviceTab):
            tab.add_content()

        tab.pack(expand=True, fill="both")
