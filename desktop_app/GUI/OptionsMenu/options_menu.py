from cgitb import text
import customtkinter as ctk

from arduinoManager import ArduinoManager


class OptionsMenu(ctk.CTkOptionMenu):
    def __init__(
        self,
        master,
        manager: ArduinoManager,
        fg_color="gray25",
        button_color="gray25",
        button_hover_color="gray26",
        dropdown_fg_color="gray25",
        dropdown_text_color="white",
        text_color="white",
        font=("Inter", 20, "bold"),
        height=50,
        corner_radius=15,
        *args,
        **kwargs,
    ) -> None:

        self._arduino_manger = manager
        self._device_map = self._build_device_map()
        options = list(self._device_map.keys())
        default_value = options[0] if options else "No devices"

        super().__init__(
            master,
            values=options,
            variable=ctk.StringVar(value=default_value),
            command=self._on_option_change,
            fg_color=fg_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            dropdown_fg_color=dropdown_fg_color,
            dropdown_text_color=dropdown_text_color,
            text_color=text_color,
            font=font,
            dropdown_font=font,
            height=height,
            corner_radius=corner_radius,
            *args,
            **kwargs,
        )

    def _build_device_map(self) -> dict:
        device_map = {}
        name_counts = {}

        for device in self._arduino_manger.devices:
            if device():
                name = device.name

                if name in device_map:
                    if name_counts.get(name, 0) == 0:
                        original_device = device_map[name]
                        short_mac_address = original_device.get_short_mac()
                        new_key = f"{name} ({short_mac_address})"
                        device_map[new_key] = original_device
                        del device_map[name]

                    name_counts[name] = name_counts.get(name, 0) + 1

                    short_mac_address = device.get_short_mac()
                    key = f"{name} ({short_mac_address})"
                    device_map[key] = device
                else:
                    device_map[name] = device
                    name_counts[name] = 0

        return device_map

    def _on_option_change(self, value) -> None:
        print(value)

    @property
    def device_map(self) -> dict:
        return self._device_map

    @property
    def manager(self) -> ArduinoManager:
        return self._arduino_manger
