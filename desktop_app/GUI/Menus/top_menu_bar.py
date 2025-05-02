import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton

from GUI.ColorTab.color_tab import ColorTab
from GUI.AnimationTab.animation_tab import AnimationTab
from GUI.DeviceTab.device_tab import DeviceTab, OptionsMenu
from GUI.SingleLEDControllTab.single_led_controll_tab import SingleLEDControllTab


class TopMenuBar(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self, master, tab: ctk.CTkFrame, options_menu: OptionsMenu, *args, **kwargs
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
        self._options_menu = options_menu
        self._active_tab = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._device_tab = DeviceTab(self._tab, self._options_menu, self)
        self._color_tab = ColorTab(self._tab, self)
        self._animation_tab = AnimationTab(self._tab, self._color_tab, self)
        self._single_led_controll_tab = SingleLEDControllTab(
            self._tab, self._options_menu
        )

        button_data = [
            ("Devices", lambda: self._load(self._device_tab)),
            ("Color", lambda: self._load(self._color_tab)),
            ("Animation", lambda: self._load(self._animation_tab)),
            ("LED", lambda: self._load(self._single_led_controll_tab)),
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
            tab.create_command()

        if isinstance(tab, DeviceTab):
            tab.update_with_load()
            pass

        if isinstance(tab, SingleLEDControllTab):
            tab.single_led_display.draw_leds()

        self._active_tab = tab
        tab.pack(expand=True, fill="both")

    @property
    def single_led_controller_tab(self) -> SingleLEDControllTab:
        return self._single_led_controll_tab

    @property
    def active_tab(self) -> str:
        return self._active_tab

    @property
    def options_menu(self) -> OptionsMenu:
        return self._options_menu

    def set_options_menu_manager(self, value) -> None:
        self._options_menu.manager = value
        self._device_tab.options_menu_manager = value
